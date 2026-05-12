# extract_mda_bruteforce.py
import os
import re
import csv

BASE_DIR = "sec_filings_dataset"
CUT_DIR = os.path.join(BASE_DIR, "cut")
NON_CUT_DIR = os.path.join(BASE_DIR, "non_cut")
MDA_BASE_DIR = os.path.join(BASE_DIR, "mda_extracts")
MDA_CUT_DIR = os.path.join(MDA_BASE_DIR, "cut")
MDA_NON_CUT_DIR = os.path.join(MDA_BASE_DIR, "non_cut")

for folder in [MDA_BASE_DIR, MDA_CUT_DIR, MDA_NON_CUT_DIR]:
    os.makedirs(folder, exist_ok=True)

def extract_mda_bruteforce(text):
    """
    Brute force approach:
    1. Find ALL "Item 2" occurrences
    2. For each, look at the next 2000 chars
    3. Score them: +10 for "management", +10 for "discussion", -100 for "unregistered", -50 for "see"
    4. Take the highest scored one
    5. Extract from that point to next "Item 3" or "PART II"
    """
    
    # Find all "Item 2" positions (case insensitive, with optional colon/period)
    pattern = re.compile(r'Item\s+2[\.:]?\s+', re.IGNORECASE)
    all_matches = list(pattern.finditer(text))
    
    if not all_matches:
        return None
    
    best_match = None
    best_score = -1000
    
    for match in all_matches:
        start = match.start()
        # Look at next 2000 characters for scoring
        chunk = text[start:start+2000]
        chunk_lower = chunk.lower()
        
        score = 0
        
        # Positive signals (good MD&A)
        if re.search(r'management', chunk_lower):
            score += 10
        if re.search(r'discussion', chunk_lower):
            score += 10
        if re.search(r'analysis', chunk_lower):
            score += 5
        if re.search(r'financial', chunk_lower):
            score += 5
        if re.search(r'condition', chunk_lower):
            score += 5
        if re.search(r'results', chunk_lower):
            score += 5
        if re.search(r'operations', chunk_lower):
            score += 5
        
        # Negative signals (NOT MD&A)
        if re.search(r'unregistered', chunk_lower):
            score -= 100
        if re.search(r'sales', chunk_lower) and 'unregistered' in chunk_lower:
            score -= 50
        if re.search(r'\bsee\s+item\s+2', chunk_lower):
            score -= 50
        if re.search(r'\brefer\s+to\s+item\s+2', chunk_lower):
            score -= 50
        if re.search(r'table of contents', chunk_lower):
            score -= 30
        if re.search(r'index', chunk_lower):
            score -= 20
        
        # Longer chunk with real content is better
        # Count how many actual words (not numbers or symbols)
        words = re.findall(r'[a-z]{3,}', chunk_lower)
        if len(words) > 50:
            score += len(words) // 10
        
        if score > best_score:
            best_score = score
            best_match = match
    
    if not best_match:
        return None
    
    start = best_match.start()
    
    # Find end (next Item 3 or PART II)
    remaining = text[start+100:]
    end_pattern = re.compile(r'Item\s+3[\.:]?|PART\s+II', re.IGNORECASE)
    end_match = end_pattern.search(remaining)
    
    if end_match:
        end = start + 100 + end_match.start()
    else:
        end = min(len(text), start + 150000)
    
    mda_text = text[start:end]
    
    # Clean up: remove page numbers and obvious TOC lines
    lines = mda_text.split('\n')
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        # Skip lines that are just a page number
        if re.match(r'^\s*\d+\s*$', line_stripped):
            continue
        # Skip lines that are a heading with page number at end
        if re.match(r'^[A-Za-z\s]+\.?\s+\d+$', line_stripped) and len(line_stripped) < 60:
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def process_folder(source_folder, dest_folder, label_name):
    results = []
    
    if not os.path.exists(source_folder):
        return results
    
    files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]
    print(f"  Found {len(files)} filings")
    
    for filename in files:
        filepath = os.path.join(source_folder, filename)
        parts = filename.replace('.txt', '').split('_')
        ticker = parts[0]
        date_str = parts[1] if len(parts) > 1 else 'unknown'
        
        print(f"    Processing: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            mda_text = extract_mda_bruteforce(text)
            
            if mda_text and len(mda_text) > 2000:
                output_filename = f"{ticker}_{date_str}_MDA.txt"
                output_path = os.path.join(dest_folder, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(mda_text)
                
                results.append({
                    'ticker': ticker,
                    'date': date_str,
                    'destination': output_path,
                    'size': len(mda_text),
                    'label': label_name
                })
                print(f"      ✓ Extracted {len(mda_text):,} chars")
            else:
                print(f"      ✗ Failed (got {len(mda_text) if mda_text else 0} chars)")
                
        except Exception as e:
            print(f"      ✗ Error: {e}")
    
    return results

def main():
    print("="*60)
    print("BRUTE FORCE MDA EXTRACTION")
    print("Scoring each 'Item 2' to find the real MD&A")
    print("="*60)
    
    all_results = []
    
    print("\n📁 Processing CUT companies:")
    if os.path.exists(CUT_DIR):
        cut_results = process_folder(CUT_DIR, MDA_CUT_DIR, "cut")
        all_results.extend(cut_results)
    
    print("\n📁 Processing NON-CUT companies:")
    if os.path.exists(NON_CUT_DIR):
        non_cut_results = process_folder(NON_CUT_DIR, MDA_NON_CUT_DIR, "non_cut")
        all_results.extend(non_cut_results)
    
    # Save training data
    training_file = os.path.join(BASE_DIR, 'training_data.csv')
    with open(training_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ticker', 'date', 'mda_file_path', 'label'])
        for r in all_results:
            label_value = 1 if r['label'] == 'cut' else 0
            writer.writerow([r['ticker'], r['date'], r['destination'], label_value])
    
    print("\n" + "="*60)
    print(f"✅ Complete! Extracted {len(all_results)} MDA files")
    print(f"Training data: {training_file}")

if __name__ == "__main__":
    main()