# # compare_filings.py
# import re
# import os

# def analyze_filing(mda_text, warning_words, safe_words):
#     text_lower = mda_text.lower()
#     warning_total = 0
#     safe_total = 0
    
#     for word in warning_words:
#         warning_total += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
#     for word in safe_words:
#         safe_total += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
    
#     ratio = warning_total/safe_total if safe_total > 0 else warning_total
#     improved = warning_total/(warning_total + safe_total) if (warning_total + safe_total) > 0 else 0
    
#     return warning_total, safe_total, ratio, improved

# warning_words = ["uncertain", "liquidity", "preserve", "reduce", "challenging", "flexible", "evaluate", "review", "suspension", "pressure", "risk", "volatile"]
# safe_words = ["committed", "confidence", "strong", "sustainable", "growing", "increase", "optimistic", "healthy"]

# print("\n=== DISNEY DIVIDEND LANGUAGE TREND (2020) ===\n")
# print(f"{'Filing Date':<12} {'Warning':<8} {'Safe':<8} {'Ratio':<8} {'Improved':<8}")
# print("-" * 50)

# # Look for all MDA files
# for filename in sorted(os.listdir()):
#     if "disney_10q_" in filename and "_MDA.txt" in filename:
#         date = filename.replace("disney_10q_", "").replace("_MDA.txt", "")
        
#         with open(filename, "r", encoding="utf-8") as f:
#             text = f.read()
        
#         w, s, ratio, improved = analyze_filing(text, warning_words, safe_words)
        
#         # Mark when dividend cut happened (May 2020)
#         cut_marker = " ← CUT HAPPENED" if date.startswith("2020-05") else ""
        
#         print(f"{date:<12} {w:<8} {s:<8} {ratio:<8.2f} {improved:<8.2f}{cut_marker}")

# print("\n=== INTERPRETATION ===")
# print("If Improved Score goes UP from Feb → May → Aug: Language became more cautious")
# print("If Improved Score goes DOWN: Language became more confident after the cut")

# test_extraction_v2.py
import os
import re

def extract_mda_v2(text):
    """Find 'Management Discussion' FIRST, then find Item 2 near it"""
    
    # Strategy 1: Find "Management's Discussion" phrase
    mgmt_pattern = r'Management[’\']?s?\s+Discussion\s+and\s+Analysis'
    mgmt_match = re.search(mgmt_pattern, text, re.IGNORECASE)
    
    if mgmt_match:
        # Look backwards up to 2000 chars to find Item 2
        search_start = max(0, mgmt_match.start() - 2000)
        before_text = text[search_start:mgmt_match.start()]
        item2_match = re.search(r'Item\s+2\.?\s*', before_text, re.IGNORECASE)
        
        if item2_match:
            start = search_start + item2_match.start()
            
            # Find end (Item 3 or PART II)
            end_search = text[start + 500:]
            end_match = re.search(r'Item\s+3\.|PART\s+II', end_search, re.IGNORECASE)
            
            if end_match:
                end = start + 500 + end_match.start()
            else:
                end = min(len(text), start + 60000)
            
            mda = text[start:end]
            
            # Validate
            if len(mda) > 3000 and 'management' in mda[:500].lower():
                return mda
    
    # Strategy 2: Find PART I first, then Item 2
    part1 = re.search(r'PART\s+I', text, re.IGNORECASE)
    if part1:
        zone = text[part1.end():part1.end() + 150000]
        
        # Find all Item 2
        for item2 in re.finditer(r'Item\s+2\.?\s*', zone, re.IGNORECASE):
            ahead = zone[item2.end():item2.end() + 300].lower()
            
            # Must have management discussion
            if 'management' in ahead and 'discussion' in ahead:
                # Must NOT have unregistered sales
                if 'unregistered' not in ahead:
                    # Find end
                    remaining = zone[item2.start():]
                    item3 = re.search(r'Item\s+3\.', remaining, re.IGNORECASE)
                    end = item3.start() if item3 else 60000
                    mda = remaining[:end]
                    if len(mda) > 3000:
                        return mda
    
    return None

# Test files
test_files = [
    ("sec_filings_dataset/cut/BA_2020-04-29.txt", "BA (CUT)"),
    ("sec_filings_dataset/non_cut/CL_2020-05-01.txt", "CL (NON-CUT)"),
    ("sec_filings_dataset/non_cut/JNJ_2020-04-29.txt", "JNJ (NON-CUT)"),
]

print("="*60)
print("TESTING IMPROVED EXTRACTION")
print("="*60)

for path, name in test_files:
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    mda = extract_mda_v2(text)
    
    if mda and len(mda) > 3000:
        print(f"✓ SUCCESS")
        print(f"  Size: {len(mda):,} chars")
        print(f"  Preview: {mda[:200].replace(chr(10), ' ')}...")
    else:
        print(f"✗ FAILED - got {len(mda) if mda else 0} chars")