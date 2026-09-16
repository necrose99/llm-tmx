import json
import urllib.request
import csv
import io
from pathlib import Path

def generate_global_map_file(output_path: str = "languages.map"):
    """
    Downloads canonical language identifier metadata from Glottolog
    and builds an optimized master .map config schema file.
    """
    glottolog_csv_url = "https://glottolog.org"
    print("⏳ Downloading global language matrices from Glottolog API...")
    
    try:
        req = urllib.request.Request(glottolog_csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            csv_content = response.read().decode('utf-8')
            
        reader = csv.DictReader(io.StringIO(csv_content))
        master_map = {}
        
        for row in reader:
            iso = row.get("iso639-3")
            glottocode = row.get("id")
            name = row.get("name")
            level = row.get("level")
            
            # Isolate genuine languages containing registered ISO tokens
            if iso and level == "language":
                master_map[iso] = {
                    "language_name": name,
                    "glottocode": glottocode,
                    "glottolog_uri": f"https://glottolog.org{glottocode}",
                    "source_url": f"https://wiktionary.org:{name}_language",
                    "dom_selectors": {
                        "entry_node": "li",
                        "lexical_lemma": "strong",
                        "definition_block": "ol"
                    },
                    "export_targets": ["ttl", "tmx", "jsonl"]
                }
                
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(master_map, f, indent=2, ensure_ascii=False)
        print(f"✅ Master map compiled successfully! {len(master_map)} languages mapped.")
        
    except Exception as e:
        print(f"⚠️ Live download interrupted ({e}). Dropping local fallback index.")
        fallback = {
            "mia": {"language_name": "Miami", "glottocode": "miam1252", "export_targets": ["ttl", "jsonl"]},
            "crj": {"language_name": "Southern East Cree", "glottocode": "sout2978", "export_targets": ["ttl", "tmx"]}
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)

if __name__ == "__main__":
    generate_global_map_file()
