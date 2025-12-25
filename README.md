# MLOps Project Template

基于 NanoMLOps 平台的标准化机器学习项目模版。集成代码规范、数据版本控制、特征存储与实验追踪。

## 🏗 技术栈

| 组件                | 工具              | 作用                                     |
| ------------------- | ----------------- | ---------------------------------------- |
| **Linting**         | **Ruff**          | 极速代码检查与格式化 (替代 Flake8/Black) |
| **Data Versioning** | **DVC**           | 大文件与数据集版本管理 (S3 Backend)      |
| **Feature Store**   | **Feast**         | 特征定义、离线检索与在线服务             |
| **Experiment**      | **MLflow**        | 模型训练指标记录与模型注册               |
| **Orchestration**   | **Prefect**       | 工作流编排与任务调度                     |
| **CI/CD**           | **Gitea Actions** | 自动化测试与部署流水线                   |

## 🚀 快速开始

### 1\. 环境初始化

本模版专为 `Dockerfile.workspace` 容器环境设计。

```bash
# 1. 安装项目依赖
make install

# 2. 检查 DVC 配置
# 注意：敏感凭证存储在 .dvc/config.local (已自动忽略)
cat .dvc/config.local
dvc status
```

### 2\. 特征工程 (Feast)

特征定义位于 `feature_repo/` 目录。

```bash
# 注册特征定义到 Registry
make feast-apply

# 将特征数据从离线存储(Postgres/File)同步到在线存储(Redis)
make feast-materialize
```

### 3\. 数据管理 (DVC)

不要将大文件直接提交到 Git。

```bash
# 添加数据文件
dvc add data/raw_dataset.csv

# 记录 DVC 元数据变更到 Git
git add data/raw_dataset.csv.dvc .gitignore
git commit -m "Update dataset"

# 推送数据到 MinIO，推送代码到 Gitea
dvc push
git push
```

### 4\. 模型训练

训练脚本位于 `src/train.py` ，会自动记录实验到 MLflow。

```bash
python src/train.py
```

## 📏 代码规范

本项目强制使用 **Ruff** 进行代码风格管理。

- **自动修复**: `make format`
- **代码检查**: `make lint`

在 VS Code 中，保存文件时会自动触发格式化。提交代码到 Gitea 时，CI 流水线会自动运行检查，不通过将无法合并。

### 环境变量配置 (.env)

项目根目录的 `.env` 文件用于管理连接 MLOps 平台服务的环境变量。您可以复制 `.env.example` 进行配置。


### DVC 凭证配置 (.dvc/config.local)

为了安全起见，DVC 的 MinIO 访问凭证存储在 `.dvc/config.local` 中，该文件 **不会** 被提交到 Git 仓库。

如果您的环境中缺少此文件，请手动创建：

**文件内容示例 (`.dvc/config.local`)**

```ini
['remote "minio_dvc"']
    # 对应 .env 中的 MINIO_ROOT_USER
    access_key_id = minioadmin

    # 对应 .env 中的 MINIO_ROOT_PASSWORD
    secret_access_key = minioadmin
```


### VS Code 配置参考

如果您的项目没有包含 `.vscode` 目录，建议手动创建以下文件以获得最佳体验（自动格式化、导入排序等）。

**1\. 推荐插件列表 (`.vscode/extensions.json`)**

```json
{
    "recommendations": [
        "charliermarsh.ruff",
        "ms-python.python",
        "ms-toolsai.jupyter"
    ]
}
```

**2\. 自动化设置 (`.vscode/settings.json`)**

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.analysis.typeCheckingMode": "basic",
    
    // 显式指定 Ruff 配置文件路径
    // 这确保了 VS Code 编辑器内的检查规则与 pyproject.toml 中定义的一模一样 (如 SIM, UP 等规则)
    "ruff.configuration": "pyproject.toml",
    
    // 使用 Ruff 官方插件作为 Python 的默认格式化工具
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            // 保存时自动修复 lint 错误 (读取 pyproject.toml 中的规则)
            "source.fixAll.ruff": "explicit",
            // 保存时自动排序导入
            "source.organizeImports.ruff": "explicit"
        }
    },

    // 排除不必要的搜索路径，提高性能
    "search.exclude": {
        "**/node_modules": true,
        "**/bower_components": true,
        "**/*.code-search": true,
        "**/.venv": true,
        "**/data": true,
        "**/.dvc": true,
        "**/mlruns": true
    }
}
```

## 📂 目录结构说明

```bash
├── .gitea/                # CI/CD 配置
│   └── workflows/
│       └── ci.yaml        # Gitea Actions 流水线定义
├── .vscode/               # VS Code 环境配置
│   ├── extensions.json    # 推荐插件列表
│   └── settings.json      # 自动化格式配置 (Ruff)
├── .dvc/                  # DVC 存储配置
│   ├── config             # 公共配置 (URL, Endpoint)
│   ├── config.local       # 敏感凭证 (Git 忽略)
│   └── .gitignore         # DVC 忽略规则
├── config/                # 项目级配置
│   └── main.yaml          # 通用参数配置
├── data/                  # 本地数据缓存 (Git 忽略)
├── feature_repo/          # Feast 特征库
│   ├── data/              # 特征注册表存储位置
│   ├── feature_store.yaml # 连接配置 (Postgres/Redis)
│   └── features.py        # 特征定义
├── models/                # 本地模型制品
├── notebooks/             # Jupyter 实验笔记本
├── scripts/               # 运维与辅助脚本
│   └── setup_env.sh
├── src/                   # 核心代码包
│   ├── __init__.py
│   ├── data.py            # 数据加载 (DVC 集成)
│   ├── train.py           # 训练逻辑 (MLflow 集成)
│   └── utils.py           # 通用工具函数
├── tests/                 # 测试用例
├── .gitignore             # Git 忽略配置
├── .python-version        # Python 版本锁定
├── Makefile               # 常用命令快捷方式
└── pyproject.toml         # 配置文件中心 (依赖 + Ruff)
```
