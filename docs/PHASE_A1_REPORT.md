# PHASE A1 — подготовка структуры проекта

Дата: 2026-10-30 (Asia/Qyzylorda). Среда: Windows.
Корень: `D:\MyProjects\MyOwnProjects\ai_agent_gemma`.
Рабочий uv-project: `kaggle/`; источник sample: `gemma4-data/sample_submission/`.

## 1. Исходное состояние и выполненная подготовка

До изменений в `kaggle/` были `.git/`, `.venv/`, `.gitignore`, `.python-version`, `README.md`, `main.py`, `pyproject.toml`; `submission/` и этот отчёт отсутствовали.
Git показывал пять стартовых файлов как untracked. Существующие файлы uv и `main.py` сохранены.
`pyproject.toml`: project name `kaggle`, `requires-python = ">=3.13"`, `dependencies = []`.
`.python-version`: `3.13`; Python в существующей `.venv`: `3.13.5`.

Проверены `AGENTS.md` в ancestors от `D:/` до корня проекта, в `kaggle/`, `gemma4-data/`, а также рекурсивно в `kaggle/` (без .git/.venv) и `sample_submission/`: не найдены.
Прочитан родительский `HARNESS_README.md`; его копия в `gemma4-data/` имеет тот же SHA-256:
`445000219b803942c469391ec8b69791a31e9cec2f934738c767e34b5ca0aa1f`.
Все ссылки на README ниже относятся к этому локальному документу.

Созданы `submission/` (10 файлов, 442238 bytes), `scripts/`, `docs/`, `dist/` и этот отчёт.
Файлы sample скопированы побайтно, без декодирования/перезаписи текста. Существующие файлы назначения не перезаписывались.
Поведение агента не настраивалось.

`.gitignore` дополнен правилами `.venv/`, `/results/`, `/runs/`.
Исходные правила, включая `__pycache__/`, `dist/`, `.venv`, `build/`, `wheels/`, сохранены.
Локальные evaluation outputs предполагаются под `results/` (как в README §9.2) или `runs/`; произвольный другой `--results-dir` потребует отдельного правила.
`scripts/` и `dist/` пока пусты; Git не хранит пустые директории, `dist/` намеренно ignored.

## 2. Итоговая структура

```text
kaggle/
├── .git/                       # существующий repository
├── .venv/                      # существующая virtual environment, ignored
├── .gitignore                  # только добавлены правила
├── .python-version             # без изменений
├── pyproject.toml              # без изменений
├── main.py                     # без изменений
├── README.md                   # без изменений
├── scripts/                    # пустая
├── dist/                       # пустая, ignored
├── docs/
│   └── PHASE_A1_REPORT.md
└── submission/
    ├── agent.yaml
    ├── eval_config.yaml
    ├── configs/
    │   └── sampling.yaml
    ├── prompts/
    │   ├── system.md
    │   └── analyzer.md
    ├── sub_agents/
    │   └── code_analyzer.yaml
    └── adapters/
        ├── main_lora/
        │   ├── adapter_config.json
        │   └── adapter_model.safetensors
        └── tool_lora/
            ├── adapter_config.json
            └── adapter_model.safetensors
```

`skills/` в sample отсутствует; согласно README §2.2 это optional, каталог не добавлялся.
Новые scripts, model configs, ZIP и результаты evaluation не создавались.

## 3. Проверка YAML и references

Проверены все 4 YAML через уже установленный **PyYAML 6.0.3** в системном Python **3.14.0**, с `-B` (без записи bytecode).
Использован SafeLoader с обработчиком `!include`, который только сохраняет строку reference, не читает/не исполняет include.
Дополнительно проверено отсутствие duplicate mapping keys. Все 4 YAML синтаксически разобраны; unknown tags/duplicate keys не обнаружены.
Это не проверка official schema, не compilation и не воспроизведение compiler path policy.

| YAML | Результат |
|---|---|
| `agent.yaml` | Mapping; name/model/adapter и tools присутствуют |
| `sub_agents/code_analyzer.yaml` | Mapping; name/model/adapter и tools присутствуют |
| `configs/sampling.yaml` | Mapping; sampling и thinking config разобраны |
| `eval_config.yaml` | Mapping с `evaluation` и четырьмя budget fields |

В `submission/` ровно один допустимый root config: **`agent.yaml`**.
Все references проверены на существование обычного файла и на нахождение внутри submission.
Для filesystem check относительный путь разрешён **от директории YAML, содержащего reference**:

| Файл:строка | Тип | Строка reference | Нормализованный путь от submission | Файл существует |
|---|---|---|---|---|
| `agent.yaml:4` | `include` | `prompts/system.md` | `prompts/system.md` | да |
| `agent.yaml:16` | `config_path` | `sub_agents/code_analyzer.yaml` | `sub_agents/code_analyzer.yaml` | да |
| `agent.yaml:18` | `include` | `configs/sampling.yaml` | `configs/sampling.yaml` | да |
| `sub_agents/code_analyzer.yaml:5` | `include` | `../prompts/analyzer.md` | `prompts/analyzer.md` | да |
| `sub_agents/code_analyzer.yaml:11` | `include` | `../configs/sampling.yaml` | `configs/sampling.yaml` | да |

Reference graph конечен: root → analyzer; includes ведут в два prompts и общий sampling config. Циклов в этих references нет.
Оба adapter declarations разрешаются в существующие директории с JSON config и safetensors weights.

### Неоднозначность `../` в includes

`sub_agents/code_analyzer.yaml:5` и `:11` содержат `../prompts/analyzer.md` и `../configs/sampling.yaml`.
При указанном filesystem разрешении оба target находятся внутри submission и существуют.
Однако README:99–102 (§2.2) прямо утверждает, что `..` traversal components блокируются с `PathTraversalError`.
README также не уточняет однозначно базовый каталог разрешения всех relative paths.
Поэтому наличие файлов **не подтверждает**, что official compiler примет эти две строки.
Это потенциальный blocker compilation; sample сохранён без исправлений.

### Models, tools и параметры

Оба агента объявляют **один и тот же** alias `gemma-4-31b-it-qat-w4a16-ct`:
`agent.yaml:2` и `sub_agents/code_analyzer.yaml:3`.
Он входит в allowed competition aliases по README §3.1–3.2; других model declarations в YAML нет.
Это статическая сверка с локальной документацией, а не вызов `validate_single_declared_model`.

| Agent | Adapter | Tools |
|---|---|---|
| `swe_baseline_agent` | `main_lora` | `run_command`, `read_file`, `edit_file`, `write_file`, `get_status`, `submit_patch`, `get_code_neighbors`, `search_similar_code`, `get_code_subgraph`; `agent_tool` → analyzer, `skip_summarization: true` |
| `code_analyzer_agent` | `tool_lora` | `read_file`, `search_similar_code`, `get_code_neighbors`, `get_code_subgraph` |

Строковые tool names входят в девять tools из README §6; runtime registry bindings не проверялись.
Sampling: `temperature=0.2`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=4096`, `include_thoughts=true`.
Числовые ограничения sampling совпадают с диапазонами README §2.4.
Evaluation: `timeout_seconds=60`, `max_tool_calls=10`, `max_time_minutes=1`, `max_turns=50`; значения только прочитаны.

## 4. Адаптеры

Прочитаны оба `adapter_config.json` как JSON. Weights только скопированы и хешированы; модель и tensor payload не загружались.

| Параметр | main_lora | tool_lora |
|---|---|---|
| `base_model_name_or_path` | `google/gemma-4-31b-it-qat-w4a16-ct` | `google/gemma-4-31b-it-qat-w4a16-ct` |
| Rank `r` | 4 | 4 |
| `target_modules` | `["q_proj", "o_proj"]` | `["q_proj", "o_proj"]` |
| `layers_to_transform` | `[0]` | `[0]` |
| `lora_alpha` | 8 | 8 |
| `peft_type` / `task_type` | `LORA` / `CAUSAL_LM` | `LORA` / `CAUSAL_LM` |
| JSON config bytes | 664 | 664 |
| `adapter_model.safetensors` bytes | 217672 (212.5703125 KiB) | 217672 (212.5703125 KiB) |

Base model names декларативно согласованы с alias обоих агентов.
JSON configs двух adapters имеют одинаковый SHA-256; weights двух adapters также имеют одинаковый SHA-256.
Нельзя по именам, небольшому размеру или hash equality подтвердить пригодность, качество или совместимость с quantized model/vLLM/PEFT.
Tensor shapes, реальные model modules, loading и inference не проверялись.

## 5. SHA-256 источников и копий

Пути в первом столбце относительны одновременно к `gemma4-data/sample_submission/` и `kaggle/submission/`.
Источник хеширован до копирования и повторно после; хеш копии рассчитан отдельно.
Все **10/10** файлов совпадают; итоговый набор путей source/destination одинаков; суммарно **442238 bytes** с каждой стороны.

| Относительный путь | Bytes | SHA-256 source | SHA-256 copy | Результат |
|---|---:|---|---|---|
| `adapters/main_lora/adapter_config.json` | 664 | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` | MATCH |
| `adapters/main_lora/adapter_model.safetensors` | 217672 | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` | MATCH |
| `adapters/tool_lora/adapter_config.json` | 664 | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` | `75a46da2db7f3c70442e5c728f64059aff52cf64174cee7aeb3a4ec37f6e78fb` | MATCH |
| `adapters/tool_lora/adapter_model.safetensors` | 217672 | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` | `dcbedd989af34f5201a39606e0bd4014d351a29162dd96da418782cbbe487ad9` | MATCH |
| `agent.yaml` | 438 | `c7fbbbbdc44778419be8e9f53a85800eeb17d0cf151e0846c46e107401b72034` | `c7fbbbbdc44778419be8e9f53a85800eeb17d0cf151e0846c46e107401b72034` | MATCH |
| `configs/sampling.yaml` | 120 | `3dab0b2506dae34ce92fef7b380d6073729104b23fe2cf66d44ac1d2f213aa6a` | `3dab0b2506dae34ce92fef7b380d6073729104b23fe2cf66d44ac1d2f213aa6a` | MATCH |
| `eval_config.yaml` | 232 | `adb486b67535fa59b427b79d44dafc131176f1f1964d184e16046ed520ede02d` | `adb486b67535fa59b427b79d44dafc131176f1f1964d184e16046ed520ede02d` | MATCH |
| `prompts/analyzer.md` | 527 | `c762b062032cc8463015e589ad8b4f0e17296062e1b0ff1e78712eef9f5e2d43` | `c762b062032cc8463015e589ad8b4f0e17296062e1b0ff1e78712eef9f5e2d43` | MATCH |
| `prompts/system.md` | 3888 | `f1cbf7943ee9687382321b1dfd9cd88581d608c1c8b8e6ea61a763bd1a3234af` | `f1cbf7943ee9687382321b1dfd9cd88581d608c1c8b8e6ea61a763bd1a3234af` | MATCH |
| `sub_agents/code_analyzer.yaml` | 361 | `7a764798e36cc68aa38900256245e4aed969b5439b992c7da4105b6ebcb7e62b` | `7a764798e36cc68aa38900256245e4aed969b5439b992c7da4105b6ebcb7e62b` | MATCH |

Исходные `.python-version`, `README.md`, `main.py`, `pyproject.toml` дополнительно проверены по SHA-256 до/после — без изменений.
Исходное содержимое `.gitignore` сохранено как неизменный byte prefix; правила только дописаны.

## 6. Границы проверки и неизвестное

- `adk_submission` и `swegemma` не найдены ни в системном Python, ни в проектной `.venv`; `swegemma` отсутствует в PATH.
- **Official validation/compilation не выполнялась**: `validate_directory`, `validate_single_declared_model`, `compile_submission` недоступны в проверенных environments. Пакеты не устанавливались.
- Синтаксис YAML, наличие путей, static model/tool declarations и SHA-256 проверены; это не означает принятие submission scorer.
- Два `../` include требуют сверки с фактической версией compiler. Неоднозначность сохранена для следующего этапа.
- Совместимость adapters с base model и serving backend не установлена; model download/loading и inference отсутствовали.
- Вне scope: поведение/prompts/budgets, качество решения задач, local eval, Docker, упаковка ZIP, Kaggle upload и git push. Эти операции не выполнялись.
