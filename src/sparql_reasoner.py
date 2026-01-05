"""
Module de raisonnement SPARQL pour le chatbot universitaire
Version optimisée avec inférence RDF et debugging amélioré
"""
from typing import List, Dict, Optional, Set
from collections import deque
import logging

try:
    from .knowledge_base import KnowledgeBase
except ImportError:
    from knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class RDFInferenceEngine:
    """
    Moteur d'inférence RDF pour déduire de nouvelles connaissances
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        logger.info("🧠 RDFInferenceEngine initialisé")
    
    
    def infer_transitive_prerequisites(self, code_cours: str) -> List[str]:
        """
        Infère tous les prérequis transitifs avec property paths SPARQL
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT DISTINCT ?prereqCode
        WHERE {{
            ?cours course:codeCours "{code_cours}" .
            ?cours course:aPrerequis+ ?prereq .
            ?prereq course:codeCours ?prereqCode .
        }}
        """
        
        results = self.kb.execute_query(query)
        codes = [r['prereqCode']['value'] for r in results]
        logger.info(f"🔗 Inférence transitive: {len(codes)} prérequis pour {code_cours}")
        return codes
    
    
    def infer_student_competencies(self, student_id: str) -> List[Dict]:
        """
        Infère les compétences d'un étudiant (possédées + acquises via cours)
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?skill ?skillLabel ?source
        WHERE {{
            {{
                # Compétences directes
                <{student_id}> course:possèdeCompetence ?skill .
                ?skill rdfs:label ?skillLabel .
                BIND("direct" AS ?source)
            }}
            UNION
            {{
                # Compétences inférées des cours suivis
                <{student_id}> course:aSuivi ?cours .
                ?cours course:enseigneCompetence ?skill .
                ?skill rdfs:label ?skillLabel .
                ?cours course:nomCours ?coursName .
                BIND(CONCAT("inferred from ", STR(?coursName)) AS ?source)
            }}
        }}
        """
        
        results = self.kb.execute_query(query)
        logger.info(f"🎯 {len(results)} compétences inférées pour {student_id}")
        return results
    
    
    def infer_recommended_level(self, student_id: str) -> str:
        """
        Infère le niveau recommandé basé sur l'historique
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?niveauLabel (COUNT(?cours) as ?count)
        WHERE {{
            <{student_id}> course:aSuivi ?cours .
            ?cours course:aNiveau ?niveau .
            ?niveau rdfs:label ?niveauLabel .
        }}
        GROUP BY ?niveauLabel
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = self.kb.execute_query(query)
        
        if results:
            current_level = results[0]['niveauLabel']['value']
            
            level_progression = {
                'Débutant': 'Intermédiaire',
                'Intermédiaire': 'Avancé',
                'Avancé': 'Avancé'
            }
            
            recommended = level_progression.get(current_level, 'Débutant')
            logger.info(f"📊 Niveau actuel: {current_level} → Recommandé: {recommended}")
            return recommended
        
        return 'Débutant'
    
    
    def infer_eligible_courses(self, student_id: str) -> List[Dict]:
        """
        Infère les cours pour lesquels l'étudiant a TOUS les prérequis
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code
        WHERE {{
            # Tous les cours
            ?cours a course:Course .
            ?cours course:nomCours ?nom .
            ?cours course:codeCours ?code .
            
            # Exclure les cours déjà suivis
            FILTER NOT EXISTS {{
                <{student_id}> course:aSuivi ?cours .
            }}
            
            # Filtrer ceux dont TOUS les prérequis sont validés
            FILTER NOT EXISTS {{
                ?cours course:aPrerequis ?prereq .
                FILTER NOT EXISTS {{
                    <{student_id}> course:aSuivi ?prereq .
                }}
            }}
        }}
        """
        
        results = self.kb.execute_query(query)
        logger.info(f"✅ {len(results)} cours éligibles inférés")
        return results


class SPARQLReasoner:
    """
    Moteur de raisonnement SPARQL avec inférence RDF intégrée
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.inference_engine = RDFInferenceEngine(kb)
        self.cache = {}
        logger.info("✅ SPARQLReasoner initialisé avec inférence RDF")
    
    
    def get_courses_by_domain(self, domain_name: str) -> List[Dict]:
        """
        Trouve les cours d'un domaine (VERSION CORRIGÉE avec 3 stratégies)
        """
        cache_key = f"domain_{domain_name}"
        if cache_key in self.cache:
            logger.info(f"📦 Cache hit pour domaine: {domain_name}")
            return self.cache[cache_key]
        
        # STRATÉGIE 1: Recherche par label du domaine
        query1 = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code ?credits ?description
        WHERE {{
            ?domain a course:Domain ;
                    rdfs:label ?domainLabel .
            FILTER(CONTAINS(LCASE(STR(?domainLabel)), LCASE("{domain_name}")))
            
            ?cours course:appartientADomaine ?domain ;
                   course:nomCours ?nom ;
                   course:codeCours ?code .
            
            OPTIONAL {{ ?cours course:credits ?credits }}
            OPTIONAL {{ ?cours course:description ?description }}
        }}
        ORDER BY ?code
        """
        
        logger.debug(f"🔍 Tentative 1: Recherche par rdfs:label du domaine")
        results = self.kb.execute_query(query1)
        
        if results:
            logger.info(f"✅ Stratégie 1 réussie: {len(results)} cours trouvés")
            self.cache[cache_key] = results
            return results
        
        # STRATÉGIE 2: Recherche par URI du domaine
        query2 = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code ?credits ?description
        WHERE {{
            ?cours course:appartientADomaine ?domain ;
                   course:nomCours ?nom ;
                   course:codeCours ?code .
            
            FILTER(CONTAINS(LCASE(STR(?domain)), LCASE("{domain_name}")))
            
            OPTIONAL {{ ?cours course:credits ?credits }}
            OPTIONAL {{ ?cours course:description ?description }}
        }}
        ORDER BY ?code
        """
        
        logger.debug(f"🔍 Tentative 2: Recherche par URI du domaine")
        results = self.kb.execute_query(query2)
        
        if results:
            logger.info(f"✅ Stratégie 2 réussie: {len(results)} cours trouvés")
            self.cache[cache_key] = results
            return results
        
        # STRATÉGIE 3: Recherche par nom/code du cours
        query3 = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code ?credits ?description
        WHERE {{
            ?cours a course:Course ;
                   course:nomCours ?nom ;
                   course:codeCours ?code .
            
            FILTER(
                CONTAINS(LCASE(?nom), LCASE("{domain_name}")) ||
                CONTAINS(LCASE(?code), LCASE("{domain_name}"))
            )
            
            OPTIONAL {{ ?cours course:credits ?credits }}
            OPTIONAL {{ ?cours course:description ?description }}
        }}
        ORDER BY ?code
        """
        
        logger.debug(f"🔍 Tentative 3: Recherche par nom/code du cours")
        results = self.kb.execute_query(query3)
        
        if results:
            logger.info(f"✅ Stratégie 3 réussie: {len(results)} cours trouvés")
        else:
            logger.warning(f"⚠️ Aucun cours trouvé pour '{domain_name}' avec toutes les stratégies")
        
        self.cache[cache_key] = results
        return results
    
    
    def get_all_prerequisites_recursive(self, code_cours: str, 
                                       visited: Set[str] = None) -> List[Dict]:
        """
        Prérequis récursifs (inchangé, fonctionne bien)
        """
        if visited is None:
            visited = set()
        
        if code_cours in visited:
            return []
        
        visited.add(code_cours)
        
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?prerequis ?nomPrerequis ?codePrerequis ?niveau
        WHERE {{
            ?cours course:codeCours "{code_cours}" .
            ?cours course:aPrerequis ?prerequis .
            ?prerequis course:nomCours ?nomPrerequis .
            ?prerequis course:codeCours ?codePrerequis .
            
            OPTIONAL {{ 
                ?prerequis course:aNiveau ?niveauURI .
                ?niveauURI rdfs:label ?niveau 
            }}
        }}
        """
        
        direct_prereqs = self.kb.execute_query(query)
        all_prereqs = list(direct_prereqs)
        
        for prereq in direct_prereqs:
            code_prereq = prereq['codePrerequis']['value']
            indirect_prereqs = self.get_all_prerequisites_recursive(code_prereq, visited)
            all_prereqs.extend(indirect_prereqs)
        
        return all_prereqs
    
    
    def find_courses_by_skills(self, skill_names: List[str]) -> List[Dict]:
        """
        Cours par compétences (VERSION CORRIGÉE)
        """
        if not skill_names:
            logger.warning("⚠️ Aucune compétence fournie")
            return []
        
        # Créer des filtres pour chaque compétence
        skill_filters = " || ".join([
            f'CONTAINS(LCASE(STR(?skillLabel)), LCASE("{skill}"))'
            for skill in skill_names
        ])
        
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code ?skillLabel
        WHERE {{
            ?cours a course:Course ;
                   course:nomCours ?nom ;
                   course:codeCours ?code .
            
            # Chercher les compétences
            ?cours course:enseigneCompetence ?skill .
            ?skill rdfs:label ?skillLabel .
            
            FILTER({skill_filters})
        }}
        ORDER BY ?code
        """
        
        logger.debug(f"🎯 Recherche de cours pour compétences: {skill_names}")
        results = self.kb.execute_query(query)
        
        if not results:
            # FALLBACK: Recherche dans le nom/description du cours
            fallback_query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            
            SELECT DISTINCT ?cours ?nom ?code
            WHERE {{
                ?cours a course:Course ;
                       course:nomCours ?nom ;
                       course:codeCours ?code .
                
                OPTIONAL {{ ?cours course:description ?desc }}
                
                FILTER(
                    {' || '.join([f'CONTAINS(LCASE(?nom), LCASE("{skill}"))' for skill in skill_names])}
                    {' || ' + ' || '.join([f'CONTAINS(LCASE(?desc), LCASE("{skill}"))' for skill in skill_names]) if len(skill_names) > 0 else ''}
                )
            }}
            """
            
            logger.debug("🔄 Fallback: Recherche dans nom/description")
            results = self.kb.execute_query(fallback_query)
        
        logger.info(f"✅ {len(results)} cours trouvés pour les compétences")
        return results
    
    
    def check_student_eligibility(self, student_id: str, code_cours: str) -> Dict:
        """
        Vérifie l'éligibilité (avec inférence RDF)
        """
        # Utiliser l'inférence pour les prérequis transitifs
        all_prereq_codes = self.inference_engine.infer_transitive_prerequisites(code_cours)
        
        if not all_prereq_codes:
            return {
                'eligible': True,
                'missing_prereqs': [],
                'message': f"Aucun prérequis pour {code_cours}"
            }
        
        # Cours suivis par l'étudiant
        query_student = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?coursCode
        WHERE {{
            <{student_id}> course:aSuivi ?cours .
            ?cours course:codeCours ?coursCode .
        }}
        """
        
        completed_courses = self.kb.execute_query(query_student)
        completed_codes = {c['coursCode']['value'] for c in completed_courses}
        
        missing = [code for code in all_prereq_codes if code not in completed_codes]
        
        if missing:
            return {
                'eligible': False,
                'missing_prereqs': missing,
                'message': f"Il manque {len(missing)} prérequis: {', '.join(missing)}"
            }
        else:
            return {
                'eligible': True,
                'missing_prereqs': [],
                'message': "Tous les prérequis sont validés !"
            }
    
    
    def compute_learning_path(self, target_course: str) -> List[Dict]:
        """
        Calcule le parcours optimal (inchangé, fonctionne)
        """
        all_prereqs = self.get_all_prerequisites_recursive(target_course)
        
        if not all_prereqs:
            course_info = self.kb.get_course_by_code(target_course)
            return [course_info] if course_info else []
        
        dependency_graph = {}
        all_codes = {target_course}
        
        for prereq in all_prereqs:
            code = prereq['codePrerequis']['value']
            all_codes.add(code)
        
        for code in all_codes:
            direct = self.kb.get_prerequisites(code)
            dependency_graph[code] = [p['codePrerequis']['value'] for p in direct]
        
        ordered_path = self._topological_sort(dependency_graph, target_course)
        
        detailed_path = []
        for code in ordered_path:
            course_info = self.kb.get_course_by_code(code)
            if course_info:
                detailed_path.append(course_info)
        
        return detailed_path
    
    
    def _topological_sort(self, graph: Dict[str, List[str]], target: str) -> List[str]:
        """Tri topologique pour ordonner les cours"""
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    
    def get_courses_by_level(self, level_name: str) -> List[Dict]:
        """Cours par niveau (inchangé)"""
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?cours ?nom ?code ?credits
        WHERE {{
            ?cours course:aNiveau ?niveau .
            ?niveau rdfs:label ?niveauLabel .
            FILTER(CONTAINS(LCASE(STR(?niveauLabel)), LCASE("{level_name}")))
            
            ?cours course:nomCours ?nom .
            ?cours course:codeCours ?code .
            
            OPTIONAL {{ ?cours course:credits ?credits }}
        }}
        ORDER BY ?code
        """
        
        return self.kb.execute_query(query)
    
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("🗑️ Cache vidé")
    
    
    def get_cache_stats(self) -> Dict:
        """Stats du cache"""
        return {
            'size': len(self.cache),
            'keys': list(self.cache.keys())
        }


# ===== SCRIPT DE TEST AMÉLIORÉ =====
if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🧪 TEST DÉTAILLÉ DE SPARQL_REASONER.PY")
    print("="*70)
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    try:
        from knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        
        if not kb.test_connection():
            print("\n❌ Connexion à Fuseki échouée")
            sys.exit(1)
        
        print("\n✅ Connexion établie")
        
        reasoner = SPARQLReasoner(kb)
        
        # Test 1: Cours par domaine
        print("\n" + "-"*70)
        print("📚 TEST 1: Recherche de cours par domaine")
        print("-"*70)
        
        domains_to_test = [
            "Intelligence Artificielle",
            "IA",
            "Machine Learning",
            "Mathématiques"
        ]
        
        for domain in domains_to_test:
            print(f"\n🔍 Domaine: '{domain}'")
            courses = reasoner.get_courses_by_domain(domain)
            print(f"   → {len(courses)} cours trouvés")
            
            if courses:
                for c in courses[:3]:  # Afficher max 3 exemples
                    print(f"      • {c.get('code', {}).get('value', 'N/A')}: "
                          f"{c.get('nom', {}).get('value', 'N/A')}")
        
        # Test 2: Cours par compétences
        print("\n" + "-"*70)
        print("🎯 TEST 2: Recherche par compétences")
        print("-"*70)
        
        skills = ["Machine Learning", "Python", "Deep Learning"]
        courses = reasoner.find_courses_by_skills(skills)
        print(f"   → {len(courses)} cours trouvés pour {skills}")
        
        # Test 3: Inférence RDF
        print("\n" + "-"*70)
        print("🧠 TEST 3: Inférence RDF")
        print("-"*70)
        
        prereqs = reasoner.inference_engine.infer_transitive_prerequisites("IA-401")
        print(f"   → Prérequis transitifs de IA-401: {len(prereqs)} cours")
        print(f"      {', '.join(prereqs)}")
        
        print("\n" + "="*70)
        print("✅ Tests terminés avec succès!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)