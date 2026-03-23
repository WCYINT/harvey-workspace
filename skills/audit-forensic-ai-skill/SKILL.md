# Enterprise Shadow AI Auditor (360-Degree Standard)

## Description
This enterprise-grade skill automates the identification, auditing, and optimization of "Shadow AI" spending. It features a **360-Degree Detection Engine** that identifies consumer SaaS, developer API infrastructure, and cloud AI services. It includes a **Zero Data Retention (ZDR) Security Matrix** to flag data leakage risks and provides **Forex Normalization** for global enterprise audits.

## Key Upgrades (2026 Standard)
1. **API & Cloud Infrastructure Detection**: Identifies AWS Bedrock, Azure OpenAI, GCP Vertex AI, Anthropic API, and major Vector DBs (Pinecone, Weaviate).
2. **ZDR Security Matrix**: Classifies tools into "Enterprise Safe (ZDR)" vs "High Risk (Public/Training)" to prevent corporate IP exposure.
3. **Forex & Departmental Normalization**: Automatically converts EUR, GBP, SAR, and JPY to USD and aggregates waste by Department/Cost Center.

## Prerequisites
- **Python 3.11+**
- **Pandas** library (`pip install pandas`)
- A corporate expense CSV with columns: `Date`, `Description`, `Amount`, `Currency` (optional), `Department` (optional).

## How to Use

### 1. Prepare Your Data
Ensure your expense CSV includes the necessary columns. Example:
```csv
Date,Description,Amount,Currency,Department
2026-01-05,Azure OpenAI Service,1200.00,EUR,Engineering
2026-01-10,ChatGPT Plus Subscription,20.00,USD,Marketing
```

### 2. Run the Audit
Execute the script with your CSV file:
```bash
python3 enterprise_ai_auditor.py your_expenses.csv
```

### 3. Review the Enterprise Report
The script generates `enterprise_shadow_ai_report.md` featuring:
- **Data Leakage Warnings**: Critical alerts for tools that train on user data.
- **ZDR Security Matrix**: A clear visual of safe vs. risky tools.
- **Departmental Waste Analysis**: Specific dollar amounts wasted per department.
- **Infrastructure Exposure**: Visibility into developer-level AI spend.

---

## Implementation Logic (Python)

```python
import pandas as pd

# 2026 Enterprise-Grade AI Tool & Infrastructure Database
AI_TOOLS_DB = {
    "ChatGPT (Free/Plus)": {"category": "General LLM", "zdr": "High Risk", "domains": ["chatgpt.com", "openai.com"]},
    "Claude (Free/Pro)": {"category": "General LLM", "zdr": "High Risk", "domains": ["claude.ai", "anthropic.com"]},
    "Midjourney": {"category": "Image Creation", "zdr": "High Risk", "domains": ["midjourney.com"]},
    "AWS Bedrock": {"category": "Cloud Infrastructure", "zdr": "Enterprise Safe", "domains": ["aws.amazon.com/bedrock"]},
    "Azure OpenAI": {"category": "Cloud Infrastructure", "zdr": "Enterprise Safe", "domains": ["openai.azure.com"]},
    "Anthropic API": {"category": "API Infrastructure", "zdr": "Enterprise Safe", "domains": ["api.anthropic.com"]},
    "Pinecone": {"category": "Vector Database", "zdr": "Enterprise Safe", "domains": ["pinecone.io"]},
    # ... (Full database included in script)
}

# 2026 Static Forex Rates
FOREX_RATES = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "SAR": 0.27, "JPY": 0.0065}

def normalize_currency(amount, currency):
    return amount * FOREX_RATES.get(str(currency).upper(), 1.0)

def identify_ai_transactions(df):
    # Logic to flag transactions against AI_TOOLS_DB and normalize currency
    # ... (Refer to full script for implementation)
    pass

def calculate_optimization(flagged_df):
    # Logic to aggregate redundant spend by Department
    # ... (Refer to full script for implementation)
    pass

# Full script available in the asset package.
```

## Compliance & Security Standards
- **ZDR (Zero Data Retention)**: Aligned with SOC2 and enterprise DPA requirements.
- **Data Leakage Warning**: Triggered when tools lack explicit "No Training" guarantees.
- **Forex Standard**: Based on 2026 Q1 average exchange rates.

---
*Developed by Manus Principal Financial Architect & AI Compliance Auditor.*
