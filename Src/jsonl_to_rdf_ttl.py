import json
from pathlib import Path

class LlmTmxSemanticStore:
    def __init__(self, map_file: str = "languages.map", custom_override_file: str = "custom.map"):
        self.map_file = Path(map_file)
        self.override_file = Path(custom_override_file)
        self.registry = self._load_unified_registry()
        
    def _load_unified_registry(self) -> dict:
        """Loads master language entries and safely layers user-pushed forks/overrides."""
        if not self.map_file.exists():
            return {}
        with open(self.map_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if self.override_file.exists():
            print(f"⚙️ Overlaying custom configuration mappings from {self.override_file.name}...")
            with open(self.override_file, "r", encoding="utf-8") as f:
                overrides = json.load(f)
            for iso, configurations in overrides.items():
                if iso in data:
                    data[iso].update(configurations)
                else:
                    data[iso] = configurations
        return data

    def stream_jsonl_to_rdf_ttl(self, input_jsonl: str, output_ttl: str, iso_code: str):
        """
        Converts streaming raw translation entries into structural Ontolex-Lemon 
        Turtle statements ensuring explicit provenance trails for historical analysis.
        """
        if iso_code not in self.registry:
            print(f"❌ Language ISO '{iso_code}' not initialized in mapping definitions.")
            return
            
        meta = self.registry[iso_code]
        glotto = meta.get("glottocode", "unknown")
        
        # Standard structural namespaces for linguistic data modeling
        ttl_header = (
            f"@prefix ontolex: <http://w3.org> .\n"
            f"@prefix lexinfo: <http://lexinfo.net> .\n"
            f"@prefix xsd:     <http://w3.org> .\n"
            f"@prefix glotto:  <https://glottolog.org> .\n"
            f"@prefix local:   <http://llm-tmx.org{iso_code}/> .\n\n"
        )
        
        with open(input_jsonl, "r", encoding="utf-8") as infile, \
             open(output_ttl, "w", encoding="utf-8") as outfile:
                 
            outfile.write(ttl_header)
            
            for index, line in enumerate(infile):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    # Extract string variables handling potential nesting schemas
                    src_phrase = payload.get("data", {}).get("source", payload.get("src", "")).replace('"', '\\"')
                    tgt_phrase = payload.get("data", {}).get("target", payload.get("tgt", "")).replace('"', '\\"')
                    
                    # Capture deep morphosynthetic tags (e.g. animacy, pos, obviation values)
                    props = payload.get("properties", payload.get("metadata", {}))
                    animacy_tag = props.get("animacy", "unspecified")
                    pos_tag = props.get("pos", "Lexeme")
                    
                    ttl_node = (
                        f"local:LexEntry_{index} a ontolex:LexicalEntry ;\n"
                        f'    ontolex:canonicalForm [ ontolex:writtenRep "{src_phrase}"@{iso_code} ] ;\n'
                        f'    ontolex:denotes [ ontolex:writtenRep "{tgt_phrase}"@en ] ;\n'
                        f'    lexinfo:partOfSpeech "{pos_tag}"^^xsd:string ;\n'
                        f'    lexinfo:gender "{animacy_tag}"^^xsd:string ;\n'
                        f'    lexinfo:provenance glotto:{glotto} .\n\n'
                    )
                    outfile.write(ttl_node)
                except Exception as parse_error:
                    print(f"Skipping damaged line entry {index}: {parse_error}")

# Usage Loop Sample:
# engine = LlmTmxSemanticStore()
# engine.stream_jsonl_to_rdf_ttl("myaamia_raw.jsonl", "myaamia_graph.ttl", "mia")
