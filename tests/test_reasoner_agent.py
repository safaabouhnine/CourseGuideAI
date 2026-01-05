"""
Tests pour SPARQLReasoner et RecommendationAgent
"""
import sys
import os

# ✅ CORRECTION : Ajouter le répertoire racine au PYTHONPATH
# Cela permet d'importer depuis 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Maintenant on peut importer depuis src
from src.knowledge_base import KnowledgeBase
from src.sparql_reasoner import SPARQLReasoner
from src.recommendation_agent import RecommendationAgent


def test_sparql_reasoner():
    """Test du SPARQLReasoner"""
    print("\n" + "="*60)
    print("🧪 TEST SPARQL REASONER")
    print("="*60)
    
    try:
        kb = KnowledgeBase()
        
        # Tester la connexion d'abord
        if not kb.test_connection():
            print("❌ Impossible de se connecter à Fuseki. Vérifie que le serveur tourne.")
            return
        
        reasoner = SPARQLReasoner(kb)
        
        # Test 1: Recherche par domaine
        print("\n📚 Test 1: Cours en Intelligence Artificielle")
        try:
            courses = reasoner.get_courses_by_domain("Intelligence Artificielle")
            if courses:
                print(f"   ✅ {len(courses)} cours trouvés")
                for course in courses[:3]:
                    code = course.get('code', {}).get('value', 'N/A')
                    nom = course.get('nom', {}).get('value', 'N/A')
                    print(f"      - {code}: {nom}")
            else:
                print("   ⚠️ Aucun cours trouvé (base peut-être vide)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 2: Prérequis récursifs
        print("\n🔗 Test 2: Prérequis récursifs pour IA-401")
        try:
            prereqs = reasoner.get_all_prerequisites_recursive("IA-401")
            if prereqs:
                print(f"   ✅ {len(prereqs)} prérequis trouvés")
                for prereq in prereqs[:5]:
                    code = prereq.get('codePrerequis', {}).get('value', 'N/A')
                    nom = prereq.get('nomPrerequis', {}).get('value', 'N/A')
                    print(f"      - {code}: {nom}")
            else:
                print("   ⚠️ Aucun prérequis (cours de base ou données manquantes)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 3: Parcours d'apprentissage
        print("\n🎯 Test 3: Parcours d'apprentissage vers IA-401")
        try:
            path = reasoner.compute_learning_path("IA-401")
            if path:
                print(f"   ✅ {len(path)} cours dans le parcours")
                for i, course in enumerate(path[:5], 1):
                    code = course.get('code', {}).get('value', 'N/A')
                    nom = course.get('nom', {}).get('value', 'N/A')
                    print(f"      {i}. {code}: {nom}")
            else:
                print("   ⚠️ Parcours vide")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 4: Recherche par compétences
        print("\n🎓 Test 4: Cours par compétences (Machine Learning)")
        try:
            courses = reasoner.find_courses_by_skills(["Machine Learning", "Python"])
            if courses:
                print(f"   ✅ {len(courses)} cours trouvés")
                for course in courses[:3]:
                    code = course.get('code', {}).get('value', 'N/A')
                    nom = course.get('nom', {}).get('value', 'N/A')
                    print(f"      - {code}: {nom}")
            else:
                print("   ⚠️ Aucun cours trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print("\n✅ Tests SPARQLReasoner terminés")
        
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()


def test_recommendation_agent():
    """Test du RecommendationAgent"""
    print("\n" + "="*60)
    print("🤖 TEST RECOMMENDATION AGENT")
    print("="*60)
    
    try:
        kb = KnowledgeBase()
        
        # Tester la connexion
        if not kb.test_connection():
            print("❌ Impossible de se connecter à Fuseki.")
            return
        
        agent = RecommendationAgent(kb)
        
        # Test 1: Recommandations par profil
        print("\n💡 Test 1: Recommandations pour un étudiant")
        student_uri = "http://www.university.edu/ontology/courses#STU-001"
        try:
            recommendations = agent.recommend_by_profile(student_uri, max_results=3)
            
            if recommendations:
                print(f"   ✅ {len(recommendations)} recommandations générées")
                for i, rec in enumerate(recommendations, 1):
                    course = rec['course']
                    code = course.get('code', {}).get('value', 'N/A')
                    nom = course.get('nom', {}).get('value', 'N/A')
                    score = rec.get('score', 0)
                    reason = rec.get('reason', 'N/A')
                    
                    print(f"\n      {i}. {code}: {nom}")
                    print(f"         Score: {score:.2f}")
                    print(f"         Raison: {reason}")
            else:
                print("   ⚠️ Aucune recommandation (profil vide ou données manquantes)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 2: Parcours vers un objectif
        print("\n🎯 Test 2: Parcours d'apprentissage vers IA-401")
        try:
            plan = agent.recommend_for_goal(student_uri, "IA-401")
            
            print(f"   Objectif: {plan.get('goal', 'N/A')}")
            print(f"   Cours dans le parcours complet: {plan.get('full_path_length', 0)}")
            print(f"   Cours restants: {plan.get('remaining_path_length', 0)}")
            print(f"   Crédits totaux: {plan.get('total_credits', 0)}")
            print(f"   Semestres estimés: {plan.get('estimated_semesters', 0)}")
            
            next_courses = plan.get('next_courses', [])
            if next_courses:
                print(f"\n   Prochains cours recommandés:")
                for course_info in next_courses:
                    course = course_info['course']
                    code = course.get('code', {}).get('value', 'N/A')
                    nom = course.get('nom', {}).get('value', 'N/A')
                    print(f"      - {code}: {nom}")
            else:
                print("   ⚠️ Aucun cours suivant (prérequis manquants)")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 3: Cours similaires
        print("\n🔎 Test 3: Cours similaires à IA-301")
        try:
            similar = agent.find_similar_courses("IA-301", limit=3)
            
            if similar:
                print(f"   ✅ {len(similar)} cours similaires trouvés")
                for course in similar:
                    code = course.get('codeSimilaire', {}).get('value', 'N/A')
                    nom = course.get('nomSimilaire', {}).get('value', 'N/A')
                    print(f"      - {code}: {nom}")
            else:
                print("   ⚠️ Aucun cours similaire trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test 4: Statistiques sur un cours
        print("\n📊 Test 4: Statistiques pour IA-401")
        try:
            stats = agent.get_course_statistics("IA-401")
            
            if 'error' not in stats:
                print(f"   Prérequis totaux: {stats.get('total_prerequisites', 0)}")
                print(f"   Cours similaires: {stats.get('similar_courses_count', 0)}")
            else:
                print(f"   ⚠️ {stats['error']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print("\n✅ Tests RecommendationAgent terminés")
        
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()


def test_connection_only():
    """Test uniquement la connexion à Fuseki"""
    print("\n" + "="*60)
    print("🔌 TEST DE CONNEXION FUSEKI")
    print("="*60)
    
    try:
        kb = KnowledgeBase()
        
        if kb.test_connection():
            print("✅ Connexion à Fuseki réussie!")
            
            # Compter les triplets
            query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
            results = kb.execute_query(query)
            
            if results:
                count = results[0]['count']['value']
                print(f"📊 Nombre de triplets: {count}")
                
                if int(count) == 0:
                    print("⚠️ La base est vide. Pense à la peupler avec:")
                    print("   python scripts/populate_knowledge_base.py")
        else:
            print("❌ Connexion échouée!")
            print("\n💡 Solutions:")
            print("   1. Vérifie que Fuseki tourne: docker-compose up -d fuseki")
            print("   2. Vérifie l'URL dans knowledge_base.py")
            print("   3. Vérifie les credentials (admin/admin123)")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 DÉMARRAGE DES TESTS DU SYSTÈME DE RECOMMANDATION")
    print("="*70)
    
    # Test de connexion d'abord
    test_connection_only()
    
    # Si connexion OK, lancer les autres tests
    print("\n" + "="*70)
    input("Appuie sur Entrée pour continuer avec les tests complets...")
    
    test_sparql_reasoner()
    test_recommendation_agent()
    
    print("\n" + "="*70)
    print("✅ TOUS LES TESTS SONT TERMINÉS!")
    print("="*70)