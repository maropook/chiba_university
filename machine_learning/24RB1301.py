from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


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
        ("clf", GradientBoostingClassifier(random_state=42)),
    ])
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    return np.asarray(predictions).astype(int)
