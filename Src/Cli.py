import sys
import argparse
from llm_tmx.core import LLMTranslationMiddleware

def main():
    parser = argparse.ArgumentParser(description="llm-tmx: Convert localization schemas to conversational JSONL arrays on-the-fly.")
    parser.add_argument("--format", choices=["tmx", "xliff"], required=True, help="Input localization file architecture standard.")
    parser.add_argument("--src", default="en", help="Source language identifier code label.")
    parser.add_argument("--tgt", default="cr", help="Target language identifier code label.")
    args = parser.parse_args()

    # Ingest the target stream file straight via standard input channel pipes
    middleware = LLMTranslationMiddleware(src_lang=args.src, tgt_lang=args.tgt)
    input_bytes = sys.stdin.buffer.read()

    try:
        if args.format == "tmx":
            stream_generator = middleware.tmx_to_jsonl(input_bytes)
        elif args.format == "xliff":
            stream_generator = middleware.xliff_to_jsonl(input_bytes)
        
        for jsonl_line in stream_generator:
            sys.stdout.write(jsonl_line + "\n")
            sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"Conversion Execution Error: {str(e)}\n")
        sys.exit(1)
