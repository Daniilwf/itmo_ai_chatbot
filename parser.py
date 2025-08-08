"""Parser that downloads Google Drive PDFs (by file ID) and extracts text with PyMuPDF.
Outputs a JSON file `curricula.json` with a list of courses (best-effort).
"""
import os
import re
import requests
import fitz  # PyMuPDF
from tqdm import tqdm

USER_AGENT = 'itmo-advisor-bot/1.0 (+https://example.org)'

def drive_download(file_id, dest_path):
    # Try direct uc download endpoint
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    s = requests.Session()
    r = s.get(url, headers={'User-Agent': USER_AGENT}, stream=True, timeout=30)
    # Google sometimes requires a confirmation token on large files; this simple approach may work for small files
    if 'Content-Disposition' not in r.headers:
        # try the open view as fallback
        view_url = f'https://drive.google.com/file/d/{file_id}/view'
        r = s.get(view_url, headers={'User-Agent': USER_AGENT}, timeout=30)
        # can't reliably parse from here without JS; so fail gracefully
        r.raise_for_status()
        raise RuntimeError('Could not download via direct link; interactive Google Drive required')
    total = int(r.headers.get('Content-Length', 0))
    with open(dest_path, 'wb') as f:
        for chunk in r.iter_content(32768):
            if chunk:
                f.write(chunk)
    return dest_path

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    pages_text = []
    for p in doc:
        pages_text.append(p.get_text('text'))
    return '\n'.join(pages_text)

def simple_course_extractor(text):
    # Heuristic: lines that look like "1. Название курса — 3 зач" or contain 'зач' or 'кред'
    courses = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.search(r'зач|кред|кредит|зачет|часы', line, flags=re.I):
            courses.append(line)
        # also pick lines that look like "№ \d+" patterns
        if re.match(r'^[0-9]+\.', line):
            courses.append(line)
    # deduplicate
    seen = set()
    out = []
    for c in courses:
        if c in seen: continue
        seen.add(c)
        out.append({'raw': c})
    return out

if __name__ == '__main__':
    import json
    if not os.path.exists('drive_links.json'):
        print('Run scraper.py first to get drive_links.json')
        raise SystemExit(1)
    with open('drive_links.json', 'r', encoding='utf-8') as f:
        links = json.load(f)
    curricula = {}
    os.makedirs('pdfs', exist_ok=True)
    for prog, ids in links.items():
        curricula[prog] = []
        for fid in ids:
            pdf_path = os.path.join('pdfs', f'{fid}.pdf')
            try:
                print('Downloading', fid)
                drive_download(fid, pdf_path)
                text = extract_text_from_pdf(pdf_path)
                courses = simple_course_extractor(text)
                curricula[prog].append({'file_id': fid, 'courses': courses})
            except Exception as e:
                print('Failed to process', fid, e)
    with open('curricula.json', 'w', encoding='utf-8') as f:
        json.dump(curricula, f, ensure_ascii=False, indent=2)
    print('Saved curricula.json')
