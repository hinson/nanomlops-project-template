#!/bin/bash

# 1. 检查环境变量
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env
else
    echo ".env already exists."
fi

# 2. 创建数据目录
mkdir -p data/raw data/processed models

# 3. 检查 DVC 连接
echo "Checking DVC connection..."
dvc status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ DVC is ready."
else
    echo "⚠️ DVC connection failed. Check .dvc/config.local"
fi