# Copyright 2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys

import datasets
import torch
import transformers
from datasets import load_dataset
from transformers import set_seed
from transformers.trainer_utils import get_last_checkpoint

import random 

from open_r1.configs import GRPOConfig, GRPOScriptArguments
from open_r1.rewards import get_reward_funcs
from open_r1.rewards_seformal import get_reward_funcs as get_reward_funcs_formal
from open_r1.rewards_seformal import remove_comments_and_docstrings 

from open_r1.utils import get_tokenizer
from open_r1.utils.callbacks import get_callbacks
from open_r1.utils.wandb_logging import init_wandb_training
from trl import GRPOTrainer, ModelConfig, TrlParser, get_peft_config


logger = logging.getLogger(__name__)

system_prompt = "You are a helpful assistant. You first think about the reasoning process in the mind and then provides the user with the answer. Show your work in <think> </think> tags. And return the final answer in <answer> </answer> tags, for example <answer> assert( x+1 ==2 ); </answer>"


def build_prompt(item, prompt_type="json_assess"):
    """
    Build the enhanced loop invariant prompt with self-debugging assessment.
    
    Args:
        item: Data item containing source code
        prompt_type: Only supports "json_assess" format
    """
    
    # Enhanced prompt with self-debugging assessment embedded in <think>
    prompt = """# Loop Invariant Generation with Self-Debugging Assessment

Given a snippet of C source code, synthesize diverse loop invariants that are both necessary and sufficient for proving program correctness. Use a self-debugging assessment process to identify and correct issues before providing your final solution.

## Requirements

1. **Generate multiple diverse loop invariants** (aim for 3-5 different assertions covering complementary aspects)
2. **Express each invariant as a C assertion** with clear, descriptive comments
3. **Self-debug your invariants** using the provided evaluation framework to identify gaps, errors, or improvements
4. **Provide a refined final solution** that incorporates insights from your self-assessment

## Response Format

```
<think>
[Your initial reasoning process for understanding the code structure, identifying key program properties, and deriving invariants that capture different aspects of program behavior]

...

Wait, let me assess my reasoning and check for issues:

```json
{
  "ifd_difficulty_score": <1-5>,
  "ifd_difficulty_reasoning": "Assessment of instruction-following difficulty - how challenging was it to generate meaningful invariants from this code?",
  
  "bidirectional_coherence_score": <1-5>, 
  "bidirectional_coherence_reasoning": "Do the generated invariants logically follow from the code structure? Could you infer the code's behavior from the invariants?",
  
  "teacher_student_compatibility_score": <1-5>,
  "teacher_student_compatibility_reasoning": "Are the invariants at an appropriate complexity level? Would they be learnable examples for instruction-following?",
  
  "statistical_consistency_score": <1-5>,
  "statistical_consistency_reasoning": "How objectively verifiable are these invariants? Would different evaluators reach similar assessments?",
  
  "training_influence_score": <1-5>,
  "training_influence_reasoning": "Do these invariants provide meaningful learning signal for code analysis and formal verification skills?",
  
  "diversity_score": <1-5>,
  "diversity_reasoning": "How diverse are the generated invariants? Do they cover different aspects (bounds, relationships, state properties)?",
  
  "correctness_confidence": <1-5>,
  "correctness_reasoning": "Confidence in the mathematical and logical correctness of the invariants",
  
  "overall_quality_score": <1-5>,
  "overall_quality_reasoning": "Synthesis of all dimensions - overall training value and correctness",
  
  "identified_issues": ["List specific problems found in initial reasoning"],
  "improvements_needed": ["List specific improvements to make"],
  "recommendation": "refine_and_improve|good_as_is|major_revision_needed"
}
```

Based on this assessment, I need to [describe specific corrections and improvements]...
</think>

<answer>
```c
// [Final refined invariants incorporating assessment insights]
// Primary invariant - [brief description]
assert([refined_invariant_1]);

// Secondary invariant - [brief description] 
assert([refined_invariant_2]);

// Additional invariant - [brief description]
assert([refined_invariant_3]);

// [Additional invariants as needed, reflecting corrections from assessment]
```
</answer>
```

## Scoring Guidelines

- **IFD Difficulty (1-5)**: 1=Trivial/Impossible, 3=Moderate challenge, 5=Optimal difficulty for learning
- **Bidirectional Coherence (1-5)**: 1=Poor alignment, 3=Moderate coherence, 5=Perfect bidirectional coherence between code and invariants
- **Teacher-Student Compatibility (1-5)**: 1=Poor learnability, 3=Appropriate complexity, 5=Excellent pedagogical value
- **Statistical Consistency (1-5)**: 1=Highly subjective, 3=Mixed objectivity, 5=Highly objective and reproducible assessment
- **Training Influence (1-5)**: 1=Minimal learning value, 3=Moderate benefit, 5=High training value for formal verification skills
- **Diversity (1-5)**: 1=Single perspective, 3=Some variety, 5=Rich diversity across multiple complementary aspects
- **Correctness Confidence (1-5)**: 1=Low confidence, 3=Moderate confidence, 5=High confidence in mathematical and logical correctness

## Self-Assessment Instructions

During the assessment phase, actively debug your initial reasoning by:
- **Identifying gaps**: What aspects of the code behavior did you miss?
- **Checking correctness**: Are your invariants mathematically sound?
- **Evaluating completeness**: Do your invariants collectively capture all essential properties?
- **Assessing diversity**: Are you covering different types of invariants?
- **Finding edge cases**: What boundary conditions or special cases need consideration?

## Diversity Encouragement

Generate invariants that systematically cover different aspects such as:
- **Loop bounds and termination conditions** (progress measures, iteration counts)
- **Variable relationships and constraints** (mathematical relationships between variables)
- **Data structure properties** (array bounds, structure invariants)
- **Pre/post-condition relationships** (input-output behavior)
- **Memory safety properties** (bounds checking, overflow safety)
- **Mathematical relationships** (exponential growth, accumulator properties)
- **Type and range safety** (unsigned integer behavior, domain preservation)

## Expected Self-Debugging Outcomes

Your assessment should lead to one of these outcomes:
- **Refine and improve**: Identify specific issues and provide corrected invariants
- **Good as-is**: Confirm that initial reasoning was sound and complete
- **Major revision needed**: Recognize fundamental flaws requiring complete rethinking

The goal is honest self-evaluation that genuinely improves the final solution quality.

=========
Now you are given this code, what is your answer to the invariants:
```
{{code}}
```"""
    
    # Get source code and optionally remove comments
    source_code = item["source_code"]
    is_remove_comment = random.randint(0, 2) == 1
    if is_remove_comment:
        source_code = remove_comments_and_docstrings(source_code)
    
    return prompt.replace("{{code}}", source_code)


def main(script_args, training_args, model_args):
    # Set seed for reproducibility
    set_seed(training_args.seed)

    ###############
    # Setup logging
    ###############
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process a small summary
    logger.warning(
        f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}"
        + f" distributed training: {bool(training_args.local_rank != -1)}, 16-bits training: {training_args.fp16}"
    )
    logger.info(f"Model parameters {model_args}")
    logger.info(f"Script parameters {script_args}")
    logger.info(f"Training parameters {training_args}")

    # Check for last checkpoint
    last_checkpoint = None
    if os.path.isdir(training_args.output_dir):
        last_checkpoint = get_last_checkpoint(training_args.output_dir)
    if last_checkpoint is not None and training_args.resume_from_checkpoint is None:
        logger.info(f"Checkpoint detected, resuming training at {last_checkpoint=}.")


    if os.path.isfile( os.path.join(training_args.output_dir,"trainer_state.json")  ):
        print ("the trained folder is existing, quit ", training_args.output_dir )
        exit(1)

    if "wandb" in training_args.report_to:
        init_wandb_training(training_args)

    # Load the dataset
    if type(script_args.dataset_name) == dict or script_args.dataset_name.endswith(".jsonl"):
        dataset = load_dataset("json", data_files=script_args.dataset_name)
    else:
        dataset = load_dataset(script_args.dataset_name, name=script_args.dataset_config)

    ################
    # Load tokenizer
    ################
    tokenizer = get_tokenizer(model_args, training_args)

    # Get reward functions from the registry
    reward_funcs_dict = get_reward_funcs(script_args)
    reward_funcs_dict.update(get_reward_funcs_formal())
    
    # Add quality assessment reward functions for the json_assess prompt
    try:
        # Import quality assessment reward functions
        from open_r1.reward_assess_quality import (
            reward_quality_assessment_format_validation,
            reward_quality_assessment_comprehensive,
            reward_assess_block_presence,
            reward_json_in_assess_block,
            reward_all_scores_in_range,
            reward_valid_recommendation
        )
        
        # Add quality assessment rewards to the registry
        quality_rewards = {
            "quality_assessment_format_validation": reward_quality_assessment_format_validation,
            "quality_assessment_comprehensive": reward_quality_assessment_comprehensive,
            "assess_block_presence": reward_assess_block_presence,
            "json_in_assess_block": reward_json_in_assess_block,
            "all_scores_in_range": reward_all_scores_in_range,
            "valid_recommendation": reward_valid_recommendation,
        }
        reward_funcs_dict.update(quality_rewards)
        
        logger.info(f"Added {len(quality_rewards)} quality assessment reward functions")
        logger.info(f"Available quality rewards: {list(quality_rewards.keys())}")
        
    except ImportError as e:
        logger.warning(f"Could not import quality assessment rewards: {e}")
        logger.warning("Make sure reward_assess_quality.py is in the Python path")
        assert 1==2 
    
    # Get the specified reward functions
    reward_funcs = [reward_funcs_dict[x] for x in script_args.reward_funcs]
    
    logger.info(f"Using reward functions: {script_args.reward_funcs}")
    logger.info(f"Using enhanced self-debugging prompt format")
    
    # Format into conversation
    def make_conversation(example):
        prompt = []

        if training_args.system_prompt is not None:
            prompt.append({"role": "system", "content": training_args.system_prompt})

        prompt.append({"role": "user", "content": build_prompt(example)})
        return {"prompt": prompt}

    dataset = dataset.map(make_conversation)

    # Clean up dataset columns
    for split in dataset:
        if "messages" in dataset[split].column_names:
            dataset[split] = dataset[split].remove_columns("messages")
        for col in dataset[split].column_names:
            if col not in ["source_code", "smt_code", "prompt", "idx"]:
                dataset[split] = dataset[split].remove_columns(col)

    logger.info("*** Initializing model kwargs ***")
    torch_dtype = (
        model_args.torch_dtype if model_args.torch_dtype in ["auto", None] else getattr(torch, model_args.torch_dtype)
    )
    model_kwargs = dict(
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
        attn_implementation=model_args.attn_implementation,
        torch_dtype=torch_dtype,
        use_cache=False if training_args.gradient_checkpointing else True,
    )
    training_args.model_init_kwargs = model_kwargs

    #############################
    # Initialize the GRPO trainer
    #############################
    trainer = GRPOTrainer(
        model=model_args.model_name_or_path,
        reward_funcs=reward_funcs,
        args=training_args,
        train_dataset=dataset[script_args.dataset_train_split],
        eval_dataset=dataset[script_args.dataset_test_split] if training_args.eval_strategy != "no" else None,
        peft_config=get_peft_config(model_args),
        callbacks=get_callbacks(training_args, model_args),
        processing_class=tokenizer,
    )

    ###############
    # Training loop
    ###############
    logger.info("*** Train ***")
    checkpoint = None
    if training_args.resume_from_checkpoint is not None:
        checkpoint = training_args.resume_from_checkpoint
    elif last_checkpoint is not None:
        checkpoint = last_checkpoint
    train_result = trainer.train(resume_from_checkpoint=checkpoint)
    metrics = train_result.metrics
    metrics["train_samples"] = len(dataset[script_args.dataset_train_split])
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    ##################################
    # Save model and create model card
    ##################################
    logger.info("*** Save model ***")
    trainer.save_model(training_args.output_dir)
    logger.info(f"Model saved to {training_args.output_dir}")

    ##########
    # Evaluate
    ##########
    if training_args.do_eval:
        logger.info("*** Evaluate ***")
        metrics = trainer.evaluate()
        metrics["eval_samples"] = len(dataset[script_args.dataset_test_split])
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    # Save everything else on main process
    kwargs = {
        "dataset_name": script_args.dataset_name,
        "tags": ["open-r1"],
    }
    
    # Optional: Create model card and push to hub
    # if trainer.accelerator.is_main_process:
    #     trainer.create_model_card(**kwargs)
    #     # Restore k,v cache for fast inference
    #     trainer.model.config.use_cache = True
    #     trainer.model.config.save_pretrained(training_args.output_dir)
    
    # if training_args.push_to_hub:
    #     logger.info("Pushing to hub...")
    #     trainer.push_to_hub(**kwargs)


if __name__ == "__main__":
    parser = TrlParser((GRPOScriptArguments, GRPOConfig, ModelConfig))
    script_args, training_args, model_args = parser.parse_args_and_config()
    print(script_args)
    main(script_args, training_args, model_args)



