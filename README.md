# 🔍 SQL Hallucination Detector

A Streamlit app using GPT‑4 to generate SQL, detect hallucinations, track token usage, and optimize cost.

## Features

- ✅ Uses GPT‑4 as judge to validate generated SQL vs provided reference  
- 🎯 Looks up CSV‑provided SQL to avoid redundant generation  
- 💸 Tracks token usage for both generation and judging via `get_openai_callback()`  
- 📊 Interactive plots: confidence distribution, hallucination rate, token usage breakdown

## Installation

```bash
git clone https://github.com/DineshBastin04/sql-hallucination-detector.git
cd sql-hallucination-detector
pip install -r requirements.txt
