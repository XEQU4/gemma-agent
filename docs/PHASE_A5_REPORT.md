# A5 — фиксация сравнения B6

Дата: 02.11.2026. Ветка: `a4-v2-budget-tools`.
v1: `36558c6e2433ac8f2495688abcf8ddf7f2b508ac`.
v2: `e3951ba9542424fe5aa439f744a23e704283db6e`.

**Решение:** v2 остаётся кандидатом для расширенной проверки. В B6 улучшились наблюдаемые показатели завершения и число ошибок выбранных категорий, но resolved осталось 2/4. Прирост качества, надёжное общее улучшение и прирост Kaggle score не доказаны. Новые prompt-изменения и прогоны в A5 не выполнялись.

## Источники и сверка

Источник: `docs/B6_review_package.zip`, SHA-256:
`8411f169bc79fdbbda3906d8129b2aaf45efdb37db2dff2b08ca277c5bddfa66`.
Прочитаны `B6_COMPARISON.txt`, `review.json` и вложенный `B6_evidence.zip`.
SHA-256 вложенного evidence совпал с review.json:
`f2b3dfed4b5bb8601bf06015f997ff3003eae727eb110f3031d6f6dd0d796397`.

Оба ZIP прошли testzip(); анализ выполнен в памяти, без исполнения архивного кода.
Во вложенном evidence прочитаны восемь result.json/agent_outcome.json, comparison_summary.json, trace_analysis.json, traces, test_output.txt и effective_config.json; проверены размеры patches.
Compilation сверена по compilation.json и compilation/{v1,v2}/result.json; controls.json совпал с восемью controls/<task>/<baseline|reference>/result.json.
Числа resolved/session timeout и счётчики tool_calls/llm_calls пересчитаны по результатам, submit/get_status — по trace calls, S/K/P — суммированием сохранённых trace_analysis.json.
Это сверка основных показателей; заявленные B6 91 consistency checks целиком заново не воспроизводились.

Есть небольшое различие metadata первого прогона: comparison_summary.json содержит пустые timeout_events.agent_command/verifier, а исходный result.json и его копия в review.json не содержат timeout_events. Остальные поля совпадают; остальные семь summary/result совпадают полностью. Отсутствие поля само по себе не доказывает отсутствие timeout.

B6 — новые парные прогоны, не прежние B2. Числа из docs/V1_TRACE_REVIEW.md не подмешиваются к этому сравнению.

## Основные результаты

| Показатель | v1 | v2 |
| --- | ---: | ---: |
| Verifier resolved | 2/4 | 2/4 |
| Agent session timeout | 4/4 | 2/4 |
| Прогоны хотя бы с одним submit_patch | 1/4 | 2/4 |
| Resolved без agent error | 0/4 | 1/4 |
| get_status calls | 0 | 6 |
| Ошибки S / K / P по B6 | 0 / 4 / 3 | 1 / 0 / 1 |
| Сумма S/K/P | 7 | 2 |
| Recorded tool_calls | 70 | 54 |
| Recorded llm_calls | 74 | 65 |

S — отсутствующий обязательный аргумент; K — неизвестный ключ tool arguments, принятый без явного отказа; P — запрещённый filepath.
Это выбранная классификация, а не все возможные ошибки агента. Attempts в traces отличаются от бюджетного tool_calls.
Число прогонов с submit не равно числу вызовов: Requests v1 вызвал submit_patch четыре раза.

### Восемь прогонов

Префикс путей ниже — `B6_evidence.zip!comparison/`. Для каждой строки источники: `<каталог>/result.json`, `agent_outcome.json`, `test_output.txt`, `traces/trace_<task>.json`.

| Каталог | Verifier | Agent timeout | submit calls | Total, с | Patch, символов |
| --- | --- | --- | ---: | ---: | ---: |
| 01_v1_requests_7309_r1 | resolved; 207 passed, 13 skipped | да | 4 | 243.52 | 842 |
| 02_v2_requests_7309_r1 | resolved; 207 passed, 13 skipped | нет | 1 | 112.94 | 692 |
| 03_v2_rich_3052_r1 | unresolved; 1 failed, 6 passed | нет | 1 | 206.71 | 2949 |
| 04_v1_rich_3052_r1 | unresolved; 1 failed, 6 passed | да | 0 | 243.50 | 2445 |
| 05_v1_fastapi_15589_r1 | verifier не запускался, exit=-1 | да | 0 | 242.16 | 0 |
| 06_v2_fastapi_15589_r1 | unresolved; 2 failed, 5 passed | да | 0 | 246.40 | 1302 |
| 07_v2_httpx_3672_r1 | resolved; 24 passed | да | 0 | 242.69 | 1354 |
| 08_v1_httpx_3672_r1 | resolved; 24 passed | да | 0 | 242.69 | 800 |

Total включает setup и verification, а не только agent phase. Лимит agent session — 240 секунд.
FastAPI v1 не оставил patch; exit=-1 не является провалом pytest.
HTTPX обеих версий прошёл verifier после восстановления рабочего diff без submit.
Session timeout определяется по agent_outcome.raw_agent_error, а не только по result.error: у Requests v1 и обоих HTTPX result.error=null при записанном agent timeout.
По B6 command/verifier timeouts не зарегистрированы; шесть timeout относятся к agent session.

## Compilation, controls и условия

По B6 обе версии прошли фактическую официальную compilation; в evidence оба compilation result имеют compiled=true и class=LlmAgent. В A5 compiler повторно не запускался.
Все восемь baseline/reference controls дали ожидаемые исходы: четыре baseline — unresolved/exit=1, четыре reference — resolved/exit=0. «Controls прошли» означает именно эту проверку, а не прохождение baseline-тестов.

Все восемь effective_config.json совпадают:

- time_minutes=4, tool_calls=50, turns=80;
- command_timeout_seconds=120, verification_timeout_seconds=300;
- backend=subprocess;
- temperature=0.2, top_p=0.95, max_output_tokens=16384, thinking_budget=4096, include_thoughts=true;
- явный sampling seed отсутствует.

B6 сообщает Python 3.12.13, 4×NVIDIA L4, Gemma 4 31B QAT W4A16 revision 2, vLLM 0.19.1 и успешные probes обоих adapters.
В agent/verifier применена локальная поправка PYTHONPATH: workspace/src и workspace. Результаты отмечают imports_ok=true; семь запусков достигли verifier.
Это локальный subprocess evaluation, не неизменённый официальный Kaggle scorer и не подтверждение нового public score.

## Открытый вопрос Requests v1

В `comparison/01_v1_requests_7309_r1/traces/trace_requests_7309.json`:

- step 24, около 161.944 с: submit_patch → status=ok, patch_size=692;
- step 25, около 164.026 с: последующий run_command;
- ещё submit_patch на steps 26, 28 и 33; между ними продолжаются рабочие calls;
- step 33, около 226.283 с: submit_patch → patch_size=842;
- agent_outcome фиксирует session timeout после примерно 240.012 с.

**Причину продолжения после submit_patch сейчас исследует B** (статус из контекста пользователя). A5 фиксирует наблюдение, не объясняет его ошибкой модели, parser или harness без установленной причины. Наличие submit не считается доказательством штатного завершения.

## Ограничения и следующий шаг

- Четыре ранее использованные диагностические задачи; один прогон каждой версии на каждой задаче, без фиксированного seed. Статистическая значимость и перенос на скрытые задачи не установлены.
- Общий server/cache и порядок запусков влияют на сопоставимость времени.
- После первого прогона runner упал при логировании run_complete из-за дублированного kind. По B6_LOGGING_RECOVERY.json изменён только logging call; исходный первый result сохранён, остальные прогоны продолжены в той же сессии. Была пауза, исторический gpu_after первого прогона отсутствует.
- Отдельная ранняя отменённая попытка без завершённого agent run исключена из сравнения по B6.
- Subprocess backend не обеспечивает строгую изоляцию host filesystem; локальная поправка PYTHONPATH ограничивает эквивалентность официальной среде.
- Requests содержит 13 skipped tests. Успех verifier не равен полной реализации требований или штатному завершению агента.
- V2 начинает с get_status во всех четырёх задачах, но cadence не соблюдается стабильно: по B6 между проверками были 11 рабочих calls у Requests и 9 у Rich; у FastAPI/HTTPX после начального статуса — 17/16. Два session timeout остаются.
- Меньше ошибок S/K/P и timeout в этих наблюдениях не доказывает причинный эффект prompt или прирост качества.

Следующий шаг — дождаться вывода B по Requests после submit, затем отдельно определить и согласовать расширенную проверку с контролируемой средой и повторениями. V2 пока сохраняет статус кандидата. Новые инструкции под диагностические задачи не добавляются; результаты verifier не превращаются в подсказки агенту.

## Изменения A5

Создан только docs/PHASE_A5_REPORT.md. Submission, ZIP, main и docs/SUBMISSIONS.md не менялись.
До начала работы docs/B3_REVIEW.txt и docs/B4_DEMO.txt уже находились в index; они сохранены staged и исключены из commit A5.
Архив B6 и извлечённые сторонние материалы в Git не добавляются. GPU, Kaggle submit и новые runtime-прогоны не выполнялись.
