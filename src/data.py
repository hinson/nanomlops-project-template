import subprocess
from pathlib import Path

import pandas as pd
from prefect import task
from sklearn.datasets import make_classification

# 定义数据存放的相对路径
DATA_DIR = Path("data")
RAW_DATA_PATH = DATA_DIR / "raw_dataset.csv"


@task(name="Pull Data from DVC")
def pull_data_from_dvc() -> None:
    """
    调用 DVC 命令行拉取最新数据。

    这确保了在训练开始前，本地拥有与 .dvc.lock 中记录一致的数据版本。
    如果 DVC 未配置或远程连接失败，将抛出异常。
    """
    print("Attempting to pull data from DVC remote...")

    # 检查当前目录下是否有 .dvc 目录，判断是否为 DVC 项目
    if not Path(".dvc").exists():
        print("Warning: Not a DVC repository. Skipping dvc pull.")
        return

    try:
        # 使用 subprocess 调用 dvc pull
        # capture_output=True 用于捕获标准输出，避免在日志中刷屏，除非出错
        subprocess.run(["dvc", "pull"], check=True, capture_output=True, text=True)
        print("✅ DVC pull completed successfully.")
    except subprocess.CalledProcessError as e:
        # 如果是因为没有配置 remote 或者是离线状态，打印警告而不是直接崩溃
        print(f"⚠️ Warning: DVC pull failed. Error: {e.stderr}")
        print("Proceeding with local files if available...")


@task(name="Load Raw Data")
def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    加载原始 CSV 数据。

    如果指定路径的文件不存在，将生成模拟数据用于演示目的。
    这使得项目模版可以在没有任何外部数据依赖的情况下直接运行。
    """
    if not file_path.exists():
        print(f"⚠️ Data file {file_path} not found.")
        print("🔄 Generating dummy data for demonstration...")

        # 生成模拟分类数据
        X, y = make_classification(
            n_samples=1000,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            random_state=42,
        )

        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
        df["target"] = y

        # 确保父目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存模拟数据，这样下次运行时就会直接加载这个文件
        df.to_csv(file_path, index=False)
        print(f"✅ Dummy data saved to {file_path}")
        return df

    print(f"📂 Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"✅ Data loaded. Shape: {df.shape}")
    return df


@task(name="Preprocess Data")
def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    执行数据预处理和特征目标分离。

    Steps:
    1. 填充缺失值 (此处简单填充为 0)
    2. 分离特征 (X) 和 目标变量 (y)
    """
    # 1. 简单的清洗逻辑
    if df.isnull().values.any():
        print("Found missing values, filling with 0...")
        df = df.fillna(0)

    # 2. 识别目标列
    # 假设 'target' 列存在，如果不存在则取最后一列
    target_col = "target"
    if target_col not in df.columns:
        target_col = df.columns[-1]
        print(f"Column 'target' not found, using last column '{target_col}' as target.")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    print(f"✅ Preprocessing done. Features: {X.shape}, Target: {y.shape}")
    return X, y
