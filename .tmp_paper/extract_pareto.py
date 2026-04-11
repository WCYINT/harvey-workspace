import zipfile, re

docm_path = "/Users/fhjtech/.openclaw/media/inbound/0-ç_å_3118426381_Cå_å_æ_ç_µæ_å_è½_å_æ_é_å_æ_å_è_é_æ_¹è_2026---104cd33c-4cd0-4f1b-80db-3d6ec216891b"

with zipfile.ZipFile(docm_path, 'r') as z:
    with z.open('word/document.xml') as f:
        content = f.read().decode('utf-8')

t_matches = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', content)
full_text = ''.join(t_matches)

# Find Chapter 3 Pareto content
pareto_idx = full_text.find('帕累托')
if pareto_idx > 0:
    end_idx = min(len(full_text), pareto_idx + 3000)
    pareto_section = full_text[pareto_idx:end_idx]
    print("=== Pareto Chart Content ===")
    print(pareto_section)

# Also find TOP or ranking related content
top_idx = full_text.find('TOP')
if top_idx > 0:
    end_idx = min(len(full_text), top_idx + 1500)
    top_section = full_text[top_idx:end_idx]
    print("\n=== TOP Content ===")
    print(top_section)

# Find IQF scoring rules
iqf_idx = full_text.find('1.1.3')
if iqf_idx > 0:
    end_idx = min(len(full_text), iqf_idx + 3000)
    iqf_section = full_text[iqf_idx:end_idx]
    print("\n=== IQF Section 1.1.3 ===")
    print(iqf_section)
