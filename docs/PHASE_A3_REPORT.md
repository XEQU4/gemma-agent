# PHASE A3 — статическая проверка и воспроизводимая упаковка

Дата: 2026-10-30 (Asia/Qyzylorda).
Проект: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle`.
Исходный HEAD: `d020691addd53ac4f4595de181deb799d68cf878` (`main`).
До начала фазы рабочее дерево было чистым; build script, отчёт и ZIP отсутствовали.
Источник ограничений: локальный `../HARNESS_README.md`, §§2.2–2.4, 3.1–3.4, 6.
SHA-256 README harness: `445000219b803942c469391ec8b69791a31e9cec2f934738c767e34b5ca0aa1f`.

## Результат

- ZIP: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle\dist\submission.zip`.
- Размер ZIP: **442571 bytes**.
- Распакованные файлы: **10**, **441237 bytes**; строго меньше 3221225472.
- SHA-256 первой сборки: `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
- SHA-256 второй сборки: `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
- SHA-256 записанного ZIP: `8c5ba7eb5d09513807ebf8756abedd0f5d66635270bd4c12a0cbdd273e01cfbf`.
- `agent.yaml` находится непосредственно в корне ZIP, без внешней папки submission/.
- Внутри ZIP только содержимое submission/: нет scripts/, docs/, uv-файлов или данных.
- ZIP ignored: `.gitignore:5:dist/`; правило проверено через git check-ignore.

## Команда и environment

Фактически выполнено из корня kaggle/:

```powershell
python -B -X utf8 scripts/build_submission.py
```

Использованы существующие Python 3.14.0 и PyYAML 6.0.3; установки пакетов в A3 не выполнялись.
PyYAML объявлен в `pyproject.toml`:

```toml
[dependency-groups]
validation = ["PyYAML==6.0.3"]
```

Команда для uv environment с этой группой:

```powershell
uv run --group validation python -B scripts/build_submission.py
```

Эта uv-команда в A3 не выполнялась; dependency synchronization и создание uv.lock не производились.
Environment проекта на Python 3.13 отдельно не использовался для запуска сборки.
При существующем ZIP скрипт останавливается без перезаписи; повторная сборка требует нового
`--output`, например `dist/submission-recheck.zip`.

## Реализованные проверки до упаковки

- Ровно один из agent.yaml/agent.yml/root_agent.yaml/root_agent.yml; профиль v1 дополнительно требует agent.yaml.
- Allowlist расширений: .yaml, .yml, .md, .txt, .py, .json, .safetensors.
- Только обычные файлы; symlinks и Windows junctions запрещены в дереве submission.
- Пути POSIX: запрещены абсолютные пути, drive letters/colon, backslash, null byte, пустые компоненты, . и ...
- Распакованный размер строго меньше 3221225472; не более 10000 файлов и 1000 YAML.
- SafeLoader: никаких Python object constructors; duplicate keys запрещены.
- Все YAML разобраны, !include для YAML раскрываются, .md/.txt читаются как UTF-8.
- Все includes/config_path разрешаются относительно содержащего YAML внутри submission и существуют.
- Reference graph проверен на циклы (включая config_path); include depth до 10; YAML/expansion до 50 MiB.
- Root, referenced и standalone agents проверены: один разрешённый alias из четырёх quantized models README.
- Tools сверены с девятью именами README; agent_tool/sub_agents требуют существующий YAML config_path.
- Adapter names проверены по README regex; config и safetensors существуют; JSON peft_type=LORA,
  rank 1–128, declared base model совпадает с agent model. Это metadata/reference checks.
- generate_content_config сверяется с allowlist, запрещённые execution-altering поля отклоняются.
- max_output_tokens: 1–32768; thinking_budget: 0–32768; проверены типы и числовые параметры sampling.
- Root и analyzer sampling после раскрытия includes точно одинаковы.

Текущий результат: **4 YAML**, **3 references**, одна модель
`gemma-4-31b-it-qat-w4a16-ct`; все перечисленные проверки прошли.

## Воспроизводимость и проверка ZIP

Скрипт строит два независимых ZIP в отдельных временных streams из одного проверенного inventory.
Entries отсортированы по относительному POSIX path. У каждого фиксирован timestamp
1980-01-01 00:00:00, create_system=Unix, regular file mode=0644, пустые extra/comment.
Используется ZIP_STORED; результат не зависит от версии zlib.
Запись окончательного output выполняется эксклюзивно только после проверки обеих сборок.

Для каждой сборки выполнены testzip(), сравнение точного списка и порядка entries,
timestamps/размеров, побайтовое сравнение с source и SHA-256 каждого файла.
Проверка повторена для записанного ZIP. Независимая последующая проверка zipfile также прошла.
Все **10/10** исходных файлов submission побайтно совпадают с blobs исходного Git commit.

## Entries, размеры и SHA-256 исходников

| Entry | Bytes | SHA-256 |
|---|---:|---|
| `adapters/main_lora/adapter_config.json` | 664 | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` |
| `adapters/main_lora/adapter_model.safetensors` | 217672 | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` |
| `adapters/tool_lora/adapter_config.json` | 664 | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` |
| `adapters/tool_lora/adapter_model.safetensors` | 217672 | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` |
| `agent.yaml` | 438 | `c7fbbbbdc44778419be8e9f53a85800eeb17d0cf151e0846c46e107401b72034` |
| `configs/sampling.yaml` | 120 | `3dab0b2506dae34ce92fef7b380d6073729104b23fe2cf66d44ac1d2f213aa6a` |
| `eval_config.yaml` | 233 | `ebaf6002217fcd4a114eadce280efd287218c61058f78ba96210c8e6304fc05f` |
| `prompts/analyzer.md` | 248 | `b6fda6c2fa29117a28af249103688d4091e0b7404350965b00037b8ce73f1f4e` |
| `prompts/system.md` | 2229 | `fe441037e16b3fa23d7b38f16cdb6712a333dd5f1bdc18133eb4608db15d8c9e` |
| `sub_agents/code_analyzer.yaml` | 1297 | `49e18699b782458f51bed9988070cba77f296aa72be30878fb0b4e4abe96e1ee` |

## Проверка отказов валидатора

На временных копиях submission успешно отклонены **19** ошибочных вариантов:
duplicate key, missing include, parent traversal, absolute include, include cycle,
config_path cycle, unknown tool, mixed models, missing adapter, forbidden generation field,
output token overflow, negative thinking budget, unequal sampling, unsafe YAML tag,
YAML alias, multiple roots, forbidden extension, ровно предельный unpacked size,
попытка перезаписать существующий output.
Дополнительно отклонены **7** небезопасных строк пути.
Реальный submission при этих проверках не менялся; временные fixtures очищены.

## Изменённые файлы и ограничения

Созданы scripts/build_submission.py и этот отчёт; README дополнен командой и статусом,
pyproject.toml — dependency group. ZIP находится в ignored dist/.
Конфигурации, prompts и adapters не изменены. Commit/push и Kaggle upload не выполнялись.

Это **статическая проверка текущей v1**, не official compilation.
Официальный compiler отсутствует; harness, модель, runtime и Docker не запускались.
Совместимость adapters с реальной моделью, serving backend и качество решения задач не проверены.

Валидатор намеренно поддерживает ограниченный профиль v1: LlmAgent, ссылки config_path и directory LoRA adapters.
Другие agent classes, inline agent dictionaries, skills, YAML aliases/merge keys отклоняются консервативно,
хотя часть этих конструкций может поддерживаться official compiler.
Полная Pydantic/ADK schema, все registry semantics и все дополнительные ceilings README не воспроизводятся.
Ограничения token fields проверяются отдельно; фактическая длина runtime context не измеряется.
Безопасность/корректность кода в разрешённых .py файлах не оценивается и такой код не исполняется.
