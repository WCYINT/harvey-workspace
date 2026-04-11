import zipfile, re

docm_path = "/Users/fhjtech/.openclaw/media/inbound/0-ç_å_3118426381_Cå_å_æ_ç_µæ_å_è½_å_æ_é_å_æ_å_è_é_æ_¹è_2026---104cd33c-4cd0-4f1b-80db-3d6ec216891b"

with zipfile.ZipFile(docm_path, 'r') as z:
    with z.open('word/document.xml') as f:
        content = f.read().decode('utf-8')

t_matches = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', content)
full_text = ''.join(t_matches)

# Find "本章旨在" which is in chapter 5 body
body_marker = full_text.find('本章旨在系统阐述')
if body_marker > 0:
    ch5_start = body_marker
    ch6_start = full_text.find('6 结论与展望', body_marker)
    if ch6_start > 0:
        ch5_content = full_text[ch5_start:ch6_start]
    else:
        ch5_content = full_text[ch5_start:ch5_start+25000]
    
    with open('/Users/fhjtech/.openclaw/workspace/.tmp_paper/chapter5_analysis.txt', 'w') as f:
        f.write(ch5_content)
    
    print(f"Chapter 5 content saved: {len(ch5_content)} chars")
    print("\n" + "="*60)
    print(ch5_content)
else:
    print("Body marker not found")
    # Try alternate approach
    idx = full_text.find('5.1 实施保障举措')
    if idx > 0:
        end_idx = full_text.find('6 结论', idx)
        ch5_content = full_text[idx:end_idx] if end_idx > 0 else full_text[idx:idx+25000]
        with open('/Users/fhjtech/.openclaw/workspace/.tmp_paper/chapter5_analysis.txt', 'w') as f:
            f.write(ch5_content)
        print(f"Chapter 5: {len(ch5_content)} chars")
        print(ch5_content[:5000])