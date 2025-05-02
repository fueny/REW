#!/bin/bash

# 数据库备份脚本

# 设置备份目录
BACKUP_DIR="/home/ubuntu/REW_backups"
DB_PATH="/home/ubuntu/REW/instance/vocabulary.db"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/vocabulary_$DATE.db"

# 确保备份目录存在
mkdir -p $BACKUP_DIR

# 备份数据库
echo "备份数据库到 $BACKUP_FILE..."
cp "$DB_PATH" "$BACKUP_FILE"

# 保留最近的10个备份
echo "清理旧备份，只保留最近10个..."
ls -t $BACKUP_DIR/vocabulary_*.db | tail -n +11 | xargs -r rm

echo "数据库备份完成！"
