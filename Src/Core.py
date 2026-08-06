import io
import json
import xml.etree.ElementTree as ET
from typing import Generator, Dict, Any, Iterable

class LLMTranslationMiddleware:
    def __init__(self, src_lang: str = "en", tgt_lang: str = "cr"):
        """
        Initializes the bi-directional localization-to-LLM bridge.
        
        Args:
            src_lang (str): Source language code identifier (e.g., 'en').
            tgt_lang (str): Target language code identifier (e.g., 'cr').
        """
        self.src_lang = src_lang.lower()
        self.tgt_lang = tgt_lang.lower()
        
        # Core standards XML configurations
        self.xml_ns = {"xml": "http://w3.org"}
        
        # Plural and contextual suffixes to strip and isolate for structural JSON keys
        self.i18n_affixes = ["_one", "_other", "_many", "_few", "_zero", "_plural", "_male", "_female"]

    def _build_jsonl_message(self, src_text: str, tgt_text: str, extra_notes: str = "") -> str:
        """Formats source/target translation tokens into standard system/user/assistant structures."""
        system_content = f"You are a translation agent converting text from {self.src_lang} to {self.tgt_lang}."
        if extra_notes:
            system_content += f" Parameters: {extra_notes}."
            
        row = {
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": src_text.strip()},
                {"role": "assistant", "content": tgt_text.strip()}
            ]
        }
        return json.dumps(row, ensure_ascii=False)

    # =========================================================================
    # 1. TMX <-> JSONL ROUTINES
    # =========================================================================
    def tmx_to_jsonl(self, tmx_bytes: bytes) -> Generator[str, None, None]:
        """Streams a TMX XML byte payload and yields formatted JSONL strings on-the-fly."""
        context = ET.iterparse(io.BytesIO(tmx_bytes), events=("end",))
        for _, elem in context:
            if elem.tag == "tu":
                tuv_dict = {}
                for tuv in elem.findall("tuv"):
                    lang = tuv.get(f"{{{self.xml_ns['xml']}}}lang", tuv.get("lang", "")).lower()
                    seg = tuv.find("seg")
                    if lang and seg is not None and seg.text:
                        tuv_dict[lang] = seg.text
                
                if self.src_lang in tuv_dict and self.tgt_lang in tuv_dict:
                    yield self._build_jsonl_message(tuv_dict[self.src_lang], tuv_dict[self.tgt_lang])
                elem.clear()

    def jsonl_to_tmx(self, jsonl_lines: Iterable[str]) -> bytes:
        """Converts an iterable collection of LLM JSONL strings back into a strict TMX payload."""
        tmx = ET.Element("tmx", version="1.4")
        ET.SubElement(tmx, "header", creationtool="llm-tmx", creationtoolversion="1.0",
                      segtype="sentence", o_tmf="PlainText", adminlang="en", srclang=self.src_lang, datatype="PlainText")
        body = ET.SubElement(tmx, "body")

        for line in jsonl_lines:
            if not line.strip(): continue
            data = json.loads(line)
            u_txt = next(m['content'] for m in data['messages'] if m['role'] == 'user')
            a_txt = next(m['content'] for m in data['messages'] if m['role'] == 'assistant')

            tu = ET.SubElement(body, "tu")
            for lang, text in [(self.src_lang, u_txt), (self.tgt_lang, a_txt)]:
                tuv = ET.SubElement(tu, "tuv")
                tuv.set(f"{{{self.xml_ns['xml']}}}lang", lang)
                ET.SubElement(tuv, "seg").text = text

        ET.indent(tmx, space="  ", level=0)
        return ET.tostring(tmx, encoding="utf-8", method="xml")

    # =========================================================================
    # 2. XLIFF <-> JSONL ROUTINES
    # =========================================================================
    def xliff_to_jsonl(self, xliff_bytes: bytes) -> Generator[str, None, None]:
        """Streams a legacy or standard XLIFF byte array, yielding structured JSONL lines."""
        context = ET.iterparse(io.BytesIO(xliff_bytes), events=("end",))
        for _, elem in context:
            tag_name = elem.tag.split("}")[-1]  # Simple approach to handle variable namespaces
            if tag_name == "trans-unit":
                src = elem.find(".//{*}source")
                tgt = elem.find(".//{*}target")
                if src is not None and tgt is not None and src.text and tgt.text:
                    yield self._build_jsonl_message(src.text, tgt.text)
                elem.clear()

    def jsonl_to_xliff(self, jsonl_lines: Iterable[str]) -> bytes:
        """Converts LLM JSONL records back into an industry-compliant localized XLIFF structure."""
        xliff = ET.Element("xliff", version="1.2", xmlns="urn:oasis:names:tc:xliff:document:1.2")
        file_node = ET.SubElement(xliff, "file", original="llm-translation-memory",
                                  source-language=self.src_lang, target-language=self.tgt_lang, datatype="plaintext")
        body = ET.SubElement(file_node, "body")

        for idx, line in enumerate(jsonl_lines):
            if not line.strip(): continue
            data = json.loads(line)
            u_txt = next(m['content'] for m in data['messages'] if m['role'] == 'user')
            a_txt = next(m['content'] for m in data['messages'] if m['role'] == 'assistant')

            tu = ET.SubElement(body, "trans-unit", id=str(idx))
            ET.SubElement(tu, "source").text = u_txt
            ET.SubElement(tu, "target").text = a_txt

        ET.indent(xliff, space="  ", level=0)
        return ET.tostring(xliff, encoding="utf-8", method="xml")

    # =========================================================================
    # 3. i18n JSON -> JSONL ROUTINES
    # =========================================================================
    def _unpack_i18n(self, item: Any, key_path: str = "") -> Dict[str, str]:
        """Recursively flattens deeply nested structural keys into dot-notation paths."""
        flat = {}
        if isinstance(item, dict):
            for k, v in item.items():
                p = f"{key_path}.{k}" if key_path else k
                flat.update(self._unpack_i18n(v, p))
        else:
            flat[key_path] = str(item)
        return flat

    def i18n_json_to_jsonl(self, src_json_bytes: bytes, tgt_json_bytes: bytes) -> Generator[str, None, None]:
        """Aligns separate localized JSON arrays, extracts affixes, and yields JSONL."""
        src_map = self._unpack_i18n(json.loads(src_json_bytes.decode('utf-8')))
        tgt_map = self._unpack_i18n(json.loads(tgt_json_bytes.decode('utf-8')))

        for path, src_text in src_map.items():
            if path in tgt_map:
                tgt_text = tgt_map[path]
                clean_key = path
                meta = []
                
                # Strip out programmatic grammar suffixes and place them into instruction context
                for suffix in self.i18n_affixes:
                    if clean_key.endswith(suffix):
                        clean_key = clean_key[:-len(suffix)]
                        meta.append(f"Grammar: {suffix.lstrip('_')}")
                        break
                        
                context_str = f"Key: {clean_key}"
                if meta: 
                    context_str += f", Context: {', '.join(meta)}"
                
                yield self._build_jsonl_message(src_text, tgt_text, extra_notes=context_str)
