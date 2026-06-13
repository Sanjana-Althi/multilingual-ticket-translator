# 🧠 Prompts Used – Multilingual Ticket Translator
## AI Usage Documentation
### Infinite Computer Solutions Placement Drive — Round 3 Case Study
**Team 9 · UC ID: SD-04 · Category: Service Desk**

---

## 📌 Overview

This document captures the key AI prompts used during the development of the **Multilingual Ticket Translator** system.

AI tools such as **Claude AI and ChatGPT** were used  for:
- System design
- Backend logic development
- Streamlit UI creation
- Debugging and refinement
- Documentation support

The project follows an AI-assisted development approach, where human implementation was combined with iterative AI guidance.

---

## 🤖 AI Tools Used

- Claude AI
- ChatGPT

---

## 🧠 What AI Helped With
## 1. System Architecture Design  
- AI helped design the full pipeline: Detect → Protect → Translate → Respond → Restore → Store.  
- It structured the system into clear stages like language detection, glossary handling, and storage.  
- This made the project modular, clean, and easy to debug.

---

## 2. Core Backend Development  
- AI assisted in building modules for language detection, translation, glossary protection, and CSV storage.  
- It guided separation into detector.py, translator.py, and storage.py for clean architecture.  
- It also helped integrate langdetect and deep-translator correctly.

---

## 3. Streamlit UI Development  
- AI helped design and fix the Streamlit dashboard and multi-page layout.  
- It supported engineer reply input, batch processing UI, and ticket display flow.  
- It also enabled CSV download and step-by-step output visualization.

---

## 4. Debugging and Error Fixing  
- AI helped fix import errors, translation bugs, and Streamlit UI issues.  
- It resolved data flow problems between modules and batch processing errors.  
- It improved overall stability of the pipeline.

---

## 5. Documentation Support  
- AI helped structure README and project documentation in submission format.  
- It assisted in writing architecture, workflow, and feature explanations.  
- It ensured clean, professional formatting for evaluation submission.

---

## ⚠️ What AI Got Wrong

During development, AI suggestions required refinement:

- **Translation Accuracy Issues**  
  Initial outputs from translation flow were inconsistent; required improvements in preprocessing and glossary protection.

- **Streamlit UI Behavior Issues**  
  Some UI layouts and state handling required manual correction after AI-generated suggestions.

- **Pipeline Flow Adjustments**  
  Minor mismatches in execution order (translation vs glossary restore) were corrected during testing.

---

## ⭐ Best Prompts Used

### 1. System Design Prompt
> Design a Python-based AI service desk system that reads multilingual support tickets from files, detects language, translates to English for engineers, allows engineer replies, translates replies back to original language, and stores everything in CSV format. Use an agent-style pipeline: Detect → Translate → Respond → Restore → Store.

---

### 2. Modular Architecture Prompt
> Break this system into clean Python modules: detector, translator, glossary handler, storage, Streamlit UI, and CLI batch processor. Ensure each module has a single responsibility and integrates into a working pipeline.

---

### 3. Bidirectional Translation Prompt
> Build a bidirectional translation flow where a ticket is translated to English for engineers and the engineer’s reply is translated back to the original language. Ensure glossary terms like VPN, Azure, and Outlook are never mistranslated.

---

### 4. Glossary Protection Prompt
> Implement a glossary protection system that replaces technical terms with placeholders before translation and restores them afterward. Ensure no change to domain-specific IT terms during translation.

---

### 5. Streamlit UI Prompt
> Create a Streamlit dashboard for a multilingual ticket translator with single ticket mode and batch processing mode. Include clean UI layout, step-by-step display of processing stages, and CSV download functionality.

---

### 6. Debugging Prompt
> Fix Python errors in a multi-module project including import errors, undefined functions, Streamlit UI issues, and broken translation pipeline flow. Ensure full end-to-end execution without crashes.

---

## 🧩 Summary of AI Role

AI tools were used as a **co-developer assistant** throughout the project lifecycle:

- Designed system architecture
- Generated core logic structure
- Assisted in UI development
- Helped debug multi-module integration issues
- Supported documentation and prompt engineering

Final system was refined manually to ensure correctness, stability, and production-like behavior.

---

## 🚀 Final Outcome

The project successfully demonstrates:

- AI-assisted software development
- Agent-style workflow implementation
- Real-world service desk automation use case
- Bidirectional multilingual translation system
- Modular Python + Streamlit architecture

---

**End of Document**
