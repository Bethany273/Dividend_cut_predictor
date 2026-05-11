from edgar import *
import yfinance as yf

# Set identity (name + email)
set_identity("Bethany Kerr bethanykerr2007@gmail.com")

# Check dividends
print("=== DISNEY DIVIDENDS ===")
dis = yf.Ticker("DIS")
print(dis.dividends.tail(15))
print("\n")

# Download SEC filings using CORRECT date syntax
print("=== DOWNLOADING DISNEY 10-Q FILINGS ===")
company = Company("DIS")

# Try a broader range: all of 2020
filings = company.get_filings(form="10-Q").filter(filing_date="2020-01-01:2020-12-31")

print(f"Found {len(filings)} filings")

if len(filings) > 0:
    for filing in filings:
        print(f"  {filing.filing_date} - {filing.form}")
    
    # Download the first filing (Q1 2020)
    filing = filings[0]
    text = filing.text()
    
    # Save it
    filename = f"disney_10q_{filing.filing_date}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"\n✓ Saved to: {filename}")
    print(f"  Size: {len(text):,} characters")
else:
    print("No filings found. Trying without date filter...")
    # Fallback: get all 10-Qs
    all_filings = company.get_filings(form="10-Q")
    print(f"Total 10-Q filings for Disney: {len(all_filings)}")
    if len(all_filings) > 0:
        print("First 3 filing dates:")
        for f in all_filings[:3]:
            print(f"  {f.filing_date}")