"""
Tests pour la base de connaissance
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.knowledge_base import KnowledgeBase


def test_connection():
    """Test 1: Connexion à Fuseki"""
    print("\n🧪 Test 1: Connexion à Fuseki")
    kb = KnowledgeBase()
    assert kb.test_connection(), "❌ Connexion échouée"
    print("✅ Connexion OK")


def test_get_all_courses():
    """Test 2: Récupération de tous les cours"""
    print("\n🧪 Test 2: Récupération de tous les cours")
    kb = KnowledgeBase()
    courses = kb.get_all_courses()
    assert len(courses) > 0, "❌ Aucun cours trouvé"
    print(f"✅ {len(courses)} cours trouvés")
    
    # Afficher les 3 premiers
    print("\n📚 Exemples de cours :")
    for course in courses[:3]:
        code = course.get('code', {}).get('value', 'N/A')
        nom = course.get('nom', {}).get('value', 'N/A')
        print(f"   - {code}: {nom}")


def test_get_course_by_code():
    """Test 3: Récupération d'un cours par code"""
    print("\n🧪 Test 3: Récupération d'un cours par code")
    kb = KnowledgeBase()
    course = kb.get_course_by_code("IA-401")
    assert course is not None, "❌ Cours IA-401 non trouvé"
    
    nom = course.get('nom', {}).get('value', 'N/A')
    credits = course.get('credits', {}).get('value', 'N/A')
    print(f"✅ Cours trouvé: {nom}")
    print(f"   Crédits: {credits}")


def test_get_prerequisites():
    """Test 4: Récupération des prérequis"""
    print("\n🧪 Test 4: Récupération des prérequis")
    kb = KnowledgeBase()
    prereqs = kb.get_prerequisites("IA-401")
    assert len(prereqs) > 0, "❌ Aucun prérequis trouvé pour IA-401"
    print(f"✅ {len(prereqs)} prérequis trouvés pour IA-401:")
    
    for prereq in prereqs:
        code = prereq.get('codePrerequis', {}).get('value', 'N/A')
        nom = prereq.get('nomPrerequis', {}).get('value', 'N/A')
        print(f"   - {code}: {nom}")


def run_all_tests():
    """Lance tous les tests"""
    print("="*70)
    print("🧪 LANCEMENT DES TESTS DE LA BASE DE CONNAISSANCE")
    print("="*70)
    
    tests = [
        test_connection,
        test_get_all_courses,
        test_get_course_by_code,
        test_get_prerequisites
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test échoué: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 RÉSULTATS: {passed} tests réussis, {failed} tests échoués")
    print("="*70)
    
    if failed == 0:
        print("✅ TOUS LES TESTS SONT PASSÉS ! 🎉\n")
    else:
        print("❌ Certains tests ont échoué. Vérifie les erreurs ci-dessus.\n")


if __name__ == "__main__":
    run_all_tests()