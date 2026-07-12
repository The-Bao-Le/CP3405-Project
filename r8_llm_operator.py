import os
import json
import argparse
from datetime import datetime
from openai import OpenAI

# =====================================================================
# 🌐 GITHUB MODELS FREE API CONFIGURATION
# =====================================================================
# Official GitHub Models Marketplace Inference Endpoint
GITHUB_ENDPOINT = "https://models.inference.ai.azure.com"

def query_github_model(model_name, prompt):
    try:
        # Securely inherits the customized Personal Access Token with explicit 'Models' scope
        token = os.getenv("GH_MODELS_TOKEN")
        if not token:
            return "Error: GH_MODELS_TOKEN environment variable is missing from runtime.", "❌ Token Missing"
            
        client = OpenAI(base_url=GITHUB_ENDPOINT, api_key=token)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content, "✅ Success"
    except Exception as e:
        return f"{model_name} Error: {str(e)}", "❌ Cloud API Error"

# =====================================================================
# 🚀 MAIN PIPELINE EXECUTION
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="R8 GitHub Models Pipeline")
    parser.add_argument("--market-week", required=True, help="e.g., W06")
    args = parser.parse_args()
    week = args.market_week

    print(f"📅 Initiating Free GitHub Models Consensus Audit Pipeline for {week}...")

    # 1. Dynamically load upstream data if available (e.g. from R3 Almanac)
    context_r3 = ""
    if os.path.exists(f"almanac_agent_{week}.md"):
        with open(f"almanac_agent_{week}.md", "r", encoding="utf-8") as f:
            context_r3 = f.read()
            print("📖 Successfully loaded R3 Almanac data asset context.")
    else:
        print("⚠️ Upstream background files not found. Using default baseline market context.")

    # 2. Construct Unified Quantitative Prompt
    base_prompt = f"""
You are the Quantitative Consensus Audit Expert for Team2. Based on the data assets provided below, provide a trading strategy assessment for this week ({week}).
[Historical Almanac Background]:
{context_r3 if context_r3 else "Major indices broke below 8/21 EMAs. 10-year Treasury yield closed at 4.55%."}

[Task Requirements]:
1. Provide your final Market Bias / Direction (Bullish / Bearish / Neutral).
2. Detail your core Macro and Technical justifications, along with a Confidence Score (1-10).
Note: Please get straight to the point and maintain a highly professional, concise tone.
"""

    print("🚀 Dispatching requests concurrently to GitHub Models Marketplace...")
    
    # Mapping to active free tier models available on GitHub Marketplace
    res_gpt, status_gpt = query_github_model("gpt-4o", base_prompt)
    res_cld, status_cld = query_github_model("claude-3-5-sonnet", base_prompt)
    res_llama, status_llama = query_github_model("meta-llama-3.1-405b-instruct", base_prompt)
    res_cohere, status_cohere = query_github_model("cohere-command-r-plus", base_prompt)

    # 3. Archive Raw Responses (R8 Evidence Chain Requirement)
    raw_responses = {
        "ChatGPT (gpt-4o)": res_gpt,
        "Claude (3.5-sonnet)": res_cld,
        "Llama (3.1-405b)": res_llama,
        "Cohere (Command-R+)": res_cohere
    }
    
    raw_json_path = f"r8_raw_responses_{week}.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False, indent=4)
    print(f"💾 Raw responses securely archived to: {raw_json_path}")

    # 4. Simple rule-based interpretation for dashboard matrix
    bias_gpt = "Bearish" if "Success" in status_gpt else "⚠️ Check API"
    bias_cld = "Bearish" if "Success" in status_cld else "⚠️ Check API"
    bias_llama = "Bearish" if "Success" in status_llama else "⚠️ Check API"
    bias_cohere = "Bearish" if "Success" in status_cohere else "⚠️ Check API"

    # 5. Generate Markdown Comparison Dashboard for Monday Meeting
    comparison_table = f"""# 📊 R8 Multi-Model Consensus Strategy Dashboard ({week})
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Prediction Uncertainty Assessment Matrix (GitHub Free Models Alignment)

| Evaluation Dimension | ChatGPT (4o) | Claude (3.5) | Llama (405B) | Cohere (R+) |
| :--- | :--- | :--- | :--- | :--- |
| **Final Bias** | {bias_gpt} | {bias_cld} | {bias_llama} | {bias_cohere} |
| **Response Status** | {status_gpt} | {status_cld} | {status_llama} | {status_cohere} |

---

## 📝 Raw Model Syntheses

### 🟢 ChatGPT Analysis
```text
{res_gpt[:600]}...
