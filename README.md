# llm-tmx

A zero-dependency, streaming, bi-directional translation middleware to convert legacy localization data architectures (`.tmx`, `.xliff`, structured `.json`) into training-ready conversational formats (`.jsonl`) on the fly. 

Designed specifically to prepare low-resource language resources (e.g., Algic language dictionary records) for local LLM pipelines like **Ollama**, **Gemini**, and **OpenAI Fine-Tuning**.

## Key Features
* **Zero Disk Storage I/O:** Runs on Python generators to stream heavy translation datasets with negligible memory footprints.
* **Smart Suffix Extraction:** Unpacks complex nested keys and automatically translates application suffixes (e.g., `_one`, `_other`) into natural text prompt instructions.
* **Universal Target Schema:** Converts all structures to standardized `system`/`user`/`assistant` payload message arrays.

## Installation
```bash
pip install llm-tmx
```

## Quick Start (Terminal Pipes)

### Convert TMX to JSONL lines
```bash
cat local_dictionary.tmx | llm-tmx --format tmx --src en --tgt cr > dataset.jsonl
```

### Convert XLIFF data
```bash
cat application.xlf | llm-tmx --format xliff --src en --tgt oj > dataset.jsonl
```

### Unpack Coupled Application JSON files
```bash
llm-tmx --format i18n-json --src en --tgt cr --src-file en.json --tgt-file cr.json > dataset.jsonl
```

## Python Integration Middleware Usage

```python
from llm_tmx.core import LLMTranslationMiddleware

# Initialize the translation adapter
middleware = LLMTranslationMiddleware(src_lang="en", tgt_lang="cr")

# Stream data over memory loops on-the-fly
with open("locales.xlf", "rb") as f:
    for jsonl_line in middleware.xliff_to_jsonl(f.read()):
        # Pipe directly into Ollama API payloads or fine-tuning wrappers
        print(jsonl_line)
```

## License
Distributed under the MIT License. See `LICENSE` for details.
# llm-tmx
