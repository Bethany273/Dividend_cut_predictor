# compare_filings.py
import re
import os

def analyze_filing(mda_text, warning_words, safe_words):
    text_lower = mda_text.lower()
    warning_total = 0
    safe_total = 0
    
    for word in warning_words:
        warning_total += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
    for word in safe_words:
        safe_total += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
    
    ratio = warning_total/safe_total if safe_total > 0 else warning_total
    improved = warning_total/(warning_total + safe_total) if (warning_total + safe_total) > 0 else 0
    
    return warning_total, safe_total, ratio, improved

warning_words = ["uncertain", "liquidity", "preserve", "reduce", "challenging", "flexible", "evaluate", "review", "suspension", "pressure", "risk", "volatile"]
safe_words = ["committed", "confidence", "strong", "sustainable", "growing", "increase", "optimistic", "healthy"]

print("\n=== DISNEY DIVIDEND LANGUAGE TREND (2020) ===\n")
print(f"{'Filing Date':<12} {'Warning':<8} {'Safe':<8} {'Ratio':<8} {'Improved':<8}")
print("-" * 50)

# Look for all MDA files
for filename in sorted(os.listdir()):
    if "disney_10q_" in filename and "_MDA.txt" in filename:
        date = filename.replace("disney_10q_", "").replace("_MDA.txt", "")
        
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
        
        w, s, ratio, improved = analyze_filing(text, warning_words, safe_words)
        
        # Mark when dividend cut happened (May 2020)
        cut_marker = " ← CUT HAPPENED" if date.startswith("2020-05") else ""
        
        print(f"{date:<12} {w:<8} {s:<8} {ratio:<8.2f} {improved:<8.2f}{cut_marker}")

print("\n=== INTERPRETATION ===")
print("If Improved Score goes UP from Feb → May → Aug: Language became more cautious")
print("If Improved Score goes DOWN: Language became more confident after the cut")