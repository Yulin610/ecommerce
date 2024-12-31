from app import db, app
from models import User

# 创建一个特殊的管理员用户
new_admin = User(username='admin', email='admin@.com', is_admin=True)

# 设置密码（确保使用合适的密码加密方法）
new_admin.set_password('admin')

# 添加到数据库并提交
with app.app_context():
    db.session.add(new_admin)
    db.session.commit()

print("管理员用户已创建！")
