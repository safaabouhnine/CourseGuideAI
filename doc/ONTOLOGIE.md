# Documentation de l'Ontologie Universitaire

## 📚 Vue d'Ensemble

Cette ontologie modélise un système de cours universitaires avec leurs relations, prérequis, et compétences enseignées.

**IRI de l'ontologie :** `http://www.university.edu/ontology/courses`

---

## 🏗️ Structure de l'Ontologie

### Classes Principales

#### 1. Course (Cours)
Représente un cours universitaire.

**Sous-classes :**
- `CourseInformatique` : Cours d'informatique
  - `CourseIA` : Cours d'intelligence artificielle
  - `CourseWeb` : Cours de développement web
  - `CourseBDD` : Cours de bases de données
- `CourseMathematiques` : Cours de mathématiques

#### 2. Student (Étudiant)
Représente un étudiant.

#### 3. Skill (Compétence)
Représente une compétence technique ou transversale.

#### 4. Domain (Domaine)
Représente un domaine d'études (IA, Web, BDD, etc.).

#### 5. Level (Niveau)
Représente le niveau de difficulté d'un cours.

**Instances :**
- `Debutant`
- `Intermediaire`
- `Avance`

---

## 🔗 Relations (Object Properties)

| Propriété | Domain | Range | Description |
|-----------|--------|-------|-------------|
| `aPrerequis` | Course | Course | Un cours prérequis pour un autre |
| `enseigneCompetence` | Course | Skill | Compétences enseignées |
| `appartientADomaine` | Course | Domain | Domaine du cours |
| `aNiveau` | Course | Level | Niveau de difficulté |
| `possèdeCompetence` | Student | Skill | Compétences de l'étudiant |
| `aInteretPour` | Student | Domain | Intérêts de l'étudiant |
| `aSuivi` | Student | Course | Cours suivis |

---

## 📊 Attributs (Data Properties)

### Pour Course

| Propriété | Type | Description |
|-----------|------|-------------|
| `nomCours` | string | Nom du cours |
| `codeCours` | string | Code unique (ex: IA-401) |
| `credits` | integer | Crédits ECTS |
| `duree` | integer | Durée en heures |
| `difficulte` | integer | Niveau 1-5 |
| `description` | string | Description détaillée |

### Pour Student

| Propriété | Type | Description |
|-----------|------|-------------|
| `nomEtudiant` | string | Nom complet |
| `emailEtudiant` | string | Email institutionnel |

---

## 🔍 Exemples de Requêtes SPARQL

### 1. Lister tous les cours
```sparql
PREFIX course: <http://www.university.edu/ontology/courses#>

SELECT ?code ?nom ?credits
WHERE {
  ?cours a course:Course .
  ?cours course:codeCours ?code .
  ?cours course:nomCours ?nom .
  ?cours course:credits ?credits .
}
ORDER BY ?code
```

### 2. Trouver les prérequis d'un cours
```sparql
PREFIX course: <http://www.university.edu/ontology/courses#>

SELECT ?prerequisCode ?prerequisNom
WHERE {
  course:IA-401 course:aPrerequis ?prerequis .
  ?prerequis course:codeCours ?prerequisCode .
  ?prerequis course:nomCours ?prerequisNom .
}
```

### 3. Cours par domaine
```sparql
PREFIX course: <http://www.university.edu/ontology/courses#>

SELECT ?code ?nom
WHERE {
  ?cours course:appartientADomaine course:IntelligenceArtificielle .
  ?cours course:codeCours ?code .
  ?cours course:nomCours ?nom .
}
```

### 4. Compétences enseignées par un cours
```sparql
PREFIX course