"""Telegram bot skeleton that answers questions about the two programs using parsed curricula.
The bot applies a relevance filter and a simple retrieval + recommendation method.
"""
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import re

DATA_FILE = 'curricula.json'

def load_curricula():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

curricula = load_curricula()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот-консультант по магистратурам ИТМО: AI и AI Product. Задавай вопросы о учебных планах, курсах и рекомендациях. Отвечаю только на релевантные вопросы.')

def is_relevant(text: str) -> bool:
    # accept if mentions 'курс', 'учеб', 'план', 'выборн', 'семестр', 'вакан', 'программа', 'магист', 'ВКР'
    return bool(re.search(r'курс|учебн|план|выборн|семестр|вакан|программ|магистр|вкр|зач', text, flags=re.I))

def simple_retrieve(program_key: str, q: str):
    # naive search over raw lines
    items = []
    for entry in curricula.get(program_key, []):
        for c in entry.get('courses', []):
            if q.lower() in c.get('raw', '').lower():
                items.append(c.get('raw'))
    return items[:10]

def recommend_electives(program_key: str, background: str, target_role: str):
    # very simple rule-based mapping
    mapping = {
        'ml engineer': ['MLOps', 'ML System Design', 'Optimization Methods', 'Deep Learning'],
        'data engineer': ['Big Data', 'Data Engineering', 'Databases', 'ETL and Pipelines'],
        'product': ['Product Management', 'Business Analysis', 'A/B Testing', 'Product Metrics'],
        'research': ['Advanced Machine Learning', 'Statistical Learning', 'Scientific Writing']
    }
    # choose role by keyword
    role = None
    for k in mapping:
        if k.split()[0] in target_role.lower():
            role = k
            break
    if role is None:
        # fallback guess by background
        if 'math' in background.lower() or 'theory' in background.lower():
            role = 'research'
        elif 'product' in background.lower() or 'pm' in background.lower():
            role = 'product'
        elif 'engineer' in background.lower() or 'dev' in background.lower():
            role = 'ml engineer'
        else:
            role = 'ml engineer'
    return mapping[role][:4]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ''
    if not is_relevant(text):
        await update.message.reply_text('Извините, я могу отвечать только на вопросы, связанные с учебными планами, курсами и выбором дисциплин по программам AI и AI Product.')
        return
    # very small parsing: detect program
    program = 'ai' if 'ai product' not in text.lower() and 'product' not in text.lower() else 'ai_product'
    # if user asks for electives
    if re.search(r'выборн|рекоменд', text, flags=re.I):
        # try to extract background and role
        # naive: look for 'у меня есть' or 'я' + background words
        background = ' '.join(context.args) if context.args else ''
        # attempt to split '->' pattern: "background -> role"
        if '->' in text:
            parts = text.split('->')
            background = parts[0]
            target_role = parts[1]
        else:
            target_role = text
        recs = recommend_electives(program, background, target_role)
        await update.message.reply_text('Рекомендованные выборные дисциплины:\n' + '\n'.join(f'- {r}' for r in recs))
        return
    # otherwise try retrieval
    found = simple_retrieve(program, text)
    if found:
        await update.message.reply_text('Нашёл в учебном плане (строки):\n' + '\n'.join(found))
    else:
        await update.message.reply_text('Не нашёл прямого совпадения в учебном плане. Могу помочь с общими рекомендациями или перечислить основные блоки программы.')

if __name__ == '__main__':
    import os
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        print('Set TELEGRAM_BOT_TOKEN environment variable and run again (bot uses polling).')
        raise SystemExit(1)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('Bot starting (polling)...')
    app.run_polling()
