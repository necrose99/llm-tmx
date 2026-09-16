## Instructions
1. **Discovery & Input Parsing**: Read the targeted ISO language variables (e.g., `mia`).
2. **Delta Extraction**: Scan live category web targets for structural document improvements.
3. **Compile Wiki Blocks**: Append newfound text segments into local `llm-wiki` repository files.
4. **Execute Core Pipeline**: Rebuild streaming `.jsonl` lines and `.ttl` Ontolex data loops.
5. **SIL Down-Compilation Pass**: Automatically call `LlmTmxSfmConverter` to transform your freshly generated `.ttl` graph straight into a `\lx` delimited `.sfm` asset file. This ensures language workers can immediately pull the model's outputs straight into FLEx/Toolbox dictionary engines.

6. # Skill: Automated Language Corpus Compilation Agent

## Description
Triggers when processing historical language book scans, PDFs, or raw XML datasets to normalize content, execute structural XSLT transforms, and construct an interactive, RAG-ready AnythingLLM notebook workspace.

## Instructions
1. **Extraction**: Run vision OCR / extraction layers over historical book fragments.
2. **Sanitization**: Process the unstructured data through the `LlmTmxDataSanitizer` block. Clear out all BLEEDING DOM elements or trailing HTML noise artifacts.
3. **Linguistic Refinement**: Apply your custom `LIFT2lemon` or `tmx_to_ontolex` routines. Build a strict, interconnected graph model containing part-of-speech annotations and provenance metadata attributes.
4. **Notebook Export**: Generate a unified Markdown Glossary Notebook containing clean vocabulary definitions and append it straight to AnythingLLM's local system storage folder.

