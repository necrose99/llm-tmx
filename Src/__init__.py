# src/llm_tmx/__init__.py
"""
llm-tmx: A streaming, bi-directional translation middleware converting 
TMX, XLIFF, and i18n JSON data to LLM JSONL lines on-the-fly.
"""

# Hardcoded version target for Hatch's dynamic regex parsing engine
__version__ = "0.1.0"

# Expose core middleware bridge for clean top-level library imports
from llm_tmx.core import LLMTranslationMiddleware

__all__ = ["LLMTranslationMiddleware", "__version__"]
