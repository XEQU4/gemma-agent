# A6 — v3: финальный ответ после submit_patch

Дата: 03.11.2026. Ветка: `a6-v3-finalize`.
Базовый commit проекта: `7a7f45c09b4e104c7b18928d6b0fbe41f1ca3e41`.
Контрольная версия v2: `e3951ba9542424fe5aa439f744a23e704283db6e`.
Параллельная B7 закреплена на v1/v2 и этой фазой не меняется.

## Основание и гипотеза

Источник: `docs/B7_preparation_package.zip!REQUESTS_V1_REVIEW.txt` и приложенные `harness_source/swegemma/tools/execution.py`, `harness_source/swegemma/harness/agent_runner.py`; SHA-256 архива:
`b8bb63a653bc552ef3450cbe9e97f8f62188ca9d0a07ae13347953af997f6a75`.
ZIP прошёл testzip(). Исходники прочитаны из архива, не выполнялись и не менялись.

`submit_patch` сохраняет отфильтрованный diff и устанавливает patch_submitted; повторный вызов заменяет сохранённый patch. Внутри `runner.run_async` ранний выход после submit требует финального обычного текста без function_call/function_response. Проверка patch_submitted после этого потока сама по себе не останавливает уже продолжающийся поток. Это подтверждается приложенными execution.py:76–116 и agent_runner.py:806–864, 920–922, 1048–1054.

По B7 Requests v1 в B6 после первого успешного submit продолжил работу, вызвал submit четырежды и добавил лишний src/dummy.py; verifier принял последний patch. Исходники сверены B с официальным wheel, но хеши файлов, фактически установленных в той Kaggle-сессии, не записаны: побайтовая идентичность среды не доказана.

**Гипотеза:** явная инструкция сразу дать финальный текст после успешного submit и не пытаться повторно включить защищённые файлы может сократить повторы и лишние изменения. Эффект не проверен runtime; instruction не является принудительным изменением harness.

## Точный diff prompt относительно v2

```diff
- With more time, verify and review the diff before submitting. submit_patch must be the final tool action: inspect its returned status, then summarize changes, checks, and limitations without further tool calls.
+ Complete checks and review the diff before submit_patch. Tests and protected configs are intentionally excluded from the patch; do not resubmit to include them or create files to test submission. After submit_patch succeeds, immediately return a short final text-only response. Do not call tools, change files, or submit again after success. If submit_patch fails, do not claim it succeeded.
```

Остальные строки prompt сохранены побайтно, включая checkpoints get_status и пороги 60/20 секунд. Правило 20 секунд по-прежнему имеет объявленный приоритет над остальным workflow.
Инструкция не предписывает поддельное подтверждение после ошибки submit, принудительный патч без оснований или конкретное решение диагностических задач.

## Проверки и артефакт

Команда из корня проекта (существующие системные Python и PyYAML 6.0.3):

```powershell
python -B -X utf8 scripts/build_submission.py --output dist/v3-finalize/submission.zip
```

- Статический validator прошёл: 4 YAML, 3 references, одна модель `gemma-4-31b-it-qat-w4a16-ct`, tool/adapter references, допустимые конфигурации и одинаковый sampling.
- Две сборки внутри скрипта имеют одинаковый SHA-256; тест архивов и побайтовое соответствие 10 entries исходникам прошли.
- Отдельно проверены testzip() v2/v3 и одинаковый список entries; между архивами изменён только `prompts/system.md`.
- Все 9 остальных файлов submission побайтно совпадают с Git blob v2; модель, budgets, sampling, analyzer и adapters неизменны.
- Размер ZIP: **443830 байт**, распаковано **442496 байт**; `dist/` ignored.
- SHA-256 v3 ZIP: `6b1317d697e65274ce40a619919c90e8b5620e1a1546bc341f6cd2e0cd1fb3e0`.
- Путь: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle\dist\v3-finalize\submission.zip`.
- Исходные ZIP v1, v2 и v2-checkpoints и архив B7 сохранили SHA-256; staged B3/B4 сохранены и исключены из commit A6.

Скрипт указывает source_commit базовой рабочей ветки `7a7f45c...`, поскольку ZIP собран до commit A6 с изменённым prompt. Хеш ZIP и содержащийся в нём prompt идентифицируют собранный кандидат.
Статические проверки — не официальная compilation и не runtime validation. GPU, Docker и Kaggle submit не запускались; модель и harness не устанавливались.

## Будущее сравнение v2/v3

После завершения параллельной B7 отдельно определить набор задач, повторы и одинаковые serving/backend/буджеты/inputs для v2 и v3; сохранять версии, ZIP, traces и raw events.
Измерять verifier resolved отдельно от agent timeout; количество submit на прогон, времена первого/последнего submit, наличие обычного финального ответа, tool calls и edits после успешного submit, ошибки submit, чистоту и защищённые файлы в последнем patch.
Сохранять отфильтрованные patches и verifier results; проверять соблюдение checkpoints, 60/20-секундных порогов и качество targeted checks.
Сравнение должно выявить влияние новой инструкции, не раскрывая агенту reference/test patches и не меняя harness ради одного варианта. До фактического прогона снижение timeout, повторов submit и улучшение score не подтверждены.
