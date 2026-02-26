import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'interstellar-dark-mode-secret-key-123'
    # Use SQLite by default for local development, easily switchable to PostgreSQL on Render
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # Render NLTK Data Path
    if os.environ.get('RENDER'):
        import nltk
        nltk.data.path.append('/opt/render/nltk_data')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
