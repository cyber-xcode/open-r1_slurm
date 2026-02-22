#!/usr/bin/env python
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

"""
Supervised fine-tuning script specifically for Llama-3.1-8B-Instruct models.

Usage:
accelerate launch --config_file=recipes/accelerate_configs/zero2.yaml sft_llama_inst.py \
    --model_name_or_path meta-llama/Llama-3.1-8B-Instruct \
    --dataset_name open-r1/OpenR1-Math-220k \
    --eos_token '<|eot_id|>' \
    --learning_rate 2.0e-5 \
    --num_train_epochs 2 \
    --max_seq_length 8192 \
    --per_device_train_batch_size 2 \
    --gradient_checkpointing \
    --bf16 \
    --use_liger_kernel \
    --output_dir data/Llama-3.1-8B-Instruct-OpenR1
"""

import logging
import os
import sys

import datasets
import transformers
from datasets import load_dataset
from transformers import set_seed
from transformers.trainer_utils import get_last_checkpoint

from open_r1.utils_v2.configs import ScriptArguments, SFTConfig
from open_r1.utils_v2 import get_dataset, get_model, get_tokenizer
from open_r1.utils_v2.callbacks import get_callbacks
from open_r1.utils_v2.wandb_logging import init_wandb_training
from trl import ModelConfig, SFTTrainer, TrlParser, get_peft_config


logger = logging.getLogger(__name__)


def validate_llama_instruct_tokenizer(tokenizer, training_args):
    """
    Validate that the tokenizer has the correct special tokens for Llama-3.1-Instruct.
    
    Args:
        tokenizer: The loaded tokenizer
        training_args: Training configuration
    
    Raises:
        AssertionError: If tokens don't match expected values
    """
    # Expected tokens for Llama-3.1-Instruct
    expected_bos = "<|begin_of_text|>"
    expected_chat_eos = "<|eot_id|>"  # EOS token for chat template
    expected_base_eos = "<|end_of_text|>"  # Base model EOS (we'll override this)
    
    # Check BOS token
    assert tokenizer.bos_token == expected_bos, (
        f"BOS token mismatch! Expected '{expected_bos}' but got '{tokenizer.bos_token}'. "
        "Make sure you're using the correct Llama-3.1-Instruct model."
    )
    logger.info(f"✓ BOS token verified: {tokenizer.bos_token}")
    
    # Check if EOS token was properly set via command line or config
    if hasattr(training_args, 'eos_token') and training_args.eos_token:
        assert training_args.eos_token == expected_chat_eos, (
            f"EOS token should be '{expected_chat_eos}' for Llama-3.1-Instruct chat template, "
            f"but got '{training_args.eos_token}'. Please use --eos_token '<|eot_id|>'"
        )
        # Update tokenizer EOS token
        tokenizer.eos_token = training_args.eos_token
        logger.info(f"✓ EOS token set to chat template token: {tokenizer.eos_token}")
    else:
        # Warn if EOS token wasn't explicitly set
        logger.warning(
            f"EOS token not explicitly set! The model's default EOS is '{tokenizer.eos_token}' "
            f"but the chat template expects '{expected_chat_eos}'. "
            f"Setting EOS token to '{expected_chat_eos}' for proper generation stopping."
        )
        tokenizer.eos_token = expected_chat_eos
        
    # Check and set PAD token
    if tokenizer.pad_token is None:
        # Common practice: set pad_token to eos_token
        tokenizer.pad_token = tokenizer.eos_token
        logger.info(f"✓ PAD token set to EOS token: {tokenizer.pad_token}")
    else:
        logger.info(f"✓ PAD token already set: {tokenizer.pad_token}")
    
    # Verify chat template exists
    assert tokenizer.chat_template is not None, (
        "Chat template is missing! This doesn't look like a Llama-3.1-Instruct model. "
        "Please verify you're using 'meta-llama/Llama-3.1-8B-Instruct'."
    )
    logger.info("✓ Chat template found")
    
    # Additional validation: Check if model path suggests it's an instruct model
    model_name = getattr(training_args, 'model_name_or_path', '')
    if 'instruct' not in model_name.lower():
        logger.warning(
            f"Model path '{model_name}' doesn't contain 'instruct'. "
            "Please verify you're using the Instruct variant, not the base model."
        )
    
    # Log token IDs for debugging
    logger.info(f"Token IDs - BOS: {tokenizer.bos_token_id}, "
                f"EOS: {tokenizer.eos_token_id}, "
                f"PAD: {tokenizer.pad_token_id}")
    
    return True


def main(script_args, training_args, model_args):
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
    #datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    logger.info("=" * 50)
    logger.info("Llama-3.1-8B-Instruct SFT Training Script")
    logger.info("=" * 50)
    logger.info(f"Model parameters {model_args}")
    logger.info(f"Script parameters {script_args}")
    logger.info(f"Training parameters {training_args}")

    # Validate model path
    if "llama" not in model_args.model_name_or_path.lower():
        logger.warning(
            f"Model path '{model_args.model_name_or_path}' doesn't appear to be a Llama model. "
            "This script is specifically designed for Llama-3.1-8B-Instruct."
        )

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

    ######################################
    # Load dataset, tokenizer, and model #
    ######################################
    if type(script_args.dataset_name) in [ dict,list]  or  script_args.dataset_name.endswith(".jsonl"):
        dataset = load_dataset("json", data_files=script_args.dataset_name )
    else:
        dataset = load_dataset(script_args.dataset_name, name=script_args.dataset_config)
    for split in dataset:
        if "messages" in dataset[split].column_names:
            remove_cl = [cl  for cl in dataset[split].column_names if cl != "messages" ] 
            dataset[split] = dataset[split].remove_columns( remove_cl )
    
    logger.info("Loading tokenizer...")
    tokenizer = get_tokenizer(model_args, training_args)
    
    # Validate tokenizer configuration for Llama-3.1-Instruct
    logger.info("Validating Llama-3.1-Instruct tokenizer configuration...")
    validate_llama_instruct_tokenizer(tokenizer, training_args)
    
    logger.info("Loading model...")
    model = get_model(model_args, training_args)

    # Double-check that chat template is properly set
    if tokenizer.chat_template is None:
        raise ValueError(
            "Chat template is missing after loading! This should not happen with "
            "Llama-3.1-8B-Instruct. Please check your model path and version."
        )

    ############################
    # Initialize the SFT Trainer
    ############################
    logger.info("Initializing SFT trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset[script_args.dataset_train_split],
        eval_dataset=(dataset[script_args.dataset_test_split] if training_args.eval_strategy != "no" else None),
        processing_class=tokenizer,
        peft_config=get_peft_config(model_args),
        callbacks=get_callbacks(training_args, model_args),
    )

    ###############
    # Training loop
    ###############
    logger.info("*** Starting Training ***")
    logger.info(f"Number of training samples: {len(dataset[script_args.dataset_train_split])}")
    logger.info(f"Max sequence length: {training_args.max_seq_length}")
    logger.info(f"Training for {training_args.num_train_epochs} epochs")
    
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
    logger.info("*** Saving Model ***")
    
    # Critical: Align the model's generation config with the tokenizer's eos token
    # This prevents unbounded generation during inference
    trainer.model.generation_config.eos_token_id = tokenizer.eos_token_id
    logger.info(f"Set generation_config.eos_token_id to {tokenizer.eos_token_id} ({tokenizer.eos_token})")
    
    trainer.save_model(training_args.output_dir)
    logger.info(f"Model saved to {training_args.output_dir}")

    # Save everything else on main process
    kwargs = {
        "dataset_name": script_args.dataset_name,
        "tags": ["open-r1", "llama-3.1-8b-instruct"],
    }
    if trainer.accelerator.is_main_process:
        trainer.create_model_card(**kwargs)
        # Restore k,v cache for fast inference
        trainer.model.config.use_cache = True
        trainer.model.config.save_pretrained(training_args.output_dir)
        

    ##########
    # Evaluate
    ##########
    if training_args.do_eval:
        logger.info("*** Evaluate ***")
        metrics = trainer.evaluate()
        metrics["eval_samples"] = len(dataset[script_args.dataset_test_split])
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    #############
    # Push to hub
    #############
    if training_args.push_to_hub:
        logger.info("Pushing to hub...")
        trainer.push_to_hub(**kwargs)



if __name__ == "__main__":
    parser = TrlParser((ScriptArguments, SFTConfig, ModelConfig))
    
    # Parse arguments
    script_args, training_args, model_args = parser.parse_args_and_config()
    
    # Ensure EOS token is set for Llama instruct
    if not hasattr(training_args, 'eos_token') or not training_args.eos_token:
        print("\n" + "=" * 60)
        print("WARNING: EOS token not set!")
        print("For Llama-3.1-8B-Instruct, you should use: --eos_token '<|eot_id|>'")
        print("=" * 60 + "\n")
    
    main(script_args, training_args, model_args)

