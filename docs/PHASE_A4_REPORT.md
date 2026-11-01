# PHASE A4 — v2: budget checkpoints и tool contracts

Дата: 01.11.2026. Ветка: `a4-v2-budget-tools`.
Baseline: `36558c6e2433ac8f2495688abcf8ddf7f2b508ac`.
При старте tracked-файлы были чистыми; посторонние untracked `docs/B3_REVIEW.txt` и `docs/B4_DEMO.txt` сохранены и не включаются в commit.

## Основание и diff

Со слов пользователя: v1 получила Kaggle public score 0.10; на четырёх dev-задачах 2/4 прошли,
зафиксированы три timeout, get_status не вызывался, были /tmp обращения через file tools и edit_file без old_string.
Это исходные наблюдения пользователя, не результаты запуска v2; traces в A4 не анализировались.

В submission изменён **только prompts/system.md**:
- get_status после начальной локализации и после каждых 4 рабочих tool calls; учитываются failed calls и analyzer delegation, исключены status/submit.
- Использованы документированные поля `time_seconds_remaining` и `tool_calls_remaining`.
- При <=60 s прекращается расширение поиска, завершается только обоснованный минимальный patch, проверяется diff; короткая targeted проверка — только с запасом 20 s на submission.
- При <=20 s — немедленный submit_patch, без новых edits/checks. Необоснованные edits не требуются.
- read_file/write_file/edit_file ограничены workspace; все /tmp операции — через run_command.
- Добавлены обязательные filepath/old_string/new_string, один общий пример edit_file и исправление конкретного вызова после ошибки аргументов.
- Сохранены minimal changes, защита tests/configs, offline-работа, честная оценка проверок и submit_patch последним tool action. Подсказок под конкретные dev-задачи нет.

В docs/SUBMISSIONS.md для v1 записаны Succeeded, public score 0.10, дата наблюдения 01.11.2026;
время завершения неизвестно. V2 не записана как отправленная.
README и прочие файлы проекта не редактировались.

## Сверка API

Источник: локальный HARNESS_README.md, §6.1–6.2 (строки 386, 406, 415–435, 441–481).
Сигнатуры: get_status(); submit_patch(); run_command(command);
read_file(filepath, start_line=None, end_line=None);
write_file(filepath, content);
edit_file(filepath, old_string, new_string, allow_multiple=False).
README: file paths разрешаются внутри /workspace; parent traversal запрещён.
Синтаксис короткого примера edit_file дополнительно разобран через Python AST: ровно три required keyword arguments с непустыми строками.

## Сборка и проверки

Выполнено существующим, неизменённым build script:

```powershell
python -B -X utf8 scripts/build_submission.py --output dist/v2/submission.zip
```

- Кандидат: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle\dist\v2\submission.zip`.
- ZIP: **443509 bytes**, 10 entries; распаковано **442175 bytes**.
- SHA-256: `93a3399f5f72d026d7bda81d068bfb0d60e1a49d0495e9835e37b00ae79841ed`.
- Вторая внутренняя сборка дала тот же SHA-256.
- 4 YAML, 3 references, одна разрешённая модель; token limits, tools, adapters и равенство sampling прошли static checks.
- testzip(), список entries и побайтовое равенство текущим исходникам прошли; agent.yaml в корне ZIP.
- Модель `gemma-4-31b-it-qat-w4a16-ct`, budgets **120/50/4/80**, sampling, analyzer и все adapter files неизменны по SHA-256.
- Остальные 9 файлов submission побайтно сохранены; system prompt SHA-256:
  `0cd54f4e3e5845768dbe476c6bb634f9b4850439af8175a86bcb474c0789b0e0`.
- ZIP v1 сохранил SHA-256 `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
- Оба ZIP ignored правилом dist/ и не включаются в Git.
- Посторонние файлы сверены по SHA-256; локальный main остался на baseline.
- source_commit в выводе builder равен baseline: сборка выполнена до commit A4, с обновлённым system prompt рабочей ветки.

## Ограничения

Это статическая проверка и упаковка, не official compilation.
Runtime v2, соблюдение checkpoint cadence, уменьшение timeout и улучшение score фактически не проверены.
Официальный compiler отсутствует; модель/harness не устанавливались. Kaggle submit не выполнялся.
Нулевой эффект sample LoRA из ADAPTER_AUDIT.md остаётся без изменений; adapters сохранены по условию.
Commit этой фазы включает только system prompt, SUBMISSIONS.md и этот отчёт; публикация — отдельной веткой, без изменения main и без force push.
