# download_organized_filings.py
import os
import csv
from edgar import *

# Set your identity for SEC access
set_identity("Bethany Kerr bethanykerr2007@gmail.com")

# Target year
TARGET_YEAR = 2020

# Create base folders
BASE_DIR = "sec_filings_dataset"
CUT_DIR = os.path.join(BASE_DIR, "cut")
NON_CUT_DIR = os.path.join(BASE_DIR, "non_cut")
RAW_DIR = os.path.join(BASE_DIR, "raw_filings")  # Backup of all raw filings

for folder in [BASE_DIR, CUT_DIR, NON_CUT_DIR, RAW_DIR]:
    os.makedirs(folder, exist_ok=True)

def load_cut_list():
    """Load the manual cut list from CSV"""
    cut_dict = {}
    
    with open('dividend_cuts_verified.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row['ticker']
            # Convert string 'True'/'False' to boolean
            did_cut = row['did_cut'] == 'True'
            cut_dict[ticker] = {
                'name': row['name'],
                'did_cut': did_cut,
                'cut_date': row['cut_date'],
                'details': row['details']
            }
    
    return cut_dict

def download_company_filings(ticker, company_info, year):
    """Download all 10-Q filings for a company in a given year"""
    try:
        company = Company(ticker)
        date_range = f"{year}-01-01:{year}-12-31"
        filings = company.get_filings(form="10-Q").filter(filing_date=date_range)
        
        downloaded = []
        
        for filing in filings:
            date_str = filing.filing_date.strftime('%Y-%m-%d')
            filename = f"{ticker}_{date_str}.txt"
            
            # Download the text
            text = filing.text()
            
            # Save to raw folder (backup)
            raw_path = os.path.join(RAW_DIR, filename)
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Also save to cut/non-cut folder
            if company_info['did_cut']:
                dest_folder = CUT_DIR
            else:
                dest_folder = NON_CUT_DIR
            
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
    
    # Load the cut list
    companies = load_cut_list()
    print(f"\n📋 Loaded {len(companies)} companies from dividend_cuts_verified.csv")
    
    cut_count = sum(1 for c in companies.values() if c['did_cut'])
    non_cut_count = len(companies) - cut_count
    print(f"  ✂️ Cut companies: {cut_count}")
    print(f"  ✅ Non-cut companies: {non_cut_count}")
    
    # Download filings for each company
    print("\n" + "="*60)
    print("DOWNLOADING FILINGS")
    print("="*60)
    
    all_downloads = {}
    total_filings = 0
    
    for ticker, info in companies.items():
        status = "CUT" if info['did_cut'] else "NO CUT"
        print(f"\n📁 {ticker} ({info['name']}) - {status}")
        
        filings = download_company_filings(ticker, info, TARGET_YEAR)
        all_downloads[ticker] = filings
        total_filings += len(filings)
        print(f"  Total: {len(filings)} filings")
    
    # Save download log
    log_file = 'download_log.csv'
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ticker', 'date', 'filename', 'dest_path', 'did_cut'])
        for ticker, filings in all_downloads.items():
            did_cut = companies[ticker]['did_cut']
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
    print(f"  Average filings per company: {total_filings/len(companies):.1f}")
    
    print(f"\n📁 FOLDER STRUCTURE:")
    print(f"  {CUT_DIR}/")
    print(f"    └── Contains {len([f for ticker in all_downloads for f in all_downloads[ticker] if companies[ticker]['did_cut']])} filings from cut companies")
    print(f"  {NON_CUT_DIR}/")
    print(f"    └── Contains {len([f for ticker in all_downloads for f in all_downloads[ticker] if not companies[ticker]['did_cut']])} filings from non-cut companies")
    print(f"  {RAW_DIR}/")
    print(f"    └── Contains all {total_filings} filings (backup)")
    
    print(f"\n📄 Log saved to: {log_file}")

if __name__ == "__main__":
    main()