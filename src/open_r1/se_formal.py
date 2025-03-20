import re
import random
import ast
import operator

"""Reward functions for GRPO training."""
import os 
import json
import math
from typing import Dict


from .formal_utils.p_check_assert_syntax import check_assert_syntax
from .formal_utils.p_is_cheating  import p_is_cheating 
from .formal_utils.wired_text_detect  import is_wired_text

from .formal_utils.smt_solver  import smt_resolve_api
from .formal_utils.smt_solver2  import smt_resolve_api as smt_resolve_api_v2
from .formal_utils.smt_solver2 import smt_resolve_api_counterexample 

def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    # if "Assistant:" in solution_str:
    #     solution_str = solution_str.split("Assistant:", 1)[1]
    # elif "<|im_start|>assistant" in solution_str:
    #     solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    # # solution_str = solution_str.split('\n')[-1]

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str,re.DOTALL)
    matches = list(match)
    if matches:
        final_answer = matches[-1].group(1).strip()
    else:
        final_answer = None
    return final_answer




def find_code_blocks(completion: str) -> str:
    return extract_solution( completion )




def format_reward(solution_str, ground_truth=None, *argv, **kwargs):
    """
    Reward function that checks if the reasoning process is enclosed within <think> and </think> tags,
    and the final answer is enclosed within <answer> and </answer> tags.
    
    This version ensures that each tag appears exactly once.
    
    Examples of valid formats:
      - "<think>\n reasoning here\n</think>\n<answer>\n final answer\n</answer>"
      - "Some prefix text <think>\n reasoning\n</think> some extra text <answer>\n answer\n</answer> some suffix text"
      
    Returns:
      1.0 if the valid block is found with exactly one <think> block and one <answer> block, 0.0 otherwise.
    """
    # Remove known system prefixes using regex for robust matching.
    prefix_pattern1 = re.compile(r"assistant:\s*let\s+me\s+solve\s+this\s+step\s+by\s+step\.\s*", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    prefix_pattern2 = re.compile(r"<\|im_start\|>assistant\s*let\s+me\s+solve\s+this\s+step\s+by\s+step\.\s*", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    
    if re.search(prefix_pattern1, solution_str):
        # Split based on the prefix pattern and take the part after the match.
        solution_str = re.split(prefix_pattern1, solution_str, maxsplit=1)[-1]
    elif re.search(prefix_pattern2, solution_str):
        solution_str = re.split(prefix_pattern2, solution_str, maxsplit=1)[-1]
        # Remove any trailing system tokens robustly.
        if "<|im_end|>" not in solution_str:
            return 0 
        solution_str = solution_str.split("<|im_end|>")[0]

    # print ("pure:", solution_str )
    solution_str = solution_str.strip()
    
    # Count occurrences of the tags using case-insensitive search.
    think_open_count = len(re.findall(r"(?i)<think>", solution_str))
    think_close_count = len(re.findall(r"(?i)</think>", solution_str))
    answer_open_count = len(re.findall(r"(?i)<answer>", solution_str))
    answer_close_count = len(re.findall(r"(?i)</answer>", solution_str))
    
    # Ensure there is exactly one occurrence for each tag.
    if not (think_open_count == 1 and think_close_count == 1 and 
            answer_open_count == 1 and answer_close_count == 1):
        return 0.0


    # A robust pattern:
    # - Allows any prefix/suffix text (with ^.* and .*$) around the blocks.
    # - Matches <think> followed by any content (captured non-greedily) until </think>.
    # - Then, matches <answer> followed by any content until </answer>.
    # - Uses \s* to absorb any extra whitespace/newlines.
    pattern = re.compile(
        r"^<think>\s*(.*?)\s*</think>\s*\n*<answer>\s*(.*?)\s*</answer>$", re.DOTALL|re.MULTILINE
    )
    
    # Check if the pattern matches.
    is_match = re.search(pattern, solution_str)
    return 1.0 if is_match else 0.0





# def tag_count_reward(content , ground_truth=None , **kwargs) -> list[float]:
#     """Reward function that checks if we produce the desired number of think and answer tags associated with `format_reward()`.
#
#     Adapted from: https://gist.github.com/willccbb/4676755236bb08cab5f4e54a0475d6fb#file-grpo_demo-py-L90
#     """
#
#     def count_tags(text: str) -> float:
#         count = 0.0
#         if text.count("<think>") == 1:
#             count += 0.25
#         if text.count("</think>") == 1:
#             count += 0.25
#         if text.count("<answer>") == 1:
#             count += 0.25
#         if text.count("</answer>") == 1:
#             count += 0.25
#         return count
#
#     return count_tags( content )



# def get_repetition_penalty_reward(ngram_size: int, max_penalty: float):
#     """
#     Computes N-gram repetition penalty as described in Appendix C.2 of https://arxiv.org/abs/2502.03373.
#     Reference implementation from: https://github.com/eddycmu/demystify-long-cot/blob/release/openrlhf/openrlhf/reward/repetition.py
#
#     Args:
#     ngram_size: size of the n-grams
#     max_penalty: Maximum (negative) penalty for wrong answers
#     """
#     if max_penalty > 0:
#         raise ValueError(f"max_penalty {max_penalty} should not be positive")
#
#     def zipngram(text: str, ngram_size: int):
#         words = text.lower().split()
#         return zip(*[words[i:] for i in range(ngram_size)])
#
#     def repetition_penalty_reward( completion, ground_truth=None , **kwargs) -> float:
#         """
#         reward function the penalizes repetitions
#         ref implementation: https://github.com/eddycmu/demystify-long-cot/blob/release/openrlhf/openrlhf/reward/repetition.py
#
#         Args:
#             completions: List of model completions
#         """
#
#         if completion == "":
#             return FLAG_ERROR
#         if len(completion.split()) < ngram_size:
#             return FLAG_ERROR
#
#         ngrams = set()
#         total = 0
#         for ng in zipngram(completion, ngram_size):
#             ngrams.add(ng)
#             total += 1
#
#         scaling = 1 - len(ngrams) / total
#         reward = scaling * max_penalty
#         return reward 
#
#     return repetition_penalty_reward



# def get_cosine_scaled_reward(
#     min_value_wrong: float = 0.0,
#     max_value_wrong: float = -0.5,
#     min_value_correct: float = 0.5,
#     max_value_correct: float = 1.0,
#     max_len: int = 1000,
# ):
#     def cosine_scaled_reward(content, is_correct ):
#         gen_len = len(content)
#
#         # Apply cosine scaling based on length
#         progress = gen_len / max_len
#         cosine = math.cos(progress * math.pi)
#
#         if is_correct:
#             min_value = min_value_correct
#             max_value = max_value_correct
#         else:
#             # Swap min/max for incorrect answers
#             min_value = max_value_wrong
#             max_value = min_value_wrong
#
#         reward = min_value + 0.5 * (max_value - min_value) * (1.0 + cosine)
#         return float(reward)
#
#
#     return cosine_scaled_reward



FLAG_FAIL = 0.1 
FLAG_ERROR = -0.1 


def _imp_asserty_p_check_assert_syntax( content ,ground_truth=None , *argv, **kwargs):
    score_syntax =  int( check_assert_syntax( content ) )
    
    return score_syntax 



def _imp_asserty_p_is_cheating(content, ground_truth, *argv, **kwargs):
    source_code = ground_truth["source_code"]
    smt_code = ground_truth["smt_code"]
    
    cheating_score = p_is_cheating(source_code =source_code, assertation= content )
    
    return 1- int( cheating_score )


def _imp_asserty_verify_with_z3(content, ground_truth , *argv, **kwargs):
    source_code = ground_truth["source_code"]
    smt_code = ground_truth["smt_code"]
    
    z3_score  = smt_resolve_api(SMT2str =smt_code, result= content, error_score=FLAG_ERROR )

    if z3_score is None:
        return FLAG_ERROR
    else:
        return  z3_score["score"]

def _imp_asserty_verify_with_z3_v2(content, ground_truth , *argv, **kwargs):

    source_code = ground_truth["source_code"]
    smt_code = ground_truth["smt_code"]
    
    z3_score  = smt_resolve_api_v2(SMT2str =smt_code, result= content, error_score=FLAG_ERROR )
    # print ("z3_score",z3_score )
    if z3_score is None:
        return FLAG_ERROR
    else:
        return  z3_score["score"]


def _imp_asserty_verify_with_z3_counterexample(content, ground_truth , *argv, **kwargs):

    source_code = ground_truth["source_code"]
    smt_code = ground_truth["smt_code"]
    
    z3_score  = smt_resolve_api_counterexample(SMT2str =smt_code, result= content, error_score=FLAG_ERROR )

    if z3_score is None:
        return FLAG_ERROR
    else:
        return  z3_score["score"]



def is_not_wired_text( content , ground_truth=None, **kwargs ):
    flg = 1- int(is_wired_text( content ) )
    return flg 

def count_asserts(code , ground_truth=None, *argv, **kwargs):
    # Use regex to find all occurrences of "assert (" or "assert("
    pattern = r'assert\s*\('
    matches = re.findall(pattern, code)
    count = len(matches)
    
    # Apply the conditions based on the count
    if count == 0:
        return 0
    elif 3 <= count <= 5:
        return 1
    elif count < 3:
        return 0.7
    elif 5 < count <= 10:
        return 0.2
    elif count > 10:
        return 0
    return 0 
    
