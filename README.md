# 🔍 SQL Hallucination Detector

A **Streamlit** app powered by **GPT‑4** that:
- Generates SQL queries from natural language questions.
- Detects and prevents hallucinated SQL using trusted references.
- Tracks token usage (cost) for both generation & judgment.
- Visualizes confidence, hallucination rate, and cost metrics.

---

## 📌 Table of Contents
1. [Features](#️-features)  
2. [Installation & Setup](#installation--setup)  
3. [Configuration (Secrets)](#configuration-secrets)  
4. [Running the App](#running-the-app)  
5. [CSV File Format](#csv-file-format)  
6. [Usage Guide](#usage-guide)  
7. [Metrics & Visualization](#metrics--visualization)  
8. [Why It Matters](#why-it-matters)  
9. [Contributing](#contributing)  
10. [License](#license)  

---

## 🛠️ Features

- ✅ **GPT‑4 Judge**: Validates generated SQL against trusted SQL.
- 🎯 **Smart Fallback**: Uses CSV reference to avoid unnecessary generation.
- 💸 **Token Cost Tracking**: Captures prompt, completion, and total tokens using `get_openai_callback()`.
- 📊 **Visual Dashboard**: Interactive charts for confidence distribution, hallucination rate, and token usage.

---

## 🧰 Installation & Setup

```bash
git clone https://github.com/DineshBastin04/sql-hallucination-detector.git
cd sql-hallucination-detector
pip install -r requirements.txt
```

---

## 🔐 Configuration (Secrets)

Create a `.streamlit/secrets.toml` file in the project root:

```toml
OPENAI_API_KEY = "sk-YOUR_OPENAI_KEY"
```

> ⚠️ **Important**: Make sure `.streamlit/secrets.toml` is included in `.gitignore`.

Streamlit automatically reads this file and uses `st.secrets["OPENAI_API_KEY"]`.

---

## 🚀 Running the App

```bash
streamlit run streamlit_app.py
```

Once running, open `http://localhost:8501` in your browser.

---

## 📁 CSV File Format

Your CSV should contain the following columns:

| question                  | provided_sql                     |
|---------------------------|----------------------------------|
| How many active users?    | SELECT COUNT(*) FROM users;      |
| Total revenue by region?  | SELECT region, SUM(revenue) ...  |

- `question`: Text-based natural language query.
- `provided_sql`: Verified SQL used as a reference for judging hallucinations.

---

## 💻 Usage Guide

1. Upload the CSV containing natural language questions and reference SQL.
2. Enter a new question in the Streamlit UI.
3. Click **Generate SQL**:
   - If the CSV has a match, the reference is reused.
   - If not, GPT‑4 is called to generate the SQL.
   - GPT‑4 is then asked to **judge** if the generated SQL matches expected intent.
4. View the outputs:
   - Final SQL
   - Confidence score
   - Hallucination detection result
   - Token usage stats

---

## 📊 Metrics & Visualization

- **Confidence Distribution**: Histogram showing model’s confidence.
- **Hallucination Rate**: Tracks % of queries with hallucinations.
- **Token Metrics**: Displays cost via prompt/completion tokens for generation and judgment.
- **Per-Question Tokens**: Visual breakdown using stacked bar plots.

---

## 🤔 Why It Matters

- 💰 **Cost Transparency**: Know how many tokens (and dollars) you're using.
- ⚠️ **Hallucination Detection**: Helps avoid production errors from invalid SQL.
- 🧪 **Prompt Tuning**: Track which types of prompts perform best.
- 📈 **Auditable**: Ideal for LLMOps workflows, debugging, and dashboards.

---

## 🤝 Contributing

We welcome your contributions!

1. Fork the repo.
2. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes.
4. Push and create a Pull Request.

---


