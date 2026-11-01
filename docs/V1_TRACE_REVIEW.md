# Разбор сохранённых traces v1 перед сравнением с v2

Дата анализа: 01.11.2026. Новые прогоны не выполнялись.
v1 dev baseline: `36558c6e2433ac8f2495688abcf8ddf7f2b508ac`.
Кандидат v2: `e3951ba9542424fe5aa439f744a23e704283db6e`.
Ветка анализа: `a4-v2-budget-tools`.
Public score v1 **0.10** — отдельный результат Kaggle из контекста пользователя; dev-результат ниже — **2/4**, не leaderboard score.

## Источники и метод

- `O = docs/B4_showcase.zip`, SHA-256:
  `1a80c34ff06eb8644a15d565d6c7bd6202205271f8ec0be223a6eb3d8d6088ff`.
- `E = O!b2_agent_evidence.zip`, SHA-256:
  `905df30b9cb09f0fb4edde84e39cc18d4012c7ea72c65e00a716eba990f76d7b`.
- `E!manifest.json`, `E!summary.json`; `O!results_summary.json`, `O!B2_report.txt`, `O!B3_REVIEW.txt`.
- Локальный `docs/B3_REVIEW.txt` совпадает с архивной копией после нормализации CRLF.
- `../HARNESS_README.md`: разделы 6 (tools), 7 (budgets), 8.1 (patch recovery), 9 (CLI).
- Текущий `submission/prompts/system.md` прочитан; Git diff baseline→v2 в `submission/` затрагивает только этот файл.

Для каждого ID прочитан весь JSON `E!<ID>/traces/trace_<ID>.json`, включая массив steps, arguments и observations; просмотрены все вызовы, результаты и сохранённые patches. Дополнительно прочитаны `E!<ID>/result.json`, `test_output.txt`, `import_probes.json`, `agent.patch`.
Ссылки вида «Requests step 7» ниже означают поле `step_id=7` в соответствующем trace, а не номер строки JSON.

Оба архива прошли `ZipFile.testzip()`; прочитаны в памяти, без распаковки данных соревнования.
Оба summary совпали между собой и с четырьмя result.json; размеры patch совпали с patch_chars.
Дубликаты Requests result/patch в O совпали с E.
Manifest подтверждён Git blobs baseline: восемь текстовых файлов совпадают после точного LF→CRLF преобразования, два weights — побайтово без преобразований. Это не равенство хешей LF и CRLF.
Во всех traces `schema_version=ATIF-v1.7`, `agent.name=adk-eval-core`, `agent.version=1.0`. Последнее — metadata producer, не доказательство установленной версии пакета.

## Четыре задачи

Ошибки в колонке «аргументы / пути» разделены:
**S** — явный отказ из-за отсутствующего обязательного аргумента;
**K** — неверное имя ключа без отказа tool;
**P** — отклонённый путь вне workspace.
Числа получены по вызовам и observations, не поиском слов в prompt.

| Task ID | Verifier | Завершение агента / timeout | Patch, байт | submit_patch | get_status | S / K / P | duration_seconds |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| requests_7309 | resolved=true; exit=0; 207 passed, 13 skipped | submit step 22; final step 24; признаков timeout нет | 692 | 1 | 0 | 1 / 0 / 1 | 145.463660 |
| rich_3052 | resolved=false; exit=1; 1 failed, 6 passed | Agent exceeded session timeout (4.0 min); trace заканчивается read_file step 20 | 2828 | 0 | 0 | 2 / 1 / 2 | 243.484085 |
| fastapi_15589 | resolved=false; exit=-1; verifier не запускался | Agent exceeded session timeout (4.0 min); последнее чтение step 29 | 0 | 0 | 0 | 0 / 0 / 1 | 242.161136 |
| httpx_3672 | resolved=true; exit=0; 24 passed | timeout сообщён B2/B3; result.error=null; trace заканчивается read_file step 26 | 2172 | 0 | 0 | 0 / 0 / 0 | 242.696273 |

Источник результата и duration: `E!<ID>/result.json`; pytest counts сверены с `test_output.txt`.
У FastAPI test_output пуст, import probe verifier отсутствует; -1 нельзя считать падением pytest.
Во всех result.json `snapshot_imports_ok=true` и `submission_unchanged=true`; текущий анализ не повторяет эти runtime-проверки.

| Task ID | Все tool attempts в trace | result.tool_calls | result.llm_calls | Steps |
| --- | ---: | ---: | ---: | ---: |
| requests_7309 | 20 | 18 | 21 | 24 |
| rich_3052 | 18 | 16 | 18 | 20 |
| fastapi_15589 | 27 | 27 | 27 | 29 |
| httpx_3672 | 24 | 24 | 24 | 26 |

Attempts — сумма tool_calls всех steps, включая отклонённые вызовы и submit.
Расхождения согласуются с отказами до выполнения tool: Requests — один missing filepath и бесплатный submit; Rich — два missing old_string.
Вызовы с отклонённым /tmp входят в наблюдаемый бюджетный счётчик.
Ни один result.tool_calls не достиг 50. Analyzer и graph tools не вызывались.

### Timeout и успешность patch — разные оси

- Rich и FastAPI: **agent session timeout** явно записан в result.error.
- HTTPX: **agent timeout по свидетельству B2/B3**, а не по доступной записи исключения. `O!B2_report.txt` сообщает: «В логе агента есть предупреждение о таймауте». Однако `E!httpx_3672/logs/httpx_3672.log` имеет 0 байт; все остальные .log также пусты. В trace нет отдельного timeout event. Полностью независимо подтвердить исходное предупреждение по raw log нельзя. Длительность около 243 секунд сама по себе тип timeout не доказывает.
- **Command timeout** в observations не обнаружен: нет error_type=TimeoutExceeded; все 29 run_command получили exit_code=0. Слова timeout внутри прочитанного исходного кода HTTPX не являются событиями timeout.
- **Verifier timeout** не обнаружен: три verifier завершились с exit 0/1 и pytest summaries; четвёртый не запускался. Его фактический настроенный timeout в этом окружении неизвестен.
- HARNESS_README §8.1 описывает automatic unsubmitted patch recovery: после session timeout непустой рабочий diff может быть извлечён и проверен без submit_patch.
- Поэтому **2/4 resolved и три timeout, заявленные B2/B3, совместимы**: Requests завершился штатно и прошёл; HTTPX прошёл с восстановленным diff; Rich оставил diff, который не прошёл; FastAPI не оставил patch. Это не три verifier timeout и не три пустых patch.

## Время и наблюдаемые операции

Время вызова взято из `tool_calls[].extra.elapsed_s`, ответа — из `observation.extra.elapsed_s`.
Разность — наблюдаемый интервал tool→response; это не профилирование CPU или сервера.
duration_seconds взят отдельно из result.json; границы его замера не описаны runner-кодом в архиве, поэтому не приравниваем его к чистому inference time.
Timestamps присутствуют, но отдельного лога длительности каждого LLM request нет.

| Task | Первый успешный edit исходников | Последнее observation / final, с | Самый долгий tool→response | Самая длинная пауза между предыдущим response и следующим call |
| --- | --- | --- | --- | --- |
| Requests | step 11, 96.235 с | final step 24: 142.488 | step 20: 1.169 с, targeted pytest | перед step 7: 25.167 с |
| Rich | step 12, 147.983 с (docstring); step 13, 158.899 с (код) | step 20: 226.005 | step 7: 0.287 с, создание и запуск repro | перед step 9: 49.488 с |
| FastAPI | нет успешных изменений | step 29: 240.116 | step 13: 0.647 с, inline Python probe | перед step 15: 40.702 с |
| HTTPX | step 18, 171.248 с | step 26: 236.570 | step 15: 0.0103 с, grep references | перед step 12: 62.719 с |

Другие заметные интервалы:
- Requests step 12: 0.205 с; step 10: 0.200 с — repro. Submit step 22: 133.778→133.793 с.
- Rich step 8: 0.152 с — второй repro; пауза перед step 6: 38.744 с, перед step 19: 32.997 с.
- FastAPI steps 26/14: 0.605/0.601 с — probes; паузы перед steps 12/26: 37.018/35.350 с.
- HTTPX step 26 read_file: 0.001889 с, но **до вызова** после предыдущего response прошло 37.305 с.

Большая часть wall time не объясняется измеренными tool→response интервалами.
Паузы могут включать генерацию, обработку контекста и orchestration; распределить их по причинам без server/runner telemetry нельзя.
Не следует называть 62.719 с длительностью read_file: это пауза перед вызовом.

## Подтверждённые проблемы по traces

### Аргументы и workspace

1. **Requests step 7**:
   `write_file` имеет только ключ `content`; `filepath` отсутствует.
   Observation: `Invoking write_file() failed ... mandatory input parameters ... filepath`.
   Step 8 исправляет ключ, но передаёт `filepath="/tmp/repro_content_type.py"`:
   `FileWriteError: Path traversal detected: '/tmp/repro_content_type.py' escapes workspace root.`
   Step 9 использует run_command для создания файла; steps 10/12 запускают его.

2. **Rich steps 9–10**, 130.147 и 140.900 с:
   `edit_file` содержит filepath/new_string, но нет обязательного old_string.
   В arguments присутствуют посторонние ключи `Args`, `optional)`, `], optional)`; текст `old_string:` попал внутрь new_string.
   Оба observations сообщают missing `old_string`; повторная попытка не устранила проблему.
   Step 12 впервые даёт успешный edit.

3. **Rich step 4**, дополнительное наблюдение относительно B3:
   `{"filepath":"rich/prompt.py","start_line\"":151}`.
   Неверный ключ — `start_line"` с лишней кавычкой. Ответ status=ok, start_line=1, end_line=150.
   Step 5 использует правильный start_line=151 и получает строки 151–300.
   Это **одна ошибка аргумента без tool error response**, поэтому она вынесена в K.

4. **Rich step 6** write_file и **step 20** read_file:
   `filepath="/tmp/repro.py"`; FileWriteError/FileReadError, escapes workspace root.
   Последний отказ произошёл примерно на 226-й секунде, после внесения patch.

5. **FastAPI step 12**:
   `write_file(filepath="/tmp/repro.py", ...)` → FileWriteError, escapes workspace root.
   Step 13 переходит к inline `python3 -c` через run_command.

Итого: **3 explicit schema failures + 1 silent wrong-key call + 4 path failures**.
Это 8 проблемных attempts, из них 7 вернули явную ошибку.
Посторонние ключи Rich steps 9–10 не считаются ещё несколькими ошибками: единица подсчёта — вызов.
По parsed trace нельзя надёжно разделить вклад генерации модели и tool-call parser.

### Завершение и содержательная проверка

- Requests единственный вызвал submit_patch, после него tools не вызывались. Agent-targeted pytest step 20: **3 passed**, не 207; **207 passed, 13 skipped** относится к отдельному verifier.
- Requests repro step 10 печатает `Test failed: Expected empty params for malformed header, got {'malformed': True}`, но exit_code=0: скрипт ловит AssertionError. Step 12 печатает Tests passed. Один exit_code недостаточен для оценки такого probe.
- Rich после семи успешных edits (steps 12–18) не выполнил проверку исправленного кода; последние действия — ls и запрещённый read_file /tmp. Verifier показывает содержательную ошибку: `tests/test_prompt.py::test_prompt_str_case_insensitive`, ожидалось `foo`, получено `FoO`. Это assertion failure, а не проблема окружения.
- FastAPI сделал 15 read_file, 11 run_command и один отклонённый write_file. Весь patch пуст. Повторное чтение и уточнение гипотез продолжаются до 240.116 с; конкретная причина всех задержек не измерена.
- HTTPX имеет шесть успешных edits только в `src/httpx/_parsers.py` и `src/ahttpx/_parsers.py`. В конце агент читает существующие вызовы complete в _pool.py, но их patch не меняет; server/network файлы также не изменены. 24 прошедших теста не доказывают полноту всех заявленных требований.
- В трёх непустых patches нет tests/protected configs: Requests меняет src/requests/utils.py, Rich — rich/prompt.py, HTTPX — два _parsers.py.
- Final diff review через run_command наблюдается только у Requests step 21. Полноценного финального цикла review→test→submit у остальных нет.

## Сопоставление с текущей инструкцией v2

| Наблюдение v1 | Что уже требует v2 | Чего эта инструкция не доказывает / не покрывает |
| --- | --- | --- |
| 0 get_status, чтение до дедлайна, только 1 submit | get_status до исследования, после каждых 4 рабочих calls, перед тестами/делегированием, после долгой команды; time_seconds_remaining и tool_calls_remaining | Нет принудительного scheduler; модель может не выполнить правило; длинный inference между checkpoints способен съесть резерв |
| Продолжение поиска и edits поздно в сессии | При <=60 с прекратить расширять поиск, закончить обоснованный минимальный patch, review/короткая проверка; при <=20 с submit сразу | Пороги не обеспечивают правильность patch или физическое завершение при задержке следующего model request |
| /tmp через write_file/read_file | Все операции /tmp только через run_command; файловые tools — workspace | Соблюдение ещё не измерено; правило создания /tmp через run_command было и в v1, но нарушалось |
| Missing filepath/old_string, повтор malformed edit | Точные сигнатуры, пример edit_file, непустой уникальный old_string; исправлять конкретный вызов | Не исправляет parser/runtime автоматически; скрытый неверный ключ при status=ok может остаться незамеченным |
| Неверный start_line" | В v2 показан правильный start_line | Нет отдельной обязательной сверки requested/returned line ranges; нового prompt в этой фазе не добавляем |
| Rich semantic failure, частичный HTTPX patch | Минимальные edits, требования, targeted tests, честное описание проверки | Общие правила не гарантируют полноту требований и покрытие tests; подсказки под эти задачи не добавляются |
| Repro exit=0 при печати failure | Различать наблюдаемые ошибки и не объявлять непроверенное успешным | Автоматический критерий успешности произвольного repro не добавлен |
| Длинные межсобытийные паузы | Контроль бюджета и раннее завершение | Настройки serving, latency, context handling, PYTHONPATH поправку v2 prompt не меняет |

Это соответствие намерений инструкции наблюдаемым проблемам, **не runtime validation v2**.
HARNESS_README §6 подтверждает реальные поля get_status, сигнатуры tools и бесплатность get_status/submit_patch.
Параметр timeout в вызовы tools не добавлялся.
Модель, budgets, sampling, analyzer и adapters кандидата не менялись относительно v1; в этой фазе submission вообще не редактируется.

## Сохранившиеся сведения о запуске и окружении

**Прямые данные из traces:**
- Requests steps 10 и 12: `PYTHONPATH=src python3 /tmp/repro_content_type.py`.
- Requests step 20: `PYTHONPATH=src pytest tests/test_utils.py::test_get_encoding_from_headers`.
- Requests step 21: `git diff src/requests/utils.py`.
- Rich steps 7/8: shell here-document `cat <<EOF > /tmp/repro.py`, затем точная завершающая команда `python3 /tmp/repro.py`; весь текст этих команд хранится в arguments.command соответствующих steps.
- FastAPI steps 13/14/26: многострочные `python3 -c '...'` probes; полное содержимое хранится в arguments.command. Это sandbox probes, не команды запуска swegemma.
- Requests step 20 stdout: `platform linux -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0`; `plugins: typeguard-4.5.1, langsmith-0.7.34`.
- Тот же stdout: `rootdir: /tmp/swegemma_sandbox_0824f595-db9_vlox65ph/workspace`, `configfile: pytest.ini`.

**Output и import paths из result.json/import_probes.json:**
- Корень результатов: `/kaggle/working/b2_agent_runs/20261030T205214365056Z`.
- Полный trace path Requests: `/kaggle/working/b2_agent_runs/20261030T205214365056Z/requests_7309/traces/trace_requests_7309.json`.
- Agent import Requests: `/tmp/swegemma_sandbox_0824f595-db9_vlox65ph/workspace/src/requests/__init__.py`.
- Agent import Rich: `/tmp/swegemma_sandbox_6c47dd89-2c5_smsc3sjx/workspace/rich/__init__.py`.
- Agent import FastAPI: `/tmp/swegemma_sandbox_d648eef2-6e3_1e5044m6/workspace/fastapi/__init__.py`.
- Agent import HTTPX: `/tmp/swegemma_sandbox_cd8a375e-434_1zaoiq1v/workspace/src/httpx/__init__.py`.
- Это пути распакованных workspaces и outputs; они не устанавливают mount path исходного Kaggle dataset.

**По manifest и текстовым отчётам, без повторной проверки сервера:**
- Модель `gemma-4-31b-it-qat-w4a16-ct`; manifest settings:
  `timeout_seconds=120, max_tool_calls=50, max_time_minutes=4, max_turns=80`.
- B2: Kaggle, 4 NVIDIA L4, vLLM tp=4, main_lora и tool_lora ответили OK.
- B3: анализ официального кода `swegemma 0.2.11 / adk_submission 0.2.13` из wheelhouse. Это свидетельство отчёта; pip freeze или вывод --version из среды прогона не приложен.
- Manifest environment_change: `workspace/src and workspace on PYTHONPATH in agent and verifier`. B2 уточняет subprocess backend и локальную поправку среды.
- B2 сообщает baseline fail/reference pass controls и исключение первого Requests baseline, импортировавшего системный пакет. Первичные артефакты controls в этом E отсутствуют; независимо повторить вывод по нему нельзя.
- B2 сообщает ensurepip unavailable; это не traceback в доступном .log.

**Не найдены в проверенных архивах/traces:** точные команды запуска vLLM/swegemma eval, runner notebook/script, версия vLLM, lock/freeze окружения, wheelhouse URL, реализация PYTHONPATH поправки, точные inputs paths для tasks.jsonl/snapshots/graphs/embeddings/модели, model revision и полная serving-конфигурация.
Команды из HARNESS_README §9 — документированные примеры, не доказательство запуска B2.
Слово timeout в исходниках и pytest выводе не используется как свидетельство session timeout.

## Критерии будущего сравнения v1/v2

1. Зафиксировать оба commits, SHA-256 submission/ZIP, model revision, adapters, sampling и одинаковые budgets. Сравнивать v1 baseline и указанный v2; не выдавать B2 за прогон другого ZIP.
2. Получить runner/notebook и точную среду: версии Python/packages/vLLM, server flags, parser, backend, input mounts, PYTHONPATH patch. Если среда отличается, провести обе версии заново в одной среде.
3. Использовать те же четыре ID и snapshots; сохранить baseline/reference controls и import paths. Reference/test_patch не передавать агенту; условия доступа subprocess должны быть одинаковыми.
4. Раздельно собирать verifier resolved/exit/tests, agent termination reason, command TimeoutExceeded и verifier timeout. Для HTTPX обязательно сохранить непустой raw log и исходный timeout event.
5. Считать все attempts, бюджетные tool_calls, llm_calls, S/K/P ошибки, повторения ошибок, get_status и submit. Проверять отсутствие silent wrong-key calls по arguments и фактическим диапазонам ответа.
6. Проверять первый get_status до repository tools, интервалы <=4 рабочих calls, checkpoint перед tests/delegation и после долгих команд. «Долгая команда» в prompt численно не определена; порог анализа следует согласовать заранее.
7. Сохранять time_seconds_remaining/tool_calls_remaining на каждом checkpoint, время первого успешного edit, начала финальной проверки и submit, последний tool action. Измерять соблюдение порогов 60/20 с, а не угадывать остаток по result.duration_seconds.
8. Проверять diff, размер и полноту patch, protected files/artifacts, агентские targeted checks и отдельный verifier. Пустой обоснованный результат отличать от правок ради patch; зелёный узкий verifier не равен полной реализации.
9. Измерять tool duration отдельно от interevent gaps; добавить server request timestamps/latency и context statistics. Нельзя объявлять проблему «медленные команды» по одной длительности сессии.
10. Сохранить одинаковые условия и при возможности повторные прогоны: один запуск на четырёх задачах слишком мал для причинного вывода об улучшении или ожидаемом Kaggle score. Критерии задаются до просмотра новых исходов.

## Ограничения и выполненные проверки

- Только анализ сохранённых данных, без запуска модели, harness, compiler, Docker или pytest.
- Пустые .log, отсутствие runner и server telemetry ограничивают объяснение timeout и задержек. Официальность runtime окружения не предполагается: B2 прямо сообщает локальную поправку subprocess.
- Источник позволяет подтвердить два session timeout непосредственно и третий — только по B2/B3. Отсутствие error у HTTPX не отменяет свидетельство отчёта.
- Analyzer/graph path, runtime-поведение v2 и причинный эффект prompt не проверены.
- Все JSON разобраны, patch lengths и summaries сверены, ZIP CRC проверены; manifest сопоставлен с Git baseline.
- Единственный создаваемый tracked файл этой фазы — `docs/V1_TRACE_REVIEW.md`. Посторонние `docs/B3_REVIEW.txt` и `docs/B4_DEMO.txt` сохраняются вне commit.
- Контроль SHA-256 submission, всех трёх существующих ZIP и исходных материалов выполнен до и после записи отчёта. v1 ZIP:
  `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
