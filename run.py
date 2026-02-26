from app import create_app, db
from app.models import Project, AIAnalysis, Analytics

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Project': Project, 'AIAnalysis': AIAnalysis, 'Analytics': Analytics}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
