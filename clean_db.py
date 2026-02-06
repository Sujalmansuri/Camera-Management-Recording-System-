from database import SessionLocal
import models

db = SessionLocal()

bad_rows = db.query(models.Recording).filter(models.Recording.filename == None).all()

for row in bad_rows:
    db.delete(row)

db.commit()
db.close()

print("✅ Bad recording rows deleted")
