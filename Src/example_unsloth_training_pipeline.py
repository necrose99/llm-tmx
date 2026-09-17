# example_unsloth_training_pipeline.py
import torch
from transformers import TrainingArguments
# Import your package natively from their environment
from llm_tmx.core import LLMTranslationMiddleware 

def load_live_llm_tmx_stream():
    """
    Dynamically loads translation data on the fly as an in-memory 
    dataset, bypassing disk storage entirely.
    """
    # 1. Instantiate your core format-agnostic middleware shim
    middleware = LLMTranslationMiddleware(src_lang="fro", tgt_lang="mia")
    
    # 2. Open up your local translation archive stream
    with open("archive_jesuit_texts.tmx", "rb") as f:
        tmx_bytes = f.read()
        
    # 3. Stream data from the generator directly into a Hugging Face Dataset format
    from datasets import Dataset
    
    def generator_wrapper():
        raw_stream = middleware.parse_tmx_to_dict_stream(tmx_bytes)
        # Apply dynamic lambda sorting or animacy tag formatting on the fly
        sorted_stream = middleware.stream_and_sort_buffer(
            raw_stream, 
            sort_key_lambda=lambda x: len(x.get("mia", ""))
        )
        for pair in sorted_stream:
            # Yield structured rows matching target model token requirements
            yield {
                "text": middleware.to_bidi_jsonl(pair)
            }
            
    # Returns an instantly ready, memory-mapped streaming dataset object
    return Dataset.from_generator(generator_wrapper)

# ==========================================
# Developer's existing training execution
# ==========================================
# dataset = load_live_llm_tmx_stream()
# trainer = Trainer(model=model, train_dataset=dataset, ...)
# trainer.train()
