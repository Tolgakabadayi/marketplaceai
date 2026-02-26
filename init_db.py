from app import create_app, db
from sqlalchemy import text

def init():
    app = create_app()
    with app.app_context():
        print("İnceleme: Veritabanı şeması kontrol ediliyor...")
        try:
            # Check if columns exist by trying a simple query
            db.session.execute(text("SELECT github_url FROM project LIMIT 1")).fetchone()
            print("Veritabanı güncel görünüyor. ✅")
        except Exception:
            print("Şema uyumsuzluğu tespit edildi! Tablolar güncelleniyor... 🔄")
            # In a production app, we'd use Alembic. 
            # For this MVP, we force-recreate to align with and fix the current error.
            db.drop_all()
            db.create_all()
            print("Tablolar başarıyla yeniden oluşturuldu. 🚀")

if __name__ == "__main__":
    init()
