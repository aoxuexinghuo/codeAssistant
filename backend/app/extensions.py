from flask_sqlalchemy import SQLAlchemy

# 统一在这里管理 Flask 扩展实例，后面接用户、错题本、学习记录时
# 也可以继续沿用同一套组织方式。
db = SQLAlchemy()
