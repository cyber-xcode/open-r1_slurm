import os
from abc import ABC, abstractmethod
from typing import List

#os.environ["HF_HOME"] = os.environ.get("HF_HOME", "./hf_home")


EOS = [
    "<|endoftext|>",
    "<|endofmask|>",
    "</s>",
    "\n</answer>",
]


class DecoderBase(ABC):
    def __init__(
        self,
        name: str,
        batch_size: int = 1,
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        direct_completion: bool = True,
        dtype: str = "bfloat16",  # default
        trust_remote_code: bool = False,
        dataset: str = None,
    ) -> None:
        print("Initializing a decoder model: {} ...".format(name))
        self.name = name
        self.batch_size = batch_size
        self.temperature = temperature
        self.eos = EOS
        self.skip_special_tokens = False
        self.max_new_tokens = max_new_tokens
        self.direct_completion = direct_completion
        self.dtype = dtype
        self.trust_remote_code = trust_remote_code

    @abstractmethod
    def codegen(self, prompt: str, do_sample: bool = True, num_samples: int = 200) -> List[str]:
        pass

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class VLlmDecoder(DecoderBase):
    def __init__(self, name: str, tensor_parallel_size = 1, **kwargs) -> None:
        from vllm import LLM
        super().__init__(name, **kwargs)

        kwargs = {
            "tensor_parallel_size": tensor_parallel_size, #int(os.getenv("VLLM_N_GPUS", "1"))
            "dtype": self.dtype,
            "trust_remote_code": self.trust_remote_code,
            "enforce_eager": True,
            "gpu_memory_utilization": os.environ.get("gpu_memory_utilization",0.94)
        }
        print(kwargs)
        self.llm = LLM(model=name, max_model_len=2048, **kwargs)

    def codegen(self, prompt: str, do_sample: bool = True, num_samples: int = 200) -> List[str]:
        from vllm import SamplingParams
        if do_sample:
            assert self.temperature > 0, "Temperature must be greater than 0!"
        batch_size = min(self.batch_size, num_samples)

        vllm_outputs = self.llm.generate(
            [prompt] * batch_size,
            SamplingParams(
                temperature=self.temperature,
                max_tokens=self.max_new_tokens,
                top_p=0.95 if do_sample else 1.0,
                stop=self.eos,
            ),
            use_tqdm=False,
        )

        gen_strs = [x.outputs[0].text.replace("\t", "    ") for x in vllm_outputs]
        return gen_strs


class VLlmAWQDecoder(DecoderBase):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)

        kwargs = {
            "tensor_parallel_size": int(os.getenv("VLLM_N_GPUS", "1")),
            "dtype": torch.float16,
            "trust_remote_code": self.trust_remote_code,
            "quantization": "AWQ",
        }

        self.llm = LLM(model=name, max_model_len=2048, **kwargs)

    def codegen(self, prompt: str, do_sample: bool = True, num_samples: int = 200) -> List[str]:
        if do_sample:
            assert self.temperature > 0, "Temperature must be greater than 0!"
        batch_size = min(self.batch_size, num_samples)

        vllm_outputs = self.llm.generate(
            [prompt] * batch_size,
            SamplingParams(
                temperature=self.temperature,
                max_tokens=self.max_new_tokens,
                top_p=0.95 if do_sample else 1.0,
                stop=self.eos,
            ),
            use_tqdm=False,
        )

        gen_strs = [x.outputs[0].text.replace("\t", "    ") for x in vllm_outputs]
        return gen_strs


class AWQChatML(VLlmAWQDecoder):
    def __init__(self, name: str, tensor_parallel_size, **kwargs) -> None:
        kwargs["direct_completion"] = False
        super().__init__(name, **kwargs)
        #self.eos += ["\n```"]

    def codegen(self, prompt: str, do_sample: bool = True, num_samples: int = 200) -> List[str]:
        if do_sample:
            assert self.temperature > 0, "Temperature must be greater than 0!"

        input = f"""<|im_start|>system
You are a helpful AI Assistant that provides well-reasoned and detailed responses. You first think about the reasoning process as an internal monologue and then provide the user with the answer. Respond in the following format: <think>\n...\n</think>\n<answer>\n...\n</answer><|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant
<think>
"""
        return VLlmDecoder.codegen(self, input, do_sample, num_samples)


class ChatML(VLlmDecoder):
    def __init__(self, name: str, tensor_parallel_size, **kwargs) -> None:
        kwargs["direct_completion"] = False
        super().__init__(name, tensor_parallel_size, **kwargs)
        #self.eos += ["\n```"]

    def codegen(self, prompt: str, do_sample: bool = True, num_samples: int = 200) -> List[str]:
        if do_sample:
            assert self.temperature > 0, "Temperature must be greater than 0!"

        input = f"""<|im_start|>system
You are a helpful AI Assistant that provides well-reasoned and detailed responses. You first think about the reasoning process as an internal monologue and then provide the user with the answer. Respond in the following format: <think>\n...\n</think>\n<answer>\n...\n</answer><|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant
<think>
"""
        return VLlmDecoder.codegen(self, input, do_sample, num_samples)


def make_model(
    model_type: str,
    model_name: str,
    model_path: str,
    batch_size: int = 1,
    temperature: float = 0.8,
    dataset: str = None,
    tensor_parallel_size = 1,
):
    import torch
    from stop_sequencer import StopSequencer
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ret_model = None 
    if model_type == "codeqwen" or model_type == "qwen2":
        if "base" not in  model_name.lower():
            if "awq" in model_name.lower():
                ret_model =  AWQChatML(
                    batch_size=batch_size,
                    name=model_path,
                    temperature=temperature,
                    max_new_tokens=2048,
                    tensor_parallel_size = tensor_parallel_size
                )
            else:
                ret_model= ChatML(
                    batch_size=batch_size,
                    name=model_path,
                    temperature=temperature,
                    max_new_tokens=2048,
                    tensor_parallel_size = tensor_parallel_size
                )
        else:
            assert 1==2, "not base in here " 
            ret_model= VLlmDecoder(
                batch_size=batch_size,
                name=model_path,
                temperature=temperature,
                dataset=dataset,
                tensor_parallel_size = tensor_parallel_size
            )
    else:
        raise ValueError(f"Invalid model name: {model_type}@{model_name}")

    setattr( ret_model , "model_name", model_name )
    return ret_model 
