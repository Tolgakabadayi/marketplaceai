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
    "electron", "flutter", "react native", "swift", "kotlin"
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
    Fetch public GitHub repo data (README + languages) via GitHub API.
    Returns a dict with 'readme', 'languages', 'description', 'stars'.
    """
    try:
        # Extract owner/repo from URL
        match = re.search(r'github\.com/([^/]+)/([^/\s?#]+)', github_url)
        if not match:
            return None
        owner, repo = match.group(1), match.group(2).rstrip('.git')

        result = {'readme': '', 'languages': [], 'description': '', 'stars': 0, 'repo_name': repo}

        # Fetch repo info
        try:
            req = urllib.request.Request(
                f'https://api.github.com/repos/{owner}/{repo}',
                headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'MarketplaceAI'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                result['description'] = data.get('description', '') or ''
                result['stars'] = data.get('stargazers_count', 0)
        except Exception:
            pass

        # Fetch README
        try:
            req = urllib.request.Request(
                f'https://api.github.com/repos/{owner}/{repo}/readme',
                headers={'Accept': 'application/vnd.github.v3.raw', 'User-Agent': 'MarketplaceAI'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                readme_text = resp.read().decode('utf-8', errors='ignore')
                # Take first 3000 chars for analysis (enough for NLP)
                result['readme'] = readme_text[:3000]
        except Exception:
            pass

        # Fetch languages
        try:
            req = urllib.request.Request(
                f'https://api.github.com/repos/{owner}/{repo}/languages',
                headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'MarketplaceAI'}
            )
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
    Use fetched GitHub data to auto-generate a rich project description.
    """
    parts = []
    
    if repo_data.get('description'):
        parts.append(repo_data['description'])
    
    if repo_data.get('readme'):
        # Clean markdown syntax for a cleaner description
        readme = repo_data['readme']
        readme = re.sub(r'#+\s*', '', readme)   # Remove markdown headers
        readme = re.sub(r'\*\*|__', '', readme)  # Remove bold
        readme = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', readme)  # Links to text
        readme = re.sub(r'```[\s\S]*?```', '', readme)  # Remove code blocks
        readme = re.sub(r'`[^`]+`', '', readme)  # Remove inline code
        readme = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', readme)  # Remove images
        readme = re.sub(r'\n{3,}', '\n\n', readme)  # Reduce whitespace
        
        # Take the first meaningful paragraphs
        paragraphs = [p.strip() for p in readme.split('\n\n') if len(p.strip()) > 30]
        summary = ' '.join(paragraphs[:4])[:1500]
        if summary:
            parts.append(summary)
    
    if repo_data.get('languages'):
        parts.append(f"Built with: {', '.join(repo_data['languages'])}.")
    
    if repo_data.get('stars') and repo_data['stars'] > 0:
        parts.append(f"GitHub Stars: {repo_data['stars']}.")
    
    return ' '.join(parts) if parts else "GitHub repository analysis completed."


# ─────────── Core Analysis Functions ───────────

def analyze_project(description, tech_stack):
    """Main entry point for AI analysis."""
    text = f"{description} {tech_stack}".lower()
    blob = TextBlob(text)
    
    tags = extract_tags(text, blob)
    complexity = calculate_complexity(text, blob)
    niche_data = predict_revenue_potential(text)
    health = calculate_health_score(description, tags, complexity)
    
    insight = generate_ai_insight(niche_data['name'], complexity, tags)
    suggestion = generate_suggestion(text, tags)
    
    return {
        "tags": ",".join(tags),
        "complexity_score": complexity,
        "niche": niche_data['name'],
        "potential_star": niche_data['stars'],
        "health_score": health,
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

def calculate_health_score(description, tags, complexity):
    """Project Health metric."""
    score = 40
    if len(description.split()) > 100:
        score += 20
    elif len(description.split()) > 30:
        score += 10
    score += min(20, len(tags) * 4)
    if complexity == "Intermediate":
        score += 10
    elif complexity == "Advanced":
        score += 20
    return min(100, score)

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
        
        # Direct keyword matching
        for word in query_keywords:
            if len(word) > 2 and word in text:
                score += 3
        
        # Noun phrase matching (higher weight)
        for phrase in query_nouns:
            if phrase in text:
                score += 5
        
        # Niche matching from AI analysis
        if project.ai_analysis:
            analysis_text = f"{project.ai_analysis.tags or ''} {project.ai_analysis.niche or ''} {project.ai_analysis.insight_comment or ''}".lower()
            for word in query_keywords:
                if len(word) > 2 and word in analysis_text:
                    score += 2
        
        if score > 0:
            scored.append((project, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:5]  # Top 5 results
