import os


class Config:

    DATABASE_CONFIG = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': os.environ.get('MYSQL_PORT', 3306),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'password'),
        'database': os.environ.get('MYSQL_DATABASE', 'testDB')
    }

    SELENIUM_CONFIG = {
        'host': os.environ.get('SELENIUM_HOST', 'localhost'),
        'port': str(os.environ.get('SELENIUM_PORT', 4444))
    }