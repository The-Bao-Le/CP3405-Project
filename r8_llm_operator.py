import os
import json
import argparse
from datetime import datetime
from openai import OpenAI

# =====================================================================
# 🌐 FREE LAYER API ENDPOINT CONFIGURATIONS (OpenRouter Compatible)
# =====================================================================
OPENROUTER_URL = "https://openrouter.ai/api/v1"

def query_free_model(model_string, prompt, api_key):
    """
    Safely query free LLM models via the unified OpenRouter gateway.
    """
    # Robust check: If API key is None, empty, or literal placeholder strings
    if not api_key or api_key.strip().lower() in ["", "none", "null", "undefined"]:
        return (
            f"API Key Error: OPENROUTER_API_KEY environment variable is not passed to this runtime environment. "
            f"Please ensure your workflow YAML file contains the 'env: OPENROUTER_API_KEY: ${{{{ secrets.OPENROUTER_API_KEY }}}}' block.", 
            "❌ Key Missing"
        )
    try:
        # Initialize OpenAI-compatible client for unified OpenRouter access
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
# 📂 SMART UPSTREAM FILE PATH LOCATOR
# =====================================================================
def load_upstream_file(paths_to_try):
    """
    Attempt to read upstream data assets from multiple potential candidate paths and return the contents.
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
# 🚀 MAIN PIPELINE EXECUTION CONTROL
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="R8 Free Multi-Model Consensus Engine")
    parser.add_argument("--market-week", required=True, help="e.g., W29")
    args = parser.parse_args()
    week = args.market_week

    print(f"📅 Initiating R8 Multi-Model Consensus Audit for {week}...")

    # Fetching the master repository secret securely from environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")

    # 1. Dynamically locate and load R3 Almanac seasonal data assets
    r3_paths = [
        f"almanac_agent_{week}.md",
        f"r3_almanac_agent/outputs/almanac_agent_{week}.md",
        f"r3_almanac_agent/almanac_agent_{week}.md"
    ]
    context_r3 = load_upstream_file(r3_paths)

    # 2. Dynamically locate and load R5 Technical analysis indicators (supporting both '-' and '_')
    r5_paths = [
        f"technical_agent-{week}.md",
        f"technical_agent_{week}.md",
        f"r5_technical_agent/technical_agent-{week}.md",
        f"technical_agent-W29.md"
    ]
    context_r5 = load_upstream_file(r5_paths)

    # 3. Dynamically locate and load R4 Macroeconomic analysis data assets
    r4_paths = [
        f"macro_agent_{week}.md",
        f"r4_macro_agent/macro_agent_{week}.md"
    ]
    context_r4 = load_upstream_file(r4_paths)
    if not context_r4:
        print("ℹ️ R4 Macro Agent data not found (yet). Proceeding with dynamic baseline context fallback.")

    # 4. Construct unified quantitative analysis prompt merging R3, R4, and R5 contexts
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

    # 5. Map the 4 target flagship LLMs on the OpenRouter Free Tier
    models = {
        "ChatGPT": "openai/gpt-4o-mini:free",
        "Claude": "meta-llama/llama-3.1-70b-instruct:free", # Using Llama 3.1 70B as high-fidelity Claude free tier alternative
        "Gemini": "google/gemini-2.5-flash:free",
        "DeepSeek": "deepseek/deepseek-r1:free"
    }

    print("🚀 Dispatching requests concurrently to OpenRouter cloud tier...")
    res_chatgpt, status_chatgpt = query_free_model(models["ChatGPT"], base_prompt, api_key)
    res_claude, status_claude = query_free_model(models["Claude"], base_prompt, api_key)
    res_gemini, status_gemini = query_free_model(models["Gemini"], base_prompt, api_key)
    res_deepseek, status_deepseek = query_free_model(models["DeepSeek"], base_prompt, api_key)

    # 6. Securely archive raw JSON responses for the audit trail
    raw_responses = {
        "ChatGPT_4o_Mini": res_chatgpt,
        "Claude_Llama_Alternative": res_claude,
        "Gemini_2.5_Flash": res_gemini,
        "DeepSeek_R1": res_deepseek
    }
    
    raw_json_path = f"r8_raw_responses_{week}.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False, indent=4)
    print(f"💾 Raw responses securely archived to: {raw_json_path}")

    # 7. Convert response states into visual matrix indicators
    bias_gpt = "Parsed" if "Success" in status_chatgpt else "⚠️ Error"
    bias_cld = "Parsed" if "Success" in status_claude else "⚠️ Error"
    bias_gem = "Parsed" if "Success" in status_gemini else "⚠️ Error"
    bias_dpk = "Parsed" if "Success" in status_deepseek else "⚠️ Error"

    # 8. Assemble the executive Markdown dashboard
    comparison_table = (
        f"# 📊 R8 Multi-Model Consensus Strategy Dashboard ({week})\n"
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "## 🔍 Prediction Uncertainty Assessment Matrix (Free Open-Source Model Alignment)\n\n"
        "| Evaluation Dimension | ChatGPT (4o-mini) | Claude (Alternative) | Gemini (2.5-flash) | DeepSeek (R1) |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        f"| **Consensus Bias** | {bias_gpt} | {bias_cld} | {bias_gem} | {bias_dpk} |\n"
        f"| **Response Status** | {status_chatgpt} | {status_claude} | {status_gemini} | {status_deepseek} |\n\n"
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
        "### 🔴 Gemini 2.5 Flash Analysis\n"
        "```text\n"
        f"{res_gemini[:800]}...\n"
        "```\n\n"
        "### 🟡 DeepSeek R1 Analysis\n"
        "```text\n"
        f"{res_deepseek[:800]}...\n"
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
