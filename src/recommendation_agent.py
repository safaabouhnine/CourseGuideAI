"""
Agent de recommandation intelligent
Génère des recommandations personnalisées basées sur le profil étudiant
"""

from typing import List, Dict, Optional, Set
import logging

# Import avec gestion des erreurs
try:
    from .knowledge_base import KnowledgeBase
    from .sparql_reasoner import SPARQLReasoner
except ImportError:
    from knowledge_base import KnowledgeBase
    from sparql_reasoner import SPARQLReasoner

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Agent IA pour générer des recommandations de cours personnalisées
    """
    
    def __init__(self, kb: KnowledgeBase):
        """
        Initialise l'agent avec une connexion KB
        
        Args:
            kb: Instance de KnowledgeBase
        """
        self.kb = kb
        self.reasoner = SPARQLReasoner(kb)
        logger.info("✅ RecommendationAgent initialisé")
    
    
    def recommend_by_profile(self, student_id: str, 
                            max_results: int = 5) -> List[Dict]:
        """
        Recommande des cours basés sur :
        - Les intérêts de l'étudiant
        - Ses compétences actuelles
        - Les cours qu'il a déjà suivis
        
        Args:
            student_id: URI de l'étudiant
            max_results: Nombre max de recommandations
            
        Returns:
            Liste de cours recommandés avec score
        """
        logger.info(f"🔍 Génération de recommandations pour {student_id}")
        
        # 1. Récupérer le profil de l'étudiant
        profile_query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?domainLabel ?skillLabel ?coursCode
        WHERE {{
            OPTIONAL {{
                <{student_id}> course:aInteretPour ?domain .
                ?domain rdfs:label ?domainLabel .
            }}
            
            OPTIONAL {{
                <{student_id}> course:possèdeCompetence ?skill .
                ?skill rdfs:label ?skillLabel .
            }}
            
            OPTIONAL {{
                <{student_id}> course:aSuivi ?cours .
                ?cours course:codeCours ?coursCode .
            }}
        }}
        """
        
        profile = self.kb.execute_query(profile_query)
        
        # Extraire intérêts, compétences et cours complétés
        interests = set()
        skills = set()
        completed = set()
        
        for row in profile:
            if 'domainLabel' in row:
                interests.add(row['domainLabel']['value'])
            if 'skillLabel' in row:
                skills.add(row['skillLabel']['value'])
            if 'coursCode' in row:
                completed.add(row['coursCode']['value'])
        
        logger.info(f"📊 Profil: {len(interests)} intérêts, {len(skills)} compétences, {len(completed)} cours suivis")
        
        # 2. Trouver des cours correspondants
        recommendations = []
        
        # Cours dans les domaines d'intérêt
        for interest in interests:
            courses = self.reasoner.get_courses_by_domain(interest)
            for course in courses:
                code = course['code']['value']
                if code not in completed:
                    # Vérifier éligibilité
                    eligibility = self.reasoner.check_student_eligibility(
                        student_id, code
                    )
                    
                    if eligibility['eligible']:
                        score = self._calculate_relevance_score(
                            course, interests, skills
                        )
                        recommendations.append({
                            'course': course,
                            'score': score,
                            'reason': f"Correspond à votre intérêt : {interest}",
                            'eligible': True
                        })
        
        # Si pas assez de recommandations, ajouter des cours généraux
        if len(recommendations) < max_results:
            logger.info("📚 Ajout de cours généraux...")
            all_courses = self.kb.get_all_courses()
            
            for course in all_courses:
                if 'code' not in course:
                    continue
                    
                code = course['code']['value']
                if code not in completed:
                    # Vérifier si déjà dans les recommandations
                    already_recommended = any(
                        r['course']['code']['value'] == code 
                        for r in recommendations
                    )
                    
                    if not already_recommended:
                        eligibility = self.reasoner.check_student_eligibility(
                            student_id, code
                        )
                        
                        if eligibility['eligible']:
                            recommendations.append({
                                'course': course,
                                'score': 0.5,  # Score neutre
                                'reason': "Cours accessible avec vos prérequis",
                                'eligible': True
                            })
        
        # Trier par score et limiter
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✅ {len(recommendations)} recommandations générées")
        return recommendations[:max_results]
    
    
    def _calculate_relevance_score(self, course: Dict, 
                                   interests: Set[str], 
                                   skills: Set[str]) -> float:
        """
        Calcule un score de pertinence pour un cours
        Score entre 0 et 1
        
        Args:
            course: Dictionnaire du cours
            interests: Set d'intérêts de l'étudiant
            skills: Set de compétences de l'étudiant
            
        Returns:
            Score de pertinence (0.0 - 1.0)
        """
        score = 0.5  # Score de base
        
        # Bonus si le cours a une description
        if 'description' in course and course['description']:
            score += 0.1
        
        # Bonus pour nombre de crédits (valoriser les cours substantiels)
        if 'credits' in course:
            try:
                credits = int(course['credits']['value'])
                if credits >= 5:
                    score += 0.1
            except:
                pass
        
        # Bonus si niveau approprié (à adapter selon vos données)
        # score += 0.2 si niveau correspond
        
        return min(1.0, score)
    
    
    def recommend_for_goal(self, student_id: str, 
                          goal_course_code: str) -> Dict:
        """
        Recommande un plan pour atteindre un cours objectif
        
        Args:
            student_id: URI étudiant
            goal_course_code: Code du cours visé
            
        Returns:
            Plan d'apprentissage détaillé
        """
        logger.info(f"🎯 Calcul du parcours vers {goal_course_code}")
        
        # 1. Calculer le parcours complet
        full_path = self.reasoner.compute_learning_path(goal_course_code)
        
        # 2. Vérifier quels cours sont déjà complétés
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?coursCode
        WHERE {{
            <{student_id}> course:aSuivi ?cours .
            ?cours course:codeCours ?coursCode .
        }}
        """
        
        completed = self.kb.execute_query(query)
        completed_codes = {c['coursCode']['value'] for c in completed}
        
        # 3. Filtrer pour ne garder que les cours restants
        remaining_path = [
            course for course in full_path
            if course.get('code', {}).get('value') not in completed_codes
        ]
        
        # 4. Identifier le(s) prochain(s) cours à suivre
        next_courses = []
        for course in remaining_path:
            if 'code' not in course:
                continue
                
            code = course['code']['value']
            eligibility = self.reasoner.check_student_eligibility(student_id, code)
            
            if eligibility['eligible']:
                next_courses.append({
                    'course': course,
                    'reason': 'Prérequis validés'
                })
        
        # 5. Calculer statistiques
        total_credits = 0
        for course in remaining_path:
            if 'credits' in course:
                try:
                    total_credits += int(course['credits']['value'])
                except:
                    pass
        
        estimated_semesters = max(1, len(remaining_path) // 4)
        
        result = {
            'goal': goal_course_code,
            'full_path': full_path,
            'full_path_length': len(full_path),
            'remaining_path': remaining_path,
            'remaining_path_length': len(remaining_path),
            'next_courses': next_courses[:3],  # 3 suggestions max
            'total_credits': total_credits,
            'estimated_semesters': estimated_semesters,
            'completed_courses': len(completed_codes)
        }
        
        logger.info(f"✅ Parcours calculé: {len(remaining_path)} cours restants")
        return result
    
    
    def find_similar_courses(self, course_code: str, 
                            limit: int = 3) -> List[Dict]:
        """
        Trouve des cours similaires (même domaine, niveau, compétences)
        
        Args:
            course_code: Code du cours de référence
            limit: Nombre de suggestions
            
        Returns:
            Liste de cours similaires
        """
        logger.info(f"🔎 Recherche de cours similaires à {course_code}")
        
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?similaire ?nomSimilaire ?codeSimilaire ?domainLabel
        WHERE {{
            # Cours de référence
            ?reference course:codeCours "{course_code}" .
            
            OPTIONAL {{
                ?reference course:appartientADomaine ?domain .
                ?domain rdfs:label ?domainLabel .
            }}
            
            OPTIONAL {{
                ?reference course:aNiveau ?niveau .
            }}
            
            # Cours similaires (même domaine et/ou niveau)
            {{
                ?similaire course:appartientADomaine ?domain .
            }} UNION {{
                ?similaire course:aNiveau ?niveau .
            }}
            
            ?similaire course:nomCours ?nomSimilaire .
            ?similaire course:codeCours ?codeSimilaire .
            
            # Exclure le cours lui-même
            FILTER(?similaire != ?reference)
        }}
        LIMIT {limit}
        """
        
        results = self.kb.execute_query(query)
        logger.info(f"✅ {len(results)} cours similaires trouvés")
        return results
    
    
    def get_course_statistics(self, code_cours: str) -> Dict:
        """
        Récupère des statistiques sur un cours
        
        Args:
            code_cours: Code du cours
            
        Returns:
            Dictionnaire avec statistiques
        """
        # Récupérer info de base
        course_info = self.kb.get_course_by_code(code_cours)
        
        if not course_info:
            return {'error': 'Cours non trouvé'}
        
        # Compter les prérequis
        prereqs = self.reasoner.get_all_prerequisites_recursive(code_cours)
        
        # Trouver cours similaires
        similar = self.find_similar_courses(code_cours, limit=5)
        
        return {
            'course': course_info,
            'total_prerequisites': len(prereqs),
            'similar_courses_count': len(similar),
            'similar_courses': similar
        }


# Fonction utilitaire
def create_recommendation_agent(kb: KnowledgeBase = None) -> RecommendationAgent:
    """
    Crée et retourne une instance de RecommendationAgent
    
    Args:
        kb: Instance de KnowledgeBase (optionnel)
        
    Returns:
        Instance de RecommendationAgent
    """
    if kb is None:
        kb = KnowledgeBase()
    
    return RecommendationAgent(kb)


# Test du module
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 TEST DE RECOMMENDATION_AGENT.PY")
    print("="*60)
    
    # Créer l'agent
    from knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    agent = RecommendationAgent(kb)
    
    # Test 1: Recommandations pour un étudiant
    print("\n💡 Test 1: Recommandations pour étudiant")
    student_uri = "http://www.university.edu/ontology/courses#Student_001"
    recommendations = agent.recommend_by_profile(student_uri, max_results=3)
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            course = rec['course']
            print(f"\n  {i}. {course.get('code', {}).get('value', 'N/A')}")
            print(f"     Nom: {course.get('nom', {}).get('value', 'N/A')}")
            print(f"     Score: {rec['score']:.2f}")
            print(f"     Raison: {rec['reason']}")
    else:
        print("  ⚠️ Aucune recommandation générée")
    
    # Test 2: Parcours d'apprentissage
    print("\n🎯 Test 2: Parcours vers un cours")
    goal = "IA-401"
    plan = agent.recommend_for_goal(student_uri, goal)
    print(f"  Objectif: {plan['goal']}")
    print(f"  Cours restants: {plan['remaining_path_length']}")
    print(f"  Crédits totaux: {plan['total_credits']}")
    print(f"  Semestres estimés: {plan['estimated_semesters']}")
    
    # Test 3: Cours similaires
    print("\n🔎 Test 3: Cours similaires")
    similar = agent.find_similar_courses("IA-301", limit=3)
    for course in similar:
        print(f"  - {course.get('codeSimilaire', {}).get('value', 'N/A')}: "
              f"{course.get('nomSimilaire', {}).get('value', 'N/A')}")
    
    print("\n✅ Tests terminés!")