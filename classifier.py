import json
import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_FILE = "nb_model.pkl"
VEC_FILE = "tfidf.pkl"


def load_dataset(path):
    texts, labels = [], []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if "text" in obj and "category" in obj:
                    texts.append(obj["text"])
                    labels.append(obj["category"])
            except Exception:
                continue

    return texts, labels


def train(path):

    texts, labels = load_dataset(path)

    # ======================================================
    # ✅ 1. Train–Test Split
    # ======================================================
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42
    )

    # ======================================================
    # ✅ 2. Model Selection
    # ======================================================
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    clf = MultinomialNB()

    # Convert training text into vectors
    X_train_vec = vectorizer.fit_transform(X_train)

    # Train the model
    clf.fit(X_train_vec, y_train)

    # ======================================================
    # ✅ 3. Model Evaluation
    # ======================================================
    X_test_vec = vectorizer.transform(X_test)
    predictions = clf.predict(X_test_vec)

    acc = accuracy_score(y_test, predictions)

    print("\n✅ Model Evaluation Results")
    print("Accuracy:", acc)
    print("\nClassification Report:\n")
    print(classification_report(y_test, predictions))

    # Save model + vectorizer
    joblib.dump(clf, MODEL_FILE)
    joblib.dump(vectorizer, VEC_FILE)

    return f"Model trained successfully on {len(texts)} documents ✅"


def predict(text):

    if not (os.path.exists(MODEL_FILE) and os.path.exists(VEC_FILE)):
        return "Model not trained"

    clf = joblib.load(MODEL_FILE)
    vec = joblib.load(VEC_FILE)

    X = vec.transform([text])

    return clf.predict(X)[0]
