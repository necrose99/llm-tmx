# Src/plugin.py
"""
Dynamic plugin broker for llm-tmx. Handles optional external parsing backends 
like pyglossary or translate-toolkit on a best-effort basis.
"""
import sys
import importlib
from typing import Generator, Dict, Any

class LLMPluginBroker:
    def __init__(self, middleware_instance):
        self.mw = middleware_instance

    def has_backend(self, backend_name: str) -> bool:
        """Checks if an optional dependency plugin is available in the current runtime environment."""
        try:
            importlib.import_module(backend_name)
            return True
        except ImportError:
            return False

    def stream_via_pyglossary(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """
        Best-effort fallback hook using pyglossary to stream complex dictionary formats 
        (e.g., StarDict, BGL, Apple Glossary) into uniform llm-tmx dict objects.
        """
        if not self.has_backend("pyglossary"):
            print("[llm-tmx plugin] pyglossary is not installed. Falling back to native core engines...", file=sys.stderr)
            return

        # Dynamically import heavy framework inside the call block to preserve zero-dependency boot
        from pyglossary import Glossary
        Glossary.init()
        glos = Glossary()
        
        # Load dictionary structure lazily
        glos.read(file_path)
        
        for entry in glos:
            # Normalize pyglossary data mapping to our universal core keys
            src_text = getattr(entry, 'word', '')
            tgt_text = getattr(entry, 'definition', '')
            
            if isinstance(src_text, list): src_text = " ".join(src_text)
            if isinstance(tgt_text, list): tgt_text = " ".join(tgt_text)
            
            if src_text and tgt_text:
                yield {
                    self.mw.src_lang: src_text,
                    self.mw.tgt_lang: tgt_text,
                    "source_format": "pyglossary_plugin"
                }

    def execute_best_effort_stream(self, file_path: str, native_generator: Generator) -> Generator[Dict[str, Any], None, None]:
        """
        Orchestrator that eats own dogfood by default, but dynamically upgrades 
        to advanced plugin libraries if available or if the extension demands it.
        """
        ext = file_path.split('.')[-1].lower()
        
        # For non-standard formats where pyglossary rules supreme, intercept early
        if ext in ['sdict', 'bgl', 'xdxf'] and self.has_backend("pyglossary"):
            yield from self.stream_via_pyglossary(file_path)
            return
            
        # Default behavior: Eat our own lean dogfood
        yield from native_generator
