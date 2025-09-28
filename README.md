# PixSell AI — Quickstart ZIP

Этот архив содержит scaffold проекта **PixSell AI** — backend (FastAPI), простой frontend (static), infra templates и скрипты для начального запуска.

## Цели
- Быстрый локальный запуск на Ubuntu 24.04
- Tinder‑flow: загрузить фото товара → получить варианты → свайп/лайк → сохранить
- Подготовлен pipeline для интеграции нескольких SOTA моделей (SDXL, ControlNet, InstructPix2Pix) — в коде есть заглушки и инструкции
- Скрипт-шаблон для LoRA fine-tuning

## Структура
```
PixSellAI/
├─ backend/
├─ frontend/
├─ infra/
├─ scripts/
└─ README.md
```

## Быстрый запуск (локально)
1. Открой терминал (Ubuntu 24.04).
2. Клонируй или распакуй архив, перейди в папку:
```bash
cd ~/Downloads/PixSellAI  # или куда распаковал
```
3. Создай виртуальное окружение и установи зависимости:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```
4. Запусти backend:
```bash
# из корня проекта
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```
5. Открой frontend в браузере (локально):
```
open frontend/index.html  # или открой файл руками в браузере
```
6. В frontend можно загружать фото и тестировать свайп-флоу. Backend сохранит uploads/, сгенерирует 2 варианта и покажет их.

## Что дальше (коротко и по делу)
- Поднять GCP проект и настроить ресурсы (см. infra/terraform).
- Подготовить GPU VM (T4) для инференса и обучения; в Dockerfile есть базовый образ.
- Запустить real pipelines: установить PyTorch с CUDA и diffusers, скачать SDXL и ControlNet модели (см. scripts/README_models.md).
- Автоматизировать LoRA fine-tuning на основе likes → scripts/train_lora_template.py

## Ссылки файлов в архиве
- backend/ — FastAPI сервер
- frontend/index.html — минимальный интерфейс
- scripts/ — templates для тренировки и инференса
- infra/ — terraform шаблон и cloudbuild

---

Если хочешь — я могу сейчас сгенерировать PR‑патч для твоего GitHub или дать точный чек-лист для развёртывания на GCP. Для скачивания архива используй ссылку, которую я отправлю после упаковки.
