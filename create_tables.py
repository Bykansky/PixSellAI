import os
from backend.app.db import init_db

print("Starting DB schema initialization...")
print("This script will create tables based on the models defined in backend/app/db.py")

# Этот скрипт импортирует функцию init_db и запускает ее.
# Он должен быть запущен один раз после создания БД.
init_db()

print("DB schema initialization finished successfully. Tables should now exist.")
