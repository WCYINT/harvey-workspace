import zipfile, re

docm_path = "/Users/fhjtech/.openclaw/media/inbound/0-ç_å_3118426381_Cå_å_æ_ç_µæ_å_è½_å_æ_é_å_æ_å_è_é_æ_¹è_2026---104cd33c-4cd0-4f1b-80db-3d6ec216891b"

with zipfile.ZipFile(docm_path, 'r') as z:
    with z.open('word/document.xml') as f:
        content = f.read().decode('utf-8')

t_matches = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', content)
full_text = ''.join(t_matches)

# Find IQF introduction in chapter 1
iqf_idx = full_text.find('IQF')
if iqf_idx > 0:
    # Get context around IQF
    start = max(0, iqf_idx - 200)
    end = min(len(full_text), iqf_idx + 1500)
    iqf_section = full_text[start:end]
    print("=== IQF Introduction ===")
    print(iqf_section)
    print("\n" + "="*60 + "\n")

# Find appendix
appendix_idx = full_text.find('附  录')
if appendix_idx > 0:
    appendix_content = full_text[appendix_idx:appendix_idx+3000]
    print("=== Appendix Content ===")
    print(appendix_content)
