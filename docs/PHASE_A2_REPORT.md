# PHASE A2 — агент v1

Дата: 2026-10-30 (Asia/Qyzylorda).
Проект: `D:\MyProjects\MyOwnProjects\ai_agent_gemma\kaggle`.
Основание: локальный `HARNESS_README.md` (§2.2, §3, §6, §7.1, §8.1, §10).
AGENTS.md в проверенных ancestor paths и дереве проекта (без .git/.venv) отсутствует.

## Изменения

- `submission/sub_agents/code_analyzer.yaml`: instruction и generate_content_config размещены inline; оба includes с parent traversal удалены. Analyzer сохранил только read-only tools: read_file, search_similar_code, get_code_neighbors, get_code_subgraph.
- Analyzer отвечает по четырём пунктам: paths/symbols с наблюдаемыми line numbers, причина или недостающее поведение, минимальное исправление, предлагаемая targeted проверка. При недостаточных graph results возвращает неопределённость и запрос на source search родителю; run_command ему не подключён.
- `submission/prompts/analyzer.md`: прежний prompt заменён коротким указателем на inline instruction. Файл не подключён ни одним agent; второй расходящийся prompt отсутствует.
- `submission/prompts/system.md`: краткий английский workflow для bug fixes и features. Требования извлекаются из содержательного текста PR, пустой шаблон игнорируется. Известные пути исследуются напрямую; analyzer вызывается при неясной локализации или межмодульных связях. Graph queries используют symbols, затем возможен source search через run_command.
- System prompt требует точечных edits, сохранения API/style, чтения и запуска targeted tests, различения implementation/environment failures, честного описания непроверенного, контроля бюджета через get_status и резервирования времени на проверку.
- Tests и protected runner configs перечислены по README §8.1 и запрещены к изменению. Reproduction scripts размещаются в /tmp через run_command. Установка пакетов и downloads запрещены для offline среды.
- Перед submission предписаны git diff/git status review и уборка собственных временных артефактов. submit_patch — последний tool action; затем только фактическое текстовое резюме.
- Удалены требования 8–10 ходов и непустых изменений любой ценой.

`submission/eval_config.yaml`:

```yaml
evaluation:
  timeout_seconds: 120
  max_tool_calls: 50
  max_time_minutes: 4
  max_turns: 80
```

## Что сохранено

`submission/agent.yaml` побайтно не изменён: root instruction → prompts/system.md, generate_content_config → configs/sampling.yaml, agent_tool → sub_agents/code_analyzer.yaml; skip_summarization остаётся true.
Модель обоих agents: **gemma-4-31b-it-qat-w4a16-ct**.
Adapters: root → main_lora, analyzer → tool_lora.

Исходный `configs/sampling.yaml` побайтно сохранён:
temperature=0.2, top_p=0.95, max_output_tokens=16384, thinking_budget=4096, include_thoughts=true.
Inline generate_content_config analyzer проверен на точное равенство разобранному исходному sampling mapping.
В дальнейшем два представления sampling потребуют синхронизации; в v1 значения одинаковы.

Все четыре adapter файла сохранены. Исходники `gemma4-data/sample_submission/` не менялись: SHA-256 всех 10 файлов соответствует исходному состоянию A1.
Стартовые uv-файлы, main.py и отчёт A1 не редактировались.

## Выполненные проверки

- Все 4 YAML разобраны установленным PyYAML SafeLoader с обработчиком !include как строкового reference; duplicate mapping keys не обнаружены.
- В submission ровно один root config: agent.yaml.
- Во всех YAML отсутствуют строки ../; во всех include/config_path references отсутствуют parent traversal components.
- Все 3 действующих references из root agent существуют внутри submission. Analyzer больше не содержит includes.
- Множество model declarations содержит ровно один alias; он входит в allowed aliases локального README.
- Adapter declarations соответствуют существующим директориям с config и weights.
- Read-only tool list analyzer и skip_summarization=true проверены.
- Evaluation mapping точно соответствует 120/50/4/80.
- Inline sampling равен original mapping; хеш исходного sampling совпадает.
- Root YAML и adapters проверены по SHA-256 до/после и против sample.
- Prompt analyzer существует только inline; оставшийся Markdown — указатель, а не runtime prompt.

| Reference в agent.yaml | Target существует |
|---|---|
| !include prompts/system.md | да |
| agent_tool.config_path: sub_agents/code_analyzer.yaml | да |
| !include configs/sampling.yaml | да |

## SHA-256 неизменённых файлов

Для каждого файла ниже хеш одинаков до A2, после A2 и в исходном sample.
Пути относительны к submission/ и sample_submission/.

| Файл | SHA-256 |
|---|---|
| `agent.yaml` | `c7fbbbbdc44778419be8e9f53a85800eeb17d0cf151e0846c46e107401b72034` |
| `configs/sampling.yaml` | `3dab0b2506dae34ce92fef7b380d6073729104b23fe2cf66d44ac1d2f213aa6a` |
| `adapters/main_lora/adapter_config.json` | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` |
| `adapters/main_lora/adapter_model.safetensors` | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` |
| `adapters/tool_lora/adapter_config.json` | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` |
| `adapters/tool_lora/adapter_model.safetensors` | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` |

## Ограничения

Официальный compiler **недоступен**: adk_submission и swegemma не обнаружены в системном Python и проектной .venv; swegemma отсутствует в PATH.
validate_directory, validate_single_declared_model и compile_submission не выполнялись.
Проверка YAML syntax и существования references не равнозначна official schema validation/compilation.

Загрузка модели, inference и evaluation не выполнялись. Полная runtime-совместимость adapters и качество v1 не подтверждены.
Новый budget не является измерением фактического времени решения; согласно README §7.1 participant evaluation config относится к Stage 1.
Runtime не устанавливался, Docker не запускался, ZIP не создавался, submission на Kaggle не отправлялся.
