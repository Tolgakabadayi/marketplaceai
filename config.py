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
    # NLTK Data Path (Local to project)
    import nltk
    nltk_data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'nltk_data')
    if os.path.exists(nltk_data_path):
        if nltk_data_path not in nltk.data.path:
            nltk.data.path.append(nltk_data_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
