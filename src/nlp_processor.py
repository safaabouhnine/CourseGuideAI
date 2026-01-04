import spacy
import re
from typing import Dict, List, Any, Optional

class NLPProcessor:
    def __init__(self):
        """Initialise le modèle spaCy français"""
        try:
            self.nlp = spacy.load("fr_core_news_md")
            print("✅ Modèle spaCy chargé avec succès")
        except OSError:
            print("❌ Erreur: Modèle spaCy non trouvé. Exécutez: python -m spacy download fr_core_news_md")
            raise
        
        # Dictionnaires de mots-clés pour la détection d'intention
        self.intent_keywords = {
            'recherche_cours': [
                'cherche', 'trouve', 'trouver', 'recherche', 'cours', 
                'recommande', 'suggère', 'propose', 'montre', 'liste',
                'affiche', 'voir', 'consulter', 'quels cours', 'quel cours'
            ],
            'verifier_prerequis': [
                'prérequis', 'prerequis', 'avant', 'nécessaire', 
                'besoin', 'puis-je suivre', 'peux suivre', 'peux-je',
                'autorisé', 'commencer', 'débuter'
            ],
            'parcours_apprentissage': [
                'parcours', 'chemin', 'progression', 'apprendre',
                'devenir', 'expert', 'maîtriser', 'commencer',
                'par où commencer', 'comment apprendre', 'plan'
            ],
            'info_cours': [
                'information', 'détails', 'description', 'c\'est quoi',
                'parle de', 'concerne', 'sujet', 'contenu', 'à propos'
            ],
            'liste_competences': [
                'compétences', 'skills', 'apprendre', 'enseigne',
                'permet d\'apprendre', 'acquérir', 'développer'
            ]
        }
        
        # Domaines connus
        self.domaines = [
            'intelligence artificielle', 'ia', 'ai',
            'machine learning', 'apprentissage automatique',
            'web', 'développement web', 'dev web',
            'base de données', 'bdd', 'database',
            'réseau', 'réseaux', 'network',
            'sécurité', 'cybersécurité', 'security'
        ]
        
        # Niveaux
        self.niveaux = ['débutant', 'intermédiaire', 'avancé', 'expert']
    
    def extract_intent(self, text: str) -> str:
        """
        Extrait l'intention principale du message utilisateur
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Intention détectée (str)
        """
        text_lower = text.lower()
        
        # Calculer les scores pour chaque intention
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Retourner l'intention avec le score le plus élevé
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        # Intention par défaut
        return 'recherche_cours'
    
    def extract_course_code(self, text: str) -> Optional[str]:
        """
        Extrait le code de cours (ex: IA-401, WEB-301)
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Code du cours ou None
        """
        # Pattern: 2-4 lettres majuscules, tiret, 3 chiffres
        pattern = r'\b([A-Z]{2,4}-\d{3})\b'
        match = re.search(pattern, text.upper())
        
        if match:
            return match.group(1)
        
        # Chercher aussi sans tiret (ex: IA401 -> IA-401)
        pattern_no_dash = r'\b([A-Z]{2,4})(\d{3})\b'
        match = re.search(pattern_no_dash, text.upper())
        
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        
        return None
    
    def extract_domain(self, text: str) -> Optional[str]:
        """
        Extrait le domaine d'étude mentionné
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Domaine ou None
        """
        text_lower = text.lower()
        
        for domaine in self.domaines:
            if domaine in text_lower:
                # Normaliser le domaine
                if domaine in ['ia', 'ai', 'intelligence artificielle']:
                    return 'Intelligence Artificielle'
                elif domaine in ['web', 'développement web', 'dev web']:
                    return 'Web'
                elif domaine in ['machine learning', 'apprentissage automatique']:
                    return 'Machine Learning'
                elif domaine in ['base de données', 'bdd', 'database']:
                    return 'Base de Données'
                elif domaine in ['réseau', 'réseaux', 'network']:
                    return 'Réseaux'
                elif domaine in ['sécurité', 'cybersécurité', 'security']:
                    return 'Sécurité'
        
        return None
    
    def extract_level(self, text: str) -> Optional[str]:
        """
        Extrait le niveau mentionné
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Niveau ou None
        """
        text_lower = text.lower()
        
        for niveau in self.niveaux:
            if niveau in text_lower:
                return niveau.capitalize()
        
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extrait les compétences mentionnées
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Liste des compétences
        """
        doc = self.nlp(text)
        skills = []
        
        # Mots-clés de compétences courantes
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'sql',
            'deep learning', 'neural networks', 'nlp',
            'algorithme', 'structure de données', 'optimisation',
            'base de données', 'réseau', 'sécurité'
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.capitalize())
        
        return skills
    
    def process_message(self, text: str) -> Dict[str, Any]:
        """
        Traite un message complet et extrait toutes les informations
        
        Args:
            text: Message de l'utilisateur
            
        Returns:
            Dictionnaire avec intention et entités extraites
        """
        result = {
            'text': text,
            'intent': self.extract_intent(text),
            'entities': {
                'course_code': self.extract_course_code(text),
                'domain': self.extract_domain(text),
                'level': self.extract_level(text),
                'skills': self.extract_skills(text)
            }
        }
        
        return result
    
    def intent_to_sparql_type(self, intent: str) -> str:
        """
        Mappe une intention vers un type de requête SPARQL
        
        Args:
            intent: Intention détectée
            
        Returns:
            Type de requête SPARQL
        """
        mapping = {
            'recherche_cours': 'search_courses',
            'verifier_prerequis': 'check_prerequisites',
            'parcours_apprentissage': 'learning_path',
            'info_cours': 'course_info',
            'liste_competences': 'list_skills'
        }
        
        return mapping.get(intent, 'search_courses')


# Test du module si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du NLPProcessor\n")
    
    processor = NLPProcessor()
    
    # Tests
    test_messages = [
        "Je cherche des cours en intelligence artificielle",
        "Est-ce que je peux suivre le cours IA-401 ?",
        "Je veux devenir expert en Machine Learning, par où commencer ?",
        "Quels sont les prérequis pour WEB301 ?",
        "Montre-moi des cours de niveau avancé en web"
    ]
    
    for msg in test_messages:
        print(f"📨 Message: {msg}")
        result = processor.process_message(msg)
        print(f"   Intent: {result['intent']}")
        print(f"   Entités: {result['entities']}")
        print(f"   Type SPARQL: {processor.intent_to_sparql_type(result['intent'])}")
        print()