"""
Adapteur Backend pour l'interface Streamlit
Connecte l'UI aux modules Phase 1, 2 et 3
Membre 4 : Interface & Visualisation
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Ajouter le chemin src
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports Phase 1 (Ontologie & KB)
from src.knowledge_base import KnowledgeBase

# Imports Phase 2 (NLP)
from src.nlp_processor import NLPProcessor
from src.conversation_manager import ConversationManager

# Imports Phase 3 (Agent IA & Raisonnement)
from src.recommendation_agent import RecommendationAgent
from src.sparql_reasoner import SPARQLReasoner
from src.sparql_query_builder import SPARQLQueryBuilder
from src.performance_monitor import get_monitor

logger = logging.getLogger(__name__)


class BackendAdapter:
    """
    Adapteur unifié entre l'interface Streamlit et tous les modules backend
    """
    
    def __init__(self):
        """Initialise tous les composants backend"""
        logger.info("🚀 Initialisation du BackendAdapter...")
        
        try:
            # Phase 1: Base de Connaissance
            self.kb = KnowledgeBase()
            logger.info("✅ KnowledgeBase initialisée")
            
            # Phase 2: NLP
            self.nlp = NLPProcessor()
            logger.info("✅ NLPProcessor initialisé")
            
            # Phase 2: Query Builder
            self.query_builder = SPARQLQueryBuilder(self.kb)
            logger.info("✅ SPARQLQueryBuilder initialisé")
            
            # Phase 2: Conversation Manager
            self.conv_manager = ConversationManager()
            logger.info("✅ ConversationManager initialisé")
            
            # Phase 3: Reasoner
            self.reasoner = SPARQLReasoner(self.kb)
            logger.info("✅ SPARQLReasoner initialisé")
            
            # Phase 3: Recommendation Agent
            self.agent = RecommendationAgent(self.kb)
            logger.info("✅ RecommendationAgent initialisé")
            
            # Performance Monitor
            self.monitor = get_monitor()
            logger.info("✅ PerformanceMonitor activé")
            
            logger.info("🎉 Backend complètement initialisé!")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation backend: {e}")
            raise
    
    # ==================== TEST & CONNEXION ====================
    
    def test_connection(self) -> bool:
        """Test la connexion à Fuseki"""
        try:
            return self.kb.test_connection()
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return False
    
    # ==================== GESTION DES COURS ====================
    
    def get_all_courses(self) -> List[Dict]:
        """Récupère tous les cours depuis Fuseki"""
        try:
            courses = self.kb.get_all_courses()
            
            # Enrichir avec domaine et niveau
            enriched = []
            for course in courses:
                code = course.get('code', {}).get('value', '')
                enriched.append({
                    'code': code,
                    'nom': course.get('nom', {}).get('value', ''),
                    'credits': int(course.get('credits', {}).get('value', 0)),
                    'duree': int(course.get('duree', {}).get('value', 0)),
                    'difficulte': int(course.get('difficulte', {}).get('value', 1)),
                    'description': course.get('description', {}).get('value', ''),
                    'domaine': self._extract_domain(code),
                    'niveau': self._extract_level(int(course.get('difficulte', {}).get('value', 1)))
                })
            
            return enriched
            
        except Exception as e:
            logger.error(f"Erreur get_all_courses: {e}")
            return []
    
    def get_course_by_code(self, course_code: str) -> Optional[Dict]:
        """Récupère un cours spécifique"""
        try:
            course = self.kb.get_course_by_code(course_code)
            
            if not course:
                return None
            
            return {
                'code': course_code,
                'nom': course.get('nom', {}).get('value', ''),
                'credits': int(course.get('credits', {}).get('value', 0)),
                'duree': int(course.get('duree', {}).get('value', 0)),
                'difficulte': int(course.get('difficulte', {}).get('value', 1)),
                'description': course.get('description', {}).get('value', ''),
                'domaine': self._extract_domain(course_code),
                'niveau': self._extract_level(int(course.get('difficulte', {}).get('value', 1)))
            }
            
        except Exception as e:
            logger.error(f"Erreur get_course_by_code({course_code}): {e}")
            return None
    
    def search_courses(self, query: str) -> List[Dict]:
        """Recherche de cours par texte libre"""
        try:
            entities = self.nlp.extract_entities(query)
            results = self.query_builder.search_courses(entities)
            
            # Formatter les résultats
            formatted = []
            for result in results:
                code = result.get('code', '')
                formatted.append({
                    'code': code,
                    'nom': result.get('label', ''),
                    'credits': int(result.get('credits', 0)),
                    'description': result.get('description', ''),
                    'domaine': self._extract_domain(code),
                    'niveau': self._extract_level(3)  # Default
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Erreur search_courses: {e}")
            return []
    
    # ==================== GESTION DES PRÉREQUIS ====================
    
    def get_all_prerequisites(self) -> List[tuple]:
        """Récupère toutes les relations de prérequis"""
        try:
            all_courses = self.get_all_courses()
            prerequisites = []
            
            for course in all_courses:
                prereqs = self.get_prerequisites_for_course(course['code'])
                for prereq in prereqs:
                    prerequisites.append((course['code'], prereq['code']))
            
            return prerequisites
            
        except Exception as e:
            logger.error(f"Erreur get_all_prerequisites: {e}")
            return []
    
    def get_prerequisites_for_course(self, course_code: str) -> List[Dict]:
        """Récupère les prérequis directs d'un cours"""
        try:
            prereqs = self.kb.get_prerequisites(course_code)
            
            formatted = []
            for prereq in prereqs:
                formatted.append({
                    'code': prereq.get('codePrerequis', {}).get('value', ''),
                    'nom': prereq.get('nomPrerequis', {}).get('value', '')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Erreur get_prerequisites_for_course({course_code}): {e}")
            return []
    
    def get_all_prerequisites_recursive(self, course_code: str) -> List[Dict]:
        """Récupère TOUS les prérequis (récursifs)"""
        try:
            prereqs = self.reasoner.get_all_prerequisites_recursive(course_code)
            
            formatted = []
            for prereq in prereqs:
                formatted.append({
                    'code': prereq.get('codePrerequis', {}).get('value', ''),
                    'nom': prereq.get('nomPrerequis', {}).get('value', '')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Erreur get_all_prerequisites_recursive: {e}")
            return []
    
    # ==================== STATISTIQUES ====================
    
    def get_statistics(self) -> Dict:
        """Calcule des statistiques sur la base"""
        try:
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
            
        except Exception as e:
            logger.error(f"Erreur get_statistics: {e}")
            return {
                'total_courses': 0,
                'domains': {},
                'levels': {},
                'total_prerequisites': 0
            }
    
    # ==================== CHAT & RECOMMANDATIONS ====================
    
    def process_chat_message(self, user_message: str) -> Dict[str, Any]:
        """
        Traite un message utilisateur via le système NLP + Agent
        """
        try:
            import time
            start_time = time.time()
        
            # Utiliser le query_builder directement
            result = self.query_builder.process_user_query(user_message)
            response_text = result.get('message', 'Réponse non disponible')
            
            # Extraire les intentions pour enrichir la réponse
            nlp_result = self.nlp.process_message(user_message)
            intent = nlp_result.get('intent', 'unknown')
            
            # Enregistrer la performance
            query_time = time.time() - start_time
            self.monitor.record_query(query_time, from_cache=False)
            
            return {
                'success': True,
                'response': response_text,
                'intent': intent,
                'query_time': query_time
            }
            
        except Exception as e:
            logger.error(f"Erreur process_chat_message: {e}")
            return {
                'success': False,
                'response': f"Erreur: {str(e)}",
                'intent': 'error',
                'query_time': 0
            }
    
    def get_recommendations_for_profile(self, profile: Dict) -> List[Dict]:
        """
        Génère des recommandations basées sur un profil étudiant
        
        Args:
            profile: Dict avec 'interests', 'skills', 'level'
        """
        try:
            # Créer un URI temporaire pour l'étudiant
            student_uri = "http://www.university.edu/ontology/courses#TempStudent"
            
            # Utiliser l'agent de recommandation
            recommendations = self.agent.recommend_by_profile(
                student_uri, 
                max_results=5
            )
            
            self.monitor.record_recommendation()
            
            # Formatter pour l'UI
            formatted = []
            for rec in recommendations:
                course = rec['course']
                formatted.append({
                    'code': course.get('code', {}).get('value', ''),
                    'nom': course.get('nom', {}).get('value', ''),
                    'score': rec['score'],
                    'reason': rec['reason'],
                    'credits': int(course.get('credits', {}).get('value', 0))
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Erreur get_recommendations_for_profile: {e}")
            return []
    
    def get_learning_path(self, goal_course: str) -> Dict:
        """
        Calcule un parcours d'apprentissage vers un cours objectif
        """
        try:
            # Utiliser le reasoner pour calculer le parcours
            path = self.reasoner.compute_learning_path(goal_course)
            
            # Formatter pour l'UI
            formatted_path = []
            for course in path:
                formatted_path.append({
                    'code': course.get('code', {}).get('value', ''),
                    'nom': course.get('nom', {}).get('value', ''),
                    'credits': int(course.get('credits', {}).get('value', 0)),
                    'domaine': self._extract_domain(course.get('code', {}).get('value', '')),
                    'niveau': self._extract_level(3)
                })
            
            return {
                'success': True,
                'path': formatted_path,
                'total_courses': len(formatted_path),
                'total_credits': sum(c['credits'] for c in formatted_path)
            }
            
        except Exception as e:
            logger.error(f"Erreur get_learning_path: {e}")
            return {
                'success': False,
                'path': [],
                'total_courses': 0,
                'total_credits': 0,
                'error': str(e)
            }
    
    def get_similar_courses(self, course_code: str, limit: int = 5) -> List[Dict]:
        """Trouve des cours similaires"""
        try:
            similar = self.agent.find_similar_courses(course_code, limit=limit)
            
            formatted = []
            for course in similar:
                formatted.append({
                    'code': course.get('codeSimilaire', {}).get('value', ''),
                    'nom': course.get('nomSimilaire', {}).get('value', ''),
                    'domaine': course.get('domainLabel', {}).get('value', '')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Erreur get_similar_courses: {e}")
            return []
    
    # ==================== GESTION CONVERSATION ====================
    
    def reset_conversation(self):
        """Réinitialise la conversation"""
        try:
            self.conv_manager.reset()
            logger.info("💬 Conversation réinitialisée")
        except Exception as e:
            logger.error(f"Erreur reset_conversation: {e}")
    
    def get_conversation_history(self) -> List[Dict]:
        """Récupère l'historique de conversation"""
        try:
            return self.conv_manager.get_history()
        except Exception as e:
            logger.error(f"Erreur get_conversation_history: {e}")
            return []
    
    def get_conversation_context(self) -> Optional[Dict]:
        """Récupère le contexte actuel"""
        try:
            return self.conv_manager.get_context()
        except Exception as e:
            logger.error(f"Erreur get_conversation_context: {e}")
            return None
    
    # ==================== PERFORMANCE ====================
    
    def get_performance_report(self) -> Dict:
        """Récupère le rapport de performance"""
        try:
            return self.monitor.get_report()
        except Exception as e:
            logger.error(f"Erreur get_performance_report: {e}")
            return {}
    
    # ==================== UTILITAIRES PRIVÉS ====================
    
    def _extract_domain(self, code: str) -> str:
        """Extrait le domaine depuis le code cours"""
        if code.startswith('IA'):
            return 'Intelligence Artificielle'
        elif code.startswith('WEB'):
            return 'Développement Web'
        elif code.startswith('BD') or code.startswith('BDD'):
            return 'Bases de Données'
        elif code.startswith('MATH'):
            return 'Mathématiques'
        elif code.startswith('INFO') or code.startswith('PROG'):
            return 'Informatique'
        else:
            return 'Informatique Générale'
    
    def _extract_level(self, difficulte: int) -> str:
        """Convertit difficulté en niveau"""
        if difficulte <= 2:
            return 'Débutant'
        elif difficulte <= 4:
            return 'Intermédiaire'
        else:
            return 'Avancé'


# ==================== FONCTION UTILITAIRE ====================

def create_backend() -> BackendAdapter:
    """Crée et retourne une instance du backend"""
    return BackendAdapter()


# ==================== TEST ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST DU BACKEND ADAPTER")
    print("="*70)
    
    # Configurer logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    try:
        # Initialiser
        backend = BackendAdapter()
        
        # Test 1: Connexion
        print("\n✅ Test 1: Connexion")
        connected = backend.test_connection()
        print(f"   Connecté: {connected}")
        
        # Test 2: Récupération cours
        print("\n✅ Test 2: Récupération des cours")
        courses = backend.get_all_courses()
        print(f"   {len(courses)} cours trouvés")
        if courses:
            print(f"   Premier: {courses[0]['code']} - {courses[0]['nom']}")
        
        # Test 3: Statistiques
        print("\n✅ Test 3: Statistiques")
        stats = backend.get_statistics()
        print(f"   Total cours: {stats['total_courses']}")
        print(f"   Domaines: {len(stats['domains'])}")
        
        # Test 4: Chat
        print("\n✅ Test 4: Traitement message")
        result = backend.process_chat_message("Je cherche des cours en IA")
        print(f"   Succès: {result['success']}")
        print(f"   Réponse: {result['response'][:100]}...")
        
        # Test 5: Performance
        print("\n✅ Test 5: Rapport de performance")
        perf = backend.get_performance_report()
        print(f"   Requêtes: {perf['total_queries']}")
        print(f"   Temps moyen: {perf['avg_query_time']}")
        
        print("\n" + "="*70)
        print("✅ Tous les tests passent!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
# """
# Adapter pour connecter l'UI aux modules existants
# """

# import sys
# sys.path.append('..')

# from src.knowledge_base import KnowledgeBase
# from src.nlp_processor import NLPProcessor
# from src.sparql_query_builder import SPARQLQueryBuilder
# from src.conversation_manager import ConversationManager
# import logging

# logger = logging.getLogger(__name__)


# class BackendAdapter:
#     """
#     Interface unifiée entre Streamlit et les modules backend
#     """
    
#     def __init__(self):
#         """Initialise tous les composants backend"""
#         try:
#             self.kb = KnowledgeBase()
#             self.nlp = NLPProcessor()
#             self.query_builder = SPARQLQueryBuilder(self.kb)
#             self.conv_manager = ConversationManager()
            
#             logger.info("✅ Backend initialisé avec succès")
            
#         except Exception as e:
#             logger.error(f"❌ Erreur initialisation backend: {e}")
#             raise
    
#     def test_connection(self):
#         """Test la connexion à Fuseki"""
#         try:
#             query = """
#             PREFIX course: <http://www.university.edu/ontology/courses#>
#             SELECT (COUNT(?cours) as ?count)
#             WHERE {
#                 ?cours a course:Course .
#             }
#             """
#             result = self.kb.execute_query(query)
#             return result is not None
#         except Exception as e:
#             logger.error(f"Erreur test connexion: {e}")
#             return False
    
#     def get_all_courses(self):
#         """Récupère tous les cours depuis Fuseki"""
#         query = """
#         PREFIX course: <http://www.university.edu/ontology/courses#>
        
#         SELECT ?code ?nom ?credits ?duree ?difficulte ?description
#         WHERE {
#             ?cours a course:Course .
#             ?cours course:codeCours ?code .
#             ?cours course:nomCours ?nom .
#             ?cours course:credits ?credits .
#             OPTIONAL { ?cours course:duree ?duree }
#             OPTIONAL { ?cours course:difficulte ?difficulte }
#             OPTIONAL { ?cours course:description ?description }
#         }
#         ORDER BY ?code
#         """
        
#         results = self.kb.execute_query(query)
        
#         if not results:
#             return []
        
#         courses = []
#         for row in results:
#             courses.append({
#                 'code': row.get('code', {}).get('value', ''),
#                 'nom': row.get('nom', {}).get('value', ''),
#                 'credits': int(row.get('credits', {}).get('value', 0)),
#                 'duree': int(row.get('duree', {}).get('value', 0)),
#                 'difficulte': int(row.get('difficulte', {}).get('value', 1)),
#                 'description': row.get('description', {}).get('value', ''),
#                 # Extraire domaine et niveau depuis l'ontologie si nécessaire
#                 'domaine': self._extract_domain(row.get('code', {}).get('value', '')),
#                 'niveau': self._extract_level(int(row.get('difficulte', {}).get('value', 1)))
#             })
        
#         return courses
    
#     def _extract_domain(self, code):
#         """Extrait le domaine depuis le code cours"""
#         if code.startswith('IA'):
#             return 'Intelligence Artificielle'
#         elif code.startswith('WEB'):
#             return 'Développement Web'
#         elif code.startswith('BD') or code.startswith('BDD'):
#             return 'Bases de Données'
#         elif code.startswith('MATH'):
#             return 'Mathématiques'
#         else:
#             return 'Informatique'
    
#     def _extract_level(self, difficulte):
#         """Convertit difficulté en niveau"""
#         if difficulte <= 2:
#             return 'Débutant'
#         elif difficulte <= 4:
#             return 'Intermédiaire'
#         else:
#             return 'Avancé'
    
#     def get_course_by_code(self, course_code):
#         """Récupère un cours spécifique"""
#         query = f"""
#         PREFIX course: <http://www.university.edu/ontology/courses#>
        
#         SELECT ?nom ?credits ?duree ?difficulte ?description
#         WHERE {{
#             ?cours course:codeCours "{course_code}" .
#             ?cours course:nomCours ?nom .
#             ?cours course:credits ?credits .
#             OPTIONAL {{ ?cours course:duree ?duree }}
#             OPTIONAL {{ ?cours course:difficulte ?difficulte }}
#             OPTIONAL {{ ?cours course:description ?description }}
#         }}
#         """
        
#         results = self.kb.execute_query(query)
        
#         if not results or len(results) == 0:
#             return None
        
#         row = results[0]
#         return {
#             'code': course_code,
#             'nom': row.get('nom', {}).get('value', ''),
#             'credits': int(row.get('credits', {}).get('value', 0)),
#             'duree': int(row.get('duree', {}).get('value', 0)),
#             'difficulte': int(row.get('difficulte', {}).get('value', 1)),
#             'description': row.get('description', {}).get('value', ''),
#             'domaine': self._extract_domain(course_code),
#             'niveau': self._extract_level(int(row.get('difficulte', {}).get('value', 1)))
#         }
    
#     def get_all_prerequisites(self):
#         """Récupère tous les prérequis"""
#         query = """
#         PREFIX course: <http://www.university.edu/ontology/courses#>
        
#         SELECT ?coursCode ?prerequisCode
#         WHERE {
#             ?cours course:aPrerequis ?prerequis .
#             ?cours course:codeCours ?coursCode .
#             ?prerequis course:codeCours ?prerequisCode .
#         }
#         """
        
#         results = self.kb.execute_query(query)
        
#         if not results:
#             return []
        
#         return [(row['coursCode']['value'], row['prerequisCode']['value']) 
#                 for row in results]
    
#     def get_prerequisites_for_course(self, course_code):
#         """Récupère les prérequis d'un cours spécifique"""
#         query = f"""
#         PREFIX course: <http://www.university.edu/ontology/courses#>
        
#         SELECT ?prerequisCode ?prerequisNom
#         WHERE {{
#             ?cours course:codeCours "{course_code}" .
#             ?cours course:aPrerequis ?prerequis .
#             ?prerequis course:codeCours ?prerequisCode .
#             ?prerequis course:nomCours ?prerequisNom .
#         }}
#         """
        
#         results = self.kb.execute_query(query)
        
#         if not results:
#             return []
        
#         return [{'code': row['prerequisCode']['value'], 
#                  'nom': row['prerequisNom']['value']} 
#                 for row in results]
    
#     def get_statistics(self):
#         """Calcule des statistiques sur la base"""
#         courses = self.get_all_courses()
#         prerequisites = self.get_all_prerequisites()
        
#         # Compter par domaine
#         domains = {}
#         for course in courses:
#             domain = course['domaine']
#             domains[domain] = domains.get(domain, 0) + 1
        
#         # Compter par niveau
#         levels = {}
#         for course in courses:
#             level = course['niveau']
#             levels[level] = levels.get(level, 0) + 1
        
#         return {
#             'total_courses': len(courses),
#             'domains': domains,
#             'levels': levels,
#             'total_prerequisites': len(prerequisites)
#         }
    
#     def process_chat_message(self, user_message):
#         """Traite un message utilisateur via le système NLP"""
#         try:
#             response = self.conv_manager.process_message(user_message)
#             return {
#                 'success': True,
#                 'response': response,
#                 'context': self.conv_manager.get_context_summary()
#             }
#         except Exception as e:
#             logger.error(f"Erreur traitement message: {e}")
#             return {
#                 'success': False,
#                 'response': f"Erreur: {str(e)}",
#                 'context': None
#             }
    
#     def reset_conversation(self):
#         """Réinitialise la conversation"""
#         self.conv_manager.clear_history()