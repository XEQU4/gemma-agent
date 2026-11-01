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

## Уточнение checkpoints — 01.11.2026

Baseline уточнения: `4874c9d0a387755c37079f431e7f30a9143471c8`; ветка прежняя.
Причина: начальная локализация может занять почти весь бюджет, поэтому первый get_status после неё запаздывает.
Новая редакция заменяет только одну строку system prompt; прежнее описание первой итерации A4 выше сохранено как история.

Точный diff инструкции:

```diff
-- Call get_status() immediately after initial localization, then after every 4 working tool calls. Count all other calls, including failed calls and analyzer delegation; exclude get_status and submit_patch. Read time_seconds_remaining and tool_calls_remaining and reserve calls for final verification and submission.
+- Call get_status() before exploring the repository, then after every 4 working tool calls even if localization is still incomplete. Also call it before running tests or delegating, and after a long command returns before continuing work. Count all other calls, including failed calls and analyzer delegation; exclude get_status and submit_patch. Read time_seconds_remaining and tool_calls_remaining and reserve calls for final verification and submission.
```

Первый status теперь до исследования; cadence из 4 рабочих calls действует и при незавершённой локализации.
Дополнительные checkpoints — перед tests/delegation и после долгой команды до продолжения.
Пороги <=60/<=20 s и все остальные инструкции сохранены побайтно; новых timeout-параметров tools нет.

Команда, выполненная неизменённым build script:

```powershell
python -B -X utf8 scripts/build_submission.py --output dist/v2-checkpoints/submission.zip
```

- ZIP: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle\dist\v2-checkpoints\submission.zip`; **443649 bytes**, распаковано **442315 bytes**, 10 entries.
- SHA-256 обеих сборок и записанного ZIP: `48ab02133476d84f0f89c104a57e7ee3ff7dc0185a10566bd4cf66038f29545a`.
- Static checks прошли: 4 YAML, 3 references, единственная допустимая модель, tools/adapters/token limits и одинаковый sampling.
- testzip(), точный список entries и побайтовое сравнение с submission прошли; agent.yaml в корне.
- Проверено точное равенство prompt исходному с одной заменой строки; остальные 9 файлов submission не изменились.
- Модель, budgets 120/50/4/80, sampling, analyzer и adapters сохранены.
- System prompt SHA-256: `a391bff5ecdc94737a00ff93722e371fd2481a852a52b6fca259256ab06057e3`.
- ZIP v1 сохранил `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
- Предыдущий ZIP v2 сохранил `93a3399f5f72d026d7bda81d068bfb0d60e1a49d0495e9835e37b00ae79841ed`.
- Новый ZIP ignored через dist/; старые ZIP не перезаписывались.
- Посторонние B3_REVIEW.txt и B4_DEMO.txt сохранены по SHA-256 и не включаются в commit.
- В commit уточнения входят только system.md и этот отчёт; main не изменяется.

Runtime не запускался. Уменьшение timeout и фактическое соблюдение checkpoints не доказаны.
Official compiler не использовался; Kaggle submit не выполнялся.
