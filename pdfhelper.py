import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

class LlmTmxGenericPipeline:
    def __init__(self, iso_code: str, glottocode: str):
        self.iso = iso_code
        self.glotto = glottocode

    def transmute_lift_to_lemon_ttl(self, lift_xml_path: str, output_ttl_path: str):
        """
        Generic LIFT-to-Ontolex-Lemon converter. Parses standard Lexical Interchange 
        Format (LIFT) files used by SIL tools into graph-ready RDF/Turtle.
        """
        try:
            tree = ET.parse(lift_xml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Failed parsing LIFT XML file: {e}")
            return

        header = (
            "@prefix ontolex: <http://w3.org> .\n"
            "@prefix lexinfo: <http://lexinfo.net> .\n"
            "@prefix xsd:     <http://w3.org> .\n"
            f"@prefix glotto:  <https://glottolog.org{self.glotto}> .\n"
            f"@prefix lex:     <http://llm-tmx.org{self.iso}/lexicon/> .\n\n"
        )

        with open(output_ttl_path, "w", encoding="utf-8") as out:
            out.write(header)
            
            # Iterate through standard LIFT entry nodes
            for idx, entry in enumerate(root.findall(".//entry")):
                lexical_unit = entry.find(".//lexical-unit/form")
                definition = entry.find(".//definition/form") or entry.find(".//gloss")
                
                if lexical_unit is not None and definition is not None:
                    lemma = lexical_unit.find("text").text if lexical_unit.find("text") is not None else ""
                    gloss = definition.find("text").text if definition.find("text") is not None else ""
                    
                    # Clean escaping for string literals
                    lemma_clean = lemma.replace('"', '\\"')
                    gloss_clean = gloss.replace('"', '\\"')
                    
                    if lemma_clean and gloss_clean:
                        ttl_node = (
                            f"lex:Entry_{idx} a ontolex:LexicalEntry ;\n"
                            f'    ontolex:canonicalForm [ ontolex:writtenRep "{lemma_clean}"@{self.iso} ] ;\n'
                            f'    ontolex:denotes [ ontolex:writtenRep "{gloss_clean}"@en ] ;\n'
                            f'    lexinfo:provenance glotto: .\n\n'
                        )
                        out.write(ttl_node)
        print(f"✅ Successfully converted LIFT to Ontolex Lemon TTL graph: {output_ttl_path}")

    def compile_markdown_to_pot(self, wiki_md_path: str, output_pot_path: str):
        """
        Reads a compiled markdown wiki page or book extraction and converts it into a 
        standard GNU gettext Portable Object Template (.pot) file for translation tool tracking.
        """
        md_content = Path(wiki_md_path).read_text(encoding="utf-8")
        
        # Simple extraction pattern tracking structural blocks or vocabulary lines
        # Captures patterns like "### Word" or custom glossary text patterns
        lines = md_content.splitlines()
        pot_entries = []
        
        for line in lines:
            if line.startswith("### ") or line.startswith("- "):
                clean_segment = line.replace("### ", "").replace("- ", "").strip()
                if clean_segment and len(clean_segment) < 100:  # Ignore full long paragraphs
                    pot_entries.append(clean_segment.replace('"', '\\"'))

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M%z")
        pot_header = (
            f"# Generated via llm-tmx engine pipeline\n"
            f'msgid ""\n'
            f'msgstr ""\n'
            f'"Project-Id-Version: llm-tmx 1.0\\n"\n'
            f'"POT-Creation-Date: {timestamp}\\n"\n'
            f'"MIME-Version: 1.0\\n"\n'
            f'"Content-Type: text/plain; charset=UTF-8\\n"\n'
            f'"Content-Transfer-Encoding: 8bit\\n"\n\n'
        )

        with open(output_pot_path, "w", encoding="utf-8") as f:
            f.write(pot_header)
            for item in sorted(list(set(pot_entries))):
                f.write(f'#. Source segment node context marker\n')
                f.write(f'msgid "{item}"\n')
                f.write(f'msgstr ""\n\n')
        print(f"📦 Portable Object Template file generated at: {output_pot_path}")

# Pipeline Usage Test Loop Setup:
# pipeline = LlmTmxGenericPipeline(iso_code="pot", glottocode="pota1247")  # Potawatomi settings example
# pipeline.transmute_lift_to_lemon_ttl("potawatomi_dictionary.lift", "potawatomi_graph.ttl")
