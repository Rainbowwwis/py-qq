import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 令牌有效期（秒），供 utils/auth.py 使用
    TOKEN_MAX_AGE = 7 * 24 * 3600


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:root123@db_dev:3306/qiaoqiao_dev'
    )


class TestingConfig(Config):
    TESTING = True
    # 单元测试默认走内存库，无需依赖 MySQL 容器
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
