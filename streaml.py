import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from langchain_openai import ChatOpenAI
import os
from langchain_community.callbacks.manager import get_openai_callback

# ➤ Streamlit UI setup
st.set_page_config("SQL Hallucination Detector")
st.title("🔍 SQL Hallucination Detector")

threshold = st.sidebar.slider("Confidence threshold", 0.0, 1.0, 0.85)
upload = st.sidebar.file_uploader("Upload Q‑SQL CSV", type="csv")
st.write("Loaded secrets keys:", list(st.secrets.keys()))

# ➤ Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.0,
    openai_api_key=st.secrets["OPENAI_API_KEY"]
)
st.write("✅ GPT-4 Initialized as Judge")

if upload:
    df = pd.read_csv(upload)
    st.sidebar.success(f"Loaded {len(df)} examples")

    if "metrics" not in st.session_state:
        st.session_state.metrics = []

    examples = df.sample(min(5, len(df))).to_dict('records')
    prompt_examples = "\n\n".join(f"Q: {e['question']}\nSQL: {e['provided_sql']}" for e in examples)

    async def judge_llm_generated_sql(question, gen_sql, reference_sql):
        judge_prompt = f"""You are a strict SQL evaluator. Compare the following two SQL queries for the same question. Determine if the second one is a hallucination.

Question: {question}

Reference SQL:
{reference_sql}

Generated SQL:
{gen_sql}

Respond with only one word: "Yes" if the generated SQL is a hallucination, "No" if it is correct."""
        with get_openai_callback() as cb:
            judge_result = await llm.apredict(judge_prompt)
            token_usage = {
                "judge_prompt_tokens": cb.prompt_tokens,
                "judge_completion_tokens": cb.completion_tokens,
                "judge_total_tokens": cb.total_tokens
            }
        hallucinated = "yes" in judge_result.lower()
        confidence = 1.0 - threshold if hallucinated else 1.0
        return hallucinated, confidence, token_usage

    async def generate_and_judge(question):
        matched = df[df["question"].str.strip().str.lower() == question.strip().lower()]
        reference_sql = matched["provided_sql"].iloc[0] if not matched.empty else None

        prompt = f"Examples:\n{prompt_examples}\n\nNow SQL for:\nQ: {question}\nSQL:"
        with get_openai_callback() as cb:
            generated_sql = await llm.apredict(prompt)
            gen_token_usage = {
                "gen_prompt_tokens": cb.prompt_tokens,
                "gen_completion_tokens": cb.completion_tokens,
                "gen_total_tokens": cb.total_tokens
            }
        generated_sql = generated_sql.strip()

        if reference_sql:
            hallucinated, confidence, judge_token_usage = await judge_llm_generated_sql(question, generated_sql, reference_sql)
            token_usage = {**gen_token_usage, **judge_token_usage}
        else:
            hallucinated, confidence = False, 1.0  # Assume valid if no reference
            token_usage = {**gen_token_usage, 
                          "judge_prompt_tokens": 0,
                          "judge_completion_tokens": 0,
                          "judge_total_tokens": 0}

        # Calculate totals
        token_usage["total_tokens"] = token_usage["gen_total_tokens"] + token_usage["judge_total_tokens"]
        
        return generated_sql, confidence, hallucinated, reference_sql, token_usage

    st.header("Ask a question")
    question = st.text_input("Enter your question")

    if st.button("Generate SQL") and question:
        gen_sql, conf, hallucinated, reference_sql, token_usage = asyncio.run(generate_and_judge(question))

        st.write("**Generated SQL:**", gen_sql)
        st.write("**Confidence:**", f"{conf:.2f}")
        st.write("**Hallucination detected?**", hallucinated)
        st.write("**Reference SQL (if available):**", reference_sql if reference_sql else "None")
        final_sql = reference_sql if hallucinated and reference_sql else gen_sql
        st.write("**SQL used:**", final_sql)
        
        # Display token usage
        st.subheader("Token Usage")
        col1, col2, col3 = st.columns(3)
        col1.metric("Generation Tokens", token_usage["gen_total_tokens"])
        col2.metric("Judging Tokens", token_usage["judge_total_tokens"])
        col3.metric("Total Tokens", token_usage["total_tokens"])

        st.session_state.metrics.append({
            "question": question,
            "confidence": conf,
            "hallucinated": hallucinated,
            "used_fallback": bool(hallucinated and reference_sql),
            **token_usage
        })

    if st.session_state.metrics:
        st.header("Metrics Overview")
        rec = pd.DataFrame(st.session_state.metrics)
        
        # Display token metrics
        st.subheader("Token Usage Statistics")
        token_cols = st.columns(3)
        token_cols[0].metric("Avg Generation Tokens", int(rec["gen_total_tokens"].mean()))
        token_cols[1].metric("Avg Judging Tokens", int(rec["judge_total_tokens"].mean()))
        token_cols[2].metric("Avg Total Tokens", int(rec["total_tokens"].mean()))
        
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Confidence Distribution")
            fig, ax = plt.subplots()
            ax.hist(rec["confidence"], bins=10, color='skyblue', edgecolor='black')
            ax.axvline(threshold, color="red", linestyle="--", label="Threshold")
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Frequency")
            ax.legend()
            st.pyplot(fig)

        with c2:
            st.subheader("Hallucination Rate")
            fig2, ax2 = plt.subplots()
            halluc_counts = rec["hallucinated"].value_counts()
            ax2.bar(["No Hallucination", "Hallucinated"],
                    [halluc_counts.get(False, 0), halluc_counts.get(True, 0)],
                    color=["green", "red"])
            ax2.set_ylabel("Count")
            st.pyplot(fig2)
            
        # Add token usage plot
        st.subheader("Token Usage Over Questions")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        rec.plot(y=["gen_total_tokens", "judge_total_tokens", "total_tokens"], 
                kind='bar', stacked=True, ax=ax3)
        ax3.set_xlabel("Question Index")
        ax3.set_ylabel("Tokens")
        ax3.set_title("Token Usage Breakdown")
        ax3.legend(["Generation", "Judging", "Total"])
        st.pyplot(fig3)
else:
    st.info("Upload a CSV with `question` and `provided_sql` columns")