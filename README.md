edgartools + sec-parser: Download and read SEC filings 

yfinance: Get historical dividend data to know when cuts happened 

scikit-learn: Build the actual prediction model

Analyses and uses actual SEC filing text to predict when a company might cut its dividend.

# Dividend Cut Predictor
1. Extracts Management Discussion & Analysis (MD&A) section from 10-Q filings
2. Uses TF-IDF to convert text to numerical features
3. Random Forest classifier predicts cut risk based on language patterns

A machine learning system that analyzes SEC 10-Q filings to predict whether a company will cut its dividend based on language patterns in the Management Discussion & Analysis (MD&A) section.

##  Project Overview

This project uses Natural Language Processing (NLP) to detect early warning signals of dividend cuts by analyzing how management communicates about financial health. The model achieves **~88% accuracy** on unseen companies from 2020.

### Key Findings

| Signal | Indicates |
|--------|-----------|
| "suspended", "liquidity", "uncertain" | 🔴 Higher cut risk |
| "confident", "committed", "strong" | 🟢 Lower cut risk |
| "evaluate", "review", "flexible" | 🟡 Cautionary signals |


