"""
教師あり機械学習プロジェクト課題

提出時には、このファイル名を自分の学生証番号に変更してください。

例：
    24RB1001.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# =========================================================
# 必要なライブラリのimport
# =========================================================
#
# 使用するモデルや前処理に応じて、
# 必要なscikit-learnのクラスを以下にimportしてください。
#
# 例：
#
# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import StandardScaler
# from sklearn.pipeline import Pipeline
# from sklearn.svm import SVC
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.ensemble import GradientBoostingClassifier
#
# 上記をすべてimportする必要はありません。
# 自分が使用するクラスだけをimportしてください。


def train_and_predict(
    train_path: str,
    test_path: str,
) -> np.ndarray:
    """
    訓練データを用いてモデルを学習し、
    テストデータに対する予測ラベルを返す。

    Parameters
    ----------
    train_path : str
        訓練データCSVファイルのパス。
        訓練データにはid、特徴量、正解ラベルyが含まれる。

    test_path : str
        テストデータCSVファイルのパス。
        テストデータにはidと特徴量が含まれる。

    Returns
    -------
    predictions : numpy.ndarray
        テストデータの各行に対する予測ラベル。
        0または1からなる一次元配列とする。
    """

    # =========================================================
    # 1. データの読み込み
    # =========================================================
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)

    # =========================================================
    # 2. 説明変数と目的変数の作成
    # =========================================================
    X_train = train.drop(columns=["id", "y"])
    y_train = train["y"]

    X_test = test.drop(columns=["id"])

    # =========================================================
    # 3. モデルの作成と学習
    # =========================================================
    #
    # ここに前処理、モデルの作成、学習を実装してください。
    #
    # 例：
    # model = ...
    # model.fit(X_train, y_train)
    #

    raise NotImplementedError(
        "モデルの学習と予測を実装してください。"
    )

    # =========================================================
    # 4. テストデータに対する予測
    # =========================================================
    # predictions = model.predict(X_test)

    # =========================================================
    # 5. 戻り値の作成
    # =========================================================
    # predictions = np.asarray(predictions).astype(int)
    # return predictions