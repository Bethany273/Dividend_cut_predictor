# train_simple.py
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("="*60)
print("TRAINING DIVIDEND CUT PREDICTOR")
print("="*60)

# Paths to your already-organized MDA files
CUT_FOLDER = "sec_filings_dataset/mda_extracts/cut"
NON_CUT_FOLDER = "sec_filings_dataset/mda_extracts/non_cut"

# Step 1: Load all MDA files
print("\nLoading MDA files...")

texts = []
labels = []


def get_earliest_files(folder):
    earliest = {}
    for filename in os.listdir(folder):
        if not filename.endswith("_MDA.txt"):
            continue
        parts = filename.replace('_MDA.txt', '').split('_')
        ticker = parts[0]
        date = parts[1] if len(parts) > 1 else None
        if not date:
            continue
        if ticker not in earliest or date < earliest[ticker][0]:
            earliest[ticker] = (date, filename)
    return [filename for _, filename in sorted(earliest.values())]

# Use only the earliest filing per ticker so the model trains on pre-cut / baseline reports.
cut_files = get_earliest_files(CUT_FOLDER)
non_cut_files = get_earliest_files(NON_CUT_FOLDER)

for filename in cut_files:
    with open(os.path.join(CUT_FOLDER, filename), 'r', encoding='utf-8') as f:
        texts.append(f.read())
        labels.append(1)
        print(f"  Cut: {filename}")

for filename in non_cut_files:
    with open(os.path.join(NON_CUT_FOLDER, filename), 'r', encoding='utf-8') as f:
        texts.append(f.read())
        labels.append(0)
        print(f"  Non-cut: {filename}")

print(f"\nSelected {len(cut_files)} earliest cut files and {len(non_cut_files)} earliest non-cut files")

print(f"\nTotal: {len(texts)} files")
print(f"   Cut (label=1): {sum(labels)}")
print(f"   Non-cut (label=0): {len(labels) - sum(labels)}")

# Step 2: Simple text cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # keep only letters and spaces
    text = re.sub(r'\s+', ' ', text)      # remove extra spaces
    return text.strip()

cleaned = [clean_text(t) for t in texts]

# Step 3: Convert to numbers (TF-IDF)
print("\nConverting text to numbers...")
vectorizer = TfidfVectorizer(
    max_features=1500,
    min_df=1,
    max_df=0.85,
    stop_words='english',
    ngram_range=(1, 2),
    sublinear_tf=True,
)
X = vectorizer.fit_transform(cleaned)
y = np.array(labels)

print(f"   {X.shape[0]} files × {X.shape[1]} features")


# Step 4: Split into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Step 5: Train model
print("\nTraining model...")
model = LogisticRegression(
    solver='liblinear',
    class_weight='balanced',
    random_state=42,
    max_iter=500,
)
model.fit(X_train, y_train)

# Step 5b: cross-validation on full dataset
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"\n5-fold CV accuracy: {cv_scores.mean():.2%} ± {cv_scores.std():.2%}")

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
coefs = model.coef_[0]

pos_idx = np.argsort(coefs)[-15:][::-1]
neg_idx = np.argsort(coefs)[:15]

print("\nTop 15 words associated with CUT:")
for i, idx in enumerate(pos_idx):
    print(f"   {i+1}. '{feature_names[idx]}' - {coefs[idx]:.4f}")

print("\nTop 15 words associated with NO CUT:")
for i, idx in enumerate(neg_idx):
    print(f"   {i+1}. '{feature_names[idx]}' - {coefs[idx]:.4f}")

# Step 8: Save model
joblib.dump(model, 'dividend_cut_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("\nModel saved to: dividend_cut_model.pkl")
print("Vectorizer saved to: vectorizer.pkl")
print("\nTraining complete!")
