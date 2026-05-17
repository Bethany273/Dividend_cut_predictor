# download_organized_filings.py
import os
import csv
import argparse
from edgar import *

# Set your identity for SEC access
set_identity("Bethany Kerr bethanykerr2007@gmail.com")

# Default target year (kept for backward compatibility)
TARGET_YEAR = 2020

# Create base folders
BASE_DIR = "sec_filings_dataset"
CUT_DIR = os.path.join(BASE_DIR, "cut")
NON_CUT_DIR = os.path.join(BASE_DIR, "non_cut")
RAW_DIR = os.path.join(BASE_DIR, "raw_filings")  # Backup of all raw filings

for folder in [BASE_DIR, CUT_DIR, NON_CUT_DIR, RAW_DIR]:
    os.makedirs(folder, exist_ok=True)

def get_default_companies():
    """Return the default list of companies with their cut status"""
    companies = {
        # ========== CUT COMPANIES (did_cut = True) ==========
        # Airlines / Travel / Leisure
        "DIS": {"name": "Disney", "did_cut": True, "cut_date": "2020-05-05", "details": "Suspended dividend"},
        "F": {"name": "Ford", "did_cut": True, "cut_date": "2020-03-19", "details": "Suspended dividend"},
        "BA": {"name": "Boeing", "did_cut": True, "cut_date": "2020-04-29", "details": "Suspended dividend"},
        "CCL": {"name": "Carnival", "did_cut": True, "cut_date": "2020-04-07", "details": "Suspended dividend"},
        "DAL": {"name": "Delta Air Lines", "did_cut": True, "cut_date": "2020-03-13", "details": "Suspended dividend"},
        "RCL": {"name": "Royal Caribbean", "did_cut": True, "cut_date": "2020-03-13", "details": "Suspended dividend"},
        "HLT": {"name": "Hilton Worldwide", "did_cut": True, "cut_date": "2020-04-21", "details": "Suspended dividend"},
        "AMC": {"name": "AMC Entertainment", "did_cut": True, "cut_date": "2020-04-07", "details": "Suspended dividend"},
        
        # Energy
        "MRO": {"name": "Marathon Oil", "did_cut": True, "cut_date": "2020-05-05", "details": "Reduced from $0.05 to $0.01"},
        "HAL": {"name": "Halliburton", "did_cut": True, "cut_date": "2020-05-20", "details": "Reduced from $0.18 to $0.045"},
        "OXY": {"name": "Occidental Petroleum", "did_cut": True, "cut_date": "2020-03-10", "details": "Reduced from $0.79 to $0.01"},
        
        # Automotive / Manufacturing
        "GM": {"name": "General Motors", "did_cut": True, "cut_date": "2020-04-27", "details": "Suspended dividend"},
        "HOG": {"name": "Harley-Davidson", "did_cut": True, "cut_date": "2020-04-14", "details": "Reduced from $0.38 to $0.02"},
        
        # Retail
        "KSS": {"name": "Kohl's", "did_cut": True, "cut_date": "2020-03-23", "details": "Suspended dividend"},
        "TPR": {"name": "Tapestry", "did_cut": True, "cut_date": "2020-04-23", "details": "Suspended dividend"},
        "TJX": {"name": "TJX Companies", "did_cut": True, "cut_date": "2020-03-23", "details": "Suspended dividend"},
        
        # Hospitality / Restaurants
        "DIN": {"name": "Dine Brands", "did_cut": True, "cut_date": "2020-04-20", "details": "Suspended dividend"},
        "LVS": {"name": "Las Vegas Sands", "did_cut": True, "cut_date": "2020-04-23", "details": "Suspended dividend"},
        "EXPE": {"name": "Expedia", "did_cut": True, "cut_date": "2020-04-16", "details": "Suspended dividend"},
        "PVH": {"name": "PVH Corp", "did_cut": True, "cut_date": "2020-04-09", "details": "Suspended dividend"},
        
        # Healthcare
        "HCA": {"name": "HCA Healthcare", "did_cut": True, "cut_date": "2020-04-29", "details": "Suspended dividend"},
        
        # ========== NON-CUT COMPANIES (did_cut = False) ==========
        # Healthcare
        "JNJ": {"name": "Johnson & Johnson", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "PFE": {"name": "Pfizer", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Consumer Goods
        "PG": {"name": "Procter & Gamble", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "KO": {"name": "Coca-Cola", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "PEP": {"name": "PepsiCo", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "CL": {"name": "Colgate-Palmolive", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "WDFC": {"name": "WD-40", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Technology
        "MSFT": {"name": "Microsoft", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "AAPL": {"name": "Apple", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "V": {"name": "Visa", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "MA": {"name": "Mastercard", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Industrial / Manufacturing
        "CAT": {"name": "Caterpillar", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "GD": {"name": "General Dynamics", "did_cut": False, "cut_date": "", "details": "No cut - actually increased dividend"},
        "GPC": {"name": "Genuine Parts", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Retail / Logistics
        "WMT": {"name": "Walmart", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "HD": {"name": "Home Depot", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "MCD": {"name": "McDonald's", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "COST": {"name": "Costco", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "VFC": {"name": "VF Corp", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        "UPS": {"name": "United Parcel Service", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Finance
        "JPM": {"name": "JPMorgan Chase", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
        
        # Restaurant
        "SYY": {"name": "Sysco", "did_cut": False, "cut_date": "", "details": "No cut - maintained dividend"},
    }
    return companies

def load_cut_list(path=None):
    """Load companies from a CSV file if provided, otherwise use default list"""
    if path is not None:
        # Load from CSV file
        companies = {}
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get('ticker') or row.get('Ticker')
                if not ticker:
                    continue
                did_cut = row.get('did_cut', 'False') == 'True'
                companies[ticker] = {
                    'name': row.get('name', ''),
                    'did_cut': did_cut,
                    'cut_date': row.get('cut_date', ''),
                    'details': row.get('details', '')
                }
        return companies
    else:
        # Use default built-in list
        return get_default_companies()

def download_company_filings(ticker, company_info, start_year, end_year):
    """Download 10-Q filings for a company over a year range"""
    try:
        company = Company(ticker)
        date_range = f"{start_year}-01-01:{end_year}-12-31"
        filings = company.get_filings(form="10-Q").filter(filing_date=date_range)

        downloaded = []

        for filing in filings:
            date_str = filing.filing_date.strftime('%Y-%m-%d')
            filename = f"{ticker}_{date_str}.txt"

            text = filing.text()

            # Save to raw backup folder
            raw_path = os.path.join(RAW_DIR, filename)
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(text)

            # Save to cut or non-cut folder
            dest_folder = CUT_DIR if company_info.get('did_cut') else NON_CUT_DIR
            dest_path = os.path.join(dest_folder, filename)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(text)

            downloaded.append({
                'ticker': ticker,
                'date': date_str,
                'filename': filename,
                'raw_path': raw_path,
                'dest_path': dest_path,
                'filing_date': filing.filing_date
            })

            print(f"    ✓ {filename}")

        return downloaded

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []

def main():
    print("="*60)
    print("DOWNLOAD ORGANIZED SEC FILINGS")
    print("="*60)
    
    parser = argparse.ArgumentParser(description='Download 10-Q filings for specified companies and year range')
    parser.add_argument('--year', type=int, help='Single target year (e.g. 2020)')
    parser.add_argument('--start-year', type=int, help='Start year for range (inclusive)')
    parser.add_argument('--end-year', type=int, help='End year for range (inclusive)')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers to download')
    parser.add_argument('--tickers-file', type=str, help='Path to a CSV file with company data')
    args = parser.parse_args()

    if args.year:
        start_year = end_year = args.year
    else:
        start_year = args.start_year or TARGET_YEAR
        end_year = args.end_year or TARGET_YEAR

    # Load companies
    if args.tickers:
        # Use command-line tickers
        tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
        companies = {t: {'name': '', 'did_cut': False, 'cut_date': '', 'details': ''} for t in tickers}
        loaded_from = 'command-line --tickers'
    elif args.tickers_file:
        # Load from CSV file
        companies = load_cut_list(path=args.tickers_file)
        loaded_from = args.tickers_file
    else:
        # Use default built-in list
        companies = get_default_companies()
        loaded_from = 'default built-in list'

    print(f"\n📋 Loaded {len(companies)} companies from {loaded_from}")

    cut_count = sum(1 for c in companies.values() if c.get('did_cut'))
    non_cut_count = len(companies) - cut_count
    print(f"  ✂️ Cut companies: {cut_count}")
    print(f"  ✅ Non-cut companies: {non_cut_count}")
    
    # Print company lists for verification
    print("\n✂️ CUT COMPANIES:")
    for ticker, info in companies.items():
        if info.get('did_cut'):
            print(f"    - {ticker}: {info.get('name', 'Unknown')}")
    
    print("\n✅ NON-CUT COMPANIES:")
    for ticker, info in companies.items():
        if not info.get('did_cut'):
            print(f"    - {ticker}: {info.get('name', 'Unknown')}")
    
    # Download filings for each company
    print("\n" + "="*60)
    print("DOWNLOADING FILINGS")
    print("="*60)
    
    all_downloads = {}
    total_filings = 0
    
    for ticker, info in companies.items():
        status = "CUT" if info.get('did_cut') else "NO CUT"
        name = info.get('name', '')
        print(f"\n📁 {ticker} ({name}) - {status}")
        filings = download_company_filings(ticker, info, start_year, end_year)
        all_downloads[ticker] = filings
        total_filings += len(filings)
        print(f"  Total: {len(filings)} filings")
    
    # Save download log
    log_file = 'download_log.csv'
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ticker', 'date', 'filename', 'dest_path', 'did_cut'])
        for ticker, filings in all_downloads.items():
            did_cut = companies[ticker].get('did_cut', False)
            for filing in filings:
                writer.writerow([
                    ticker, 
                    filing['date'], 
                    filing['filename'], 
                    filing['dest_path'],
                    did_cut
                ])
    
    print("\n" + "="*60)
    print("✅ DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"\n📊 STATISTICS:")
    print(f"  Companies processed: {len(companies)}")
    print(f"  Total filings downloaded: {total_filings}")
    if len(companies) > 0:
        print(f"  Average filings per company: {total_filings/len(companies):.1f}")
    
    # Count files in each folder
    cut_file_count = len([f for ticker in all_downloads for f in all_downloads[ticker] if companies[ticker].get('did_cut')])
    non_cut_file_count = len([f for ticker in all_downloads for f in all_downloads[ticker] if not companies[ticker].get('did_cut')])
    
    print(f"\n📁 FOLDER STRUCTURE:")
    print(f"  {CUT_DIR}/")
    print(f"    └── Contains {cut_file_count} filings from cut companies")
    print(f"  {NON_CUT_DIR}/")
    print(f"    └── Contains {non_cut_file_count} filings from non-cut companies")
    print(f"  {RAW_DIR}/")
    print(f"    └── Contains all {total_filings} filings (backup)")
    
    print(f"\n📄 Log saved to: {log_file}")

if __name__ == "__main__":
    main()