
import os
import re
import joblib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from edgar import *
import threading
import webbrowser

# Set identity for SEC access
set_identity("Bethany Kerr bethanykerr2007@gmail.com")

# Load the trained model
MODEL_PATH = 'dividend_cut_model_v2.pkl'
VECTORIZER_PATH = 'vectorizer_v2.pkl'

# Try to load model, fall back to older version if needed
model = None
vectorizer = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✅ Loaded model v2")
elif os.path.exists('dividend_cut_model.pkl'):
    model = joblib.load('dividend_cut_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    print("✅ Loaded model v1")
else:
    print("❌ No model found. Please train the model first.")
    exit()

def extract_mda_simple(text):
    """Extract MD&A section from filing text"""
    # Look for Management Discussion pattern
    mgmt_pattern = r'Management[’\']?s?\s+Discussion\s+and\s+Analysis'
    mgmt_match = re.search(mgmt_pattern, text, re.IGNORECASE)
    
    if mgmt_match:
        start = max(0, mgmt_match.start() - 500)
        end = min(len(text), start + 50000)
        return text[start:end]
    
    # Fallback: look for Item 2
    item2_match = re.search(r'Item\s+2\.?\s*', text, re.IGNORECASE)
    if item2_match:
        start = item2_match.start()
        end = min(len(text), start + 50000)
        return text[start:end]
    
    return text[:30000]  # Last resort

def clean_text(text):
    """Clean text for model input"""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text[:10000]  # Limit length

def predict_filing(text):
    """Predict if a filing indicates dividend cut risk"""
    mda = extract_mda_simple(text)
    cleaned = clean_text(mda)
    
    if len(cleaned) < 100:
        return None, "Extracted text too short (likely wrong section)"
    
    X = vectorizer.transform([cleaned])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0]
    
    return pred, prob

def get_company_10q(ticker, year=2020):
    """Download and return 10-Q filings for a company"""
    try:
        company = Company(ticker)
        filings = company.get_filings(form="10-Q").filter(filing_date=f"{year}-01-01:{year}-12-31")
        
        results = []
        for filing in filings:
            text = filing.text()
            date = filing.filing_date.strftime('%Y-%m-%d')
            pred, prob = predict_filing(text)
            
            results.append({
                'date': date,
                'prediction': pred,
                'confidence': prob[pred] if pred is not None else 0,
                'prob_cut': prob[1] if prob is not None else 0,
                'prob_no_cut': prob[0] if prob is not None else 0,
                'status': 'success' if pred is not None else 'error'
            })
        
        return results
    except Exception as e:
        return {'error': str(e)}

class DividendPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dividend Cut Predictor")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e2e')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e2e', foreground='#cdd6f4', font=('Segoe UI', 10))
        style.configure('TButton', background='#89b4fa', foreground='#1e1e2e', font=('Segoe UI', 10, 'bold'))
        style.configure('TFrame', background='#1e1e2e')
        
        # Header
        header = tk.Label(root, text="📊 Dividend Cut Predictor", 
                          font=('Segoe UI', 20, 'bold'), 
                          bg='#1e1e2e', fg='#89b4fa')
        header.pack(pady=20)
        
        subtitle = tk.Label(root, text="Analyze SEC 10-Q filings to predict dividend cut risk",
                           font=('Segoe UI', 10), bg='#1e1e2e', fg='#a6adc8')
        subtitle.pack()
        
        # Input frame
        input_frame = tk.Frame(root, bg='#1e1e2e')
        input_frame.pack(pady=30)
        
        tk.Label(input_frame, text="Company Ticker:", font=('Segoe UI', 12), 
                bg='#1e1e2e', fg='#cdd6f4').pack(side=tk.LEFT, padx=5)
        
        self.ticker_entry = tk.Entry(input_frame, font=('Segoe UI', 14), width=10,
                                      bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4')
        self.ticker_entry.pack(side=tk.LEFT, padx=5)
        self.ticker_entry.bind('<Return>', lambda e: self.predict())
        
        self.year_entry = tk.Entry(input_frame, font=('Segoe UI', 12), width=6,
                                    bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4')
        self.year_entry.insert(0, "2020")
        self.year_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_frame, text="Year:", font=('Segoe UI', 12), 
                bg='#1e1e2e', fg='#cdd6f4').pack(side=tk.LEFT, padx=5)
        
        self.predict_btn = tk.Button(input_frame, text="🔍 Predict", 
                                      font=('Segoe UI', 12, 'bold'),
                                      bg='#89b4fa', fg='#1e1e2e',
                                      activebackground='#89b4fa',
                                      command=self.predict)
        self.predict_btn.pack(side=tk.LEFT, padx=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, mode='indeterminate', length=400)
        
        # Results frame
        self.results_frame = tk.Frame(root, bg='#1e1e2e')
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Output text area
        self.output = scrolledtext.ScrolledText(self.results_frame, 
                                                  font=('Consolas', 10),
                                                  bg='#181825', fg='#cdd6f4',
                                                  insertbackground='#cdd6f4',
                                                  wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status = tk.Label(root, text="Ready. Enter a ticker (e.g., AAPL, MSFT, DIS)",
                               font=('Segoe UI', 9), bg='#1e1e2e', fg='#6c7086')
        self.status.pack(pady=10)
        
        # Footer with info
        footer_frame = tk.Frame(root, bg='#1e1e2e')
        footer_frame.pack()
        info_btn = tk.Button(footer_frame, text="ℹ️ About", command=self.show_about,
                             font=('Segoe UI', 9), bg='#313244', fg='#cdd6f4')
        info_btn.pack(side=tk.LEFT, padx=5)
        
    
    def predict(self):
        ticker = self.ticker_entry.get().strip().upper()
        year = self.year_entry.get().strip()
        
        if not ticker:
            messagebox.showwarning("Input Error", "Please enter a ticker symbol")
            return
        
        if not year.isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid year")
            return
        
        year = int(year)
        
        # Disable button and show progress
        self.predict_btn.config(state=tk.DISABLED, text="⏳ Downloading...")
        self.progress.pack(pady=5)
        self.progress.start()
        self.status.config(text=f"Fetching {ticker} 10-Q filings for {year}...")
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"🔍 Analyzing {ticker} for {year}...\n\n")
        self.output.see(tk.END)
        
        # Run in thread to prevent GUI freezing
        thread = threading.Thread(target=self._run_prediction, args=(ticker, year))
        thread.daemon = True
        thread.start()
    
    def _run_prediction(self, ticker, year):
        try:
            company = Company(ticker)
            filings = company.get_filings(form="10-Q").filter(filing_date=f"{year}-01-01:{year}-12-31")
            
            filings_list = list(filings)
            
            if not filings_list:
                self.root.after(0, self._show_error, f"No 10-Q filings found for {ticker} in {year}")
                return
            
            results = []
            for filing in filings_list:
                text = filing.text()
                date = filing.filing_date.strftime('%Y-%m-%d')
                pred, prob = predict_filing(text)
                
                results.append({
                    'date': date,
                    'prediction': pred,
                    'confidence': prob[pred] if pred is not None else 0,
                    'prob_cut': prob[1] if prob is not None else 0,
                    'prob_no_cut': prob[0] if prob is not None else 0
                })
            
            self.root.after(0, self._display_results, ticker, year, results)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error: {str(e)}")
    
    def _display_results(self, ticker, year, results):
        self.progress.stop()
        self.progress.pack_forget()
        self.predict_btn.config(state=tk.NORMAL, text="🔍 Predict")
        
        self.output.delete(1.0, tk.END)
        
        # Header
        self.output.insert(tk.END, "="*60 + "\n")
        self.output.insert(tk.END, f"📊 DIVIDEND CUT PREDICTION RESULTS\n")
        self.output.insert(tk.END, f"   Company: {ticker}\n")
        self.output.insert(tk.END, f"   Year: {year}\n")
        self.output.insert(tk.END, "="*60 + "\n\n")
        
        # Results table
        self.output.insert(tk.END, f"{'Filing Date':<15} {'Prediction':<12} {'Confidence':<12} {'Cut Prob':<10} {'No-Cut Prob':<12}\n")
        self.output.insert(tk.END, "-"*65 + "\n")
        
        cut_count = 0
        no_cut_count = 0
        
        for r in results:
            pred_text = " CUT" if r['prediction'] == 1 else "✅ NO CUT"
            if r['prediction'] == 1:
                cut_count += 1
            else:
                no_cut_count += 1
            
            self.output.insert(tk.END, f"{r['date']:<15} {pred_text:<12} {r['confidence']:.0%} {' ' * 6} {r['prob_cut']:.0%} {' ' * 8} {r['prob_no_cut']:.0%}\n")
        
        self.output.insert(tk.END, "-"*65 + "\n\n")
        
        # Summary
        self.output.insert(tk.END, "📈 SUMMARY:\n")
        total = len(results)
        if cut_count > no_cut_count:
            self.output.insert(tk.END, f"   ⚠️ {cut_count}/{total} filings indicate DIVIDEND CUT RISK\n")
            self.output.insert(tk.END, "   → Management language suggests financial stress\n")
        else:
            self.output.insert(tk.END, f"   ✅ {no_cut_count}/{total} filings indicate DIVIDEND SAFE\n")
            self.output.insert(tk.END, "   → Management language suggests confidence\n")
        
        # Interpretation
        self.output.insert(tk.END, "\n💡 INTERPRETATION:\n")
        avg_cut_prob = sum(r['prob_cut'] for r in results) / len(results)
        
        if avg_cut_prob > 0.6:
            self.output.insert(tk.END, "   🔴 HIGH RISK - Company shows strong signals of dividend concerns\n")
        elif avg_cut_prob > 0.4:
            self.output.insert(tk.END, "   🟡 MODERATE RISK - Mixed signals, monitor closely\n")
        else:
            self.output.insert(tk.END, "   🟢 LOW RISK - Company language appears confident\n")
        
        self.output.insert(tk.END, "\n" + "="*60 + "\n")
        self.output.insert(tk.END, "📝 Note: Based on analysis of Management Discussion & Analysis (MD&A) sections.\n")
        self.output.insert(tk.END, "      The model learns from historical 2020 dividend cut patterns.\n")
        
        self.status.config(text=f"✅ Analysis complete for {ticker}")
    
    def _show_error(self, message):
        self.progress.stop()
        self.progress.pack_forget()
        self.predict_btn.config(state=tk.NORMAL, text="🔍 Predict")
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"❌ ERROR\n\n{message}\n\n")
        self.output.insert(tk.END, "Possible solutions:\n")
        self.output.insert(tk.END, "  • Check if the ticker symbol is correct\n")
        self.output.insert(tk.END, "  • Try a different year (e.g., 2021, 2022)\n")
        self.output.insert(tk.END, "  • The company may not have 10-Q filings for that year\n")
        self.status.config(text=f"❌ Error: {message[:50]}")
        messagebox.showerror("Error", message)
    
    def show_about(self):
        about_text = """📊 Dividend Cut Predictor

A machine learning model that analyzes SEC 10-Q filings to predict whether a company will cut its dividend.

How it works:
1. Extracts Management Discussion & Analysis (MD&A) section from 10-Q filings
2. Uses TF-IDF to convert text to numerical features
3. Random Forest classifier predicts cut risk based on language patterns

Key signals:
• 🔴 "suspended", "liquidity", "uncertain" → Higher cut risk
• 🟢 "confident", "committed", "strong" → Lower cut risk

Accuracy: ~88% on unseen test data

Built with: Python, scikit-learn, edgartools, tkinter"""
        
        messagebox.showinfo("About Dividend Cut Predictor", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DividendPredictorApp(root)
    root.mainloop()