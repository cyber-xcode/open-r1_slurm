import json
import os
from os import PathLike
import random 
from typing import List, Optional
from multiprocessing import Pool, cpu_count, Manager
import traceback




from chat_model import make_model


HF_HUB_CACHE=os.environ.get("HF_HUB_CACHE", os.path.expanduser("~/.cache/huggingface/hub") )
os.environ["HF_HUB_CACHE"] =HF_HUB_CACHE

#print ("HF_HUB_CACHE", HF_HUB_CACHE, "-->", os.environ["HF_HUB_CACHE"]   )

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

PMPT_answer = """
Given a snippet of C source code, synthesize a loop invariant that is both necessary and sufficient.  
**Requirements:**  
1. Express the invariant as a C assertion.  
2. Do not include any explanation or additional commentary in your <answer>; output only the invariant.  

**Example:**
<answer>
```c
assert(x <= 1);
```
</answer>

=========
Now you are given this code, what is you answer to the invariant. 
```
{{source_code}}
```
"""

PMPT_think_answer = """
Given a snippet of C source code, synthesize a loop invariant that is both necessary and sufficient.  
**Requirements:**  
1. Express the invariant as a C assertion.  
2. Do not include any explanation or additional commentary in your <answer>; output only the invariant.  

**Example:**
<think>
....
</think>
<answer>
```c
assert(x <= 1);
```
</answer>

=========
Now you are given this code, what is you answer to the invariant. 
```
{{source_code}}
```
"""

def build_prompt(source_code: str, prompt_type: str) -> str:
    if prompt_type == "think_answer":
        return PMPT_think_answer.replace("{{source_code}}", source_code)
    else:
        return PMPT_answer.replace("{{source_code}}", source_code)

def codegen(
    target_path: PathLike,
    model_kwargs: dict,
    dataset: str,
    greedy: bool = False,
    n_samples: int = 1,
    version: str = "default",
    resume: bool = True, 
    prompt_type: str = "think_answer",
    args: Optional[object] = None  # Added args parameter
):
    # Load dataset
    assert os.path.isfile(dataset), f"Dataset file not found: {dataset}"
    data_list = [json.loads(x) for x in open(dataset).readlines()]
    data_list = [{"idx": x["idx"], "prompt": build_prompt(x["source_code"], prompt_type)} for x in data_list]
    data_list = list({x["idx"]: x for x in data_list}.values())
    random.shuffle(data_list)
    dataset_dict = {x["idx"]: x for x in data_list}

    # Load existing tasks if resume is enabled
    task2nexist = {}
    task2nneed = {}
    if resume :
        if os.path.isfile(target_path):
            with open(target_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        task_id = json.loads(line)["task_id"]
                        task2nexist[task_id] = task2nexist.get(task_id, 0) + 1
                    except json.JSONDecodeError:
                        traceback.print_exc()
                        continue

        for task_id,_ in dataset_dict.items():
            n_existing = task2nexist.get(task_id, 0)
            nsamples = n_samples - n_existing
            if nsamples >0 :
                task2nneed[ task_id ] = nsamples
    assert  len(task2nneed), task2nneed

    # Initialize model
    model = make_model(**model_kwargs)
    p_name = model_kwargs.get("model_path", "unknown")
    
    with Progress(
        TextColumn(f"{os.path.basename(dataset)} • [progress.percentage]{{task.percentage:>3.0f}}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
    ) as p:
        for task_id, task in p.track(dataset_dict.items()):
            log = f"Codegen: {task_id } @ {getattr(model,'model_name')}"
            n_existing = 0
            if resume:
                n_existing = task2nexist.get(task_id, 0)
                if n_existing > 0:
                    log += f" (resuming from {n_existing})"

            nsamples = n_samples - n_existing
            p.console.print(log)

            sidx = n_samples - nsamples
            while sidx < n_samples:
                outputs = model.codegen(
                    task["prompt"],
                    do_sample=not greedy,
                    num_samples=n_samples - sidx,
                )
                assert outputs, "No outputs from model!"
                
                for solution in outputs:
                    if not  solution.strip().startswith("<think>"):
                        solution = "<think>\n"+solution 
                    if "<answer>" in solution and "</answer>" not in solution and   not solution.strip().endswith("</answer>"):
                        solution = solution+"\n</answer>"
                    if model.direct_completion:
                        solution = task["prompt"] + solution

                    with open(target_path, "a") as f:
                        f.write(json.dumps({
                            "task_id": task_id, 
                            "solution": solution,
                            "prompt_type": prompt_type,
                            #"prompt":  task["prompt"] ,
                            "model": model_kwargs["model_path"]
                        }) + "\n")

                    sidx += 1

def main(
    model_path: str,
    dataset: str,
    root: str,
    model_type:str="qwen2",
    bs: int = 1,
    n_samples: int = 1,
    temperature: float = 0.0,
    greedy: bool = False,
    version: str = "default",
    backend: str = "vllm",
    tp: int = 1,
    resume: bool = True,
    prompt_type: str = "think_answer",
    model_root :str = None ,  
):
    assert backend in ["vllm", "hf", "openai"]
    assert prompt_type in ["answer", "think_answer"], f"Invalid prompt_type: {prompt_type}"

    if greedy:
        temperature = 0.0
        bs = 1
        n_samples = 1


    model_name = None 
    os.makedirs(root, exist_ok=True)
    if  os.path.isfile( model_path ) or model_root is None :
        model_name = model_path 
    else:
        if os.path.isdir( os.path.join(model_root, model_path ) ):
            model_name= model_path 
            model_path = os.path.join( model_root, model_path )
            assert os.path.isfile( os.path.join( model_path,  "tokenizer.json") ), model_path 
        elif   os.path.isdir( os.path.join( os.environ["HF_HUB_CACHE"] ,"models--"+ model_path.replace("/","--") ) ) :
            model_name = model_path 
    
    assert model_name  is not None , ( root, model_path, model_root, )

    model_kwargs = {
        "model_path": model_path,
        "model_name":model_name,
        "model_type":model_type,
        "batch_size": bs,
        "temperature": temperature,
        "dataset": dataset,
        "tensor_parallel_size": tp,
    }

    identifier = model_name.replace("/", "--") + f"_{backend}_temp_{temperature}_{prompt_type}"
    target_path = os.path.join(
        root, 
        os.path.basename(dataset).replace(".jsonl", f"_{identifier}_answer.jsonl")
    )


    if is_filename_too_long( target_path ):
        target_path = target_path.replace("remain_verified_z3_benchmarks528_assert_y_withsmt_12faff6210799edbf0e7ec4939d8b6ee","remain_")
        target_path = target_path.replace("verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446","verified_")


    target_path_exist= target_path.replace("save_dir/","save_dir_l40/")
    if  os.path.isfile( target_path_exist ):
        print ("exist in l40", target_path_exist )
        exit(1)

    #target_path_exist= target_path.replace("save_dir/","save_dir_large/")
    #if  os.path.isfile( target_path_exist ):
    #    print ("exist in large", target_path_exist )
    #    exit(1)


    # Create a simple args object if needed
    class Args:
        pass
    args = Args()
    args.n_samples = n_samples
    args.greedy = greedy
    args.resume = resume
    args.dataset = os.path.basename(dataset)

    codegen(
        target_path=target_path,
        model_kwargs=model_kwargs,
        dataset=dataset,
        greedy=greedy,
        n_samples=n_samples,
        version=version,
        resume=resume,
        prompt_type=prompt_type,
        args=args  # Pass the args object
    )



def is_filename_too_long(path: str, check_full_path: bool = False) -> bool:
    MAX_FILENAME = 255   # Most Linux/macOS/Windows
    MAX_PATH = 4096      # Linux typical PATH_MAX
    
    if check_full_path:
        return len(path.encode("utf-8")) > MAX_PATH
    else:
        filename = os.path.basename(path)
        return len(filename.encode("utf-8")) > MAX_FILENAME


if __name__ == "__main__":
    from fire import Fire
    Fire(main)

