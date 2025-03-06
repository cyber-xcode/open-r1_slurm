"""Reward functions for GRPO training."""

import json
import math
import re
from typing import Dict

from latex2sympy2_extended import NormalizationConfig
from math_verify import LatexExtractionConfig, parse, verify

from .utils import is_e2b_available

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
import re 

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



def request_auto(payload, target_path=""):
    url = os.path.join(BASE_URL, target_path)
    try:
        response = requests.post(url, json=payload, timeout=30 )
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
    """Reward function that checks if the reasoning process is enclosed within <think> and </think> tags, while the final answer is enclosed within <answer> and </answer> tags."""
    pattern = r"^<think>\n.*?\n</think>\n<answer>\n.*?\n</answer>$"
    completion_contents = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completion_contents]
    return [1.0 if match else 0.0 for match in matches]


def tag_count_reward(completions, **kwargs) -> list[float]:
    """Reward function that checks if we produce the desired number of think and answer tags associated with `format_reward()`.

    Adapted from: https://gist.github.com/willccbb/4676755236bb08cab5f4e54a0475d6fb#file-grpo_demo-py-L90
    """

    def count_tags(text: str) -> float:
        count = 0.0
        if text.count("<think>\n") == 1:
            count += 0.25
        if text.count("\n</think>\n") == 1:
            count += 0.25
        if text.count("\n<answer>\n") == 1:
            count += 0.25
        if text.count("\n</answer>") == 1:
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

    assert "source_code" in  kwargs 
    
    def rewrite_content(source_code,assertation ):
        if "assert" not in assertation.lower():
            return {"new_code":None}
        
        data = {'source_code': source_code }
        ret =  request_auto(payload=data, target_path="rewrite")
        new_code = ret.get("new_code", None )
        
        
        if new_code is None :
            return {"new_code":None}
        
        data = {'source_code': new_code, "assertation":"\n"+assertation+"\n" }
        inserted_code = request_auto(payload=data, target_path="p_insert_invariant_from_clangindex")
        inserted_code = inserted_code.get("p_insert_invariant_from_clangindex",None)
        # print ("during rewrite the raw code is \n",source_code,   "\nthe assert -->", assertation," the compkleted ----->\n", inserted_code)
        
        if inserted_code is None :
            return {"new_code":None}
        
        return {"new_code":inserted_code}
    
    # def rewrite_content(source_code,assertation ):
    #     data = {'source_code': source_code, "assertation":assertation }
    #     inserted_code = request_auto(payload=data, target_path="p_insert_invariant_from_clangindex")
    #     inserted_code = inserted_code.get("p_insert_invariant_from_clangindex",None)
    #     if inserted_code is None :
    #         return {"new_code":None}
    #     # print ("during rewrite the raw code is \n",source_code,   "\nthe assert -->", assertation," the compkleted ----->\n", inserted_code)
    #
    #     data = {'source_code': inserted_code }
    #     ret =  request_auto(payload=data, target_path="rewrite")
    #     new_code = ret.get("new_code", inserted_code )
    #
    #     return {"new_code":new_code}
    
    
    def lemur_verifier_with_prop(source_code, property="unreach-call"):
        # print ("after rewrite the new code is ", "----->\n", source_code)
        assert property in ["unreach-call", "termination"]
        data = {'source_code': source_code, "property": property}
        return request_auto(payload=data, target_path="lemur_verifier_with_prop")
    
    
    assert_snippets = [find_code_blocks(completion[-1]["content"]) for completion in completions]
    if "source_code" not in kwargs :
        logger.info("source code is null, current keawrgs == {}".format( list(kwargs ) ) )
    raw_source_code = kwargs["source_code"]
    
    
    # raw_source_code = [x.decode() for x in raw_source_code ] 
    # print ("kwargs \n\n\n\n ---->", "----->"*8 , raw_source_code[0].encode() )
    new_completions = list( zip(raw_source_code, assert_snippets ) )
    
    completion_contents = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for source_code,assertation in new_completions:
            # logger.info ("soource code from post {}".format( source_code  ) )
            # logger.info ("assertation from post {}".format( assertation  ) )
            
            # source_code = completion[0]["content"]
            # source_code = find_code_blocks(source_code)
            future = executor.submit(rewrite_content, source_code ,assertation )
            futures.append((future, source_code))
        
        for future, source_code in futures:
            rewrite_result = future.result()
            new_content = rewrite_result.get('new_code', None)
            if new_content is not None :
                future_lemur = executor.submit(lemur_verifier_with_prop, new_content, property=kwargs.get("property", "unreach-call"))
                lemur_verifier_result_rewrite = future_lemur.result()
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


