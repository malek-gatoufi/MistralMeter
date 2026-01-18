# 🎯 Application pour le poste de Software Engineer Intern chez Mistral AI

**Candidat:** Malek Gatoufi  
**Projet:** MistralMeter - Production-Grade LLM Evaluation Platform  
**Repository:** https://github.com/malek-gatoufi/MistralMeter
**Date:** Janvier 2026

---

## 📦 Projet Soumis

### MistralMeter - Plateforme d'Évaluation LLM

**Technologies utilisées:**
- ✅ **Backend:** Python + FastAPI (async, type-safe avec Pydantic)
- ✅ **Frontend:** Nuxt 3 + TypeScript + Tailwind CSS
- ✅ **Containerisation:** Docker/Podman avec docker-compose
- ✅ **API Mistral:** Intégration complète avec le SDK officiel

**Scope du projet:**
- Évaluation de qualité des réponses LLM (LLM-as-Judge)
- Mesure de performance (latency, TTFT, throughput)
- Analyse statistique avec variance multi-runs
- Comparaison A/B de modèles Mistral
- Dashboard interactif avec streaming SSE
- Gestion de datasets et batch evaluation

---

## ✨ Pourquoi ce projet?

### 1. Résout un problème réel
En production, évaluer les LLMs est complexe:
- Non-déterminisme des réponses
- Trade-offs entre qualité, latence et coût
- Biais des juges automatiques

MistralMeter rend ces trade-offs **explicites et mesurables**.

### 2. Démontre des compétences techniques solides
- Architecture full-stack moderne et scalable
- APIs REST bien conçues avec documentation OpenAPI
- Code type-safe (Pydantic + TypeScript)
- Containerisation et déploiement facile
- UI/UX soignée avec Tailwind

### 3. Best Practices respectées
- ✅ README détaillé avec Quick Start
- ✅ Facile à tester (docker-compose up)
- ✅ Code structuré et maintenable
- ✅ Documentation technique complète
- ✅ Séparation des responsabilités (modèle évalué ≠ juge)

---

## 🚀 Quick Start pour les Reviewers

### Lancement en 2 minutes:

```bash
# 1. Clone
git clone git@github.com:malek-gatoufi/MistralMeter.git
cd mistral-eval-platform

# 2. Ajouter la clé API
echo "MISTRAL_API_KEY=your_key_here" > .env

# 3. Lancer tout avec Docker
docker-compose up -d
```

**Services disponibles:**
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Test rapide sans Docker:

```bash
# Backend seulement
pip install -r requirements.txt
cp .env.example .env  # Ajouter votre MISTRAL_API_KEY
uvicorn app.main:app --reload

# Puis tester dans le navigateur:
# http://localhost:8000/docs
```

---

## 📖 Documentation

Le projet inclut une documentation complète:

### README principal
- Vue d'ensemble du projet
- Justification technique
- Quick Start complet
- Référence API
- Architecture
- Future work

### Documentation interne (dans /docs - privé)
- `ENGINEERING_DECISIONS.md` - Choix architecturaux
- `FEATURES_SUMMARY.md` - Liste des fonctionnalités
- `FRONTEND_IMPROVEMENTS.md` - Améliorations frontend
- `experiments.md` - Notes de développement
- `Project.md` - Notes du projet

### Documentation conceptuelle (dans /guides - public)
- 9 documents expliquant les concepts d'évaluation LLM
- Topics: LLM-as-judge, variance, tokenization, streaming, etc.

---

## 💡 Highlights Techniques

### 1. LLM-as-Judge avec Séparation des Modèles
```python
# Le modèle évalué ≠ le modèle juge (évite le biais)
{
  "model": "mistral-small-latest",      # Évalué
  "judge_model": "mistral-large-latest" # Juge
}
```

### 2. Mesure de Variance Multi-Runs
```python
# Analyse statistique sur 5 runs
{
  "runs": 5,
  "metrics": {
    "quality": {
      "mean": 8.2,
      "std_dev": 0.4,
      "p50": 8.3,
      "p95": 8.7
    }
  }
}
```

### 3. Streaming SSE pour UI Réactive
```python
@app.post("/stream")
async def stream_tokens():
    async for chunk in stream:
        yield f"data: {json.dumps(chunk)}\n\n"
```

### 4. Architecture Async-First
```python
# FastAPI async pour gérer les appels IO-bound
async def evaluate_prompt(prompt: str):
    async with mistral_client as client:
        response = await client.chat(...)
```

---

## 🎯 Alignment avec l'Offre Mistral

### Compétences demandées:

✅ **Full-stack (Python/TypeScript)** → FastAPI + Nuxt 3  
✅ **UX de qualité** → Dashboard Tailwind soigné  
✅ **Solutions basées sur Chat APIs** → Intégration complète SDK Mistral  
✅ **Adaptation rapide** → Projet complet réalisé en temps limité  
✅ **Outils pour développeurs** → API docs, CLI-friendly, containerisé

### Types de projets suggérés:

**Python Project avec FastAPI** ✅
- Utilise FastAPI pour l'API backend
- Intègre le SDK Mistral
- Démontre des patterns de production

**Flexible avec TypeScript** ✅
- Frontend Nuxt 3 + TypeScript
- Composables réutilisables
- Type-safety complète

---

## 🔮 Évolution Potentielle

Si ce projet était adopté en interne chez Mistral, il pourrait évoluer vers:

### Court terme:
- Pipeline d'évaluation continue sur chaque release
- Système de détection de régression qualité
- Export de résultats pour analyse externe

### Moyen terme:
- Dashboard client pour utilisateurs Enterprise
- A/B testing framework pour optimisation prompts
- Intégration avec pipelines RLHF

### Long terme:
- Support multi-providers (benchmarking compétitif)
- Évaluation de fine-tuned models
- Métriques RAG et agents multi-steps

---

## 📊 Statistiques du Projet

```bash
# Code statistics
Backend:  ~800 lignes Python (app/)
Frontend: ~1200 lignes TypeScript/Vue (frontend/)
Docs:     9 documents techniques + README complet
Tests:    [À ajouter selon vos tests]
```

**Temps de développement:** ~15-20 heures  
**Complexité:** Production-grade, pas over-engineered  
**Testabilité:** Docker one-command deployment

---

## 🎓 Ce que j'ai Appris

### Techniques:
- Patterns d'évaluation LLM (LLM-as-judge, variance analysis)
- Optimisation de latence et throughput
- Streaming SSE pour UI temps-réel
- Architecture async-first en Python

### Engineering:
- Trade-offs architecture (simplicité vs features)
- Documentation pour onboarding rapide
- Containerisation pour reproductibilité
- API design pour developer experience

### Business:
- Problématiques réelles des équipes LLM en production
- Importance de la mesure vs l'intuition
- Besoins d'évaluation pour clients Enterprise

---

## 🚀 Prochaines Étapes

### Pour le push GitHub:

1. ✅ Vérifier que `.gitignore` exclut bien:
   - `.env` (secrets)
   - `reports/` (docs internes)
   - `__pycache__/`, `.venv/`

2. ✅ S'assurer que le README est à jour

3. 📤 Push sur GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: MistralMeter evaluation platform"
   git remote add origin <votre-repo>
   git push -u origin main
   ```

4. 📧 Dans l'email de candidature, inclure:
   - Lien vers le repo GitHub
   - Ce document APPLICATION.md
   - Bref pitch (2-3 phrases)

### Email Template:

```
Objet: Software Engineer Intern - MistralMeter Project

Bonjour,

Je soumets ma candidature pour le poste de Software Engineer Intern chez Mistral AI.

Projet: MistralMeter - Production-Grade LLM Evaluation Platform
GitHub: [VOTRE_LIEN]

MistralMeter est une plateforme d'évaluation LLM construite avec FastAPI + Nuxt 3, 
démontrant des compétences en full-stack development et une compréhension des défis 
d'évaluation LLM en production (variance, LLM-as-judge, metrics collection).

Le projet est entièrement containerisé et démarre avec une seule commande: 
`docker-compose up`.

Documentation complète dans le README.

Cordialement,
Malek Gatoufi
```

---

## ✨ Pourquoi Mistral?

### Vision technique
Mistral combine excellence technique (Mixtral MoE, performance SOTA) et pragmatisme 
(modèles optimisés pour production). C'est exactement le type d'environnement où je 
veux apprendre.

### Impact européen
Contribuer à un champion européen de l'IA qui prouve que l'Europe peut rivaliser 
techniquement avec les géants US.

### Open Science
L'engagement de Mistral vers l'open source (Mistral 7B, Mixtral) aligne avec mes 
valeurs sur la démocratisation de l'IA.

### Croissance rapide
Environnement startup où l'impact individuel est élevé et l'apprentissage accéléré.

---

**🎯 Ready to push and apply!**

---

*Document créé le 17 janvier 2026*
