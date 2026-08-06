import sys
import argparse
from pathlib import Path
from llm_tmx.core import LLMTranslationMiddleware

def main():
    parser = argparse.ArgumentParser(
        description="llm-tmx: Bi-directional translation layout converter for LLM middleware pipelines."
    )
    parser.add_argument(
        "--format", 
        choices=["tmx", "xliff", "i18n-json"], 
        required=True, 
        help="Input translation data standard format."
    )
    parser.add_argument("--src", default="en", help="Source language identifier code label.")
    parser.add_argument("--tgt", default="cr", help="Target language identifier code label.")
    
    # Paths required specifically for matching separate i18n JSON collections
    parser.add_argument("--src-file", type=str, help="Path to source file (Required for i18n-json).")
    parser.add_argument("--tgt-file", type=str, help="Path to target file (Required for i18n-json).")
    
    args = parser.parse_args()
    middleware = LLMTranslationMiddleware(src_lang=args.src, tgt_lang=args.tgt)

    try:
        if args.format == "i18n-json":
            if not args.src_file or not args.tgt_file:
                sys.stderr.write("Error: --src-file and --tgt-file are required when format is 'i18n-json'.\n")
                sys.exit(1)
            
            src_bytes = Path(args.src_file).read_bytes()
            tgt_bytes = Path(args.tgt_file).read_bytes()
            stream_generator = middleware.i18n_json_to_jsonl(src_bytes, tgt_bytes)
            
        else:
            # TMX and XLIFF can ingest raw bytes straight from standard input pipes
            input_bytes = sys.stdin.buffer.read()
            if args.format == "tmx":
                stream_generator = middleware.tmx_to_jsonl(input_bytes)
            elif args.format == "xliff":
                stream_generator = middleware.xliff_to_jsonl(input_bytes)

        # Output rows sequentially to preserve memory overhead
        for jsonl_line in stream_generator:
            sys.stdout.write(jsonl_line + "\n")
            sys.stdout.flush()

    except Exception as e:
        sys.stderr.write(f"Conversion Execution Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
