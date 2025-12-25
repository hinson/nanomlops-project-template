.PHONY: install format lint test clean dvc-pull dvc-push feast-apply feast-materialize

# 初始化与依赖安装
install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"

# 代码规范化 (Ruff)
format:
	@echo "Running Ruff Format..."
	ruff format .
	ruff check --fix .

lint:
	@echo "Running Ruff Lint..."
	ruff check .
	ruff format --check .

# 测试
test:
	pytest

# DVC 数据操作
dvc-pull:
	dvc pull

dvc-push:
	dvc push

# Feast 特征操作
feast-apply:
	cd feature_repo && feast apply

feast-materialize:
	# 同步当前时间的数据到 Redis
	cd feature_repo && feast materialize-incremental $$(date -u +"%Y-%m-%dT%H:%M:%S")

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +