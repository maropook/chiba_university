from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# =========================================================
# 開発用：モデル比較
# =========================================================

train = pd.read_csv("machine_learning/train.csv")
X = train.drop(columns=["id", "y"])
y = train["y"]

models = {
    "LogisticRegression      ": LogisticRegression(random_state=42),
    "LogisticRegression (L1) ": LogisticRegression(l1_ratio=1, solver="saga", random_state=42),
    "LinearDiscriminantAnalysis": LinearDiscriminantAnalysis(),
    "GaussianNB              ": GaussianNB(),
    "SVC                     ": SVC(kernel="rbf", random_state=42),
    "DecisionTree            ": DecisionTreeClassifier(random_state=42),
    "RandomForest            ": RandomForestClassifier(random_state=42),
    "GradientBoosting        ": GradientBoostingClassifier(random_state=42),
}

print("=== モデル比較 (5分割交差検証, balanced_accuracy) ===")
for name, clf in models.items():
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
    scores = cross_val_score(pipe, X, y, cv=5, scoring="balanced_accuracy")
    print(f"{name}: {scores.mean():.4f} (+/- {scores.std():.4f})")


# =========================================================
# 提出用関数
# =========================================================

def train_and_predict(
    train_path: str,
    test_path: str,
) -> np.ndarray:
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)

    X_train = train.drop(columns=["id", "y"])
    y_train = train["y"]
    X_test = test.drop(columns=["id"])

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(random_state=42)),  # 比較後に最良モデルに変更
    ])
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    return np.asarray(predictions).astype(int)
