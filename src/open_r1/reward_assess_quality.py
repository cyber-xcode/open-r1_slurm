import json
import re
from typing import List, Dict, Any, Callable

'''
def extract_json_from_assess_block(completion_text: str) -> str:
    """Extract JSON content from <assess> blocks."""
    # Look for <assess> block with JSON content
    assess_pattern = r"<assess>\s*```json\s*(.*?)\s*```\s*</assess>"
    match = re.search(assess_pattern, completion_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: look for any JSON-like content in <assess> block
    assess_fallback = r"<assess>\s*(.*?)\s*</assess>"
    match = re.search(assess_fallback, completion_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1).strip()
        # Try to extract JSON from the content
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            return content[json_start:json_end]
    
    return ""
'''

def extract_json_from_assess_block(completion_text: str) -> str:
    """Extract JSON content from <think> blocks (keeping old function name for compatibility)."""
    # Updated to look for JSON content within <think> blocks instead of <assess> blocks
    think_pattern = r"<think>.*?```json\s*(.*?)\s*```.*?</think>"
    match = re.search(think_pattern, completion_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: look for any JSON-like content in <think> block
    think_fallback = r"<think>.*?(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}).*?</think>"
    match = re.search(think_fallback, completion_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        json_content = match.group(1).strip()
        if '"' in json_content and ':' in json_content:
            return json_content
    
    return ""

def reward_quality_assessment_format_validation(completions, **kwargs):
    """
    Comprehensive reward function for validating quality assessment format and content.
    
    Checks:
    1. JSON format validity
    2. Presence of all required assessment aspects
    3. Score boundary validation (1-5 scale)
    4. Recommendation value validation
    5. Reasoning content presence
    """
    
    # Required assessment aspects from the quality framework
    REQUIRED_ASPECTS = [
        "ifd_difficulty_score",
        "ifd_difficulty_reasoning", 
        "bidirectional_coherence_score",
        "bidirectional_coherence_reasoning",
        "teacher_student_compatibility_score", 
        "teacher_student_compatibility_reasoning",
        "statistical_consistency_score",
        "statistical_consistency_reasoning",
        "training_influence_score",
        "training_influence_reasoning",
        "diversity_score",
        "diversity_reasoning",
        "correctness_confidence",
        "correctness_reasoning",
        "overall_quality_score",
        "overall_quality_reasoning",
        "recommendation"
    ]
    
    SCORE_ASPECTS = [
        "ifd_difficulty_score",
        "bidirectional_coherence_score", 
        "teacher_student_compatibility_score",
        "statistical_consistency_score",
        "training_influence_score",
        "diversity_score",
        "correctness_confidence",
        "overall_quality_score"
    ]
    
    REASONING_ASPECTS = [
        "ifd_difficulty_reasoning",
        "bidirectional_coherence_reasoning",
        "teacher_student_compatibility_reasoning", 
        "statistical_consistency_reasoning",
        "training_influence_reasoning",
        "diversity_reasoning",
        "correctness_reasoning",
        "overall_quality_reasoning"
    ]
    
    VALID_RECOMMENDATIONS = ["include", "exclude", "review"]
    
    def validate_single_completion(completion_text: str) -> float:
        """Validate a single completion and return reward score."""
        total_score = 0.0
        max_score = 0.0
        
        # Extract JSON from assess block
        json_text = extract_json_from_assess_block(completion_text)
        
        # 1. JSON Format Validation (20% of total score)
        max_score += 0.2
        try:
            json_valid = False
            if json_text:
                assessment_data = json.loads(json_text)
                if type(assessment_data) ==dict :
                    total_score += 0.2
                    json_valid = True
            else:
                assessment_data = {}
        except json.JSONDecodeError:
            json_valid = False
            assessment_data = {}
        
        if not json_valid:
            return total_score  # Return early if JSON is invalid
        
        # 2. Required Aspects Presence (30% of total score)
        max_score += 0.3
        aspects_present = 0
        for aspect in REQUIRED_ASPECTS:
            if aspect in assessment_data and assessment_data[aspect] is not None:
                aspects_present += 1
        
        aspect_score = (aspects_present / len(REQUIRED_ASPECTS)) * 0.3
        total_score += aspect_score
        
        # 3. Score Boundary Validation (25% of total score)
        max_score += 0.25
        valid_scores = 0
        total_score_aspects = len(SCORE_ASPECTS)
        
        for score_aspect in SCORE_ASPECTS:
            if score_aspect in assessment_data:
                try:
                    score_value = float(assessment_data[score_aspect])
                    if 1 <= score_value <= 5:
                        valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if total_score_aspects > 0:
            score_boundary_score = (valid_scores / total_score_aspects) * 0.25
            total_score += score_boundary_score
        
        # 4. Recommendation Validation (10% of total score)
        max_score += 0.1
        if "recommendation" in assessment_data:
            recommendation = assessment_data["recommendation"]
            if isinstance(recommendation, str) and recommendation.lower() in VALID_RECOMMENDATIONS:
                total_score += 0.1
        
        # 5. Reasoning Content Quality (15% of total score)
        max_score += 0.15
        reasoning_scores = 0
        valid_reasonings = 0
        
        for reasoning_aspect in REASONING_ASPECTS:
            if reasoning_aspect in assessment_data:
                reasoning_text = assessment_data[reasoning_aspect]
                if isinstance(reasoning_text, str) and len(reasoning_text.strip()) >= 10:
                    # Basic quality check: non-empty, meaningful length
                    reasoning_scores += 1
                valid_reasonings += 1
        
        if valid_reasonings > 0:
            reasoning_quality_score = (reasoning_scores / valid_reasonings) * 0.15
            total_score += reasoning_quality_score
        
        # Normalize to [0, 1] range
        return total_score / max_score if max_score > 0 else 0.0
    
    # Process all completions
    completion_contents = [completion[0]["content"] for completion in completions]
    rewards = [validate_single_completion(content) for content in completion_contents]
    
    return rewards


def reward_quality_assessment_comprehensive(completions, **kwargs):
    """
    Enhanced reward function that also validates the actual content quality 
    beyond just format validation.
    """
    
    def comprehensive_validation(completion_text: str) -> float:
        """Comprehensive validation including content quality."""
        base_score = reward_quality_assessment_format_validation([[{"content": completion_text}]])[0]
        
        # Additional content quality checks
        content_bonus = 0.0
        
        # Extract JSON for content analysis
        json_text = extract_json_from_assess_block(completion_text)
        try:
            assessment_data = json.loads(json_text) if json_text else {}
        except json.JSONDecodeError:
            return base_score
        if type(assessment_data) != dict:
            return base_score
        
        # Check for thoughtful reasoning (keyword diversity)
        reasoning_quality_keywords = [
            "challenging", "appropriate", "complex", "analysis", "evaluation",
            "assessment", "difficulty", "coherence", "alignment", "consistency",
            "training", "learning", "objective", "subjective", "reliable"
        ]
        
        reasoning_texts = []
        for key in assessment_data:
            if "reasoning" in key and isinstance(assessment_data[key], str):
                reasoning_texts.append(assessment_data[key].lower())
        
        combined_reasoning = " ".join(reasoning_texts)
        keyword_matches = sum(1 for keyword in reasoning_quality_keywords 
                            if keyword in combined_reasoning)
        
        # Bonus for diverse vocabulary in reasoning (up to 0.1 additional points)
        vocabulary_bonus = min(0.1, keyword_matches / len(reasoning_quality_keywords) * 0.1)
        content_bonus += vocabulary_bonus
        
        # Check for score consistency (scores should be reasonably related)
        scores = []
        for key in assessment_data:
            if "score" in key and key != "overall_quality_score":
                try:
                    scores.append(float(assessment_data[key]))
                except (ValueError, TypeError):
                    pass
        
        # Bonus for reasonable score variance (not all same, not too extreme)
        if len(scores) >= 3:
            score_variance = max(scores) - min(scores)
            if 1 <= score_variance <= 3:  # Reasonable variance
                content_bonus += 0.05
        
        return min(1.0, base_score + content_bonus)
    
    completion_contents = [completion[0]["content"] for completion in completions]
    rewards = [comprehensive_validation(content) for content in completion_contents]
    
    return rewards


def reward_assess_block_presence(completions, **kwargs):
    """Simple reward function to check presence of <assess> blocks."""
    def has_assess_block(completion_text: str) -> float:
        assess_pattern = r"<assess>.*?</assess>"
        return 1.0 if re.search(assess_pattern, completion_text, re.DOTALL | re.IGNORECASE) else 0.0
    
    completion_contents = [completion[0]["content"] for completion in completions]
    return [has_assess_block(content) for content in completion_contents]


def reward_json_in_assess_block(completions, **kwargs):
    """Reward function specifically for JSON presence and validity in assess blocks."""
    def has_valid_json_in_assess(completion_text: str) -> float:
        json_text = extract_json_from_assess_block(completion_text)
        if not json_text:
            return 0.0
        
        try:
            json.loads(json_text)
            return 1.0
        except json.JSONDecodeError:
            return 0.0
    
    completion_contents = [completion[0]["content"] for completion in completions]
    return [has_valid_json_in_assess(content) for content in completion_contents]


def reward_all_scores_in_range(completions, **kwargs):
    """Reward function to check if all scores are in valid 1-5 range."""
    def all_scores_valid(completion_text: str) -> float:
        json_text = extract_json_from_assess_block(completion_text)
        try:
            assessment_data = json.loads(json_text) if json_text else {}
        except json.JSONDecodeError:
            return 0.0
        if type(assessment_data) != dict :
            return 0.0
        
        score_keys = [key for key in assessment_data.keys() if "score" in key]
        if not score_keys:
            return 0.0
        
        valid_count = 0
        for key in score_keys:
            try:
                score = float(assessment_data[key])
                if 1 <= score <= 5:
                    valid_count += 1
            except (ValueError, TypeError):
                pass
        
        return valid_count / len(score_keys)
    
    completion_contents = [completion[0]["content"] for completion in completions]
    return [all_scores_valid(content) for content in completion_contents]


def reward_valid_recommendation(completions, **kwargs):
    """Reward function to check if recommendation is valid."""
    def has_valid_recommendation(completion_text: str) -> float:
        json_text = extract_json_from_assess_block(completion_text)
        try:
            assessment_data = json.loads(json_text) if json_text else {}
        except json.JSONDecodeError:
            return 0.0
        if type(assessment_data) !=dict :
            return 0.0
        
        recommendation = assessment_data.get("recommendation", "")
        valid_recommendations = ["include", "exclude", "review"]
        
        return 1.0 if recommendation.lower() in valid_recommendations else 0.0
    
    completion_contents = [completion[0]["content"] for completion in completions]
    return [has_valid_recommendation(content) for content in completion_contents]


# Integration function to add these to the existing reward registry
def extend_reward_funcs_registry(existing_registry: Dict[str, Callable]) -> Dict[str, Callable]:
    """Extend the existing reward functions registry with quality assessment rewards."""
    
    quality_assessment_rewards = {
        "quality_assessment_format_validation": reward_quality_assessment_format_validation,
        "quality_assessment_comprehensive": reward_quality_assessment_comprehensive,
        "assess_block_presence": reward_assess_block_presence,
        "json_in_assess_block": reward_json_in_assess_block,
        "all_scores_in_range": reward_all_scores_in_range,
        "valid_recommendation": reward_valid_recommendation,
    }
    
    # Merge with existing registry
    extended_registry = existing_registry.copy()
    extended_registry.update(quality_assessment_rewards)
    
    return extended_registry


# Usage example - add this to your get_reward_funcs function:
def get_reward_funcs_updated(script_args=None) -> Dict[str, Callable]:
    """Updated version of get_reward_funcs with quality assessment rewards."""
    
    # Get your existing reward functions
    REWARD_FUNCS_REGISTRY = {
        "reward_remote_check_syntax": reward_remote_check_syntax,
        "reward_remote_check_is_loop": reward_remote_check_is_loop,
        "reward_remote_is_loop_invariant_format": reward_remote_is_loop_invariant_format,
        "reward_remote_check_has_post_condition": reward_remote_check_has_post_condition,
        "reward_remote_check_is_cheating": reward_remote_check_is_cheating,
        "reward_remote_verify": reward_remote_verify,
        "reward_asserty_p_check_assert_syntax": reward_asserty_p_check_assert_syntax, 
        "reward_asserty_p_is_cheating": reward_asserty_p_is_cheating,
        "reward_asserty_verify": reward_asserty_verify,
        "reward_asserty_verify_with_esbmc": reward_asserty_verify_with_esbmc,
        "reward_asserty_verify_with_z3": reward_asserty_verify_with_z3,
        "reward_asserty_verify_with_z3_counterexample_local": reward_asserty_verify_with_z3_counterexample_local,
        "reward_asserty_verify_with_z3_counterexample": reward_asserty_verify_with_z3_counterexample,
        "reward_asserty_verify_with_z3_v2": reward_asserty_verify_with_z3_v2,
        "reward_asserty_verify_with_z3_v2treesitter": reward_asserty_verify_with_z3_v2treesitter,
        "reward_asserty_verify_counter_treesitter_norandom": reward_asserty_verify_counter_treesitter_norandom,
        "format_seformal": format_reward,
        "is_wired_text": is_wired_text,
    }
    
    # Extend with quality assessment rewards
    return extend_reward_funcs_registry(REWARD_FUNCS_REGISTRY)



