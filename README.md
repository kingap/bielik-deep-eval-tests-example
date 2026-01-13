# BielikDeepEvalTestsExample — Evals (PL / EN)

Repozytorium zawiera lokalne testy ewaluacyjne (rules/golden/judge) dla modeli LLM uruchamianych przez **Ollama** i ocenianych przez **DeepEval**.

This repository contains local evaluation tests (rules/golden/judge) for LLMs running via **Ollama** and evaluated with **DeepEval**.


- [PL 🇵🇱 — Ewaluacje (rules / golden / judge)](#pl--ewaluacje-rules--golden--judge)
- [EN 🇬🇧 — Evals (rules / golden / judge)](#en--evals-rules--golden--judge)

---

# PL 🇵🇱 — Ewaluacje (rules / golden / judge)

Ten katalog zawiera zestaw testów ewaluacyjnych dla modelu językowego (LLM), przygotowany tak, aby:

- był **łatwy do uruchomienia lokalnie** (CPU-only też działa),
- miał **czytelne raporty HTML** (prompt + output modelu),
- wspierał **CI/CD** (JSON report),
- dało się nad nim pracować zespołowo (cases w `.jsonl`, łatwe PR-y).

---

## Jak to działa?

Wspieramy 3 typy testów:

### 1) **Rules tests** (`rules.jsonl`)
Szybkie, deterministyczne sprawdzenia oparte o reguły (`must_contain_any`, `must_not_contain_any`).

✅ Najlepsze dla:
- krótkich, jednoznacznych promptów,
- testów regresji,
- sytuacji gdzie wynik musi zawierać konkretne słowo/frazę.

---

### 2) **Golden tests** (`golden.jsonl`)
Porównanie outputu modelu do odpowiedzi wzorcowej (token F1).

✅ Najlepsze dla:
- krótkich/średnich odpowiedzi, które mogą być parafrazą,
- testów poprawności treści bez potrzeby judge.

---

### 3) **Judge tests** (`judge.jsonl`)
LLM-as-a-judge (DeepEval): model ocenia model.

✅ Najlepsze dla:
- złożonych scenariuszy,
- wieloetapowego rozumowania,
- odpowiedzi jakościowych/subiektywnych.

⚠️ Wolniejsze, zależne od jakości modelu judge (musi trzymać format/JSON).

---

## Struktura katalogów

Datasety są uporządkowane wg **test setów** (kategorii):

```
evals/
  datasets/
    common_sense/
      rules.jsonl
      golden.jsonl
      judge.jsonl
    polish_context/
      rules.jsonl
      golden.jsonl
```

Testy są generyczne i automatycznie znajdują datasety:

```
evals/tests/
  test_rules_all.py
  test_golden_all.py
  test_judge_all.py
  conftest.py
```

Raporty zapisują się do:

```
evals/reports/
```

---

## Wymagania

- Python 3.11+ (rekomendowane)
- Ollama: https://ollama.com/

Testowany model działa lokalnie przez OpenAI-compatible endpoint:
- `http://localhost:11434/v1`

---

## Setup

### 1) Virtualenv

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

---

### 2) Konfiguracja `.env`

Utwórz `.env` w root repo:

```env
# Ollama OpenAI-compatible endpoint
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama

# Model testowany (SUT)
OLLAMA_MODEL=SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M

# Model judge (zalecane: mały, szybki, dobry w JSON)
OLLAMA_JUDGE_MODEL=phi3:mini

# Timeout dla DeepEval (sekundy)
DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE=300
```

---

## Uruchamianie testów (zalecane)

Uruchamiaj przez runner:

```bash
python -m evals.run_tests
```

Tworzy raporty:
- `evals/reports/pytest_report_*.html`
- `evals/reports/pytest_report_*.json`
- `evals/reports/latest_*.html/json`

✅ HTML zawiera logi (prompt + output).

---

## Najczęstsze komendy

### Szybkie testy (rules + golden)
```bash
python -m evals.run_tests --fast
```

### Wszystkie testy dla jednego setu (rules + golden + judge)
```bash
python -m evals.run_tests common_sense
```

### Jeden set, szybko (rules + golden)
```bash
python -m evals.run_tests common_sense --fast
```

---

## Uruchamianie konkretnych test setów

### Tylko rules dla danego setu
```bash
python -m evals.run_tests common_sense --rules
```

### Golden + judge dla danego setu
```bash
python -m evals.run_tests common_sense --golden --judge
```

### Kilka setów naraz
```bash
python -m evals.run_tests common_sense extraction --rules
```

---

## Uruchamianie wg typu (dla wszystkich setów)

### Wszystkie rules
```bash
python -m evals.run_tests --rules
```

### Wszystkie golden
```bash
python -m evals.run_tests --golden
```

### Wszystkie judge
```bash
python -m evals.run_tests --judge
```

---

## Wszystkie testy pytest (bez filtrów)

Jeśli chcesz uruchomić absolutnie wszystko, co pytest wykryje w `evals/tests`:

```bash
python -m evals.run_tests --all-tests
```

To przydaje się, jeśli w repo pojawią się dodatkowe testy poza “eval suites”.

---

## Uruchamianie bez runnera (pytest bezpośrednio)

### Bash (Linux/macOS/Git Bash)
```bash
mkdir -p evals/reports

pytest -vv --capture=tee-sys -rA \
  --json-report --json-report-file=evals/reports/all.json \
  --html=evals/reports/all.html --self-contained-html
```

### PowerShell (Windows)
```powershell
New-Item -ItemType Directory -Force evals\\reports | Out-Null

pytest -vv --capture=tee-sys -rA `
  --json-report --json-report-file=evals\\reports\\all.json `
  --html=evals\\reports\\all.html --self-contained-html
```

---

## Dodawanie nowego test setu (kategorii)

1) Utwórz folder:
```
evals/datasets/<nazwa_setu>/
```

2) Dodaj pliki:
- `rules.jsonl`
- `golden.jsonl`
- `judge.jsonl` (opcjonalnie)

Przykłady:

**`evals/datasets/common_sense/rules.jsonl`**
```jsonl
{"id":"cs_01","input":"Pada deszcz. Co zabierasz?","must_contain_any":["parasol"]}
```

**`evals/datasets/common_sense/golden.jsonl`**
```jsonl
{"id":"cs_g_01","input":"Po co lodówka?","expected":"Aby dłużej utrzymać świeżość jedzenia.","f1_threshold":0.35}
```

**`evals/datasets/common_sense/judge.jsonl`**
```jsonl
{"id":"cs_j_01","input":"Wyjaśnij, dlaczego pasy w aucie są ważne.","notes":"Should emphasize safety"}
```

3) Odpal:
```bash
python -m evals.run_tests <nazwa_setu>
```

✅ Nie trzeba dodawać nowych plików `.py` — runner sam znajdzie dataset.

---

---

# EN 🇬🇧 — Evals (rules / golden / judge)

This folder contains evaluation tests for an LLM (large language model) designed to be:

- **easy to run locally** (CPU-only supported),
- **human-reviewable** via HTML reports (prompt + output),
- **CI/CD friendly** via JSON reports,
- **easy to collaborate on** (test cases are stored in `.jsonl`, PR-friendly).

---

## How it works

We support 3 test types:

### 1) **Rules tests** (`rules.jsonl`)
Fast deterministic checks based on rules (`must_contain_any`, `must_not_contain_any`).

✅ Best for:
- short unambiguous prompts,
- regression checks,
- cases where output must contain a specific keyword/phrase.

---

### 2) **Golden tests** (`golden.jsonl`)
Compare model output to a reference answer using similarity scoring (token F1).

✅ Best for:
- short–medium answers where paraphrasing is expected,
- correctness checks without needing a judge LLM.

---

### 3) **Judge tests** (`judge.jsonl`)
LLM-as-a-judge (DeepEval): a separate model evaluates the model output.

✅ Best for:
- complex scenarios,
- multi-step reasoning,
- qualitative/subjective answers.

⚠️ Slower, and requires a judge model that follows strict structured/JSON outputs.

---

## Directory structure

Datasets are grouped by **test sets** (categories):

```
evals/
  datasets/
    common_sense/
      rules.jsonl
      golden.jsonl
      judge.jsonl
    polish_context/
      rules.jsonl
      golden.jsonl
```

Generic tests discover datasets automatically:

```
evals/tests/
  test_rules_all.py
  test_golden_all.py
  test_judge_all.py
  conftest.py
```

Reports are saved under:

```
evals/reports/
```

---

## Requirements

- Python 3.11+ (recommended)
- Ollama: https://ollama.com/

We run the model locally through an OpenAI-compatible endpoint:
- `http://localhost:11434/v1`

---

## Setup

### 1) Create a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

---

### 2) Configure `.env`

Create `.env` in repo root:

```env
# Ollama OpenAI-compatible endpoint
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama

# Model under test (SUT)
OLLAMA_MODEL=SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M

# Judge model (recommended: small + fast + JSON-friendly)
OLLAMA_JUDGE_MODEL=phi3:mini

# DeepEval timeout (seconds)
DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE=300
```

---

## Running tests (recommended)

Use the project runner:

```bash
python -m evals.run_tests
```

It generates:
- `evals/reports/pytest_report_*.html`
- `evals/reports/pytest_report_*.json`
- `evals/reports/latest_*.html/json`

✅ HTML reports include captured logs (prompt + output).

---

## Most common commands

### Fast tests (rules + golden)
```bash
python -m evals.run_tests --fast
```

### All tests for a single set (rules + golden + judge)
```bash
python -m evals.run_tests common_sense
```

### Single set, fast (rules + golden)
```bash
python -m evals.run_tests common_sense --fast
```

---

## Running specific test sets

### Rules only for a test set
```bash
python -m evals.run_tests common_sense --rules
```

### Golden + judge only
```bash
python -m evals.run_tests common_sense --golden --judge
```

### Multiple sets
```bash
python -m evals.run_tests common_sense extraction --rules
```

---

## Running by type across all sets

### Run all rules
```bash
python -m evals.run_tests --rules
```

### Run all golden
```bash
python -m evals.run_tests --golden
```

### Run all judge
```bash
python -m evals.run_tests --judge
```

---

## Run ALL pytest tests (no filtering)

If you want to run *everything* pytest discovers under `evals/tests`:

```bash
python -m evals.run_tests --all-tests
```

Useful if the repository grows additional test files outside the eval suites.

---

## Running without runner (direct pytest)

### Bash (Linux/macOS/Git Bash)
```bash
mkdir -p evals/reports

pytest -vv --capture=tee-sys -rA \
  --json-report --json-report-file=evals/reports/all.json \
  --html=evals/reports/all.html --self-contained-html
```

### PowerShell (Windows)
```powershell
New-Item -ItemType Directory -Force evals\\reports | Out-Null

pytest -vv --capture=tee-sys -rA `
  --json-report --json-report-file=evals\\reports\\all.json `
  --html=evals\\reports\\all.html --self-contained-html
```

---

## Adding a new test set (category)

1) Create a folder:
```
evals/datasets/<set_name>/
```

2) Add dataset files:
- `rules.jsonl`
- `golden.jsonl`
- `judge.jsonl` (optional)

Examples:

**`evals/datasets/common_sense/rules.jsonl`**
```jsonl
{"id":"cs_01","input":"It is raining. What should you take?","must_contain_any":["umbrella"]}
```

**`evals/datasets/common_sense/golden.jsonl`**
```jsonl
{"id":"cs_g_01","input":"Why do people use fridges?","expected":"To keep food fresh longer and slow down spoilage.","f1_threshold":0.35}
```

**`evals/datasets/common_sense/judge.jsonl`**
```jsonl
{"id":"cs_j_01","input":"Explain why seatbelts matter.","notes":"Should emphasize safety"}
```

3) Run:
```bash
python -m evals.run_tests <set_name>
```

✅ No new `.py` files needed — tests are discovered automatically.