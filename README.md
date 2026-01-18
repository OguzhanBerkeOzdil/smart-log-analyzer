# Smart Log Analyzer

![CI Pipeline](https://github.com/OguzhanBerkeOzdil/smart-log-analyzer/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

A high-performance, type-safe log analysis tool designed to process server logs, aggregate error patterns, and identify performance bottlenecks. Built for the **Advanced Python Programming** course, this project demonstrates modern software engineering practices, including strict static analysis, automated CI/CD and Generative AI integration.

## 🛠️ Tech Stack

* **Core**: Python 3.12+, Pydantic
* **Project Management**: `uv`
* **AI**: Google Generative AI SDK
* **Testing & Quality**: Pytest, Black, MyPy, Pyright, Pre-commit
* **CI/CD**: GitHub Actions

---

## 📦 Installation

This project uses `uv` for dependency management.

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/OguzhanBerkeOzdil/smart-log-analyzer.git](https://github.com/OguzhanBerkeOzdil/smart-log-analyzer.git)
   cd smart-log-analyzer
   ```
2. **Install dependencies:**

   ```bash
   uv sync
   ```
3. **Set up the environment:**
   Create a `.env` file (or export variables directly) for AI features:

   ```bash
   export GEMINI_API_KEY="your_google_api_key_here"
   ```

---

## 💻 Usage

Run the analyzer via the command line interface. The entry point is managed by `uv`.

### Basic Analysis

Analyze a local log file and print a textual report:

```bash
uv run python -m smart_log_analyzer.cli data/synthetic_logs.jsonl
```

### AI Debugging ModeAutomatically ask Google Gemini to explain the most frequent error found in the logs:

```bash
uv run python -m smart_log_analyzer.cli data/synthetic_logs.jsonl --ai
```

### Options

* `--limit N`: Show top N slowest requests (default: 10).
* `--ai`: Enable AI-driven error explanation.

---

## 🧪 Development Workflow

This project enforces strict code quality standards. Ensure you run the local quality gates before pushing code.

### 1. The Makefile (Shortcut)

We provide a `Makefile` to automate common tasks.

* **Run everything (Format, Check, Test):**

```bash
make all
```

* **Run only tests:**

```bash
make test
```

* **Format code:**

```bash
make format
```

### 2. Pre-commit Hooks

This project uses Git hooks to prevent bad commits. Install them once:

```bash
uv run pre-commit install
```

Now, every `git commit` will automatically run **Black** (formatting) and **MyPy** (type checking).

### 3. Running Tests Manually

```bash
# Unit & Integration tests
uv run pytest -v
```

---
