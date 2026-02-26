from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Project, AIAnalysis, Analytics, User, Message
from app import db
import time
import os
from werkzeug.utils import secure_filename
from app.logic.ai_engine import (
    analyze_project, fetch_github_repo_data, 
    generate_description_from_github, search_projects_by_query
)

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ──────────────────── Public Pages ────────────────────

@bp.route('/')
def index():
    total_projects = Project.query.count()
    return render_template('index.html', total_projects=total_projects)

@bp.route('/listings')
def listings():
    projects = Project.query.all()
    return render_template('listings.html', projects=projects)

@bp.route('/lab/<int:project_id>')
def product_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.ai_analysis:
        analysis = analyze_project(project.description, project.tech_stack or '')
        new_analysis = AIAnalysis(
            project_id=project.id,
            tags=analysis["tags"],
            complexity_score=analysis["complexity_score"],
            niche=analysis["niche"],
            potential_star=analysis["potential_star"],
            health_score=analysis["health_score"],
            insight_comment=analysis["insight_comment"],
            suggestion=analysis["suggestion"]
        )
        db.session.add(new_analysis)
        db.session.commit()
    
    if not project.analytics:
        analytics = Analytics(project_id=project.id, views=1)
        db.session.add(analytics)
    else:
        project.analytics.views += 1
    db.session.commit()
        
    return render_template('product.html', project=project)

# ──────────────────── Authentication ────────────────────

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.cockpit'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        error = None
        if not username or not email or not password:
            error = 'Tüm alanları doldurunuz.'
        elif len(password) < 6:
            error = 'Şifre en az 6 karakter olmalıdır.'
        elif password != password2:
            error = 'Şifreler eşleşmiyor.'
        elif User.query.filter_by(username=username).first():
            error = 'Bu kullanıcı adı zaten alınmış.'
        elif User.query.filter_by(email=email).first():
            error = 'Bu e-posta adresi zaten kayıtlı.'
        if error:
            flash(error, 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Hoş geldiniz, {username}! 🚀', 'success')
            return redirect(url_for('main.cockpit'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.cockpit'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('E-posta veya şifre hatalı.', 'danger')
        else:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Tekrar hoş geldiniz, {user.username}! ⚡', 'success')
            return redirect(next_page or url_for('main.cockpit'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('main.index'))

# ──────────────────── Seller Dashboard (Protected) ────────────────────

@bp.route('/cockpit')
@login_required
def cockpit():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).limit(10).all()
    unread_count = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    return render_template('dashboard.html', projects=projects, messages=messages, unread_count=unread_count)

@bp.route('/cockpit/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        price = request.form.get('price', '0')
        github_url = request.form.get('github_url', '').strip()
        
        error = None
        if not title:
            error = 'Başlık alanı zorunludur.'
        
        try:
            price = float(price)
        except ValueError:
            error = 'Geçerli bir fiyat giriniz.'
        
        if error:
            flash(error, 'danger')
        else:
            try:
                # If GitHub URL provided, fetch and enrich description
                if github_url:
                    repo_data = fetch_github_repo_data(github_url)
                    if repo_data:
                        auto_desc = generate_description_from_github(repo_data)
                        if not description:
                            description = auto_desc
                        else:
                            description = description + "\n\n--- AI Generated from GitHub ---\n" + auto_desc
                        
                        # Auto-fill tech stack from languages
                        if not tech_stack and repo_data.get('languages'):
                            tech_stack = ', '.join(repo_data['languages'])
                        elif repo_data.get('languages'):
                            existing = set(t.strip().lower() for t in tech_stack.split(','))
                            for lang in repo_data['languages']:
                                if lang.lower() not in existing:
                                    tech_stack += f', {lang}'
                        
                        if not title or title == '':
                            title = repo_data.get('repo_name', 'Untitled Project').replace('-', ' ').title()
                    else:
                        flash('GitHub repo erişilemedi, ancak proje manuel bilgilerle oluşturuldu.', 'info')
                
                if not description:
                    description = 'Açıklama eklenmedi.'
                
                # Handle image uploads
                image_filenames = []
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                files = request.files.getlist('images')
                for f in files:
                    if f and f.filename and allowed_file(f.filename):
                        fname = secure_filename(f'{current_user.id}_{int(time.time())}_{f.filename}')
                        f.save(os.path.join(upload_dir, fname))
                        image_filenames.append(fname)
                
                project = Project(
                    title=title,
                    description=description,
                    tech_stack=tech_stack,
                    price=price,
                    user_id=current_user.id,
                    github_url=github_url if github_url else None,
                    images=','.join(image_filenames) if image_filenames else None
                )
                db.session.add(project)
                db.session.flush()
                
                # Run AI analysis
                try:
                    analysis_result = analyze_project(description, tech_stack)
                    ai = AIAnalysis(
                        project_id=project.id,
                        tags=analysis_result["tags"],
                        complexity_score=analysis_result["complexity_score"],
                        niche=analysis_result["niche"],
                        potential_star=analysis_result["potential_star"],
                        health_score=analysis_result["health_score"],
                        insight_comment=analysis_result["insight_comment"],
                        suggestion=analysis_result["suggestion"]
                    )
                    db.session.add(ai)
                except Exception as ai_err:
                    current_app.logger.error(f"AI Analysis Error: {ai_err}")
                
                analytics = Analytics(project_id=project.id, views=0)
                db.session.add(analytics)
                db.session.commit()
                
                flash('Projeniz başarıyla yüklendi! 🧠', 'success')
                return redirect(url_for('main.cockpit'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Listing Error: {e}")
                flash(f"Bir hata oluştu: {str(e)}", 'danger')
                return redirect(url_for('main.new_listing'))
    
    return render_template('new_listing.html')

@bp.route('/cockpit/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_listing(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Bu projeyi silme yetkiniz yok.', 'danger')
        return redirect(url_for('main.cockpit'))
    db.session.delete(project)
    db.session.commit()
    flash('Proje başarıyla silindi.', 'info')
    return redirect(url_for('main.cockpit'))

# ──────────────────── Contact Seller (Messaging) ────────────────────

@bp.route('/contact/<int:project_id>', methods=['POST'])
@login_required
def contact_seller(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.owner:
        return jsonify({"error": "Satıcı bulunamadı."}), 404
    if project.user_id == current_user.id:
        return jsonify({"error": "Kendi projenize mesaj gönderemezsiniz."}), 400
    
    body = request.form.get('message', '').strip()
    if not body:
        return jsonify({"error": "Mesaj boş olamaz."}), 400
    
    msg = Message(
        sender_id=current_user.id,
        recipient_id=project.user_id,
        project_id=project.id,
        body=body
    )
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Mesajınız satıcıya iletildi! ✉️"})

@bp.route('/cockpit/messages/read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    msg = Message.query.get_or_404(message_id)
    if msg.recipient_id == current_user.id:
        msg.is_read = True
        db.session.commit()
    return jsonify({"success": True})

# ──────────────────── AI Chat Assistant ────────────────────

@bp.route('/api/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        user_query = data.get('message', '').strip() if data else ''
        
        if not user_query:
            return jsonify({"reply": "Merhaba! Size nasıl yardımcı olabilirim? Aradığınız proje türünü anlatın.", "projects": []})
        
        projects = Project.query.all()
        # search_projects_by_query uses TextBlob which needs NLTK data
        results = search_projects_by_query(user_query, projects)
        
        if results:
            project_data = []
            for proj, score in results:
                project_data.append({
                    "id": proj.id,
                    "title": proj.title,
                    "niche": proj.ai_analysis.niche if proj.ai_analysis else "General",
                    "stars": proj.ai_analysis.potential_star if proj.ai_analysis else 1,
                    "price": proj.price,
                    "url": url_for('main.product_detail', project_id=proj.id)
                })
            
            reply = f"Aramanızla eşleşen {len(project_data)} proje buldum! İşte en uygun sonuçlar:"
        else:
            project_data = []
            reply = "Maalesef aramanızla eşleşen bir proje bulamadım. Farklı kelimelerle tekrar deneyin veya daha genel tanımlayın."
        
        return jsonify({"reply": reply, "projects": project_data})
    except Exception as e:
        current_app.logger.error(f"Chat Error: {e}")
        return jsonify({
            "reply": f"Üzgünüm, AI motorunda bir hata oluştu: {str(e)}", 
            "projects": [],
            "error": True
        }), 200 # Return 200 so the UI can show the error gracefully

# ──────────────────── API ────────────────────

@bp.route('/api/analyze/<int:project_id>')
def api_analyze(project_id):
    project = Project.query.get_or_404(project_id)
    time.sleep(1.5) 
    return jsonify({
        "status": "success",
        "message": "Analysis Complete",
        "health_score": project.ai_analysis.health_score if project.ai_analysis else 0
    })
