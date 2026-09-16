const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * AnythingLLM Background Plugin Event Loop Interface
 */
function onWorkspaceUpdate(workspaceSettings) {
  const pythonBinary = 'python3';
  const scriptPath = path.join(__dirname, 'bin', 'tmx_worker.py');
  
  // Extract background properties saved from user settings panel
  const targetIso = workspaceSettings.target_iso || 'mia';
  const glotto = workspaceSettings.glottocode || 'miam1252';
  const ollamaUrl = workspaceSettings.ollama_endpoint || 'http://localhost:11434';
  
  // Locate AnythingLLM's internal system path to dump generated markdown notes
  const anythingllmDocumentsFolder = path.resolve(__dirname, '../../storage/documents');
  const targetNotebookPath = path.join(anythingllmDocumentsFolder, `${targetIso}_glossary_notebook.md`);

  console.log(`[llm-tmx] Ingesting updates for ${targetIso}...`);

  execFile(pythonBinary, [scriptPath, targetIso, glotto, ollamaUrl, targetNotebookPath], (error, stdout, stderr) => {
    if (error) {
      console.error(`[llm-tmx-error] Sync routine crashed: ${stderr}`);
      return;
    }
    console.log(`[llm-tmx-success] System logs updated successfully: ${stdout}`);
  });
}

module.exports = { onWorkspaceUpdate };
