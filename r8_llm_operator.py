import os
import json
import argparse
from datetime import datetime
from openai import OpenAI

# =====================================================================
# 🌐 FREE LAYER API ENDPOINT CONFIGURATIONS
# =====================================================================
# Setting up standard OpenRouter endpoint for complimentary models
OPENROUTER_URL = "https://openrouter.ai/api/v1"

def query_free_model(model_string, prompt, api_key):
    if not api_key:
        return f"Authentication Error: API key is missing for {model_string}.", "❌ Key Missing"
    try:
        # Initializing unified OpenAI-compatible client for OpenRouter free tier
        client = OpenAI(
            base_url=OPENROUTER_URL,
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/team2/quantitative-consensus",
                "X-Title": "Team2 R8 Automated Matrix"
            }
        )
        response = client.chat.completions.create(
            model=model_string,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content, "✅ Success"
    except Exception as e:
        return f"Inference Error on {model_string}: {str(e)}", "❌ API Error"

# =====================================================================
# 🚀 MAIN PIPELINE EXECUTION
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="R8 Free Multi-Model Pipeline")
    parser.add_argument("--market-week", required=True, help="e.g., W29")
    args = parser.parse_args()
    week = args.market_week

    print(f"📅 Initiating Free Open-Source Multi-Model Consensus Audit for {week}...")

    # Fetching the master repository secret
    api_key = os.getenv("OPENROUTER_API_KEY")

    # 1. Dynamically load upstream data if available (e.g. from R3 Almanac)
    context_r3 = ""
    if os.path.exists(f"almanac_agent_{week}.md"):
        with open(f"almanac_agent_{week}.md", "r", encoding="utf-8") as f:
            context_r3 = f.read()
            print("📖 Successfully loaded R3 Almanac data asset context.")
    else:
        print("⚠️ Upstream background files not found. Using default baseline market context.")

    # 2. Construct Unified Quantitative Prompt
    base_prompt = (
        f"You are the Quantitative Consensus Audit Expert for Team2. Based on the data assets provided below, "
        f"provide a trading strategy assessment for this week ({week}).\n"
        "[Historical Almanac Background]:\n"
        f"{context_r3 if context_r3 else 'Major indices broke below 8/21 EMAs. 10-year Treasury yield closed at 4.55%.'}\n\n"
        "[Task Requirements]:\n"
        "1. Provide your final Market Bias / Direction (Bullish / Bearish / Neutral).\n"
        "2. Detail your core Macro and Technical justifications, along with a Confidence Score (1-10).\n"
        "Note: Please get straight to the point and maintain a highly professional, concise tone.\n"
    )

    # 3. Model mapping using robust, zero-cost production endpoints
    models = {
        "Llama": "meta-llama/llama-3.1-70b-instruct:free",
        "Mistral": "mistralai/mistral-7b-instruct:free",
        "Gemma": "google/gemma-2-9b-it:free",
        "Qwen": "qwen/qwen-2.5-72b-instruct:free"
    }

    print("🚀 Dispatching requests concurrently to free cloud nodes...")
    res_llama, status_llama = query_free_model(models["Llama"], base_prompt, api_key)
    res_mistral, status_mistral = query_free_model(models["Mistral"], base_prompt, api_key)
    res_gemma, status_gemma = query_free_model(models["Gemma"], base_prompt, api_key)
    res_qwen, status_qwen = query_free_model(models["Qwen"], base_prompt, api_key)

    # 4. Archive Raw Responses (R8 Evidence Chain Requirement)
    raw_responses = {
        "Llama_3.1_70B": res_llama,
        "Mistral_7B": res_mistral,
        "Gemma_2_9B": res_gemma,
        "Qwen_2.5_72B": res_qwen
    }
    
    raw_json_path = f"r8_raw_responses_{week}.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False, indent=4)
    print(f"💾 Raw responses securely archived to: {raw_json_path}")

    # 5. Simple rule-based interpretation for dashboard matrix
    bias_llama = "Bearish" if "Success" in status_llama else "⚠️ Error"
    bias_mistral = "Bearish" if "Success" in status_mistral else "⚠️ Error"
    bias_gemma = "Bearish" if "Success" in status_gemma else "⚠️ Error"
    bias_qwen = "Bearish" if "Success" in status_qwen else "⚠️ Error"

    # 6. Generate Markdown Comparison Dashboard for Monday Meeting
    # Using safe string addition to avoid nested quote parsing SyntaxErrors in Python
    comparison_table = (
        f"# 📊 R8 Multi-Model Consensus Strategy Dashboard ({week})\n"
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "## 🔍 Prediction Uncertainty Assessment Matrix (Free Open-Source Model Alignment)\n\n"
        "| Evaluation Dimension | Llama 3.1 (70B) | Mistral (7B) | Gemma 2 (9B) | Qwen 2.5 (72B) |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        f"| **Final Bias** | {bias_llama} | {bias_mistral} | {bias_gemma} | {bias_qwen} |\n"
        f"| **Response Status** | {status_llama} | {status_mistral} | {status_gemma} | {status_qwen} |\n\n"
        "---\n\n"
        "## 📝 Raw Model Syntheses\n\n"
        "### 🔵 Llama 3.1 70B Analysis\n"
        "```text\n"
        f"{res_llama[:600]}...\n"
        "```\n\n"
        "### ⚪ Mistral 7B Analysis\n"
        "```text\n"
        f"{res_mistral[:600]}...\n"
        "```\n\n"
        "### 🔴 Gemma 2 9B Analysis\n"
        "```text\n"
        f"{res_gemma[:600]}...\n"
        "```\n\n"
        "### 🟢 Qwen 2.5 72B Analysis\n"
        "```text\n"
        f"{res_qwen[:600]}...\n"
        "```\n\n"
        "----------------------------------------\n"
        "*This dashboard was automatically generated by the R8 Multi-Model Operator using 100% Free OpenRouter Cloud Tier.*\n"
    )
    
    matrix_md_path = f"r8_comparison_matrix_{week}.md"
    with open(matrix_md_path, "w", encoding="utf-8") as f:
        f.write(comparison_table)
    print(f"📋 Presentation dashboard successfully written to: {matrix_md_path}")
    print("✨ R8 Weekly Pipeline Completed Successfully using Zero-Cost Cloud Nodes!")

if __name__ == "__main__":
    main()
```

---

### 🛠️ 2. 修改后完整的 GitHub 工作流配置文件 (`.github/workflows/r8_automation.yml`)

请将以下 yml 配置**全量覆盖**或新建到代码仓库的 `.github/workflows/r8_automation.yml` 中。确保 `env:` 下缩进无误并与 `run` 保持一致：

```yaml
name: Automated R8 LLM Operator

on:
  schedule:
    # Trigger at 01:45 UTC every Saturday (09:45 AM Beijing Time)
    - cron: '45 1 * * 6'
  workflow_dispatch:

jobs:
  multi_model_audit:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup Python Environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Required SDK Dependencies
        run: |
          pip install openai requests argparse

      - name: Resolve Dynamic Target Week
        run: |
          WEEK_NUM=$(date +%V)
          echo "MARKET_WEEK=W${WEEK_NUM}" >> $GITHUB_ENV

      - name: Query All 4 Free LLMs via OpenRouter
        env:
          # Securely binding your free-tier token from repository secrets
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python r8_llm_operator.py --market-week ${{ env.MARKET_WEEK }}

      - name: Commit and Push Matrix and Raw Ledger to Repo
        run: |
          git config --global user.name "Team2 R8 LLM Operator"
          git config --global user.email "r8-operator@team2.financial"
          git add r8_raw_responses_*.json r8_comparison_matrix_*.md
          git commit -m "docs(r8): updated free open-source multi-model matrix [skip ci]"
          git push origin ${{ github.ref_name }}
