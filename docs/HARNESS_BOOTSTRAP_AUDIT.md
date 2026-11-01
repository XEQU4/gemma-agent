# Аудит локальных компонентов harness bootstrap

Дата: 01.11.2026. Ветка: `a4-v2-budget-tools`.
HEAD перед работой: `a56c68ea145743a1ce010d2cff940b1e69d13850`.
Кандидат v2: `e3951ba9542424fe5aa439f744a23e704283db6e`.

**Вывод:** архив содержит данные задач, sample submission, публичные wheels для sandbox и его setup-код. Полного комплекта запуска harness/vLLM нет. По одному этому архиву воспроизводимый запуск v2 собрать нельзя: отсутствуют пакеты harness, источник их установки, serving/CLI implementation и точная настройка CLI budgets. Ничего не устанавливалось и не запускалось.

## Архив и границы поиска

Путь: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\gemma-4-developer-agent.zip`.
Размер: **21 929 290 938 байт**. Формат: ZIP, **524 entries**.

Listing прочитан через Python stdlib `zipfile.ZipFile.infolist()`: чтение central directory с произвольным доступом, без последовательной распаковки 22 ГБ.
Модель, snapshots, graphs, embeddings, tasks.jsonl и wheels не извлекались.
Вложенные snapshots/*.tgz и внутренности публичных wheels не исследовались: выводы об отсутствии относятся к entries внешнего ZIP, а не ко всем файлам внутри snapshots.
Полный testzip()/SHA-256 большого ZIP намеренно не запускались: это потребовало бы чтения всего содержимого. CRC проверен при чтении каждого из 12 выбранных entries.

| Группа entries | Число | Сумма file_size, байт |
| --- | ---: | ---: |
| HARNESS_README.md | 1 | 55 940 |
| docker/ | 4 | 25 931 |
| sandbox/ | 1 | 13 883 |
| sample_submission/ | 10 | 442 238 |
| tasks.jsonl | 1 | 1 984 455 |
| snapshots/ | 129 | 21 496 844 379 |
| graphs/ | 127 | 422 050 109 |
| embeddings/ | 127 | 467 546 088 |
| wheels/ | 124 | 27 810 465 |

Для идентификации listing вычислен SHA-256:
`459660729719bfd1f70cf55f723d2ca9526135d5a5f0b6cc74c2830968516a78`.
Это **не хеш всего ZIP**. Алгоритм: JSON UTF-8 списка `(filename,file_size,compress_size,CRC)` в порядке infolist, `ensure_ascii=False,separators=(',',':')`, затем SHA-256.
Размер и mtime_ns архива проверены до и после анализа; исходный архив не изменялся.

## Найденные и отсутствующие компоненты

| Что искали | Результат |
| --- | --- |
| swegemma wheel / source | Нет соответствующего entry |
| adk_submission / adk-submission wheel / source | Нет |
| adk_eval_core / adk-eval-core wheel / source | Нет |
| vLLM wheel / source / installation lock | Нет |
| Notebooks *.ipynb, install/bootstrap shell scripts | Нет |
| scripts/inference.py, scripts/metric.py | Нет; упоминаются только в README |
| src/swegemma/cli.py, models.yaml | Нет; упоминаются только в README |
| requirements / lock-файлы harness | Нет |
| README | Только HARNESS_README.md; внешний wheelhouse URL и рецепт установки harness/vLLM в нём не найдены |
| Sandbox setup | sandbox/setup.py |
| Sandbox image recipes | docker/Dockerfile.sandbox, docker/Dockerfile.public |
| Python compatibility shims | docker/imp.py, docker/telnetlib.py |
| Sample agents/adapters/configs | sample_submission/agent.yaml, sub_agents/code_analyzer.yaml, eval_config.yaml, configs/sampling.yaml, prompts/*.md, adapters/{main_lora,tool_lora}/ |
| Task inputs | tasks.jsonl, snapshots/, graphs/, embeddings/ присутствуют в listing |

Все три непосредственных Python entries внешнего ZIP: `docker/imp.py`, `docker/telnetlib.py`, `sandbox/setup.py`. Отдельного CLI или runner среди них нет.
Дополнительно выполнен поиск имён файлов в родительском проекте, включая hidden/ignored файлы и локальную .venv, с исключением больших каталогов snapshots/graphs/embeddings. Пути swegemma/adk_submission/adk_eval_core, inference.py/metric.py/models.yaml/notebooks/bootstrap также не найдены. Это не поиск по всей машине.

124 entries `wheels/*.whl` — набор публичных зависимостей; например:

- `wheels/pytest-8.3.4-py3-none-any.whl`;
- `wheels/httpx-0.28.1-py3-none-any.whl`;
- `wheels/fastapi-0.141.1-py3-none-any.whl`;
- `wheels/pydantic-2.13.4-py3-none-any.whl`;
- `wheels/setuptools-83.0.0-py3-none-any.whl`.

Имён пакетов harness, vllm, torch, transformers, google-adk или litellm в списке wheels нет. Совместимость и полнота этих 124 wheels не проверялись; есть варианты cp312/cp313 и Linux manylinux.
`docker/Dockerfile.public:24` прямо описывает этот cache как public wheels, без private wheels/internal code artifacts. Наличие папки wheels не означает наличие официального harness wheelhouse.
Собственные requirements/lock-файлы тестируемых репозиториев могут находиться внутри snapshots; они не являются подтверждённым bootstrap harness и здесь не извлекались.

## Выборочное извлечение

Каталог вне Git:
`C:\Users\barah\AppData\Local\Temp\gemma_harness_bootstrap_audit_omtz4qlo`.

Извлечены **12 файлов, 98 233 байта**. Их код не импортировался и не выполнялся.
Проверены безопасные относительные пути, отсутствие symlink, размер каждого <100 000 байт, CRC при чтении и побайтовое равенство копии с entry.

| Entry внутри ZIP | Байт |
| --- | ---: |
| HARNESS_README.md | 55940 |
| docker/Dockerfile.public | 988 |
| docker/Dockerfile.sandbox | 773 |
| docker/imp.py | 834 |
| docker/telnetlib.py | 23336 |
| sandbox/setup.py | 13883 |
| sample_submission/agent.yaml | 438 |
| sample_submission/sub_agents/code_analyzer.yaml | 361 |
| sample_submission/eval_config.yaml | 232 |
| sample_submission/configs/sampling.yaml | 120 |
| sample_submission/adapters/main_lora/adapter_config.json | 664 |
| sample_submission/adapters/tool_lora/adapter_config.json | 664 |

SHA-256 ключевых извлечённых файлов:

- `HARNESS_README.md`: `445000219b803942c469391ec8b69791a31e9cec2f934738c767e34b5ca0aa1f`.
- `sandbox/setup.py`: `0263995ade90f83c8efa0ab5c7c9b7629696f39bc75274d58fc27ab774568409`.
- `docker/Dockerfile.public`: `c92dfd9cd9ce019c4910a5334d6ecac606b612ec736a933b4af36da9c6fdf06c`.
- `docker/Dockerfile.sandbox`: `2fef37c9275522eea4dc3371c60b54d9ba3cfa7871f89f1749aa92f34beff70a`.

Архивный HARNESS_README побайтово совпадает с `../HARNESS_README.md`.
Извлечённые sample configs — оригиналы соревнования, а не текущий v2: в них сохраняются старые includes и budgets. В рабочую submission они не копировались.

## Что подтверждает доступный код

### Источник установки

**Harness/vLLM:** источник установки, package index/wheelhouse URL, полный pinned список зависимостей и команда установки не найдены. Не следует заменять это догадкой о PyPI или произвольной версии vLLM.

**Docker sandbox:** оба Dockerfile используют `FROM python:3.13-slim`.
В RUN записаны apt-зависимости `git patch protobuf-compiler pigz` и точная команда:
`pip install --no-cache-dir pytest pytest-timeout==2.1.0 typer pdm-backend setuptools wheel poetry-core hatchling flit-core editables`.
В ней нет harness или vLLM; конкретный pip index не задан.
Dockerfile.public дополнительно содержит `COPY wheels/ /wheels/`, оба копируют imp.py/telnetlib.py в Python 3.13 site-packages.
Это рецепты среды для тестов, а не host inference stack. Сборка не выполнялась.
Build context в рецептах требует imp.py/telnetlib.py и, для public, wheels/ рядом в context; готовый script подготовки такого context не найден.

**sandbox/setup.py:**

- Строка 28: `WHEELS_DIR = Path("/wheels")`.
- Строки 193–213: editable install текущего workspace с `sys.executable -m pip install --no-index --find-links=/wheels --no-build-isolation --no-deps -e <workspace>`.
- При ненулевом exit выполняется fallback `[sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(workspace)]` (строка 210). В нём нет --no-index/--no-build-isolation; код нельзя описывать как безусловно offline при любых ветвях.
- main (323–396) разбирает --fast-path/-f, --no-fast-path, --workspace/-w и repo как positional. Это параметры setup.py, **не swegemma CLI flags**.
- setup_git_exclude и install_editable_package вызываются **до** выбора fast path (352–355).
- Slow path читает pyproject dependencies/optional-dependencies и requirements*.txt/test-requirements*.txt, выбирает доступные wheels и вызывает pip. Фактического чтения setup.cfg нет, несмотря на формулировку docstring.
- execute_fast_path (290–320) создаёт workspace_paths.pth в site-packages, добавляет workspace и его непосредственные каталоги с именами, не начинающимися с точки, затем настраивает pytest.ini/conftest.py.
- Эти действия предназначены для sandbox, а не для репозитория submission. Скрипт в этом аудите не запускался.

## Документированная схема serving и adapters

Следующее подтверждено **текстом HARNESS_README, не доступным исходником runtime**:

1. §3.1, строки 163–169: setup_vllm_server в scripts/inference.py использует tp=4, gpu_memory_utilization=0.90, max_model_len=32768, scheduler_reserve_full_isl=False, enable_auto_tool_choice=True, tool_call_parser/reasoning_parser="gemma4".
2. §3.3, строка 202: VllmServer на 127.0.0.1:8000; endpoint `http://127.0.0.1:8000/v1`; routing через `LiteLlm(model=f"openai/{served_model}", api_base="http://127.0.0.1:8000/v1")`, create_model_registry и install_litellm_reasoning_patch.
3. §3.4, строки 206–208: discover_adapters находит adapters/<name>, serving получает `--lora-modules name1=path1 name2=path2 ...`, запросы идут на `openai/<adapter_name>`.
4. В sample root объявлен `adapter: main_lora`, у code_analyzer — `adapter: tool_lora`; обе adapter_config.json имеют r=4 и base_model_name_or_path=`google/gemma-4-31b-it-qat-w4a16-ct`.
5. Из документированной формулы для этих двух adapters следует enable_lora=True, max_loras=2, max_lora_rank=4. Это вычисление по metadata, не проверка загрузки.
6. Для агентской фазы eval нужны работающий совместимый model endpoint и registry/routing base alias + обоих adapters. Автоматизирует ли это конкретный CLI, как передаётся model filesystem path и какие версии библиотек нужны — по имеющемуся архиву неизвестно.

Готовой команды запуска сервера нет. Не восстановлены constructor/signatures VllmServer и create_model_registry: многоточие в README не заменяет Python API.
model name в adapter_config — metadata, не подтверждённый путь модели на Kaggle и не инструкция скачивания.
Источник `models.yaml` отсутствует; формат файла полностью по коду не проверен.

## Пути данных и subprocess backend

README §9.1 документирует `--tasks tasks.jsonl`, `--snapshots-dir snapshots`, `--submission-dir sample_submission`, `--results-dir results/run_01`.
Для выбора задач указан --task-id/--task-ids; --models-yaml задаёт пользовательский registry.
Относительные inputs в примере соответствуют entries архива, но конкретные Kaggle mounts и полный рецепт для v2 не заданы.
Документированный механизм передачи CLI путей wheels/graphs/embeddings в прочитанном разделе отсутствует; не выдумываем дополнительные flags.
setup.py явно ожидает /wheels; каким CLI параметром или config host выбирает cache и staging, установить без CLI/container_setup.py нельзя.

README §4.1, строки 259–261, описывает --sandbox subprocess:

- временные workspace/, tmp/, wheels/, venv/;
- переписывание ссылок /workspace, /tmp, /wheels, /usr/local/bin;
- start_new_session=True, os.killpg(..., signal.SIGKILL) при command timeout.

Доступны данные и sandbox/setup.py, **но нет реализации SubprocessSandbox из adk-eval-core**, swegemma container_setup.py/agent_runner.py, dependency staging и запуска модели.
Наличие setup.py недостаточно для subprocess backend. Поддержка native Windows этим backend не подтверждена; описанные process-group операции относятся к POSIX. Запуск в Windows не проверялся.
Локальная PYTHONPATH поправка из предыдущего B2-отчёта не восстановлена: её runner-код в большом архиве также отсутствует.

## CLI budgets и eval_config.yaml — отдельная неопределённость

**Исходник CLI недоступен. Нельзя подтвердить ни то, что swegemma eval читает eval_config.yaml, ни то, что он его игнорирует.**
В README строки 98 и 542 прямо привязывают `load_submission_eval_config()` к **scripts/inference.py**.
В таблице строки 552 столбец environment override тоже подписан scripts/inference.py.
Нельзя автоматически переносить этот loader, env overrides или precedence на CLI.

| Budget | Что документировано | Что не установлено для CLI |
| --- | --- | --- |
| timeout_seconds | --timeout-seconds, §9.1; per-command Phase 1 | Чтение YAML и precedence относительно flag/default |
| max_tool_calls | --max-tool-calls 50 в примере §9.1 | Автоматическая загрузка из submission/eval_config.yaml |
| max_time_minutes | --max-time-minutes 30 в примере §9.1 | YAML/CLI/env precedence |
| max_turns | config.budget.turns; evaluation.max_turns; SWE_MAX_TURNS / SWE_MAX_LOOP_ITERATIONS указаны для inference.py | Наличие CLI flag, точное имя и обработка env/YAML |
| verifier timeout | --verification-timeout-seconds, §9.1 | Соответствие фактической установленной версии и связь с остальными timeout |

В README примере §9.1 лимит времени 30 минут: это пример, **не команда сравнения v1/v2**.
Архивный sample eval_config: timeout_seconds=60, max_tool_calls=10, max_time_minutes=1, max_turns=50.
Текущий v2: **120 / 50 / 4 / 80**. Само наличие такого файла ещё не доказывает применение этих значений CLI.
Флаг --max-turns и использование SWE_MAX_TURNS для CLI в этом отчёте не предлагаются как подтверждённые способы.
После получения исходников надо проследить CLI options → создание EvalConfig/EvaluationBudget → agent loop, отдельно проверив loader YAML и его приоритеты.

## Недостающее и следующий конкретный шаг

Запуск нельзя воспроизвести только из найденных материалов. Требуется получить у организаторов или владельца работавшего окружения **сам официальный harness wheelhouse либо точную ссылку на него вместе с installation/bootstrap notebook/script**.
Нужны wheels swegemma, adk-submission, adk-eval-core, их dependency metadata и источник совместимого vLLM с gemma4 parsers; версии/URL по памяти не подставлять.

После получения файлов следующий шаг **без запуска модели**:

1. Прочитать wheel metadata/entry_points и извлечь только CLI/config, server manager, adapter registry, SubprocessSandbox и dependency staging code.
2. Найти реальную обработку eval_config.yaml, max_turns и precedence; сформировать точный способ выставить 120/50/4/80.
3. Сопоставить scripts/inference.py/metric.py и models.yaml, если они поставляются отдельно; установить точные model/input/cache paths и команды запуска.
4. Получить pinned версии среды и runner/PYTHONPATH поправку B2; только затем подготовить воспроизводимый рецепт сравнения.

Это перечень необходимых артефактов, не утверждение, что все они распространяются одним wheelhouse.
Сетевого поиска, скачивания, установки, GPU/Docker запуска и Kaggle submit в этой фазе не было.

## Контроль изменений

До работы: ветка a4-v2-budget-tools, staged/tracked diff пуст; untracked docs/B3_REVIEW.txt и docs/B4_DEMO.txt сохранены.
Создаваемый tracked файл — только docs/HARNESS_BOOTSTRAP_AUDIT.md.
Проверены неизменность SHA-256 submission, трёх dist ZIP, B3_REVIEW.txt/B4_DEMO.txt/B4_showcase.zip; большой архив контролируется по size/mtime и повторному listing, без полного хеширования.
Извлечённые сторонние файлы остаются во временном каталоге и в Git не включаются.
Никакая статическая проверка здесь не является runtime validation кандидата.
