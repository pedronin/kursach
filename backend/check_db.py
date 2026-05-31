import sys
sys.path.insert(0, '.')

import os
os.environ.setdefault("SECRET_KEY", "check")

from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
print(f"Users in DB: {len(users)}")
for u in users:
    print(f"  id={u.id} username={u.username} hash_prefix={u.password_hash[:10]}")
    if u.password_hash.startswith("$2b$"):
        print(f"    -> bcrypt hash (OK)")
    elif "pbkdf2" in u.password_hash:
        print(f"    -> passlib/pbkdf2 hash (СТАРЫЙ, нужно удалить юзера)")
    else:
        print(f"    -> неизвестный формат")
db.close()
