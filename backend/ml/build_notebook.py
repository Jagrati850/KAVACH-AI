"""Build and execute the training notebook for the call transcript classifier."""
import nbformat as nbf
from nbclient import NotebookClient
import os

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
"""# KAVACH AI — Call Transcript Scam Classifier Training

Trains a lightweight NLP classifier that categorizes call transcripts into
**15 categories** (4 normal + 11 scam types) and outputs scam probability.

**Pipeline:** TF-IDF (word 1-2 grams + char 3-5 grams) → Logistic Regression

- Dataset: `../data/call_transcripts/call_transcripts_dataset.csv`
- Model artifact: `../data/models/call_scam_classifier.joblib`

The char n-grams make the model robust to Whisper ASR noise
(e.g. *"aadhaar" → "adhar card"*, *"lakh" → "lock"*, *"PIN" → "pen"*)."""))

cells.append(nbf.v4.new_code_cell(
"""import pandas as pd
import numpy as np
import joblib, os, json

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

RANDOM_STATE = 42
DATA_PATH = os.path.join('..', 'data', 'call_transcripts', 'call_transcripts_dataset.csv')
MODEL_DIR = os.path.join('..', 'data', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'call_scam_classifier.joblib')

df = pd.read_csv(DATA_PATH)
print(f"Dataset shape: {df.shape}")
df['category'].value_counts()"""))

cells.append(nbf.v4.new_markdown_cell("## Train / test split (stratified)"))

cells.append(nbf.v4.new_code_cell(
"""X = df['transcript']
y = df['category']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
)
print(f"Train: {len(X_train)}  Test: {len(X_test)}")"""))

cells.append(nbf.v4.new_markdown_cell(
"""## Model: TF-IDF (word + char n-grams) → Logistic Regression

Word n-grams capture scam phrases ("digital arrest", "share the otp");
char n-grams handle ASR spelling noise."""))

cells.append(nbf.v4.new_code_cell(
"""features = FeatureUnion([
    ('word', TfidfVectorizer(analyzer='word', ngram_range=(1, 2),
                             sublinear_tf=True, min_df=2)),
    ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5),
                             sublinear_tf=True, min_df=2, max_features=50000)),
])

model = Pipeline([
    ('tfidf', features),
    ('clf', LogisticRegression(max_iter=2000, C=10.0,
                               class_weight='balanced',
                               random_state=RANDOM_STATE)),
])

model.fit(X_train, y_train)
print('Model trained.')"""))

cells.append(nbf.v4.new_markdown_cell("## Evaluation"))

cells.append(nbf.v4.new_code_cell(
"""y_pred = model.predict(X_test)
print(f"Test accuracy: {accuracy_score(y_test, y_pred):.4f}\\n")
print(classification_report(y_test, y_pred))"""))

cells.append(nbf.v4.new_code_cell(
"""cv = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"5-fold CV accuracy: {cv.mean():.4f} +/- {cv.std():.4f}")"""))

cells.append(nbf.v4.new_markdown_cell(
"""## Scam vs Not-Scam sanity check
Binary correctness matters even when the fine-grained category is confused
(e.g. courier_scam vs customs_scam are close cousins)."""))

cells.append(nbf.v4.new_code_cell(
"""SCAM_CATEGORIES = set(df.loc[df['is_scam'] == 1, 'category'].unique())

bin_true = y_test.isin(SCAM_CATEGORIES)
bin_pred = pd.Series(y_pred, index=y_test.index).isin(SCAM_CATEGORIES)
print(f"Binary scam/not-scam accuracy: {(bin_true == bin_pred).mean():.4f}")
print(f"Scam categories: {sorted(SCAM_CATEGORIES)}")"""))

cells.append(nbf.v4.new_markdown_cell("## Save model artifact"))

cells.append(nbf.v4.new_code_cell(
"""os.makedirs(MODEL_DIR, exist_ok=True)

artifact = {
    'model': model,
    'scam_categories': sorted(SCAM_CATEGORIES),
    'classes': sorted(df['category'].unique()),
    'version': '1.0',
    'trained_on': DATA_PATH,
    'n_samples': len(df),
}
joblib.dump(artifact, MODEL_PATH)
print(f"Saved: {os.path.abspath(MODEL_PATH)}")
print(f"Size: {os.path.getsize(MODEL_PATH) / 1024:.0f} KB")"""))

cells.append(nbf.v4.new_markdown_cell("## Smoke test — different transcripts → different predictions"))

cells.append(nbf.v4.new_code_cell(
"""samples = [
    "Hi mummy, I reached the hostel safely. Did you take your medicines? I will call you after dinner.",
    "This is Inspector Verma from CBI. You are under digital arrest. Do not disconnect and transfer fifty thousand rupees for verification.",
    "Congratulations, your number won twenty five lakh in the lucky draw. Pay the registration fee of five hundred rupees to claim your prize.",
    "Sir your parcel from FedEx contains illegal drugs, the call is being transferred to Mumbai cyber police, stay on the line.",
    "Thank you for calling Amazon support, your refund for order 45298 will be processed to your original payment method within seven days.",
    "Your bank account KYC has expired, share the OTP you just received right now or your account will be blocked in two hours.",
]

loaded = joblib.load(MODEL_PATH)
clf = loaded['model']
scam_set = set(loaded['scam_categories'])

proba = clf.predict_proba(samples)
for text, p in zip(samples, proba):
    idx = np.argmax(p)
    cat = clf.classes_[idx]
    scam_p = sum(pp for c, pp in zip(clf.classes_, p) if c in scam_set)
    print(f"[{cat:22s}] conf={p[idx]:.2f} scam_prob={scam_p:.2f} :: {text[:65]}...")"""))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.13'},
}

out_path = os.path.join(os.path.dirname(__file__), 'train_call_scam_classifier.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print('Notebook written, executing...')
client = NotebookClient(nb, timeout=600, kernel_name='python3',
                        resources={'metadata': {'path': os.path.dirname(__file__)}})
client.execute()

with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f'Executed notebook saved: {out_path}')
