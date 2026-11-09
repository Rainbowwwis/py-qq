"""Flask 扩展实例集中定义，避免 app 包与 models/api 之间循环导入。"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
