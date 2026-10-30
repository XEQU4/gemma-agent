# Gemma Developer Agent

Проект агента для Kaggle Gemma 4 Developer Agent Competition. Рабочий uv-project находится в этой папке; конфигурация отправляемого агента — в `submission/`.

## Структура

- `submission/` — declarative YAML, prompts, sampling и два sample LoRA adapters.
- `docs/PHASE_A1_REPORT.md` — исходная структура и проверки sample.
- `docs/PHASE_A2_REPORT.md` — изменения v1, проверки и ограничения.
- `pyproject.toml`, `.python-version`, `main.py` — стартовые uv-файлы; `main.py` пока содержит только стартовый пример.
- `scripts/build_submission.py` — статическая проверка v1 и воспроизводимая сборка ZIP.
- `dist/`, `results/`, `runs/` — локальные артефакты и результаты, исключены из Git.

Данные соревнования хранятся отдельно в **`../gemma4-data/`**. Snapshots, graphs, embeddings, wheels и исходные архивы не включаются в этот репозиторий.

## Статус v1

Используется `gemma-4-31b-it-qat-w4a16-ct`. Оба sample adapters сохранены без изменений.
Analyzer работает read-only; его instruction и sampling размещены inline, parent traversal в includes устранён.
Evaluation budgets: 120 секунд на команду, 50 tool calls, 4 минуты, 80 turns.

Проверены YAML syntax, references, единственная модель и SHA-256 неизменённых файлов.
**Official compiler и runtime evaluation не запускались**: harness отсутствует в проверенных environments. Совместимость adapters при загрузке модели и качество решения задач не подтверждены.
В A3 выполнены статическая проверка и воспроизводимая сборка локального ZIP. По сообщению пользователя, первая отправка v1 на Kaggle выполнена 30.10.2026 около 18:02 по Астане; последний сообщённый статус — Notebook Running, score пока нет. Подробности: [журнал отправок](docs/SUBMISSIONS.md).

Не коммитьте `.env`, credentials, токены, приватные ключи и локальные данные.

## Статическая проверка и сборка ZIP

Зависимость проверки объявлена в `pyproject.toml`: группа `validation`, `PyYAML==6.0.3`.
Команда из корня проекта для environment с этой группой (uv может синхронизировать dependency environment):

```powershell
uv run --group validation python -B scripts/build_submission.py
```

В A3 фактически выполнено с уже установленным PyYAML 6.0.3 и системным Python 3.14.0:

```powershell
python -B -X utf8 scripts/build_submission.py
```

Скрипт проверяет submission, дважды строит ZIP с фиксированными timestamps и сортировкой entries,
сравнивает SHA-256, проверяет CRC через `testzip()` и побайтовое равенство исходникам.
Результат: `dist/submission.zip`; `agent.yaml` расположен в корне архива.
В ZIP входят только файлы `submission/`; используется `ZIP_STORED` без сжатия.

Существующий output не перезаписывается. Для повторного запуска выберите новое имя:

```powershell
python -B -X utf8 scripts/build_submission.py --output dist/submission-recheck.zip
```

Это **статическая проверка v1**, не official compilation и не runtime validation.
Проверяются LlmAgent и ссылки config_path; YAML aliases/merge keys, skills и другие agent classes
консервативно отклоняются. Подробнее: `docs/PHASE_A3_REPORT.md`.
