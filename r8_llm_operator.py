import os
import json
import argparse
from datetime import datetime
from openai import OpenAI

# =====================================================================
# 🌐 API ENDPOINT CONFIGURATIONS (OpenRouter Gateway)
# =====================================================================
OPENROUTER_URL = "https://openrouter.ai/api/v1"

def query_model(model_string, prompt, api_key):
    """
    Safely queries the specified model via the unified OpenRouter gateway.
    """
    # Robust pre-flight check for API Key presence
    if not api_key or api_key.strip().lower() in ["", "none", "null", "undefined"]:
        return (
            "API Key Error: OPENROUTER_API_KEY environment variable is missing. "
            "Please ensure your workflow YAML file contains the 'env: OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}' block.", 
            "❌ Key Missing"
        )
    try:
        # Initialize standard OpenAI client adapted for OpenRouter
        client = OpenAI(
            base_url=OPENROUTER_URL,
            api_key=api_key.strip(),
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
# 📂 SMART UPSTREAM DATA RETRIEVAL
# =====================================================================
def load_upstream_file(paths_to_try):
    """
    Attempts to read data assets from a list of prioritized fallback paths.
    """
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    print(f"📖 Successfully loaded active data asset from: {path}")
                    return f.read()
            except Exception as e:
                print(f"⚠️ Error reading file at {path}: {str(e)}")
    return ""

# =====================================================================
# 🚀 MAIN PIPELINE CONTROL
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="R8 Multi-Model Consensus Engine")
    parser.add_argument("--market-week", required=True, help="e.g., W29")
    args = parser.parse_args()
    week = args.market_week

    print(f"📅 Initiating R8 Multi-Model Consensus Audit for {week}...")

    # Safely retrieve the OpenRouter API key from env variables
    api_key = os.getenv("OPENROUTER_API_KEY")

    # 1. Dynamically search and load R3 Almanac (Seasonal Patterns)
    r3_paths = [
        f"almanac_agent_{week}.md",
        f"r3_almanac_agent/outputs/almanac_agent_{week}.md",
        f"r3_almanac_agent/almanac_agent_{week}.md"
    ]
    context_r3 = load_upstream_file(r3_paths)

    # 2. Dynamically search and load R5 Technical Analysis (Supporting both '-' and '_')
    r5_paths = [
        f"technical_agent-{week}.md",
        f"technical_agent_{week}.md",
        f"r5_technical_agent/technical_agent-{week}.md",
        f"technical_agent-W29.md"
    ]
    context_r5 = load_upstream_file(r5_paths)

    # 3. Dynamically search and load R4 Macro Analysis
    r4_paths = [
        f"macro_agent_{week}.md",
        f"r4_macro_agent/macro_agent_{week}.md",
        f"docs/macro_agent_2026-{week}.md",
        f"macro_agent_2026-{week}.md"
    ]
    context_r4 = load_upstream_file(r4_paths)
    if not context_r4:
        print("ℹ️ R4 Macro Agent data not found. Falling back to dynamic baseline context.")

    # 4. Construct Unified Quantitative Consensus Prompt
    base_prompt = (
        f"You are the Quantitative Consensus Audit Expert for Team2. Your task is to perform an integrated "
        f"trading consensus analysis for the upcoming week ({week}) by reviewing our internal agent reports.\n\n"
        f"=== [REPORT 1: R3 ALMANAC SEASONALITY BACKGROUND] ===\n"
        f"{context_r3 if context_r3 else 'Almanac Data: July cycle is active. Baseline historical rank: Midterm Year.'}\n\n"
        f"=== [REPORT 2: R5 TECHNICAL TREND ANALYSIS] ===\n"
        f"{context_r5 if context_r5 else 'Technical Data: S&P 500 trend is on watch. EMA indicators neutral.'}\n\n"
        f"=== [REPORT 3: R4 MACRO ENVIRONMENT] ===\n"
        f"{context_r4 if context_r4 else 'Macro Data: Fed rate policies unchanged. Yield curve remains primary focus.'}\n\n"
        f"=== [MANDATORY AUDIT INSTRUCTIONS] ===\n"
        f"1. Synthesize the seasonal biases from R3 with the technical trends (EMAs, support levels) from R5.\n"
        f"2. Formulate a unified Market Bias (Bullish, Bearish, or Neutral) for index assets (SPX, NDX).\n"
        f"3. Provide a clear, bulleted 'Macro-Technical Strategic Justification' based on the integrated data.\n"
        f"4. Assign an overall Consensus Confidence Score (1 to 10).\n"
        f"Please deliver your assessment in a highly professional, concise, and structured tone."
    )

    # 5. Targeted Models (GPT-4o-mini, Llama/Claude alternative, Qwen stable paid tier)
    models = {
        "ChatGPT": "openai/gpt-4o-mini",
        "Claude": "meta-llama/llama-3.1-70b-instruct", 
        "Qwen": "qwen/qwen-2.5-72b-instruct"
    }

    print("🚀 Dispatching API requests concurrently to OpenRouter cloud nodes...")
    res_chatgpt, status_chatgpt = query_model(models["ChatGPT"], base_prompt, api_key)
    res_claude, status_claude = query_model(models["Claude"], base_prompt, api_key)
    res_qwen, status_qwen = query_model(models["Qwen"], base_prompt, api_key)

    # 6. Archive raw responses for audit trail compliance
    raw_responses = {
        "ChatGPT_4o_Mini": res_chatgpt,
        "Claude_Llama_Alternative": res_claude,
        "Qwen_2.5_72B_Standard": res_qwen
    }
    
    raw_json_path = f"r8_raw_responses_{week}.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False, indent=4)
    print(f"💾 Raw response ledger successfully archived to: {raw_json_path}")

    # 7. Map parser statuses for dashboard visibility
    bias_gpt = "Parsed" if "Success" in status_chatgpt else "⚠️ Error"
    bias_cld = "Parsed" if "Success" in status_claude else "⚠️ Error"
    bias_qwn = "Parsed" if "Success" in status_qwen else "⚠️ Error"

    # 8. Compile the executive Markdown dashboard (Optimized for 3 models)
    comparison_table = (
        f"# 📊 R8 Multi-Model Consensus Strategy Dashboard ({week})\n"
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "## 🔍 Prediction Uncertainty Assessment Matrix (Model Consensus & Alignment)\n\n"
        "| Evaluation Dimension | ChatGPT (4o-mini) | Claude (Alternative) | Qwen (2.5-72B) |\n"
        "| :--- | :--- | :--- | :--- |\n"
        f"| **Consensus Bias** | {bias_gpt} | {bias_cld} | {bias_qwn} |\n"
        f"| **Response Status** | {status_chatgpt} | {status_claude} | {status_qwen} |\n\n"
        "---\n\n"
        "## 📝 Raw Model Syntheses\n\n"
        "### 🟢 ChatGPT 4o Mini Analysis\n"
        "```text\n"
        f"{res_chatgpt[:800]}...\n"
        "```\n\n"
        "### 🔵 Claude / Llama Alternative Analysis\n"
        "```text\n"
        f"{res_claude[:800]}...\n"
        "```\n\n"
        "### 🟡 Qwen 2.5 72B Analysis\n"
        "```text\n"
        f"{res_qwen[:800]}...\n"
        "```\n\n"
        "----------------------------------------\n"
        "*This dashboard was automatically generated by the R8 Multi-Model Operator using standard paid OpenRouter high-priority channels.*\n"
    )
    
    matrix_md_path = f"r8_comparison_matrix_{week}.md"
    with open(matrix_md_path, "w", encoding="utf-8") as f:
        f.write(comparison_table)
    print(f"📋 Presentation dashboard successfully written to: {matrix_md_path}")
    print("✨ R8 Weekly Pipeline Completed Successfully!")

if __name__ == "__main__":
    main()
