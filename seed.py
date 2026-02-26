from app import create_app, db
from app.models import Project, AIAnalysis, Analytics, User, Message

app = create_app()

def seed_data():
    with app.app_context():
        # Clear existing
        db.drop_all()
        db.create_all()

        # Create a test user
        user = User(username="admin", email="admin@example.com")
        user.set_password("admin123")
        db.session.add(user)
        
        user2 = User(username="testuser", email="test@example.com")
        user2.set_password("password123")
        db.session.add(user2)
        db.session.commit()

        projects = [
            {
                "title": "Quantum Auth Gateway",
                "description": "A high-performance authentication gateway built with FastAPI and Redis. Supports OAuth2, JWT rotation, and rate limiting out of the box. Designed for SaaS platforms needing a scalable, cloud-native auth layer with Docker orchestration.",
                "tech_stack": "Fastapi, Redis, Docker, OAuth2, JWT",
                "price": 4500.0,
                "github_url": "https://github.com/fastapi/fastapi",
                "user_id": user.id
            },
            {
                "title": "NexCart - Headless Storefront",
                "description": "A complete headless e-commerce solution with React frontend and Node.js backend. Includes Stripe payment integration, cart management, checkout flow, and admin dashboard. Fully responsive and optimized for SEO.",
                "tech_stack": "React, Node.Js, Stripe, Tailwind, Express",
                "price": 12000.0,
                "github_url": "https://github.com/vercel/next.js",
                "user_id": user.id
            },
            {
                "title": "MediTrack Patient CMS",
                "description": "A secure patient record and clinic management system built with Django and Vue.js. Features appointment scheduling, medical history tracking, and HIPAA-compliant data encryption. Suitable for private practices.",
                "tech_stack": "Django, Vue.Js, Postgresql, Docker",
                "price": 8500.0,
                "github_url": "https://github.com/django/django",
                "user_id": user.id
            },
            {
                "title": "Astra Analytics Engine",
                "description": "Real-time user behavior analytics engine using Go and ClickHouse. Capable of processing millions of events per second. Includes a Kibana-inspired visualization dashboard.",
                "tech_stack": "Go, Clickhouse, Grpc, Terraform",
                "price": 15000.0,
                "github_url": "https://github.com/golang/go",
                "user_id": user2.id
            },
            {
                "title": "EcoSense IoT Hub",
                "description": "Smart home environmental monitoring system with ESP32 and MQTT. Tracks humidity, temperature, and air quality. Includes a mobile companion app built with Flutter.",
                "tech_stack": "C++, ESP32, MQTT, Flutter, Firebase",
                "price": 3200.0,
                "github_url": "https://github.com/espressif/arduino-esp32",
                "user_id": user2.id
            }
        ]

        from app.logic.ai_engine import analyze_project

        for p_data in projects:
            p = Project(
                title=p_data["title"],
                description=p_data["description"],
                tech_stack=p_data["tech_stack"],
                price=p_data["price"],
                github_url=p_data["github_url"],
                user_id=p_data["user_id"]
            )
            db.session.add(p)
            db.session.flush()

            # AI Analysis
            analysis = analyze_project(p.description, p.tech_stack)
            ai = AIAnalysis(
                project_id=p.id,
                tags=analysis["tags"],
                complexity_score=analysis["complexity_score"],
                niche=analysis["niche"],
                potential_star=analysis["potential_star"],
                health_score=analysis["health_score"],
                insight_comment=analysis["insight_comment"],
                suggestion=analysis["suggestion"]
            )
            db.session.add(ai)

            # Analytics
            analytics = Analytics(project_id=p.id, views=5, clicks=2)
            db.session.add(analytics)

        # Add some mock messages for the admin user
        msg1 = Message(
            sender_id=user2.id,
            recipient_id=user.id,
            project_id=1,
            body="Merhaba, Quantum Auth Gateway projenizle ilgileniyorum. Docker konfigürasyonu Kubernetes ile uyumlu mu?",
            is_read=False
        )
        msg2 = Message(
            sender_id=user2.id,
            recipient_id=user.id,
            project_id=2,
            body="NexCart için toplu lisans alımı yapabiliyor muyuz? Şirketimiz için 5 kurulum planlıyoruz.",
            is_read=True
        )
        db.session.add_all([msg1, msg2])
        db.session.commit()

    print("✅ Seeded database with Users, Projects (GitHub links), AI analysis, and Messages.")

if __name__ == "__main__":
    seed_data()
