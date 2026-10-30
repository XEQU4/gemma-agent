# Gemma Developer Agent

Проект агента для Kaggle Gemma 4 Developer Agent Competition. Рабочий uv-project находится в этой папке; конфигурация отправляемого агента — в `submission/`.

## Структура

- `submission/` — declarative YAML, prompts, sampling и два sample LoRA adapters.
- `docs/PHASE_A1_REPORT.md` — исходная структура и проверки sample.
- `docs/PHASE_A2_REPORT.md` — изменения v1, проверки и ограничения.
- `pyproject.toml`, `.python-version`, `main.py` — стартовые uv-файлы; `main.py` пока содержит только стартовый пример.
- `scripts/` — локально подготовленный пустой каталог; пустые каталоги Git не хранит.
- `dist/`, `results/`, `runs/` — локальные артефакты и результаты, исключены из Git.

Данные соревнования хранятся отдельно в **`../gemma4-data/`**. Snapshots, graphs, embeddings, wheels и исходные архивы не включаются в этот репозиторий.

## Статус v1

Используется `gemma-4-31b-it-qat-w4a16-ct`. Оба sample adapters сохранены без изменений.
Analyzer работает read-only; его instruction и sampling размещены inline, parent traversal в includes устранён.
Evaluation budgets: 120 секунд на команду, 50 tool calls, 4 минуты, 80 turns.

Проверены YAML syntax, references, единственная модель и SHA-256 неизменённых файлов.
**Official compiler и runtime evaluation не запускались**: harness отсутствует в проверенных environments. Совместимость adapters при загрузке модели и качество решения задач не подтверждены.
Проект подготовлен для дальнейшей проверки; ZIP не создан, отправка на Kaggle не выполнялась.

Не коммитьте `.env`, credentials, токены, приватные ключи и локальные данные.
