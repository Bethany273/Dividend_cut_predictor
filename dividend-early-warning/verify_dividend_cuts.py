# manual_cut_list.py
import csv

# Manually verified cut companies
CUT_COMPANIES = {
    "DIS": "Disney",
    "F": "Ford",
    "BA": "Boeing", 
    "CCL": "Carnival",
    "DAL": "Delta Air Lines",
    "RCL": "Royal Caribbean",
    "MRO": "Marathon Oil",
    "HAL": "Halliburton",
    "OXY": "Occidental Petroleum",
}

# Manually verified non-cut companies
NON_CUT_COMPANIES = {
    "JNJ": "Johnson & Johnson",
    "PG": "Procter & Gamble",
    "KO": "Coca-Cola",
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "PEP": "PepsiCo",
    "MCD": "McDonald's",
    "WMT": "Walmart",
    "HD": "Home Depot",
    "JPM": "JPMorgan Chase",
}

def main():
    print("="*60)
    print("MANUAL DIVIDEND CUT LIST (2020)")
    print("="*60)
    
    results = []
    
    # Add cut companies
    for ticker, name in CUT_COMPANIES.items():
        results.append({
            'ticker': ticker,
            'name': name,
            'did_cut': True,
            'cut_date': '2020',
            'details': 'Known dividend cut/suspension in 2020'
        })
    
    # Add non-cut companies
    for ticker, name in NON_CUT_COMPANIES.items():
        results.append({
            'ticker': ticker,
            'name': name,
            'did_cut': False,
            'cut_date': '',
            'details': 'Maintained dividend through 2020'
        })
    
    # Save to CSV
    with open('dividend_cuts_verified.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ticker', 'name', 'did_cut', 'cut_date', 'details'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✂️ CUT COMPANIES ({len(CUT_COMPANIES)}):")
    for ticker, name in CUT_COMPANIES.items():
        print(f"  - {ticker}: {name}")
    
    print(f"\n✅ NON-CUT COMPANIES ({len(NON_CUT_COMPANIES)}):")
    for ticker, name in NON_CUT_COMPANIES.items():
        print(f"  - {ticker}: {name}")
    
    print(f"\n📁 Total companies: {len(results)}")
    print(f"✅ Saved to: dividend_cuts_verified.csv")

if __name__ == "__main__":
    main()