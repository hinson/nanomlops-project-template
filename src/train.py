import os
from typing import Any

import mlflow
import pandas as pd
from prefect import flow, task
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 你的 .env 文件中定义了 MLflow 地址，但在代码中也可以读取
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")


@task(name="Load Data")
def load_data() -> pd.DataFrame:
    """Simulate loading data."""
    # 使用 sklearn 生成的简单数据模拟
    from sklearn.datasets import make_classification

    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(20)])
    df["target"] = y
    return df


@task(name="Train Model")
def train_model(df: pd.DataFrame) -> dict[str, Any]:
    """Train a simple logistic regression model."""
    X = df.drop("target", axis=1)
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 启用 MLflow 自动记录
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("ruff-template-experiment")

    with mlflow.start_run():
        model = LogisticRegression()
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        # Log extra metrics if needed
        mlflow.log_metric("custom_accuracy", acc)
        print(f"Model Accuracy: {acc}")

        return {"model": model, "accuracy": acc}


@flow(name="ML Training Pipeline")
def main_flow():
    """Main workflow entrypoint."""
    data = load_data()
    train_model(data)


if __name__ == "__main__":
    main_flow()
