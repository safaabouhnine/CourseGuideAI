"""
Adapter pour connecter l'UI aux modules existants
"""

import sys
sys.path.append('..')

from src.knowledge_base import KnowledgeBase
from src.nlp_processor import NLPProcessor
from src.sparql_query_builder import SPARQLQueryBuilder
from src.conversation_manager import ConversationManager
import logging

logger = logging.getLogger(__name__)


class BackendAdapter:
    """
    Interface unifiée entre Streamlit et les modules backend
    """
    
    def __init__(self):
        """Initialise tous les composants backend"""
        try:
            self.kb = KnowledgeBase()
            self.nlp = NLPProcessor()
            self.query_builder = SPARQLQueryBuilder(self.kb)
            self.conv_manager = ConversationManager()
            
            logger.info("✅ Backend initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation backend: {e}")
            raise
    
    def test_connection(self):
        """Test la connexion à Fuseki"""
        try:
            query = """
            PREFIX course: <http://www.university.edu/ontology/courses#>
            SELECT (COUNT(?cours) as ?count)
            WHERE {
                ?cours a course:Course .
            }
            """
            result = self.kb.execute_query(query)
            return result is not None
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return False
    
    def get_all_courses(self):
        """Récupère tous les cours depuis Fuseki"""
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?code ?nom ?credits ?duree ?difficulte ?description
        WHERE {
            ?cours a course:Course .
            ?cours course:codeCours ?code .
            ?cours course:nomCours ?nom .
            ?cours course:credits ?credits .
            OPTIONAL { ?cours course:duree ?duree }
            OPTIONAL { ?cours course:difficulte ?difficulte }
            OPTIONAL { ?cours course:description ?description }
        }
        ORDER BY ?code
        """
        
        results = self.kb.execute_query(query)
        
        if not results:
            return []
        
        courses = []
        for row in results:
            courses.append({
                'code': row.get('code', {}).get('value', ''),
                'nom': row.get('nom', {}).get('value', ''),
                'credits': int(row.get('credits', {}).get('value', 0)),
                'duree': int(row.get('duree', {}).get('value', 0)),
                'difficulte': int(row.get('difficulte', {}).get('value', 1)),
                'description': row.get('description', {}).get('value', ''),
                # Extraire domaine et niveau depuis l'ontologie si nécessaire
                'domaine': self._extract_domain(row.get('code', {}).get('value', '')),
                'niveau': self._extract_level(int(row.get('difficulte', {}).get('value', 1)))
            })
        
        return courses
    
    def _extract_domain(self, code):
        """Extrait le domaine depuis le code cours"""
        if code.startswith('IA'):
            return 'Intelligence Artificielle'
        elif code.startswith('WEB'):
            return 'Développement Web'
        elif code.startswith('BD') or code.startswith('BDD'):
            return 'Bases de Données'
        elif code.startswith('MATH'):
            return 'Mathématiques'
        else:
            return 'Informatique'
    
    def _extract_level(self, difficulte):
        """Convertit difficulté en niveau"""
        if difficulte <= 2:
            return 'Débutant'
        elif difficulte <= 4:
            return 'Intermédiaire'
        else:
            return 'Avancé'
    
    def get_course_by_code(self, course_code):
        """Récupère un cours spécifique"""
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?nom ?credits ?duree ?difficulte ?description
        WHERE {{
            ?cours course:codeCours "{course_code}" .
            ?cours course:nomCours ?nom .
            ?cours course:credits ?credits .
            OPTIONAL {{ ?cours course:duree ?duree }}
            OPTIONAL {{ ?cours course:difficulte ?difficulte }}
            OPTIONAL {{ ?cours course:description ?description }}
        }}
        """
        
        results = self.kb.execute_query(query)
        
        if not results or len(results) == 0:
            return None
        
        row = results[0]
        return {
            'code': course_code,
            'nom': row.get('nom', {}).get('value', ''),
            'credits': int(row.get('credits', {}).get('value', 0)),
            'duree': int(row.get('duree', {}).get('value', 0)),
            'difficulte': int(row.get('difficulte', {}).get('value', 1)),
            'description': row.get('description', {}).get('value', ''),
            'domaine': self._extract_domain(course_code),
            'niveau': self._extract_level(int(row.get('difficulte', {}).get('value', 1)))
        }
    
    def get_all_prerequisites(self):
        """Récupère tous les prérequis"""
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?coursCode ?prerequisCode
        WHERE {
            ?cours course:aPrerequis ?prerequis .
            ?cours course:codeCours ?coursCode .
            ?prerequis course:codeCours ?prerequisCode .
        }
        """
        
        results = self.kb.execute_query(query)
        
        if not results:
            return []
        
        return [(row['coursCode']['value'], row['prerequisCode']['value']) 
                for row in results]
    
    def get_prerequisites_for_course(self, course_code):
        """Récupère les prérequis d'un cours spécifique"""
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?prerequisCode ?prerequisNom
        WHERE {{
            ?cours course:codeCours "{course_code}" .
            ?cours course:aPrerequis ?prerequis .
            ?prerequis course:codeCours ?prerequisCode .
            ?prerequis course:nomCours ?prerequisNom .
        }}
        """
        
        results = self.kb.execute_query(query)
        
        if not results:
            return []
        
        return [{'code': row['prerequisCode']['value'], 
                 'nom': row['prerequisNom']['value']} 
                for row in results]
    
    def get_statistics(self):
        """Calcule des statistiques sur la base"""
        courses = self.get_all_courses()
        prerequisites = self.get_all_prerequisites()
        
        # Compter par domaine
        domains = {}
        for course in courses:
            domain = course['domaine']
            domains[domain] = domains.get(domain, 0) + 1
        
        # Compter par niveau
        levels = {}
        for course in courses:
            level = course['niveau']
            levels[level] = levels.get(level, 0) + 1
        
        return {
            'total_courses': len(courses),
            'domains': domains,
            'levels': levels,
            'total_prerequisites': len(prerequisites)
        }
    
    def process_chat_message(self, user_message):
        """Traite un message utilisateur via le système NLP"""
        try:
            response = self.conv_manager.process_message(user_message)
            return {
                'success': True,
                'response': response,
                'context': self.conv_manager.get_context_summary()
            }
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            return {
                'success': False,
                'response': f"Erreur: {str(e)}",
                'context': None
            }
    
    def reset_conversation(self):
        """Réinitialise la conversation"""
        self.conv_manager.clear_history()