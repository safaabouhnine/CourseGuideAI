"""
Vocabulaire RDF pour l'ontologie des cours universitaires
"""
from rdflib import Namespace

# Namespace de base de l'ontologie
COURSE_NS = Namespace("http://www.university.edu/ontology/courses#")

# Classes principales
COURSE = COURSE_NS.Course
COURSE_IA = COURSE_NS.CourseIA
COURSE_WEB = COURSE_NS.CourseWeb
COURSE_BDD = COURSE_NS.CourseBDD
COURSE_MATH = COURSE_NS.CourseMathematiques
COURSE_INFO = COURSE_NS.CourseInformatique

STUDENT = COURSE_NS.Student
SKILL = COURSE_NS.Skill
DOMAIN = COURSE_NS.Domain
LEVEL = COURSE_NS.Level

# Niveaux
DEBUTANT = COURSE_NS.Debutant
INTERMEDIAIRE = COURSE_NS.Intermediaire
AVANCE = COURSE_NS.Avance

# Domaines
INTELLIGENCE_ARTIFICIELLE = COURSE_NS.IntelligenceArtificielle
DEVELOPPEMENT_WEB = COURSE_NS.DeveloppementWeb
BASE_DE_DONNEES = COURSE_NS.BaseDeDonnees
INFORMATIQUE = COURSE_NS.Informatique
MATHEMATIQUES = COURSE_NS.Mathematiques

# Object Properties (Relations)
A_PREREQUIS = COURSE_NS.aPrerequis
ENSEIGNE_COMPETENCE = COURSE_NS.enseigneCompetence
APPARTIENT_A_DOMAINE = COURSE_NS.appartientADomaine
A_NIVEAU = COURSE_NS.aNiveau
POSSEDE_COMPETENCE = COURSE_NS.possèdeCompetence
A_INTERET_POUR = COURSE_NS.aInteretPour
A_SUIVI = COURSE_NS.aSuivi

# Data Properties (Attributs)
NOM_COURS = COURSE_NS.nomCours
CODE_COURS = COURSE_NS.codeCours
CREDITS = COURSE_NS.credits
DUREE = COURSE_NS.duree
DIFFICULTE = COURSE_NS.difficulte
DESCRIPTION = COURSE_NS.description

NOM_ETUDIANT = COURSE_NS.nomEtudiant
EMAIL_ETUDIANT = COURSE_NS.emailEtudiant

NOM_COMPETENCE = COURSE_NS.nomCompetence
NOM_DOMAINE = COURSE_NS.nomDomaine