import re
from typing import Dict, Any, Generator
from translate.storage import tmx

class LlmTmxDataSanitizer:
    """
    Integrates necrose99/Myaamia web sanitization routines natively 
    into the streaming llm-tmx toolkit engine pipeline.
    """
    def __init__(self, src_lang: str = "en", tgt_lang: str = "mia"):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def clean_mhtml_bloat(self, text: str) -> str:
        """
        Removes HTML tags, DOM paths, and MHTML/Blink frame trailing metadata
        to prevent downstream token pollution in Ollama/Gemma datasets.
        """
        if not text:
            return ""
        # 1. Strip MHTML/Blink frame string IDs
        text = re.sub(r'\+saved\.frame-[a-z0-9]+@mhtml\S+', '', text)
        # 2. Strip bleeding DOM structural paths
        text = re.sub(r'\.div\.\S+', '', text)
        # 3. Strip raw HTML tag enclosures
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def process_jsonl_stream_to_tmx(self, jsonl_lines: Generator[str, None, None]) -> tmx.tmxfile:
        """
        Accepts streamable JSONL string data, cleans the content on the fly, 
        and maps fields cleanly into a valid translate-toolkit TMX object.
        """
        # Create an empty, structurally correct translate-toolkit TMX unit asset
        tmx_file = tmx.tmxfile()
        
        for line in jsonl_lines:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                # Handle both normalized keys and nested data payload schemes
                raw_src = payload.get("src", payload.get("data", {}).get("source", ""))
                raw_tgt = payload.get("tgt", payload.get("data", {}).get("target", ""))
                
                clean_src = self.clean_mhtml_bloat(raw_src)
                clean_tgt = self.clean_mhtml_bloat(raw_tgt)
                
                # Filter out empty records or structural DOM leakage artifacts
                if clean_src and not clean_src.startswith('.'):
                    unit = tmx_file.add_source_string(clean_src)
                    unit.settarget(clean_tgt)
                    # Preserve implicit language directional mappings inside properties
                    unit.setnotes(f"ISO maps: {self.src_lang} -> {self.tgt_lang}")
            except Exception:
                continue
                
        return tmx_file
