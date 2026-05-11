import os
import re

# Define your signal word lists
WARNING_WORDS = [
    "prudent", "flexible", "evaluate", "review", "uncertain", 
    "challenging", "liquidity", "preserve", "suspension", 
    "reduce", "modify", "capital allocation", "reassessment",
    "difficult", "pressure", "risk", "uncertainty", "volatile"
]

SAFE_WORDS = [
    "committed", "growing", "increase", "sustainable", 
    "long-term", "shareholder return", "confidence", 
    "strong", "healthy", "improved", "optimistic"
]

def count_words(text, word_list):
    """Count how many times words from a list appear in text"""
    text_lower = text.lower()
    counts = {}
    total = 0
    
    for word in word_list:
        # Count occurrences (word boundaries to avoid partial matches)
        pattern = r'\b' + re.escape(word) + r'\b'
        count = len(re.findall(pattern, text_lower))
        if count > 0:
            counts[word] = count
            total += count
    
    return total, counts

def analyze_filing(mda_text):
    """Analyze a single filing and return signal scores"""
    warning_total, warning_details = count_words(mda_text, WARNING_WORDS)
    safe_total, safe_details = count_words(mda_text, SAFE_WORDS)
    
    # Calculate a "risk score" (higher = more likely to cut)
    if safe_total > 0:
        risk_score = warning_total / safe_total
    else:
        risk_score = warning_total if warning_total > 0 else 0
    
    return {
        'warning_count': warning_total,
        'safe_count': safe_total,
        'risk_score': risk_score,
        'warning_details': warning_details,
        'safe_details': safe_details
    }

# Analyze all downloaded MDA files
print("=== SIGNAL WORD ANALYSIS ===\n")

mda_files = [f for f in os.listdir() if f.endswith("_MDA.txt")]

results = []

for filename in sorted(mda_files):
    print(f"Analyzing: {filename}")
    
    with open(filename, "r", encoding="utf-8") as f:
        mda_text = f.read()
    
    analysis = analyze_filing(mda_text)
    
    # Extract date from filename
    date = filename.replace("disney_10q_", "").replace("_MDA.txt", "")
    
    results.append({
        'date': date,
        'filename': filename,
        **analysis
    })
    
    print(f"  Warning words: {analysis['warning_count']}")
    print(f"  Safe words: {analysis['safe_count']}")
    print(f"  Risk score: {analysis['risk_score']:.2f}")
    
    if analysis['warning_details']:
        print(f"  Top warnings: {list(analysis['warning_details'].keys())[:3]}")
    print()

# Summary
print("=== SUMMARY TABLE ===")
print(f"{'Date':<12} {'Warning':<10} {'Safe':<10} {'Risk Score':<10}")
print("-" * 45)
for r in results:
    print(f"{r['date']:<12} {r['warning_count']:<10} {r['safe_count']:<10} {r['risk_score']:<10.2f}")
