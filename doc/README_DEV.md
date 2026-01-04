# README_DEV.md — CourseGuideAI (Dev / Équipe)

## 1) Ce qui est déjà fait (par moi)
- Apache Jena **Fuseki** est configuré et lancé via **Docker Compose**.
- Le dataset Fuseki **`university`** est utilisé.
- La base de connaissance RDF est **peuplée** depuis les CSV (`cours`, `prerequis`, `competences`).
- Correction appliquée : chaque cours est inséré avec `rdf:type course:Course` + son type spécifique (CourseIA, CourseWeb, etc.).  
  Résultat : `Nombre de cours : 15` (ok).
- Les tests de la base passent : `tests/test_knowledge_base.py` (connexion, liste des cours, cours par code, prérequis).

---

## 2) Ce que les autres membres peuvent faire sans Protégé
Protégé n’est **pas nécessaire** pour continuer le développement applicatif.

Les membres peuvent :
- interroger Fuseki via SPARQL (Query)
- intégrer la base dans le code Python via `src/knowledge_base.py`
- développer NLP / chatbot :
  - extraire entités (ex: code cours `IA-401`)
  - détecter l’intention (ex: “prérequis de IA-401”)
  - mapper intention → requête SPARQL
  - appeler `KnowledgeBase.execute_query()` et formater la réponse

---

## 3) URLs / Identifiants Fuseki
Interface web :  
- http://localhost:3030

Dataset : `university`

Endpoints :
- Query : `http://localhost:3030/university/query`
- Update : `http://localhost:3030/university/update`

Authentification admin (pages Manage/Update) :
- Username : `admin`
- Password : `admin123`

---

## 4) Commandes indispensables pour démarrer (nouveau membre)

### A) Lancer Fuseki
Dans le dossier où est `docker-compose.yml` :
```bash
docker compose up -d
