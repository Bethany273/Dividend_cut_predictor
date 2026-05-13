# test.py - prediction and Edgar MDA extraction test harness
# "# evaluate_all.py
# import os
# import re
# import joblib
# from sklearn.metrics import accuracy_score

# model = joblib.load('dividend_cut_model.pkl')
# vectorizer = joblib.load('vectorizer.pkl')

# def predict_text(text):
#     text = re.sub(r'[^a-z\s]', '', text.lower())
#     X = vectorizer.transform([text])
#     return model.predict(X)[0], model.predict_proba(X)[0]

# # Test all cut files
# cut_folder = "sec_filings_dataset/mda_extracts/cut"
# cut_correct = 0
# cut_total = 0

# print("Testing CUT companies (should predict 1):")
# for filename in os.listdir(cut_folder):
#     with open(os.path.join(cut_folder, filename), 'r', encoding='utf-8') as f:
#         pred, prob = predict_text(f.read())
#         correct = "✓" if pred == 1 else "✗"
#         print(f"  {correct} {filename}: {prob[1]:.0%} confident")
#         cut_total += 1
#         if pred == 1:
#             cut_correct += 1

# # Test all non-cut files
# non_cut_folder = "sec_filings_dataset/mda_extracts/non_cut"
# non_cut_correct = 0
# non_cut_total = 0

# print("\nTesting NON-CUT companies (should predict 0):")
# for filename in os.listdir(non_cut_folder):
#     with open(os.path.join(non_cut_folder, filename), 'r', encoding='utf-8') as f:
#         pred, prob = predict_text(f.read())
#         correct = "✓" if pred == 0 else "✗"
#         print(f"  {correct} {filename}: {prob[0]:.0%} confident no-cut")
#         non_cut_total += 1
#         if pred == 0:
#             non_cut_correct += 1

# print("\n" + "="*50)
# print("OVERALL ACCURACY")
# print("="*50)
# print(f"Cut companies correct: {cut_correct}/{cut_total} ({cut_correct/cut_total:.1%})")
# print(f"Non-cut correct: {non_cut_correct}/{non_cut_total} ({non_cut_correct/non_cut_total:.1%})")
# print(f"Total accuracy: {(cut_correct + non_cut_correct)/(cut_total + non_cut_total):.1%}")"

# test_new_company.py
import os
import re
import joblib
from edgar import *
from extract_mda import extract_mda_bruteforce

# Load your trained model
model = joblib.load('dividend_cut_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Set your identity
set_identity("Bethany Kerr bethanykerr2007@gmail.com")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def get_mda_section(text):
    extracted = extract_mda_bruteforce(text)
    if extracted and len(extracted) > 1000:
        return extracted

    lower = text.lower()
    start = lower.find("item 2")
    if start < 0:
        return text[:50000]

    end = lower.find("item 3", start + 100)
    if end < 0:
        end = lower.find("part ii", start + 100)
    if end < 0:
        end = start + 50000

    return text[start:end]


def test_company(ticker, expected="CUT or NO CUT"):
    """Download and test a company's 2020 10-Q filings"""
    print(f"\n{'='*50}")
    print(f"Testing: {ticker}")
    print(f"Expected: {expected}")
    print(f"{'='*50}")
    
    try:
        company = Company(ticker)
        filings = company.get_filings(form="10-Q").filter(filing_date="2020-01-01:2020-12-31")
        
        if len(filings) == 0:
            print(f"  No 2020 10-Q filings found for {ticker}")
            return
        
        for filing in filings[:3]:  # Test first 3 filings
            date = filing.filing_date.strftime('%Y-%m-%d')
            text = filing.text()
            
            mda = get_mda_section(text)
            cleaned = clean_text(mda)
            X = vectorizer.transform([cleaned])
            pred = model.predict(X)[0]
            prob = model.predict_proba(X)[0]
            
            result = "CUT" if pred == 1 else "NO CUT"
            confidence = prob[pred]
            
            match = "✓" if (pred == 1 and expected == "CUT") or (pred == 0 and expected == "NO CUT") else "✗"
            print(f"  {match} {date}: {result} ({confidence:.0%})")
            print(f"    MDA length: {len(mda.split())} words")
            print(f"    Extracted start: {mda[:120].strip().replace('\n', ' ')}...\n")

    except Exception as e:
        print(f"  Error: {e}")

# Test new companies
print("="*60)
print("TESTING MODEL ON UNSEEN COMPANIES")
print("="*60)

# Companies that CUT (should predict CUT)
cut_companies = [
    ("DIN", "CUT"),      # Dine Brands Global (IHOP/Applebee's) - suspended 76¢ dividend April 2020 [citation:7]
    ("AMC", "CUT"),      # AMC Entertainment - suspended 3¢ dividend April 2020 [citation:7]
    ("HCA", "CUT"),      # HCA Healthcare - suspended dividend April 2020 [citation:5]
    ("HLT", "CUT"),      # Hilton Worldwide - suspended dividend April 2020 [citation:5]
    ("KSS", "CUT"),      # Kohl's - suspended dividend April 2020 [citation:5]
    ("TPR", "CUT"),      # Tapestry (Coach, Kate Spade) - suspended dividend April 2020 [citation:5]
    ("PVH", "CUT"),      # PVH Corp (Calvin Klein, Tommy Hilfiger) - suspended dividend April 2020 [citation:5]
    ("TJX", "CUT"),      # TJX Companies (TJ Maxx, Marshalls) - suspended dividend April 2020 [citation:5]
    ("GT", "CUT"),       # Goodyear Tire & Rubber - suspended 16¢ dividend April 2020 [citation:7]
    ("SLB", "CUT"),      # Schlumberger - cut dividend by 75% in April 2020 [citation:1][citation:5]
    ("IVZ", "CUT"),      # Invesco - cut dividend from 31¢ to 15.5¢ [citation:5][citation:7]
    ("WYNN", "CUT"),     # Wynn Resorts - suspended dividend May 2020 [citation:9]
    ("ALK", "CUT"),      # Alaska Air Group - suspended dividend May 2020 [citation:9]
    ("AAL", "CUT"),      # American Airlines Group - suspended dividend May 2020 [citation:9]
    ("WDC", "CUT"),      # Western Digital - suspended dividend May 2020 [citation:9]
    ("MGM", "CUT"),      # MGM Resorts - cut dividend to 1¢ annually [citation:9]
    ("COTY", "CUT"),     # Coty - suspended dividend May 2020 [citation:9]
    ("TAP", "CUT"),      # Molson Coors Beverage - suspended dividend May 2020 [citation:9]
    ("RL", "CUT"),       # Ralph Lauren - suspended dividend May 2020 [citation:9]
    ("ROST", "CUT"),     # Ross Stores - suspended dividend May 2020 [citation:9]
]
# Companies that DID NOT cut (should predict NO CUT)
safe_companies = [
    ("UPS", "NO CUT"),   # UPS - maintained dividend, only suspended buybacks [citation:7]
    ("GPC", "NO CUT"),   # Genuine Parts - maintained dividend, suspended buybacks [citation:7]
    ("WDFC", "NO CUT"),  # WD-40 - maintained dividend, only suspended buybacks [citation:7]
    ("FTS", "NO CUT"),   # Fortis (Canadian utility) - 47-year dividend growth streak [citation:8]
    ("BCE", "NO CUT"),   # BCE (Canadian telecom) - maintained dividend through 2020 [citation:8]
    ("GD", "NO CUT"),    # General Dynamics - actually INcreased dividend in April 2020 [citation:10]
    ("JNJ", "NO CUT"),   # Johnson & Johnson - 58-year dividend growth streak [citation:10] (you may already have)
    ("CL", "NO CUT"),    # Colgate-Palmolive - 57-year dividend growth streak [citation:10] (you may already have)
    ("VFC", "NO CUT"),   # VF Corp - paused buybacks but maintained dividend [citation:7]
    ("DGX", "NO CUT"),   # Quest Diagnostics - maintained dividend, suspended buybacks [citation:7]
    ("COST", "NO CUT"),  # Costco - maintained dividend through 2020
    ("PFE", "NO CUT"),   # Pfizer - healthcare, maintained dividend
    ("V", "NO CUT"),     # Visa - maintained dividend through pandemic
    ("MA", "NO CUT"),    # Mastercard - maintained dividend through pandemic
    ("MMM", "NO CUT"),   # 3M - maintained dividend
    ("CSCO", "NO CUT"),  # Cisco - maintained dividend
    ("HON", "NO CUT"),   # Honeywell - maintained dividend
    ("LMT", "NO CUT"),   # Lockheed Martin - maintained dividend
]

for ticker, expected in cut_companies:
    test_company(ticker, expected)

for ticker, expected in safe_companies:
    test_company(ticker, expected)