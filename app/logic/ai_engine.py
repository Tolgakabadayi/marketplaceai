from textblob import TextBlob
import re
import urllib.request
import json

# ─────────── Tech Dictionary & Niches ───────────

TECH_DICTIONARY = [
    "flask", "django", "react", "vue", "angular", "node", "express",
    "fastapi", "spring", "docker", "kubernetes", "aws", "gcp", "azure",
    "sql", "postgresql", "mongodb", "redis", "elasticsearch", "machine learning",
    "ai", "nlp", "computer vision", "tensorflow", "pytorch", "stable diffusion",
    "saas", "ecommerce", "blockchain", "web3", "tailwind", "bootstrap",
    "python", "javascript", "typescript", "java", "go", "rust", "c#",
    "next.js", "nuxt", "svelte", "graphql", "rest api", "microservice",
    "electron", "flutter", "react native", "swift", "kotlin", "arduino", "esp32",
    "embedded", "iot", "opencv", "scikit-learn", "numpy", "pandas", "pytorch",
    "php", "laravel", "symfony", "codeigniter", "wordpress"
]

NICHES = {
    "SaaS": ["saas", "subscription", "cloud", "multi-tenant", "tenant", "dashboard", "analytics"],
    "E-commerce": ["ecommerce", "shop", "store", "cart", "checkout", "payment", "stripe", "order"],
    "Healthcare": ["health", "medical", "patient", "doctor", "clinic", "hospital"],
    "Gaming": ["game", "unity", "unreal", "multiplayer", "mmo", "rpg"],
    "Finance": ["finance", "fintech", "banking", "crypto", "blockchain", "trading", "wallet"],
    "AI/ML": ["ai", "machine learning", "deep learning", "nlp", "vision", "model", "prediction", "neural"],
    "Restaurant/POS": ["restaurant", "pos", "order", "table", "menu", "kitchen", "waiter", "sipariş", "masa"],
    "Education": ["education", "learn", "course", "student", "teacher", "quiz", "exam"],
    "Social Media": ["social", "feed", "post", "comment", "like", "follow", "influencer"],
    "CRM": ["crm", "customer", "lead", "pipeline", "contact", "sales"]
}

# ─────────── GitHub Repo Fetching ───────────

def fetch_github_repo_data(github_url):
    """
    Fetch public GitHub repo data (README, languages, file tree) via GitHub API.
    Does deep structure analysis to find entry points and architecture.
    """
    import os
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'MarketplaceAI'}
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        match = re.search(r'github\.com/([^/]+)/([^/\s?#]+)', github_url)
        if not match:
            return None
        owner, repo = match.group(1), match.group(2).rstrip('.git').rstrip('/')
        
        result = {
            'readme': '', 
            'languages': [], 
            'description': '', 
            'stars': 0, 
            'repo_name': repo,
            'file_tree': [],
            'entry_points': [],
            'configs': {}
        }

        # 1. Fetch Basic Repo Info & Default Branch
        default_branch = 'main'
        try:
            req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}', headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                result['description'] = data.get('description', '') or ''
                result['stars'] = data.get('stargazers_count', 0)
                default_branch = data.get('default_branch', 'main')
        except Exception:
            return None

        # 2. Fetch Recursive Git Tree
        try:
            req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1', headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                tree_data = json.loads(resp.read().decode())
                # Capture first 200 files for architectural analysis
                result['file_tree'] = [f['path'] for f in tree_data.get('tree', []) if f['type'] == 'blob'][:200]
                
                # Detect structural patterns
                paths_str = " ".join(result['file_tree']).lower()
                if "src/" in paths_str: result['structure'] = "Standard Source Layout"
                elif "app/" in paths_str: result['structure'] = "App-centric Layout"
                
                # Detect entry points
                potential_entries = ["app.py", "main.py", "index.js", "main.js", "index.php", "run.py", "server.js"]
                for p in result['file_tree']:
                    fname = p.split('/')[-1]
                    if fname in potential_entries:
                        result['entry_points'].append(p)
        except Exception:
            pass

        # 3. Fetch Config Files for Deep Tech Analysis
        config_files = {
            'package.json': 'json',
            'requirements.txt': 'text',
            'composer.json': 'json',
            'docker-compose.yml': 'text',
            'app.py': 'text',
            'main.py': 'text'
        }
        for path in result['file_tree']:
            fname = path.split('/')[-1]
            if fname in config_files:
                try:
                    req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={default_branch}', headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        content_data = json.loads(resp.read().decode())
                        if content_data.get('content'):
                            import base64
                            raw_content = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                            result['configs'][fname] = raw_content[:2000] # store snippet
                except Exception:
                    pass

        # 4. Fetch README
        try:
            req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/readme', 
                                         headers={**headers, 'Accept': 'application/vnd.github.v3.raw'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result['readme'] = resp.read().decode('utf-8', errors='ignore')[:5000]
        except Exception:
            pass

        # 5. Fetch Languages
        try:
            req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/languages', headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                langs = json.loads(resp.read().decode())
                result['languages'] = list(langs.keys())
        except Exception:
            pass

        return result
    except Exception:
        return None


def generate_description_from_github(repo_data):
    """
    Synthesize a deep "Autonomous Project Review" based on files and content.
    Works even if README is totally missing.
    """
    parts = []
    
    # 1. Project Identity
    if repo_data.get('description'):
        parts.append(f"### 🎯 Project Mission\n{repo_data['description']}")
    
    # 2. Structural & Architectural Discovery
    tree = repo_data.get('file_tree', [])
    if tree:
        arch_type = "Modern Modular"
        if any("docker" in p.lower() for p in tree): arch_type += " (Containerized)"
        if any("test" in p.lower() or "spec" in p.lower() for p in tree): arch_type += " (Tested Architecture)"
        
        parts.append(f"### 📂 Functional Architecture\n- **Architecture Style**: {arch_type}")
        parts.append(f"- **Directory Layout**: {repo_data.get('structure', 'Self-contained structure')}")
        
        # Identify core modules
        folders = set()
        for p in tree:
            if '/' in p: 
                folder = p.split('/')[0]
                if folder not in ['node_modules', '.git', 'vendor', '__pycache__']:
                    folders.add(folder)
        if folders:
            parts.append(f"- **Key Components Detected**: `{', '.join(list(folders)[:8])}`")

    # 3. Deep "How It Works" Synthesis
    configs = repo_data.get('configs', {})
    how_it_works = []
    
    if configs.get('package.json'):
        how_it_works.append("This appears to be a Node.js/Web application. It uses npm/yarn for dependency management.")
    if configs.get('requirements.txt') or configs.get('app.py'):
        how_it_works.append("Based on the code footprint, this is a Python-powered back-end or CLI tool.")
    
    if repo_data.get('entry_points'):
        how_it_works.append(f"The execution flow starts at `{repo_data['entry_points'][0]}`.")
    
    if how_it_works:
        parts.append("### ⚙️ Operational Logic\n" + " ".join(how_it_works))

    # 4. Content Synthesis (README Fallback)
    if repo_data.get('readme'):
        readme = repo_data['readme']
        readme = re.sub(r'#+\s*', '', readme)
        readme = re.sub(r'```[\s\S]*?```', '', readme)
        paragraphs = [p.strip() for p in readme.split('\n\n') if len(p.strip()) > 40]
        if paragraphs:
            summary_text = '\n\n'.join(paragraphs[:3])[:1000]
            parts.append(f"### 📖 Discovery Insights\n{summary_text}")
    elif tree:
        # Deep tree-based descriptive fallback
        core_tech = repo_data['languages'][0] if repo_data.get('languages') else "modern libraries"
        logic_brief = "standalone utility"
        if any("api" in p.lower() for p in tree): logic_brief = "RESTful API / Service"
        elif any("web" in p.lower() or "public" in p.lower() for p in tree): logic_brief = "Web Application"
        
        parts.append(f"### 📖 Automated Project Profiling\nREADME bulunamadı; ancak projenin `{len(tree)}` aktif dosyası incelendiğinde, bu projenin bir **{logic_brief}** olduğu ve temelinde **{core_tech}** kullandığı anlaşılmaktadır.")
        
        # Categorize folders for the "How it Works" section
        key_dirs = sorted(list(folders))[:5]
        if key_dirs:
            parts.append(f"Proje mimarisi `{', '.join(key_dirs)}` klasörleri etrafında şekilleniyor, bu da modüler ve genişletilebilir bir yapı olduğunu gösteriyor.")

    # 5. Technical DNA
    tech_info = []
    if repo_data.get('languages'):
        tech_info.append(f"**Primary Languages**: {', '.join(repo_data['languages'])}")
    if repo_data.get('stars'):
        tech_info.append(f"**Reliability Signal**: {repo_data['stars']} GitHub Stars")
        
    if tech_info:
        parts.append("### 🛠️ Technical Ecosystem\n" + "\n".join([f"- {i}" for i in tech_info]))
    
    return '\n\n'.join(parts) if parts else "GitHub data processed successfully."


# ─────────── Core Analysis Functions ───────────

def analyze_project(description, tech_stack):
    """Main entry point for AI analysis."""
    text = f"{description} {tech_stack}".lower()
    blob = TextBlob(text)
    
    tags = extract_tags(text, blob)
    complexity = calculate_complexity(text, blob)
    niche_data = predict_revenue_potential(text)
    
    health_score, breakdown = calculate_health_score(description, tags, complexity)
    revenue_range = calculate_revenue_range(niche_data['name'], niche_data['stars'], complexity)
    
    insight = generate_ai_insight(niche_data['name'], complexity, tags)
    suggestion = generate_suggestion(text, tags)
    
    return {
        "tags": ",".join(tags),
        "complexity_score": complexity,
        "niche": niche_data['name'],
        "potential_star": niche_data['stars'],
        "health_score": health_score,
        "health_breakdown": json.dumps(breakdown),
        "revenue_estimate": revenue_range,
        "insight_comment": insight,
        "suggestion": suggestion
    }

def extract_tags(text, blob):
    """Smart Tagging"""
    tags = set()
    for tech in TECH_DICTIONARY:
        if re.search(r'\b' + re.escape(tech) + r'\b', text):
            tags.add(tech.title() if len(tech) > 3 else tech.upper())
    for phrase in blob.noun_phrases:
        if len(phrase.split()) <= 2 and phrase not in tags:
            if len(phrase) > 4:
                tags.add(phrase.title())
                if len(tags) > 10:
                    break
    return list(tags)

def calculate_complexity(text, blob):
    """Complexity Score"""
    words = blob.words
    if not words:
        return "Beginner"
    tech_word_count = sum(1 for word in words if word in TECH_DICTIONARY)
    avg_sentence_length = sum(len(s.words) for s in blob.sentences) / len(blob.sentences) if blob.sentences else 0
    score = (tech_word_count * 2) + (avg_sentence_length * 0.5)
    if score > 20:
        return "Advanced"
    elif score > 10:
        return "Intermediate"
    else:
        return "Beginner"

def predict_revenue_potential(text):
    """Revenue Predictor"""
    niche_scores = {niche: 0 for niche in NICHES}
    for niche, keywords in NICHES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                niche_scores[niche] += 1
    best_niche = max(niche_scores, key=niche_scores.get)
    max_score = niche_scores[best_niche]
    stars = min(5, max(1, max_score + 1))
    if max_score == 0:
        best_niche = "General Software"
        stars = 2
    return {"name": best_niche, "stars": stars}

def calculate_revenue_range(niche, stars, complexity):
    """Predicts a dollar range based on market demand."""
    base = 100
    if niche == "SaaS": base = 500
    elif niche == "Fintech": base = 800
    elif niche == "AI/ML": base = 1000
    elif niche == "E-commerce": base = 300
    
    multiplier = stars * 1.5
    if complexity == "Advanced": multiplier *= 2
    elif complexity == "Intermediate": multiplier *= 1.3
    
    min_val = int(base * multiplier)
    max_val = int(min_val * 2.5)
    
    # Round to nice numbers
    min_val = (min_val // 50) * 50
    max_val = (max_val // 100) * 100
    
    return f"${min_val:,} - ${max_val:,} / mo"

def calculate_health_score(description, tags, complexity):
    """Detailed Project Health metric."""
    breakdown = {
        "documentation": 0,
        "stack_modernity": 0,
        "complexity_depth": 0
    }
    
    # Doc Score
    words = len(description.split())
    if words > 150: breakdown["documentation"] = 100
    elif words > 80: breakdown["documentation"] = 80
    elif words > 30: breakdown["documentation"] = 50
    else: breakdown["documentation"] = 20
    
    # Stack Score
    stack_score = min(100, len(tags) * 15)
    breakdown["stack_modernity"] = stack_score
    
    # Depth Score
    if complexity == "Advanced": breakdown["complexity_depth"] = 100
    elif complexity == "Intermediate": breakdown["complexity_depth"] = 70
    else: breakdown["complexity_depth"] = 40
    
    avg_score = sum(breakdown.values()) // 3
    return avg_score, breakdown

def generate_ai_insight(niche, complexity, tags):
    """Dynamic comment for Insight Box."""
    if not tags:
        return "Bu proje temel seviye bir altyapıya sahip, geliştirilmeye açık."
    techizer = tags[0] if tags else "modern teknolojiler"
    if complexity == "Advanced" and niche == "SaaS":
        return f"Bu proje yüksek oranda kompleks mimari içeriyor. {techizer} tabanlı SaaS olarak ölçeklenmeye %92 oranında uyumlu."
    elif complexity == "Advanced":
        return f"Proje, {techizer} kullanılarak ileri seviye mühendislik kalıplarıyla inşa edilmiş. Özel enterprise çözümler için ideal."
    elif niche == "E-commerce":
        return f"Ticari potansiyeli yüksek bir yapı. {techizer} entegrasyonlarıyla pazar payını kolayca büyütebilir."
    else:
        return f"Hızlı uygulanabilir bir {niche} çözümü. {techizer} mimarisiyle stabil bir çalışma vadediyor."

def generate_suggestion(text, tags):
    """Actionable seller advice."""
    if "docker" not in [t.lower() for t in tags] and "kubernetes" not in [t.lower() for t in tags]:
        return "Açıklamaya 'Docker' veya 'Containerization' süreçlerini eklerseniz, enterprise yatırımcılarının ilgisi %15 artabilir."
    elif "scalability" not in text and "ölçeklenebilir" not in text:
        return "Projenin ne kadar trafik kaldırabildiğinden ('Scalability') bahsederseniz, ürün değerini daha hızlı gösterebilirsiniz."
    else:
        return "İlan açıklamanız çok güçlü. Görsellerle destekleyerek inandırıcılığı artırabilirsiniz."


# ─────────── AI Chat: Project Search ───────────

def search_projects_by_query(query, projects):
    """
    NLP-based project search: takes user's natural language query,
    compares it against all projects, returns sorted matches.
    """
    query_lower = query.lower()
    query_blob = TextBlob(query_lower)
    query_keywords = set(query_blob.words)
    query_nouns = set(query_blob.noun_phrases)
    
    scored = []
    for project in projects:
        score = 0
        text = f"{project.title} {project.description} {project.tech_stack or ''}".lower()
        
        # 1. Direct keyword matching
        for word in query_keywords:
            if len(word) > 2 and word in text:
                score += 4 # increased
        
        # 2. Noun phrase matching (higher weight)
        for phrase in query_nouns:
            if phrase in text:
                score += 8 # increased
        
        # 3. AI Analysis metadata matching (Deep Search)
        if project.ai_analysis:
            analysis_text = f"{project.ai_analysis.tags or ''} {project.ai_analysis.niche or ''} {project.ai_analysis.insight_comment or ''} {project.ai_analysis.suggestion or ''}".lower()
            for word in query_keywords:
                if len(word) > 2 and word in analysis_text:
                    score += 5 # High weight for AI identified tags
            
            # Semantic boost for specific niches
            niche = (project.ai_analysis.niche or '').lower()
            for query_word in query_keywords:
                if query_word in niche:
                    score += 10 # Massive boost if niche matches a keyword
        
        if score > 0:
            # Complexity/Health boost (quality preference)
            if project.ai_analysis:
                if project.ai_analysis.complexity_score == "Advanced":
                    score += 5
                score += (project.ai_analysis.health_score / 20)
            
            scored.append((project, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:5]  # Top 5 results
