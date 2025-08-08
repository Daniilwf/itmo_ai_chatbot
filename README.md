# ITMO AI Programs — Admission Advisor (prototype)

This repository contains a prototype solution for the contest task:
a chat-bot that helps applicants choose between two ITMO master's programs 
(AI Talent Hub and AI Product) by parsing program pages, extracting curricula 
and providing study / elective recommendations based on student's background.

**What is included**
- `scraper.py` — scrapes the program pages and finds curriculum PDF links.
- `parser.py` — downloads PDFs and extracts text (uses PyMuPDF / fitz).
- `bot.py` — a simple Telegram-bot skeleton (python-telegram-bot v20) that loads parsed curricula and answers constrained questions.
- `requirements.txt` — Python packages required.
- `example_output.json` — example structure with parsed curricula (minimal placeholder).

**How I solved the task (summary)**
1. Inspect program pages (abit.itmo.ru and ai.itmo.ru / aiproduct.itmo.ru) and find links to curriculum files (Google Drive).
2. Download curriculum PDFs and parse them (text + table extraction) to obtain course lists, semesters, credits.
3. Store curricula as JSON (course metadata: title, semester, hours, type).
4. Implement a Telegram bot that answers only relevant questions about the two master's programs, using a rule-based retriever and a simple recommendation engine that maps student's background and target role to electives.

**Notes / limitations**
- The drive.google.com curriculum links are publicly linked from program pages; in some environments Google Drive may require interactive auth or confirm tokens for large files — the parser includes a fallback for direct download via `https://drive.google.com/uc?export=download&id=FILE_ID`.
- PDF parsing is inherently noisy; for best results you may need to tune the heuristics per PDF layout or convert PDF tables with `camelot`/`tabula` (Java required) if the PDFs contain structured tables.

**How to run (locally)**
1. Create a Python 3.10+ virtual environment.
2. `pip install -r requirements.txt`
3. Run `python scraper.py` to discover curriculum links and download PDFs.
4. Run `python parser.py` to parse PDFs into `curricula.json`.
5. Fill `config.py` with your TELEGRAM_BOT_TOKEN and run `python bot.py` to start the bot (polling).

