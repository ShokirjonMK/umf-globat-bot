#!/bin/bash

# Backup and Move Script with Logging

# BACKUP_DIR="/var/snap/docker/common/var-lib-docker/volumes/monolith_local_postgres_data_backups/_data"
# TARGET_DIR="/home/javokhir/Viva-Med-Backend/monolith/viva_backups"
# LOG_FILE="/home/javokhir/Viva-Med-Backend/monolith/backup_and_move.log"

# mkdir -p $TARGET_DIR

# timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# echo "$timestamp: Starting backup and move process" >> $LOG_FILE

# echo "$timestamp: Running backup command" >> $LOG_FILE
# docker-compose -f /home/javokhir/Viva-Med-Backend/monolith/production.yml exec postgres backup
# if [ $? -eq 0 ]; then
#     echo "$timestamp: Backup command completed successfully" >> $LOG_FILE
# else
#     echo "$timestamp: Backup command failed" >> $LOG_FILE
#     exit 1
# fi

# if [ "$(ls -A $BACKUP_DIR)" ]; then
#     mv $BACKUP_DIR/* $TARGET_DIR/
#     echo "$timestamp: Moved backups from $BACKUP_DIR to $TARGET_DIR" >> $LOG_FILE
# else
#     echo "$timestamp: No backups found in $BACKUP_DIR to move" >> $LOG_FILE
# fi

# echo "$timestamp: Backup and move process completed" >> $LOG_FILE
