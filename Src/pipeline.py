import json
import xml.etree.ElementTree as ET
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD
from translate.storage import tmx, xliff, po

class LlmTmxPipelineEngine:
    """
    Generalized Linguistic Ingestion Engine extending necrose99/Myaamia algorithms.
    Integrates XSLT transformations, OLAC metadata structures, and Ontolex-Lemon semantic graphs.
    """
    def __init__(self, src_lang: str = "en", tgt_lang: str = "mia", glottocode: str = "miam1252"):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.glottocode = glottocode
        self.base_uri = f"http://llm-tmx.org{self.tgt_lang}/"

    def execute_xslt_transmute(self, xml_input_path: str, xslt_sheet_path: str, output_path: str):
        """
        Generic hook executing your custom linguistics-suite XSLT layers
        (e.g., LIFT2lemon.xslt, xliff-to-tmx.xsl) via standard lxml bindings.
        """
        from lxml import etree
        
        print(f"⚙️ Running XSLT transmute: {Path(xslt_sheet_path).name}")
        dom = etree.parse(xml_input_path)
        xslt = etree.parse(xslt_sheet_path)
        transform = etree.XSLT(xslt)
        new_dom = transform(dom)
        
        with open(output_path, "wb") as f:
            f.write(etree.tostring(new_dom, pretty_print=True, encoding="utf-8"))

    def stream_jsonl_to_ontolex_ttl(self, jsonl_path: str, ttl_output_path: str):
        """
        Ported from your OLAC-import-standalone.py engine. Translates streamable
        JSONL objects directly into valid W3C Ontolex-Lemon RDF graphs.
        """
        g = Graph()
        ONTOLEX = Namespace("http://w3.org")
        LEXINFO = Namespace("http://lexinfo.net")
        
        g.bind("ontolex", ONTOLEX)
        g.bind("lexinfo", LEXINFO)
        g.bind("skos", SKOS)
        g.bind("rdfs", RDFS)
        
        base_ref = URIRef(self.base_uri)
        
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    src_word = payload.get("src", payload.get("data", {}).get("source", "")).strip()
                    tgt_gloss = payload.get("tgt", payload.get("data", {}).get("target", "")).strip()
                    props = payload.get("properties", payload.get("metadata", {}))
                    
                    if not src_word:
                        continue
                        
                    # Build individual node URIs cleanly
                    entry_uri = URIRef(f"{self.base_uri}entry/{src_word.replace(' ', '_')}")
                    form_uri = URIRef(f"{self.base_uri}form/{src_word.replace(' ', '_')}")
                    sense_uri = URIRef(f"{self.base_uri}sense/{src_word.replace(' ', '_')}")
                    
                    g.add((entry_uri, RDF.type, ONTOLEX.LexicalEntry))
                    g.add((entry_uri, ONTOLEX.canonicalForm, form_uri))
                    g.add((form_uri, RDF.type, ONTOLEX.Form))
                    g.add((form_uri, ONTOLEX.writtenRep, Literal(src_word, lang=self.tgt_lang)))
                    
                    g.add((entry_uri, ONTOLEX.sense, sense_uri))
                    g.add((sense_uri, RDF.type, ONTOLEX.LexicalSense))
                    g.add((sense_uri, RDFS.label, Literal(tgt_gloss, lang=self.src_lang)))
                    
                    # Map morphosynthetic parameters if they exist in the metadata stream
                    if "pos" in props:
                        g.add((entry_uri, LEXINFO.partOfSpeech, Literal(props["pos"])))
                    if "animacy" in props:
                        g.add((entry_uri, LEXINFO.gender, Literal(props["animacy"])))
                        
                except Exception:
                    continue
                    
        g.serialize(destination=ttl_output_path, format="turtle")
        print(f"✨ Successfully serialized Ontolex Turtle Graph: {ttl_output_path} ({len(g)} triples)")
