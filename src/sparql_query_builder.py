"""
Module pour construire des requêtes SPARQL à partir des intentions NLP
Membre 2 : Spécialiste NLP - VERSION CORRIGÉE avec bon namespace
"""

from typing import Dict, Any, List, Optional
from src.knowledge_base import KnowledgeBase
from src.nlp_processor import NLPProcessor


class SPARQLQueryBuilder:
    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initialise le builder de requêtes SPARQL
        
        Args:
            knowledge_base: Instance de KnowledgeBase pour exécuter les requêtes
        """
        self.kb = knowledge_base
        self.nlp = NLPProcessor()
        
        # Préfixes SPARQL CORRIGÉS
        self.prefixes = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        """
    
    def search_courses(self, entities: Dict[str, Any]) -> List[Dict]:
        """
        Recherche des cours selon les entités extraites
        
        Args:
            entities: Dictionnaire des entités (domain, level, skills, etc.)
            
        Returns:
            Liste de cours correspondants
        """
        domain = entities.get('domain')
        level = entities.get('level')
        course_code = entities.get('course_code')
        
        # Requête de base utilisant nomCours au lieu de rdfs:label
        base_query = """
        SELECT DISTINCT ?course ?nomCours ?code ?credits ?description
        WHERE {
            ?course rdf:type course:Course .
            ?course course:nomCours ?nomCours .
            ?course course:codeCours ?code .
            OPTIONAL { ?course course:credits ?credits . }
            OPTIONAL { ?course course:description ?description . }
        """
        
        # Si un code spécifique est demandé
        if course_code:
            query = self.prefixes + base_query + f"""
            FILTER(CONTAINS(UCASE(?code), "{course_code.upper()}"))
            }}
            LIMIT 10
            """
        
        # Si un domaine est spécifié
        elif domain:
            # Mapper les domaines
            domain_map = {
                'Intelligence Artificielle': 'IA',
                'Web': 'WEB',
                'Machine Learning': 'IA',
                'Base de Données': 'BDD',
                'Mathématiques': 'MATH',
                'Informatique': 'INFO|PROG'
            }
            
            pattern = domain_map.get(domain, domain)
            
            query = self.prefixes + base_query + f"""
            FILTER(REGEX(?nomCours, "{pattern}", "i") || REGEX(?code, "{pattern}", "i"))
            """
            
            # Filtre de niveau
            if level:
                level_map = {'débutant': '1', 'intermédiaire': '2', 'avancé': '3', 'expert': '4'}
                if level.lower() in level_map:
                    num = level_map[level.lower()]
                    query += f" FILTER(CONTAINS(?code, '{num}'))"
            
            query += "} LIMIT 10"
        
        else:
            # Tous les cours
            query = self.prefixes + base_query + "} ORDER BY ?code LIMIT 15"
        
        results = self.kb.execute_query(query)
        return self._format_course_results(results)
    
    def check_prerequisites(self, course_code: str) -> Dict[str, Any]:
        """
        Vérifie les prérequis d'un cours
        
        Args:
            course_code: Code du cours (ex: IA-401)
            
        Returns:
            Dictionnaire avec le cours et ses prérequis
        """
        course_code = course_code.strip().upper()
        
        query = self.prefixes + f"""
        SELECT ?course ?nomCours ?code ?prereq ?prereqNom ?prereqCode
        WHERE {{
            ?course rdf:type course:Course .
            ?course course:nomCours ?nomCours .
            ?course course:codeCours ?code .
            FILTER(CONTAINS(UCASE(?code), "{course_code}"))
            
            OPTIONAL {{
                ?course course:aPrerequis ?prereq .
                ?prereq course:nomCours ?prereqNom .
                ?prereq course:codeCours ?prereqCode .
            }}
        }}
        """
        
        results = self.kb.execute_query(query)
        
        if not results or len(results) == 0:
            return {
                'course': None,
                'prerequisites': [],
                'message': f"Aucun cours trouvé avec le code '{course_code}'"
            }
        
        course_info = {
            'course': results[0].get('nomCours', {}).get('value', 'Cours inconnu'),
            'code': results[0].get('code', {}).get('value', course_code),
            'prerequisites': []
        }
        
        for result in results:
            if 'prereqNom' in result:
                course_info['prerequisites'].append({
                    'label': result['prereqNom']['value'],
                    'code': result['prereqCode']['value']
                })
        
        return course_info
    
    def get_learning_path(self, domain: str, target_level: str = 'expert') -> List[Dict]:
        """
        Construit un parcours d'apprentissage pour un domaine
        
        Args:
            domain: Domaine d'étude
            target_level: Niveau cible
            
        Returns:
            Liste ordonnée de cours
        """
        domain_map = {
            'Intelligence Artificielle': 'IA',
            'Machine Learning': 'IA',
            'Web': 'WEB',
            'Base de Données': 'BDD',
            'Mathématiques': 'MATH',
            'Informatique': 'INFO|PROG'
        }
        
        pattern = domain_map.get(domain, domain)
        
        query = self.prefixes + f"""
        SELECT DISTINCT ?course ?nomCours ?code ?prereq ?prereqCode
        WHERE {{
            ?course rdf:type course:Course .
            ?course course:nomCours ?nomCours .
            ?course course:codeCours ?code .
            FILTER(REGEX(?nomCours, "{pattern}", "i") || REGEX(?code, "{pattern}", "i"))
            
            OPTIONAL {{
                ?course course:aPrerequis ?prereq .
                ?prereq course:codeCours ?prereqCode .
            }}
        }}
        ORDER BY ?code
        """
        
        results = self.kb.execute_query(query)
        
        if not results or len(results) == 0:
            return self.list_all_courses()
        
        return self._organize_by_level(results)
    
    def get_course_info(self, course_code: str) -> Optional[Dict]:
        """
        Récupère les informations détaillées d'un cours
        
        Args:
            course_code: Code du cours
            
        Returns:
            Dictionnaire avec toutes les infos du cours
        """
        course_code = course_code.strip().upper()
        
        query = self.prefixes + f"""
        SELECT ?course ?nomCours ?code ?credits ?description ?duree ?difficulte 
               ?skill ?skillNom ?domain ?domainNom
        WHERE {{
            ?course rdf:type course:Course .
            ?course course:nomCours ?nomCours .
            ?course course:codeCours ?code .
            FILTER(CONTAINS(UCASE(?code), "{course_code}"))
            
            OPTIONAL {{ ?course course:credits ?credits . }}
            OPTIONAL {{ ?course course:description ?description . }}
            OPTIONAL {{ ?course course:duree ?duree . }}
            OPTIONAL {{ ?course course:difficulte ?difficulte . }}
            OPTIONAL {{
                ?course course:enseigneCompetence ?skill .
                ?skill course:nomCompetence ?skillNom .
            }}
            OPTIONAL {{
                ?course course:appartientADomaine ?domain .
                ?domain course:nomDomaine ?domainNom .
            }}
        }}
        """
        
        results = self.kb.execute_query(query)
        
        if not results or len(results) == 0:
            return None
        
        first = results[0]
        course_info = {
            'label': first.get('nomCours', {}).get('value', 'Inconnu'),
            'code': first.get('code', {}).get('value', course_code),
            'credits': first.get('credits', {}).get('value', 'N/A'),
            'description': first.get('description', {}).get('value', 'Pas de description'),
            'duree': first.get('duree', {}).get('value', 'N/A'),
            'difficulte': first.get('difficulte', {}).get('value', 'N/A'),
            'domain': first.get('domainNom', {}).get('value', 'N/A'),
            'skills': []
        }
        
        for result in results:
            if 'skillNom' in result:
                skill = result['skillNom']['value']
                if skill not in course_info['skills']:
                    course_info['skills'].append(skill)
        
        return course_info
    
    def list_all_courses(self) -> List[Dict]:
        """Liste tous les cours disponibles"""
        query = self.prefixes + """
        SELECT DISTINCT ?course ?nomCours ?code ?credits
        WHERE {
            ?course rdf:type course:Course .
            ?course course:nomCours ?nomCours .
            ?course course:codeCours ?code .
            OPTIONAL { ?course course:credits ?credits . }
        }
        ORDER BY ?code
        """
        
        results = self.kb.execute_query(query)
        return self._format_course_results(results)
    
    def process_user_query(self, user_message: str) -> Dict[str, Any]:
        """Traite une requête utilisateur complète"""
        nlp_result = self.nlp.process_message(user_message)
        intent = nlp_result['intent']
        entities = nlp_result['entities']
        
        if intent == 'recherche_cours':
            courses = self.search_courses(entities)
            
            if not courses:
                courses = self.list_all_courses()
                return {
                    'intent': intent,
                    'data': courses,
                    'message': f"Voici tous les {len(courses)} cours disponibles"
                }
            
            return {
                'intent': intent,
                'data': courses,
                'message': f"J'ai trouvé {len(courses)} cours correspondant à votre recherche."
            }
        
        elif intent == 'verifier_prerequis':
            course_code = entities.get('course_code')
            if not course_code:
                return {
                    'intent': intent,
                    'data': None,
                    'message': "Veuillez spécifier un code de cours (ex: IA-401, WEB-301)"
                }
            
            prereqs = self.check_prerequisites(course_code)
            return {
                'intent': intent,
                'data': prereqs,
                'message': self._format_prerequisites_message(prereqs)
            }
        
        elif intent == 'parcours_apprentissage':
            domain = entities.get('domain', 'Intelligence Artificielle')
            path = self.get_learning_path(domain)
            return {
                'intent': intent,
                'data': path,
                'message': f"Voici un parcours d'apprentissage recommandé ({len(path)} cours)"
            }
        
        elif intent == 'info_cours':
            course_code = entities.get('course_code')
            if not course_code:
                return {
                    'intent': intent,
                    'data': None,
                    'message': "Veuillez spécifier un code de cours"
                }
            
            info = self.get_course_info(course_code)
            
            if not info:
                all_courses = self.list_all_courses()
                return {
                    'intent': 'liste_cours',
                    'data': all_courses,
                    'message': f"Cours '{course_code}' non trouvé. Voici tous les cours disponibles."
                }
            
            return {
                'intent': intent,
                'data': info,
                'message': self._format_course_info_message(info)
            }
        
        else:
            courses = self.list_all_courses()
            return {
                'intent': 'liste_cours',
                'data': courses,
                'message': f"Voici les {len(courses)} cours disponibles"
            }
    
    # Méthodes utilitaires
    
    def _format_course_results(self, results: List[Dict]) -> List[Dict]:
        """Formate les résultats de cours"""
        courses = []
        for result in results:
            courses.append({
                'label': result.get('nomCours', {}).get('value', 'Inconnu'),
                'code': result.get('code', {}).get('value', 'N/A'),
                'credits': result.get('credits', {}).get('value', 'N/A'),
                'description': result.get('description', {}).get('value', '')
            })
        return courses
    
    def _organize_by_level(self, results: List[Dict]) -> List[Dict]:
        """Organise les cours par niveau"""
        courses = {}
        for result in results:
            code = result.get('code', {}).get('value', '')
            if code not in courses:
                courses[code] = {
                    'label': result.get('nomCours', {}).get('value', ''),
                    'code': code,
                    'prerequisites': []
                }
            
            if 'prereqCode' in result:
                prereq = result['prereqCode']['value']
                if prereq not in courses[code]['prerequisites']:
                    courses[code]['prerequisites'].append(prereq)
        
        return sorted(courses.values(), key=lambda x: x['code'])
    
    def _format_prerequisites_message(self, prereqs: Dict) -> str:
        """Formate le message des prérequis"""
        if not prereqs.get('course'):
            return prereqs.get('message', 'Cours non trouvé')
        
        course_name = prereqs['course']
        prereq_list = prereqs['prerequisites']
        
        if not prereq_list:
            return f"🎉 Le cours '{course_name}' n'a pas de prérequis. Vous pouvez le suivre directement !"
        
        prereq_text = ", ".join([f"{p['label']} ({p['code']})" for p in prereq_list])
        return f"Pour suivre '{course_name}', vous devez d'abord compléter : {prereq_text}"
    
    def _format_course_info_message(self, info: Optional[Dict]) -> str:
        """Formate le message d'info cours"""
        if not info:
            return "Cours non trouvé"
        
        msg = f"📚 **{info['label']}** ({info['code']})\n\n"
        msg += f"🎓 Crédits: {info['credits']}\n"
        msg += f"⏱️ Durée: {info['duree']} heures\n"
        msg += f"📊 Difficulté: {info['difficulte']}/5\n"
        msg += f"🏷️ Domaine: {info['domain']}\n\n"
        msg += f"📝 {info['description']}\n"
        
        if info['skills']:
            msg += f"\n💡 Compétences enseignées:\n"
            for skill in info['skills'][:5]:  # Limiter à 5 compétences
                msg += f"  • {skill}\n"
        
        return msg


# Test
if __name__ == "__main__":
    print("🧪 Test du SPARQLQueryBuilder (Version CORRIGÉE)\n")
    
    kb = KnowledgeBase()
    builder = SPARQLQueryBuilder(kb)
    
    test_queries = [
        "Montre-moi tous les cours",
        "Je cherche des cours en IA",
        "Quels sont les prérequis pour IA-401 ?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"📨 Question: {query}")
        result = builder.process_user_query(query)
        print(f"   Intent: {result['intent']}")
        if isinstance(result['data'], list):
            print(f"   Données: {len(result['data'])} résultat(s)")
            if result['data']:
                print(f"   Premier résultat: {result['data'][0]}")
        elif isinstance(result['data'], dict):
            print(f"   Données: Dictionnaire avec {len(result['data'])} clés")
        else:
            print(f"   Données: {result['data']}")