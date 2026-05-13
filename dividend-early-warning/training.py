# train_simple.py
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("="*60)
print("TRAINING DIVIDEND CUT PREDICTOR")
print("="*60)

# Paths to your already-organized MDA files
CUT_FOLDER = "sec_filings_dataset/mda_extracts/cut"
NON_CUT_FOLDER = "sec_filings_dataset/mda_extracts/non_cut"

# Step 1: Load all MDA files
print("\n📂 Loading MDA files...")

texts = []
labels = []

# Load cut files (label = 1)
for filename in os.listdir(CUT_FOLDER):
    if filename.endswith("_MDA.txt"):
        with open(os.path.join(CUT_FOLDER, filename), 'r', encoding='utf-8') as f:
            texts.append(f.read())
            labels.append(1)  # 1 = cut
            print(f"  ✓ Cut: {filename}")

# Load non-cut files (label = 0)
for filename in os.listdir(NON_CUT_FOLDER):
    if filename.endswith("_MDA.txt"):
        with open(os.path.join(NON_CUT_FOLDER, filename), 'r', encoding='utf-8') as f:
            texts.append(f.read())
            labels.append(0)  # 0 = no cut
            print(f"  ✓ Non-cut: {filename}")

print(f"\n✅ Total: {len(texts)} files")
print(f"   Cut (label=1): {sum(labels)}")
print(f"   Non-cut (label=0): {len(labels) - sum(labels)}")

# Step 2: Simple text cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # keep only letters and spaces
    text = re.sub(r'\s+', ' ', text)      # remove extra spaces
    return text

cleaned = [clean_text(t) for t in texts]

# Step 3: Convert to numbers (TF-IDF)
print("\n🔢 Converting text to numbers...")
vectorizer = TfidfVectorizer(max_features=500, min_df=2, max_df=0.8)
X = vectorizer.fit_transform(cleaned)
y = np.array(labels)

print(f"   {X.shape[0]} files × {X.shape[1]} features")


# Step 4: Split into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Step 5: Train model
print("\n🤖 Training model...")
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Step 6: Test model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"ACCURACY: {accuracy:.2%}")
print(f"{'='*50}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['NO CUT', 'CUT']))

# Step 7: Show top words
feature_names = vectorizer.get_feature_names_out()
importances = model.feature_importances_
top_idx = importances.argsort()[-15:][::-1]

print("\n🔑 Top 15 most important words:")
for i, idx in enumerate(top_idx):
    print(f"   {i+1}. '{feature_names[idx]}' - {importances[idx]:.4f}")

# Step 8: Save model
joblib.dump(model, 'dividend_cut_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("\n💾 Model saved to: dividend_cut_model.pkl")
print("💾 Vectorizer saved to: vectorizer.pkl")
print("\n✅ Training complete!")
