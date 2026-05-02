---
title: personal-agent — brain reference
date: 2026-05-02
type: project-reference
status: active
tags: [personal, telegram, vps, ai-agent]
slug: personal-agent
code-path: ~/Projects/personal-agent/
---

# personal-agent

## Что это

Персональный AI-ассистент, доступный через Telegram. Работает на Hetzner VPS.
Отдельно от Shopify listing automation.

## Архитектура

```
User → Telegram → Python bot → Redis queue → Node.js worker
  → enrichPrompt() [datetime + weather + RAG memory]
  → Claude CLI (cwd=/home/agent/workspace)
  → Response → Telegram (text + optional TTS voice)
```

## VPS layout

- `/opt/server-agent/` — runtime (bot + worker + Redis + Postgres)
- `/home/agent/workspace/` — рабочая директория агента (CLAUDE.md + memory/)
- `/opt/listing_automation/` — отдельный Shopify app, не трогать

## Где код

`~/Projects/personal-agent/` (локальная разработка)
VPS: `ssh hetzner`

## Ключевые файлы

- `CLAUDE.md` — локальный обзор
- VPS: `/opt/server-agent/worker/worker.js` — Node.js queue worker (systemd)
- VPS: `/opt/server-agent/bot/main.py` — Python Telegram bot (Docker)
- VPS: `/home/agent/workspace/CLAUDE.md` — agent identity & memory
- VPS: `/home/agent/workspace/memory/INDEX.md` — RAG memory index

## Стек

- **Bot:** Python (Docker)
- **Worker:** Node.js (systemd)
- **Infra:** Redis, Postgres (Docker-compose)
- **Brain:** Claude CLI с `--dangerously-skip-permissions`, cwd=workspace
- **Voice:** TTS через `gpt-4o-mini-tts`, voice=ash

## Memory / RAG

- `memory/user_profile.md` — всегда инжектится
- `memory/conversations/` — extracts после notable разговоров
- `memory/knowledge/` — документы от пользователя

Claude читает и пишет memory-файлы автономно.

## Env vars (на VPS, `~/.config/agent/secrets.env`)

- TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER_ID
- OPENAI_API_KEY, AGENT_CITY, AGENT_TIMEZONE, AGENT_ADDRESS
- TTS_MODEL, TTS_VOICE, TTS_SPEED

## Правила

- **Никогда** не коммитить секреты
- Shopify проект отдельно
- Worker changes: edit на VPS → `systemctl restart claude-worker`
- Bot changes: edit на VPS → `docker compose restart telegram-bot`
- **Новые сервисы — только через Docker + docker-compose**, не systemd

## Текущая цель

Стабильность. Memory разрастается органично — следить за сигналом/шумом.

## Где искать больше

- [goals.md](goals.md)
- [open-questions.md](open-questions.md)
