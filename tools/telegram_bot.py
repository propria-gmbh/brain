#!/usr/bin/env python3
"""Telegram bot: forwards messages to Claude Code CLI (brain/ context)."""

import asyncio
import json
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

CONFIG_PATH = Path.home() / ".config" / "telegram-bot" / "config.json"
BRAIN_PATH = Path.home() / "Projects" / "brain"
TODAY_FILE = BRAIN_PATH / "05_PLANS" / "today.md"
LOG_PATH = Path.home() / ".config" / "telegram-bot" / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def authorized(update: Update, cfg: dict) -> bool:
    chat_id = update.effective_chat.id
    if "allowed_chat_id" not in cfg:
        cfg["allowed_chat_id"] = chat_id
        save_config(cfg)
        log.info(f"First message — whitelisted chat_id: {chat_id}")
    if chat_id != cfg["allowed_chat_id"]:
        log.warning(f"Rejected message from chat_id: {chat_id}")
        return False
    return True


def find_claude_cli() -> Path:
    base = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code"
    candidates = sorted(base.glob("*/claude.app/Contents/MacOS/claude"), reverse=True)
    if not candidates:
        raise FileNotFoundError("Claude CLI not found")
    return candidates[0]


TELEGRAM_SYSTEM_PROMPT = (
    "Ты работаешь в Telegram-режиме. "
    "MCP инструменты (Gmail, Calendar, Drive, Slack) НЕДОСТУПНЫ — не вызывай их и не упоминай их статус. "
    "Работай только с локальными файлами brain/. "
    "Не делай старт-сессию, не проверяй почту, не проверяй платежи. "
    "Отвечай коротко и по делу."
)


def call_claude(message: str) -> str:
    cli = find_claude_cli()
    result = subprocess.run(
        [
            str(cli), "-p", message,
            "--dangerously-skip-permissions",
            "--append-system-prompt", TELEGRAM_SYSTEM_PROMPT,
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(BRAIN_PATH),
    )
    return result.stdout.strip() or result.stderr.strip() or "(пустой ответ)"


# ---------------------------------------------------------------------------
# Direct file commands (no Claude call)
# ---------------------------------------------------------------------------

def cmd_today_text() -> str:
    if not TODAY_FILE.exists():
        return "today.md не найден"
    content = TODAY_FILE.read_text(encoding="utf-8")
    return content[:4000] + "\n...[обрезано]" if len(content) > 4000 else content


def cmd_done_text(task: str) -> str:
    if not TODAY_FILE.exists():
        return "today.md не найден"
    content = TODAY_FILE.read_text(encoding="utf-8")
    today_date = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(
        r"^([ \t]*- \[[ ]\] )(.*" + re.escape(task) + r".*)$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(content)
    if not match:
        return f"Задача не найдена: {task}"
    new_line = match.group(1).replace("[ ]", "[x]") + match.group(2) + f" {today_date}"
    TODAY_FILE.write_text(content.replace(match.group(0), new_line, 1), encoding="utf-8")
    return f"Отмечено: {match.group(2).strip()}"


def cmd_add_text(task: str) -> str:
    if not TODAY_FILE.exists():
        return "today.md не найден"
    content = TODAY_FILE.read_text(encoding="utf-8")
    new_line = f"- [ ] {task}"
    section = re.search(r"^## Задачи\s*$", content, re.MULTILINE)
    if section:
        pos = section.end()
        while pos < len(content) and content[pos] == "\n":
            pos += 1
        new_content = content[:pos] + new_line + "\n" + content[pos:]
    else:
        new_content = content.rstrip() + "\n\n" + new_line + "\n"
    TODAY_FILE.write_text(new_content, encoding="utf-8")
    return f"Добавлено: {task}"


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def handle_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update, load_config()):
        return
    await update.message.reply_text(cmd_today_text())


async def handle_done(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update, load_config()):
        return
    task = " ".join(ctx.args).strip() if ctx.args else ""
    if not task:
        await update.message.reply_text("Использование: /done <название задачи>")
        return
    await update.message.reply_text(cmd_done_text(task))


async def handle_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update, load_config()):
        return
    task = " ".join(ctx.args).strip() if ctx.args else ""
    if not task:
        await update.message.reply_text("Использование: /add <текст задачи>")
        return
    await update.message.reply_text(cmd_add_text(task))


async def handle_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update, load_config()):
        return
    await update.message.reply_text(
        "Brain Bot online.\n\n"
        "/today — дневной план\n"
        "/done <задача> — отметить выполненной\n"
        "/add <текст> — добавить задачу\n\n"
        "Или просто напиши — Claude ответит."
    )


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cfg = load_config()
    if not authorized(update, cfg):
        return

    text = update.message.text
    if not text:
        return

    log.info(f"Message: {text[:80]}")
    thinking_msg = await update.message.reply_text("...")

    try:
        response = await asyncio.get_event_loop().run_in_executor(None, call_claude, text)
    except subprocess.TimeoutExpired:
        response = "Timeout (>3 мин)"
    except Exception as e:
        response = f"Ошибка: {e}"
        log.exception("Claude call failed")

    await thinking_msg.delete()

    for i in range(0, len(response), 4096):
        await update.message.reply_text(response[i : i + 4096])


# ---------------------------------------------------------------------------
# Push: send message from external scripts
# ---------------------------------------------------------------------------

async def _async_send(token: str, chat_id: int, text: str):
    from telegram import Bot
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=text)


def send_push(text: str):
    cfg = load_config()
    token = cfg.get("token")
    chat_id = cfg.get("allowed_chat_id")
    if not token or not chat_id:
        raise ValueError("Token or chat_id not configured")
    asyncio.run(_async_send(token, chat_id, text))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    import sys
    if "--send" in sys.argv:
        idx = sys.argv.index("--send")
        text = " ".join(sys.argv[idx + 1:])
        send_push(text)
        return

    cfg = load_config()
    token = cfg.get("token") or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Token not found. Set it in ~/.config/telegram-bot/config.json")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("today", handle_today))
    app.add_handler(CommandHandler("done", handle_done))
    app.add_handler(CommandHandler("add", handle_add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info(f"Bot started. Brain path: {BRAIN_PATH}")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
