"""Reward functions for GRPO training."""
import json
import math
import re
from typing import Dict

from latex2sympy2_extended import NormalizationConfig
from math_verify import LatexExtractionConfig, parse, verify
from typing import Callable, Dict

from .utils import is_e2b_available
from .utils import wired_text_detect 

import random

import json
import math
import re
from typing import Dict
import os
import requests
import backoff
import logging
from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ThreadPoolExecutor, as_completed

import re 

#from .se_formal import _imp_asserty_verify_with_z3_counterexample


logger = logging.getLogger(__file__)
BASE_URL = "http://127.0.0.1:5000"



if is_e2b_available():
    from dotenv import load_dotenv
    from e2b_code_interpreter import Sandbox

    load_dotenv()


def find_code_blocks(completion: str) -> str:
    # Updated pattern to match any language (optional language after ``` and before \n)
    pattern = re.compile(r"```[a-zA-Z+]*\n(.*?)```", re.DOTALL | re.MULTILINE | re.IGNORECASE)
    pattern_backup = re.compile(r"```(.*?)```", re.DOTALL | re.MULTILINE | re.IGNORECASE)
    matches = pattern.findall(completion)
    if len(matches) <= 0:
        matches = pattern_backup.findall(completion)
    extracted_answer = matches[-1] if len(matches) >= 1 else ""
    return extracted_answer



def request_auto(payload, target_path="", timeout=10):
    url = os.path.join(BASE_URL, target_path)
    try:
        response = requests.post(url, json=payload, timeout=timeout )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as ex:
        # logger.info(str(ex))
        return None
    except requests.exceptions.ReadTimeout as ex:
        # logger.info(str(ex))
        return None



def reward_remote_check_syntax(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="check_syntax")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    with ThreadPoolExecutor() as executor:
        # Using executor.map preserves the order of completion_contents
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["check_syntax"]) if x is not None else 0.5 for x in completion_contents]
    return completion_contents


def reward_remote_check_is_loop(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="check_is_loop")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    with ThreadPoolExecutor() as executor:
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["check_is_loop"]) if x is not None else 0.5 for x in completion_contents]
    return completion_contents


def reward_remote_is_loop_invariant_format(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="is_loop_invariant_format")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    with ThreadPoolExecutor() as executor:
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["is_loop_invariant_format"]) if x is not None else 0.5 for x in completion_contents]
    return completion_contents


def reward_remote_check_has_post_condition(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="check_has_post_condition")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    # print(completions, "completion_contents...........", completion_contents)
    with ThreadPoolExecutor() as executor:
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["has_post_condition"]) if x is not None else 0.5 for x in completion_contents]
    return completion_contents


def reward_remote_check_is_cheating(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="check_is_cheating")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    with ThreadPoolExecutor() as executor:
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["check_is_cheating"]) if x is not None else 0.5 for x in completion_contents]
    completion_contents = [ 1-x  for x in completion_contents]

    return completion_contents


def reward_remote_verify(completions, **kwargs):
    def rewrite_content(source_code):
        url = f"{BASE_URL}/rewrite"
        data = {'source_code': source_code}
        d= request_auto(payload=data, target_path="rewrite")
        return d 
    
    def lemur_verifier_with_prop(source_code, property="unreach-call"):
        assert property in ["unreach-call", "termination"]
        data = {'source_code': source_code, "property": property}
        return request_auto(payload=data, target_path="lemur_verifier_with_prop")
    
    completion_contents = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for completion in completions:
            source_code = completion[0]["content"]
            source_code = find_code_blocks(source_code)
            future = executor.submit(rewrite_content, source_code)
            futures.append((future, source_code))
        
        for future, source_code in futures:
            rewrite_result = future.result()
            flg = 0 
            if rewrite_result is not None :
                new_content = rewrite_result.get('new_code', source_code)
                future_lemur = executor.submit(lemur_verifier_with_prop, new_content, property=kwargs.get("property", "unreach-call"))
                lemur_verifier_result_rewrite = future_lemur.result()
                status = lemur_verifier_result_rewrite["status"]
                if status == 1:
                    flg = 1
                elif status == 2:
                    flg = 0
                elif status == 3:
                    flg = 0.1  # unknown error, less trust
                else:
                    flg = 0.2  # timeout
            completion_contents.append(float(flg))
    return completion_contents




def format_reward(completions, **kwargs):
    completion_contents = [completion[0]["content"] for completion in completions]
    completion_contents = [_format_reward (x) for x in completion_contents ]
    return completion_contents 
#    """Reward function that checks if the reasoning process is enclosed within <think> and </think> tags, while the final answer is enclosed within <answer> and </answer> tags."""
#    pattern = r"^<think>\n.*?\n</think>\n<answer>\n.*?\n</answer>$"
#    matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completion_contents]
#    return [1.0 if match else 0.0 for match in matches]


def tag_count_reward(completions, **kwargs) -> list[float]:
    """Reward function that checks if we produce the desired number of think and answer tags associated with `format_reward()`.

    Adapted from: https://gist.github.com/willccbb/4676755236bb08cab5f4e54a0475d6fb#file-grpo_demo-py-L90
    """

    def count_tags(text: str) -> float:
        count = 0.0
        if text.count("<think>") == 1:
            count += 0.25
        if text.count("</think>") == 1:
            count += 0.25
        if text.count("<answer>") == 1:
            count += 0.25
        if text.count("</answer>") == 1:
            count += 0.25
        return count

    contents = [completion[0]["content"] for completion in completions]
    return [count_tags(c) for c in contents]


def reasoning_steps_reward(completions, **kwargs):
    r"""Reward function that checks for clear step-by-step reasoning.
    Regex pattern:
        Step \d+: - matches "Step 1:", "Step 2:", etc.
        ^\d+\. - matches numbered lists like "1.", "2.", etc. at start of line
        \n- - matches bullet points with hyphens
        \n\* - matches bullet points with asterisks
        First,|Second,|Next,|Finally, - matches transition words
    """
    pattern = r"(Step \d+:|^\d+\.|\n-|\n\*|First,|Second,|Next,|Finally,)"
    completion_contents = [completion[0]["content"] for completion in completions]
    matches = [len(re.findall(pattern, content)) for content in completion_contents]

    # Magic number 3 to encourage 3 steps and more, otherwise partial reward
    return [min(1.0, count / 3) for count in matches]






def get_repetition_penalty_reward(ngram_size: int, max_penalty: float):
    """
    Computes N-gram repetition penalty as described in Appendix C.2 of https://arxiv.org/abs/2502.03373.
    Reference implementation from: https://github.com/eddycmu/demystify-long-cot/blob/release/openrlhf/openrlhf/reward/repetition.py

    Args:
    ngram_size: size of the n-grams
    max_penalty: Maximum (negative) penalty for wrong answers
    """
    if max_penalty > 0:
        raise ValueError(f"max_penalty {max_penalty} should not be positive")

    def zipngram(text: str, ngram_size: int):
        words = text.lower().split()
        return zip(*[words[i:] for i in range(ngram_size)])

    def repetition_penalty_reward(completions, **kwargs) -> float:
        """
        reward function the penalizes repetitions
        ref implementation: https://github.com/eddycmu/demystify-long-cot/blob/release/openrlhf/openrlhf/reward/repetition.py

        Args:
            completions: List of model completions
        """

        contents = [completion[0]["content"] for completion in completions]
        rewards = []
        for completion in contents:
            if completion == "":
                rewards.append(0.0)
                continue
            if len(completion.split()) < ngram_size:
                rewards.append(0.0)
                continue

            ngrams = set()
            total = 0
            for ng in zipngram(completion, ngram_size):
                ngrams.add(ng)
                total += 1

            scaling = 1 - len(ngrams) / total
            reward = scaling * max_penalty
            rewards.append(reward)
        return rewards

    return repetition_penalty_reward


def extract_code(completion: str) -> str:
    pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
    matches = pattern.findall(completion)
    extracted_answer = matches[-1] if len(matches) >= 1 else ""
    return extracted_answer



def get_code_format_reward(language: str = "c"):
    """Format reward function specifically for code responses.

    Args:
        language: Programming language supported by E2B https://e2b.dev/docs/code-interpreting/supported-languages
    """
    pattern = rf"^<think>\n.*?\n</think>\n<answer>\n.*?```{language}.*?```.*?\n</answer>$"

    def code_format_reward(completions, **kwargs):
        completion_contents = [completion[0]["content"] for completion in completions]
        matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completion_contents]
        return [1.0 if match else 0.0 for match in matches]

    return code_format_reward








def reward_asserty_p_check_assert_syntax(completions, **kwargs):
    func = lambda x: request_auto({"source_code": x}, target_path="p_check_assert_syntax")
    completion_contents = [find_code_blocks(completion[0]["content"]) for completion in completions]
    with ThreadPoolExecutor() as executor:
        # Using executor.map preserves the order of completion_contents
        completion_contents = list(executor.map(func, completion_contents))
    completion_contents = [float(x["p_check_assert_syntax"]) if x is not None else 0 for x in completion_contents]
    return completion_contents



def reward_asserty_p_is_cheating(completions, **kwargs):
    # assert "source_code" in  kwargs 
    raw_source_code = kwargs.get("source_code",[""]*len(completions) )
    
    assert_snippets = [find_code_blocks(completion[0]["content"]) for completion in completions]

    new_completions = list( zip(raw_source_code, assert_snippets ) )

    func = lambda x: request_auto({"source_code": x[0], "assertation":x[-1] } , target_path="p_is_cheating")

    with ThreadPoolExecutor() as executor:
        completion_contents = list(executor.map(func, new_completions))
    completion_contents = [float(x["p_is_cheating"]) if x is not None else 0 for x in completion_contents]

    completion_contents = [ 1-x  for x in completion_contents]

    return completion_contents





def reward_asserty_verify(completions, **kwargs):
    assert "source_code" in kwargs

    def rewrite_content(source_code, assertion):
        if "assert" not in assertion.lower():
            return {"new_code": None}

        data = {'source_code': source_code}
        ret = request_auto(payload=data, target_path="rewrite")
        new_code = ret.get("new_code", None)

        if new_code is None:
            return {"new_code": None}

        data = {'source_code': new_code, "assertation": "\n" + assertion + "\n"}
        inserted_code = request_auto(payload=data, target_path="p_insert_invariant_from_clangindex")
        inserted_code = inserted_code.get("p_insert_invariant_from_clangindex", None)

        if inserted_code is None:
            return {"new_code": None}

        return {"new_code": inserted_code}

    def lemur_verifier_with_prop(source_code, property="unreach-call"):
        assert property in ["unreach-call", "termination"]
        data = {'source_code': source_code, "property": property}
        return request_auto(payload=data, target_path="lemur_verifier_with_prop")

    assert_snippets = [find_code_blocks(completion[-1]["content"]) for completion in completions]
    raw_source_code = kwargs["source_code"]
    new_completions = list(zip(raw_source_code, assert_snippets))

    completion_contents = []

    with ThreadPoolExecutor() as executor:
        # Use executor.map to process new_completions in order
        rewrite_results = executor.map(lambda x: rewrite_content(x[0], x[1]), new_completions)

        for rewrite_result in rewrite_results:
            new_content = rewrite_result.get('new_code', None)

            if new_content is not None:
                lemur_verifier_result_rewrite = lemur_verifier_with_prop(new_content, property=kwargs.get("property", "unreach-call"))
                status = lemur_verifier_result_rewrite["status"]
            else:
                status = 2

            if status == 1:
                flg = 1
            elif status == 2:
                flg = 0
            elif status == 3:
                flg = 0.1  # unknown error, less trust
            else:
                flg = 0.2  # timeout

            completion_contents.append(float(flg))

    return completion_contents



def reward_asserty_verify_with_esbmc(completions, **kwargs):
    assert "source_code" in kwargs
    assert "idx" in kwargs, list(kwargs)

    def rewrite_content(source_code, assertion, idx):
        if "assert" not in assertion.lower():
            return {"new_code": None}

        data = {'source_code': source_code, "idx": idx}
        ret = request_auto(payload=data, target_path="rewrite")
        if ret is None:
            return {"new_code": None}
        new_code = ret.get("new_code", None)

        if new_code is None:
            return {"new_code": None}

        data = {'source_code': new_code, "assertation": "\n" + assertion + "\n"}
        inserted_code = request_auto(payload=data, target_path="p_insert_invariant_from_clangindex")
        inserted_code = inserted_code.get("p_insert_invariant_from_clangindex", None)

        if inserted_code is None:
            return {"new_code": None}

        return {"new_code": inserted_code}

    def esbmc_verifier_with_k_induction(source_code, property="unreach-call", timeout=5):
        assert property in ["unreach-call", "termination"]
        data = {'source_code': source_code, "timeout": timeout}
        return request_auto(payload=data, target_path="esbmc_verifier_with_k_induction", timeout=timeout)

    assert_snippets = [find_code_blocks(completion[-1]["content"]) for completion in completions]
    raw_source_code = kwargs["source_code"]
    raw_idx = kwargs["idx"]

    new_completions = list(zip(raw_source_code, assert_snippets, raw_idx))

    completion_contents = []

    with ThreadPoolExecutor() as executor:
        # Use executor.map to process new_completions in order
        rewrite_results = executor.map(lambda x: rewrite_content(x[0], x[1], x[2]), new_completions)

        for rewrite_result in rewrite_results:
            new_content = rewrite_result.get('new_code', None)

            if new_content is not None:
                esbmc_verifier_result_rewrite = esbmc_verifier_with_k_induction(new_content, property=kwargs.get("property", "unreach-call"))
                status = esbmc_verifier_result_rewrite["status"] if esbmc_verifier_result_rewrite is not None else 2
            else:
                status = 2

            if status == 1:
                flg = 1
            else:
                flg = 0

            completion_contents.append(float(flg))

    return completion_contents



def reward_asserty_verify_with_z3(completions, **kwargs):
    assert "smt_code" in kwargs
    do_print  = random.randint(0,64)==1

    def _z3_verify(smt_code, assertion,idx):
        if "assert" not in assertion.lower():
            return None
        
        data = {'source_code': smt_code, "assertation": assertion,"idx":idx}
        return  request_auto(payload=data, target_path="smt_verify")

    assert_snippets = [extract_asserts(completion[-1]["content"]) for completion in completions]
    raw_source_code = kwargs["smt_code"]
    raw_idx  = kwargs["idx"]

    new_completions = list(zip(raw_source_code, assert_snippets,raw_idx))

    x_fail = 0
    x_pass = 1

    with ThreadPoolExecutor() as executor:
        # Use executor.map to process new_completions in order
        results = executor.map(lambda x: _z3_verify(x[0], x[1],x[-1]), new_completions)

        completion_contents = []
        for rewrite_result in results:
            if rewrite_result is None:
                completion_contents.append(x_fail)
            elif "smt_verify" not in rewrite_result:
                completion_contents.append(x_fail)
            else:
                if do_print:
                    print("rewrite_result", rewrite_result)
                completion_contents.append(rewrite_result["smt_verify"]["score"])

    return completion_contents

def is_wired_text( completions, **kwargs ):
    assert_snippets = [ completion[-1]["content"] for completion in completions]
    flg_list =[ 1- int(wired_text_detect.is_wired_text( v_str ) ) for v_str in assert_snippets ] 
    return  flg_list


def _format_reward(solution_str: str, ground_truth=None, *argv, **kwargs) -> float:


    def extract_think_and_answer(solution_str: str):
        solution_str = solution_str.strip()
        
        # Count occurrences of the tags (case-insensitive)
        think_open_count = len(re.findall(r"(?i)<think>", solution_str))
        think_close_count = len(re.findall(r"(?i)</think>", solution_str))
        answer_open_count = len(re.findall(r"(?i)<answer>", solution_str))
        answer_close_count = len(re.findall(r"(?i)</answer>", solution_str))
        
        # if not (think_open_count == 1 and think_close_count == 1 and 
        #         answer_open_count == 1 and answer_close_count == 1):
        #     return None  # or raise an error if the format is not as expected
    
        # Define the strict pattern for the format
        pattern = re.compile(
            r"^<think>\s*(.*?)\s*</think>\n*\s*<answer>\s*```(?:cpp|php|python|java|c)?\n(.*?)\n```\s*</answer>$",
            re.DOTALL | re.IGNORECASE
        )
        
        match = re.search(pattern, solution_str)
        if match:
            think_content = match.group(1)
            answer_content = match.group(2)
            
            answer_content_str = _extract_asserts( solution_str )
            if not answer_content_str:
                return None 
            return think_content , answer_content
        return None


    matched_t_a = extract_think_and_answer( solution_str=solution_str )    
    return 1.0 if matched_t_a else 0.0

def _extract_asserts(response_str: str):
    """
    Remove code block markers (```) from the response string and extract all assert statements.
    Returns a list of assert statements found.
    """
    def extract_solution(solution_str: str) -> str:
        """
        Extract the content between <answer> and </answer> tags from the solution string.
        If no such tags are found, returns the original (stripped) string.
        """
        answer_open_count = len(re.findall(r"(?i)<answer>", solution_str))
        answer_close_count = len(re.findall(r"(?i)</answer>", solution_str))

        if not (answer_open_count == 1 and answer_close_count == 1):
            return ""  # or raise an error if the format is not as expected

        answer_pattern = r"<answer>\s*```(?:cpp|php|python|java|c)?\n(.*?)\n```\s*</answer>"

        matches = list(re.finditer(answer_pattern, solution_str, re.DOTALL|re.MULTILINE))
        if matches:
            final_answer = matches[-1].group(1).strip()
        else:
            final_answer  = ""
        # print ("final_answer", final_answer)
        return final_answer

    response_str = extract_solution( response_str )
    # Remove code block markers (```...```) from the response string
    response_str = re.sub(
        r'```[\s\S]*?```', 
        lambda m: m.group(0).replace('```', ''), 
        response_str
    )

    return  re.findall(r'assert\s*\(.*?\)\s*;', response_str, re.DOTALL)



def extract_asserts(response_str: str):
    return "\n".join( _extract_asserts(response_str) )







import asyncio
import traceback
from functools import partial
from concurrent.futures import ProcessPoolExecutor 
# as ThreadPoolExecutor 

async def single_compute_score(evaluation_func, completion, reference, task_extra_info, executor, timeout=300.):
    loop = asyncio.get_running_loop()
    try:
        task = asyncio.wait_for(
            loop.run_in_executor(
                executor,
                partial(evaluation_func, completion, reference, task_extra_info)
            ),
            timeout=timeout
        )
        return await asyncio.gather(task)
    except asyncio.TimeoutError:
        traceback.print_exc()
        print(f"Timeout occurred for completion: {completion}")
        return None
    except Exception as e:
        traceback.print_exc()
        print(f"Error processing completion: {completion[:10]}, Error: {e}")
        return None



async def parallel_compute_score_async(evaluation_func, completions, references, extra_info=None, num_threads=64):
    scores = []
    with ProcessPoolExecutor(max_workers=num_threads) as executor:
        if extra_info is None:
            extra_info = [None] * len(completions)
        tasks_async = [
            single_compute_score(evaluation_func, comp, ref, info, executor, timeout=300.)
            for comp, ref, info in zip(completions, references, extra_info)
        ]
        try:
            results = await asyncio.gather(*tasks_async, return_exceptions=False)
        except Exception:
            traceback.print_exc()
            raise

    for result, comp, ref in zip(results, completions, references):
        if result is None or isinstance(result, Exception):
            scores.append(0.0)
        elif isinstance(result[0], (int, float, bool)):
            scores.append(float(result[0]))
        else:
            scores.append(float(result[0][0]))
    return scores




def _process_with_inputx_outputy(function_name, sequences_str, ground_truth=None):
    if ground_truth is None:
        ground_truth = [None] * len(sequences_str)
    assert len(sequences_str) == len(ground_truth)
    try:
        scores = asyncio.run(
            parallel_compute_score_async(function_name, sequences_str, ground_truth, num_threads=64)
        )
    except asyncio.TimeoutError:
        traceback.print_exc()
        print('Global timeout in reward computing! Setting all as 0.')
        scores = [0.0 for _ in range(len(sequences_str))]
    except Exception as e:
        traceback.print_exc()
        print(f"Unexpected error in batched reward computing. Setting all as 0.: {e}")
        scores = [0.0 for _ in range(len(sequences_str))]
    return scores


def reward_asserty_verify_with_z3_counterexample_local(completions, **kwargs):
    assert "smt_code" in kwargs, "smt_code is required"
    smt_code = kwargs["smt_code"]
    s_code = kwargs.get("source_code", [None] * len(completions))
    ground_truth = [{"smt_code": x, "source_code": y} for x, y in zip(smt_code, s_code)]
    solution_list = [comp[0]["content"] for comp in completions]
    solution_list = [extract_asserts(s) for s in solution_list]
    return _process_with_inputx_outputy(
        _imp_asserty_verify_with_z3_counterexample,
        sequences_str=solution_list,
        ground_truth=ground_truth
    )



def extract_code_old(completion: str, language: str = "c") -> str:
    pattern = re.compile(rf"```{language}\n(.*?)```", re.DOTALL)
    matches = pattern.findall(completion)
    extracted_answer = matches[-1] if len(matches) >= 1 else ""
    return extracted_answer

def reward_asserty_verify_with_z3_v2(completions, **kwargs):
    assert "smt_code" in kwargs
    do_print  = random.randint(0,64)==1

    def _z3_verify(smt_code, assertion,one_completeion, idx ):
        if "assert" not in assertion.lower():
            return None
        
        data = {'source_code': smt_code, "assertation": assertion,"idx":idx}
        rewrite_result =   request_auto(payload=data, target_path="smt_verify")
        if do_print and rewrite_result :
            print(json.dumps({** rewrite_result,"assertion": assertion,"one_completeion":one_completeion}  ) )
        return rewrite_result 

    assert_snippets = [extract_code_old(completion[-1]["content"]) for completion in completions]
    raw_source_code = kwargs["smt_code"]
    raw_idx  = kwargs["idx"]

    new_completions = list(zip(raw_source_code, assert_snippets,completions,raw_idx ))

    x_fail = 0
    x_pass = 1

    with ThreadPoolExecutor() as executor:
        # Use executor.map to process new_completions in order
        results = executor.map(lambda x: _z3_verify(x[0], x[1],x[2],x[-1]), new_completions)

        completion_contents = []
        for rewrite_result in results:
            if rewrite_result is None:
                completion_contents.append(x_fail)
            elif "smt_verify" not in rewrite_result:
                completion_contents.append(x_fail)
            else:
                completion_contents.append(rewrite_result["smt_verify"]["score"])

    return completion_contents

def reward_asserty_verify_with_z3_counterexample(completions, **kwargs):
    assert "smt_code" in kwargs
    do_print  = random.randint(0,64)==1

    def _z3_verify(smt_code, assertion,one_completeion, idx ):
        if "assert" not in assertion.lower():
            return None
        
        data = {'source_code': smt_code, "assertation": assertion,"idx":idx}
        rewrite_result =   request_auto(payload=data, target_path="smt_verify_counter")
        if do_print and rewrite_result :
            print(json.dumps({** rewrite_result,"assertion": assertion,"one_completeion":one_completeion}  ) )
        return rewrite_result 

    assert_snippets = [extract_code_old(completion[-1]["content"]) for completion in completions]
    raw_source_code = kwargs["smt_code"]
    raw_idx  = kwargs["idx"]

    new_completions = list(zip(raw_source_code, assert_snippets,completions,raw_idx ))

    x_fail = 0
    x_pass = 1

    with ThreadPoolExecutor() as executor:
        # Use executor.map to process new_completions in order
        results = executor.map(lambda x: _z3_verify(x[0], x[1],x[2],x[-1]), new_completions)

        completion_contents = []
        for rewrite_result in results:
            if rewrite_result is None:
                completion_contents.append(x_fail)
            elif "smt_verify" not in rewrite_result:
                completion_contents.append(x_fail)
            else:
                completion_contents.append(rewrite_result["smt_verify"]["score"])

    return completion_contents


import re
from io import StringIO
import  tokenize
def remove_comments_and_docstrings(source,lang="c"):
    if lang in ['python']:
        """
        Returns 'source' minus comments and docstrings.
        """
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass
            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
            # This is likely a docstring; double-check we're not inside an operator:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp=[]
        for x in out.split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        return source
    else:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # note: a space and not an empty string
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp=[]
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)



def get_reward_funcs(script_args=None) -> list[Callable]:
    # Get reward functions
    REWARD_FUNCS_REGISTRY = {
        "reward_remote_check_syntax": reward_remote_check_syntax,
        "reward_remote_check_is_loop": reward_remote_check_is_loop,
        "reward_remote_is_loop_invariant_format": reward_remote_is_loop_invariant_format,
        "reward_remote_check_has_post_condition": reward_remote_check_has_post_condition,
        "reward_remote_check_is_cheating": reward_remote_check_is_cheating,
        "reward_remote_verify": reward_remote_verify,
        
        
        
        "reward_asserty_p_check_assert_syntax":reward_asserty_p_check_assert_syntax, 
        "reward_asserty_p_is_cheating":reward_asserty_p_is_cheating,
        "reward_asserty_verify":reward_asserty_verify,
        
        "reward_asserty_verify_with_esbmc":reward_asserty_verify_with_esbmc,
        "reward_asserty_verify_with_z3":reward_asserty_verify_with_z3,
        
        "reward_asserty_verify_with_z3_counterexample_local" :reward_asserty_verify_with_z3_counterexample_local,
        "reward_asserty_verify_with_z3_counterexample" :reward_asserty_verify_with_z3_counterexample,
        
        "reward_asserty_verify_with_z3_v2":reward_asserty_verify_with_z3_v2,
        
        "format_seformal": format_reward,
        # "reasoning_steps": reasoning_steps_reward,
        # # "cosine": get_cosine_scaled_reward(
        # #     min_value_wrong=script_args.cosine_min_value_wrong,
        # #     max_value_wrong=script_args.cosine_max_value_wrong,
        # #     min_value_correct=script_args.cosine_min_value_correct,
        # #     max_value_correct=script_args.cosine_max_value_correct,
        # #     max_len=script_args.cosine_max_len,
        # # ),
        # "repetition_penalty": get_repetition_penalty_reward(
        #     ngram_size=script_args.repetition_n_grams,
        #     max_penalty=script_args.repetition_max_penalty,
        # ),
        # "length": len_reward,
        # "code_format": get_code_format_reward(),
        "is_wired_text":is_wired_text,
        # "tag_count": tag_count_reward,
    }


    return REWARD_FUNCS_REGISTRY

