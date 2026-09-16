# 📚 llm-tmx-anythingllm

A pluggable, zero-configuration background data ingestion tool and interactive notebook wrapper for **AnythingLLM**. It automates the extraction, transformation, and linguistic normalization of legacy translation datasets into RAG-ready vector spaces.

This subsystem provides a clean local bridge for low-resource, ancient, or under-documented languages (e.g., Miami-Illinois, Lenape, Potawatomi) where standard commercial translation infrastructure does not exist or fails critical academic validation audits.

## 🧠 The Problem It Solves

### 1. Eliminating Token Pollution (DOM/MHTML Bloat)
Raw data collection from archives or web mirrors often introduces structural layout artifacts. If inputs contain leaking browser serialization paths (e.g., `.div.mw-category` or frame tracking variables like `+saved.frame-...@mhtml`), local models waste contextual parameters trying to tokenize and process markup noise. This core automatically scrubs these markers on the fly.

### 2. Ensuring Accuracy for Rare Morphosyntax
Low-resource and polysynthetic languages require precise structural tracking. For instance, in Algonquian/Algic languages, a feature contrast like animate vs. inanimate forces entirely different morphosyntactic structures (e.g., distinguishing a family of four from five inanimate objects). `llm-tmx` leverages **Ontolex-Lemon (`.ttl`)** graphs to ensure models are trained on morphosyntactically sound data footprints rather than speculative text blobs.

### 3. Streamlined 24/7 "Data Cooking"
Instead of forcing researchers to manually parse and enter entries, this plugin sets up a clean automation loop:
