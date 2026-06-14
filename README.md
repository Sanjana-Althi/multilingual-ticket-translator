# 🌐 Multilingual Ticket Translator

> An AI-powered Service Desk automation prototype that detects the language of incoming support tickets, translates them to English for engineers, collects replies, and delivers responses back in the customer's original language — with glossary protection and automatic CSV storage.

---

<div align="center">

## 🏷️ Submission Identity

| | |
|---|---|
| 🏆 **Competition** | Infinite Computer Solutions Placement Drive — Round 3 Case Study |
| 👥 **Team** | **TEAM 9** |
| 🆔 **UC ID** | **SD-04** |
| 🗂️ **Category** | **SERVICE DESK** |

</div>

---

## 👥 Team Members

| Name | Roll Number | Branch |
|---|---|---|
| Mangi Nitya Sai Vardhani | 23U41A4427 | CSE |
| Althi Sanjana | 23U41A0504 | CSE |
| Kandregula Divya Vani | 23U41A0520 | CSE |
| Kanapaka Dilleswara Rao | 23U41A0430 | ECE |

> 📄 Resume files are available in the `resumes/` folder.

---

## 🔗 Quick Links

- **🎥 Demo Video:** `[PASTE YOUR DEMO VIDEO LINK HERE]`
- **🚀 Live Application:** (https://multilingual-ticket-translator-infinite-campuss.streamlit.app/)
- **📁 GitHub Repository:** (https://github.com/Sanjana-Althi/multilingual-ticket-translator)


---

## 📌 Problem Statement

IT service desks receive support tickets from end users across multiple regional languages. Engineers are typically fluent only in English, so every non-English ticket requires a manual copy-paste translation before it can even be read — let alone resolved.

This process introduces three consistent problems:

1. **Delays** — Resolution time increases because translation is done manually per ticket.
2. **Mistranslation of technical terms** — Tools like Google Translate often corrupt product names and IT terms such as `VPN`, `Outlook`, `Azure`, and `Server`, making the translated ticket harder to action.
3. **No structured audit trail** — Translated content and engineer responses are not stored in any systematic way for reporting or review.

---

## ✅ Solution Overview

The Multilingual Ticket Translator is a Python and Streamlit-based prototype that automates the full lifecycle of a multilingual support ticket.

The system reads tickets written in Telugu, Hindi, Tamil, Kannada, or English, detects the language automatically, translates the content to English for the engineer, collects the engineer's reply, translates it back to the customer's original language, and stores the complete record in a CSV file.

A glossary protection layer ensures that technical IT terms are never altered during translation. The system works both as an interactive Streamlit web interface and as a command-line batch processor.

---

## ⭐ Key Features

- ✔ Automatic language detection for Telugu, Hindi, Tamil, Kannada, and English
- ✔ Bidirectional translation: ticket to English, reply back to original language
- ✔ Glossary protection: technical terms are preserved exactly through translation
- ✔ Single-ticket mode via Streamlit UI with step-by-step processing
- ✔ Batch processing mode: upload up to 10 `.txt` files and process all at once
- ✔ Default reply fallback when engineer does not enter a custom response
- ✔ Validation before submission: empty reply fields are flagged before saving
- ✔ Automatic CSV storage with full context per ticket
- ✔ One-click CSV export from the Streamlit dashboard
- ✔ No paid APIs or external databases required

---

## 🏗️ System Architecture

```
INPUT
-----
tickets/*.txt files   OR   Streamlit UI (paste ticket text)
          |
          v
+---------------------------+
|  STAGE 1: DETECTION       |
|  detect_ticket_language() |
|  → Identifies language    |
|    name and ISO code      |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 2: GLOSSARY LOAD   |
|  load_glossary()          |
|  → Reads glossary.json    |
|    (VPN, Azure, Outlook,  |
|     Server, Database...)  |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 3: TERM PROTECTION |
|  protect_terms()          |
|  → Replaces protected     |
|    terms with placeholders|
|    before translation     |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 4: TRANSLATION     |
|  translate_to_english()   |
|  → Ticket translated to   |
|    English for engineer   |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 5: ENGINEER REPLY  |
|  UI input OR default reply|
|  → Engineer reads English |
|    ticket and responds    |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 6: REPLY TRANSLATE |
|  translate_from_english() |
|  → Reply translated back  |
|    to original language   |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 7: TERM RESTORE    |
|  restore_terms()          |
|  → Placeholders replaced  |
|    with original IT terms |
+---------------------------+
          |
          v
+---------------------------+
|  STAGE 8: STORAGE         |
|  save_ticket_record()     |
|  → Full record appended   |
|    to output/tickets.csv  |
+---------------------------+
          |
          v
OUTPUT
------
output/tickets.csv
[ticket_id | timestamp | language | original | english | reply_en | reply_translated]
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Core Language | Python 3.10+ |
| Web Interface | Streamlit |
| Data Handling | pandas |
| Language Detection | langdetect |
| Translation | deep-translator (Google Translate backend) |
| Glossary Management | JSON file + Python `re` module |
| Storage | CSV via Python standard library `csv` module |
| Unique ID Generation | Python standard library `uuid` module |

> No paid APIs. No external databases. No machine learning model training required.

---

## 🔄 Workflow

### Single Ticket Mode (Streamlit UI)

```
Step 1  →  Engineer pastes ticket text into the UI
Step 2  →  System detects language automatically
Step 3  →  Glossary terms replaced with placeholders before translation
Step 4  →  Ticket translated to English
Step 5  →  Placeholders restored in English translation
Step 6  →  Engineer reads English ticket and enters reply
           (or leaves blank to use the default support response)
Step 7  →  Reply glossary terms protected before translation
Step 8  →  Reply translated back to original language
Step 9  →  Placeholders restored in translated reply
Step 10 →  Full record saved automatically to output/tickets.csv
```

### Batch Processing Mode (Streamlit UI)

```
Step 1  →  Engineer uploads up to 10 .txt ticket files
Step 2  →  Click "Process Tickets"
           → Language detection runs for all files
           → English translation runs for all files
Step 3  →  Engineer reviews each ticket
           → Enters reply per ticket (or leaves empty)
Step 4  →  Click "Translate & Save All"
           → Validation checks: empty replies are flagged
           → Engineer chooses default reply or returns to edit
Step 5  →  All replies translated back to original languages
Step 6  →  All records saved to output/tickets.csv
Step 7  →  Download CSV available from Export Results page
```

### CLI Batch Mode (main.py)

```
Step 1  →  System reads all .txt files from tickets/ folder
Step 2  →  Processes each ticket through the full pipeline
Step 3  →  Prompts engineer for reply per ticket (Enter for default)
Step 4  →  Saves all records to output/tickets.csv
```

### 🛡️ How Glossary Protection Works

```
Original ticket :  "My VPN is not connecting to the Azure portal."
After protect   :  "My ##TERM_0## is not connecting to the ##TERM_1## portal."
After translate :  "मेरा ##TERM_0## ##TERM_1## पोर्टल से कनेक्ट नहीं हो रहा।"
After restore   :  "मेरा VPN Azure पोर्टल से कनेक्ट नहीं हो रहा।"
```

> Technical terms pass through translation completely unchanged.

---

## 📁 Folder Structure

```
multilingual-ticket-translator/
│
├── app.py                     # Streamlit web interface
├── main.py                    # CLI batch processor
│
├── detector.py                # Language detection module
├── translator.py              # Bidirectional translation module
├── glossary_handler.py        # Glossary protection and restoration
├── storage.py                 # CSV record storage module
│
├── glossary.json              # Protected IT terms list
│
├── tickets/                   # Input folder for .txt ticket files
│   ├── ticket_001_telugu.txt
│   ├── ticket_002_hindi.txt
│   ├── ticket_003_tamil.txt
│   ├── ticket_004_kannada.txt
│   └── ticket_005_english.txt
│
├── output/                    # Auto-created on first save
│   └── tickets.csv            # All processed ticket records
│
├── resumes/                   # Team member resume files
├── requirements.txt           # Python dependencies
└── README.md
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Active internet connection (required for translation)

### Steps

**1. Clone the repository**

```bash
git clone [PASTE YOUR GITHUB REPO LINK HERE]
cd multilingual-ticket-translator
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

`requirements.txt` contains:

```
streamlit>=1.35.0
pandas>=2.0.0
langdetect>=1.0.9
deep-translator>=1.11.4
```

---

## ▶️ How to Run

### Option 1 — Streamlit Web Interface (Recommended)

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

The dashboard contains five pages accessible from the top navigation bar:

- **Home** — System overview and feature summary
- **Single Ticket** — Paste a ticket and process it end-to-end
- **Batch Processing** — Upload multiple `.txt` files and process in one workflow
- **Summary** — View all saved records in a table
- **Export Results** — Download the full CSV

### Option 2 — CLI Batch Mode

```bash
python main.py
```

The system reads all `.txt` files from the `tickets/` folder, processes each through the full pipeline, prompts for engineer replies, and saves all records to `output/tickets.csv`. If the `tickets/` folder does not exist, sample tickets are created automatically for demonstration.

---

## 📥 Sample Input and Output

### Input (`tickets/ticket_001_telugu.txt`)

```
నా VPN కనెక్ట్ అవడం లేదు. Server కి access లేదు. దయచేసి సహాయం చేయండి.
```

### Output (row saved to `output/tickets.csv`)

| Field | Value |
|---|---|
| ticket_id | TICKET_001_TELUGU |
| timestamp | 2025-06-13 10:45:22 |
| original_language | Telugu |
| original_ticket | నా VPN కనెక్ట్ అవడం లేదు... |
| english_ticket | My VPN is not connecting. I cannot access the Server. Please help. |
| engineer_reply | Please restart your VPN client and contact your network administrator. |
| translated_reply | దయచేసి మీ VPN క్లయింట్‌ను పునఃప్రారంభించి మీ నెట్‌వర్క్ అడ్మినిస్ట్రేటర్‌ను సంప్రదించండి. |

> **Note:** `VPN` and `Server` are preserved exactly in both the English and Telugu output.

---

## 🤖 AI Capability Demonstration

This prototype is built around an **agent-style pipeline** where each stage is a discrete, composable processing step — the same architectural pattern used in production AI automation systems.

### Agent Behavior Breakdown

| Agent Capability | Implementation |
|---|---|
| **Perceive** | Reads `.txt` ticket files or UI input |
| **Understand** | Detects language using `langdetect` |
| **Reason** | Applies domain knowledge via glossary protection |
| **Act** | Translates bidirectionally using `deep-translator` |
| **Communicate** | Delivers translated reply back to customer language |
| **Store** | Appends structured records to CSV with full audit context |

### Domain Intelligence

The glossary protection mechanism simulates domain-aware reasoning. Rather than naive translation, the system applies IT service desk knowledge by shielding technical terms from the translation engine. This mirrors how production translation memory systems used in enterprise helpdesks operate.

### Closed-Loop Communication

The system implements a complete communication loop:

- **Customer → Engineer:** Regional language → English
- **Engineer → Customer:** English → Regional language

This bidirectional, context-preserving flow is the core AI behavior the prototype demonstrates.

---

## ⚠️ Assumptions and Limitations

| Item | Detail |
|---|---|
| Internet connection | Required; translation uses Google Translate via `deep-translator` |
| Supported languages | Telugu, Hindi, Tamil, Kannada, English only |
| Input format | Plain `.txt` files; no PDF, image, or OCR support |
| Translation accuracy | Dependent on Google Translate quality; may vary for informal or highly technical text |
| Batch file limit | Streamlit UI supports up to 10 files per session |
| Glossary scope | Fixed list defined in `glossary.json`; new terms require manual addition |
| Authentication | Not implemented; this is a prototype without login or access control |

---

## 🚀 Future Improvements

| Improvement | Description |
|---|---|
| Expanded language support | Add Bengali, Marathi, Gujarati, Odia, and other Indian regional languages |
| OCR integration | Accept scanned ticket images or PDFs |
| LLM-based auto-reply | Use an open-source LLM to generate contextual engineer replies automatically |
| Ticket priority classification | NLP-based urgency detection (Low / Medium / High / Critical) |
| Analytics dashboard | Language distribution charts, volume trends, resolution time tracking |
| ITSM integration | Connect with Zendesk, Freshdesk, or ServiceNow for live ticket ingestion |
| Dynamic glossary editor | Manage protected terms through the UI without editing JSON |
| Role-based access control | Engineer and Admin login with separate permissions |

---

## 📝 Submission Note

This project was developed as a case study prototype for the **Infinite Computer Solutions Placement Drive — Round 3**, under the **Service Desk** category.

All modules are original implementations using open-source Python libraries only. No paid APIs, no external databases, and no pre-trained model hosting was used. The system is fully runnable on any standard Python environment with internet access.

---

<div align="center">

**Team 9 &nbsp;|&nbsp; UC ID: SD-04 &nbsp;|&nbsp; Category: Service Desk**

*Infinite Computer Solutions Placement Drive — Round 3 Case Study*

</div>
# multilingual-ticket-translator
