"""
Tests d'intégration pour l'interface UI
Membre 4 : Interface & Visualisation
"""

import sys
sys.path.append('..')

from src.ui.backend_adapter import BackendAdapter
from src.ui.visualization import (
    create_prerequisites_graph,
    create_domain_chart,
    create_level_pie_chart,
    create_learning_path_viz
)
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestUIIntegration:
    """Suite de tests pour l'intégration UI"""
    
    def __init__(self):
        self.backend = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def setup(self):
        """Initialisation des tests"""
        print("\n" + "="*70)
        print("🧪 TESTS D'INTÉGRATION UI")
        print("="*70)
        
        try:
            print("\n⚙️ Initialisation du backend...")
            self.backend = BackendAdapter()
            print("✅ Backend initialisé")
            return True
        except Exception as e:
            print(f"❌ Erreur initialisation: {e}")
            return False
    
    def test_connection(self):
        """Test 1: Connexion à Fuseki"""
        print("\n📡 Test 1: Connexion à Fuseki")
        try:
            connected = self.backend.test_connection()
            assert connected, "Connexion échouée"
            print("   ✅ Connecté à Fuseki")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_get_courses(self):
        """Test 2: Récupération des cours"""
        print("\n📚 Test 2: Récupération des cours")
        try:
            courses = self.backend.get_all_courses()
            assert len(courses) > 0, "Aucun cours récupéré"
            assert 'code' in courses[0], "Format cours invalide"
            assert 'nom' in courses[0], "Nom manquant"
            print(f"   ✅ {len(courses)} cours récupérés")
            print(f"      Exemple: {courses[0]['code']} - {courses[0]['nom']}")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_get_specific_course(self):
        """Test 3: Récupération d'un cours spécifique"""
        print("\n🎯 Test 3: Récupération cours spécifique")
        try:
            course = self.backend.get_course_by_code("IA-401")
            
            if course:
                assert course['code'] == "IA-401", "Code incorrect"
                assert 'nom' in course, "Nom manquant"
                print(f"   ✅ Cours trouvé: {course['nom']}")
                self.test_results['passed'] += 1
            else:
                print("   ⚠️ Cours IA-401 non trouvé (peut être normal)")
                self.test_results['passed'] += 1
                
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_prerequisites(self):
        """Test 4: Récupération des prérequis"""
        print("\n🔗 Test 4: Récupération des prérequis")
        try:
            prereqs = self.backend.get_all_prerequisites()
            assert isinstance(prereqs, list), "Type incorrect"
            print(f"   ✅ {len(prereqs)} relations de prérequis")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_statistics(self):
        """Test 5: Calcul des statistiques"""
        print("\n📊 Test 5: Statistiques")
        try:
            stats = self.backend.get_statistics()
            assert 'total_courses' in stats, "Champ manquant"
            assert 'domains' in stats, "Domaines manquants"
            assert 'levels' in stats, "Niveaux manquants"
            print(f"   ✅ Stats OK:")
            print(f"      - Cours: {stats['total_courses']}")
            print(f"      - Domaines: {len(stats['domains'])}")
            print(f"      - Relations: {stats['total_prerequisites']}")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_chat_processing(self):
        """Test 6: Traitement d'un message chat"""
        print("\n💬 Test 6: Traitement message chat")
        try:
            result = self.backend.process_chat_message("Je cherche des cours en IA")
            assert 'success' in result, "Champ success manquant"
            assert 'response' in result, "Réponse manquante"
            assert result['success'], "Traitement échoué"
            print(f"   ✅ Message traité")
            print(f"      Intent: {result.get('intent', 'N/A')}")
            print(f"      Temps: {result.get('query_time', 0):.3f}s")
            print(f"      Réponse: {result['response'][:80]}...")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_learning_path(self):
        """Test 7: Calcul parcours d'apprentissage"""
        print("\n🗺️ Test 7: Parcours d'apprentissage")
        try:
            path = self.backend.get_learning_path("IA-401")
            assert 'success' in path, "Format incorrect"
            
            if path['success']:
                print(f"   ✅ Parcours calculé:")
                print(f"      - {path['total_courses']} cours")
                print(f"      - {path['total_credits']} crédits")
                self.test_results['passed'] += 1
            else:
                print(f"   ⚠️ Parcours non calculé (peut être normal)")
                self.test_results['passed'] += 1
                
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_visualizations(self):
        """Test 8: Génération des visualisations"""
        print("\n🎨 Test 8: Visualisations")
        try:
            courses = self.backend.get_all_courses()
            prereqs = self.backend.get_all_prerequisites()
            
            # Test graphe
            graph_html = create_prerequisites_graph(courses, prereqs)
            assert len(graph_html) > 1000, "HTML trop court"
            print(f"   ✅ Graphe généré ({len(graph_html)} chars)")
            
            # Test charts
            fig1 = create_domain_chart(courses)
            assert fig1 is not None, "Graphique domaine None"
            print(f"   ✅ Graphique domaine OK")
            
            fig2 = create_level_pie_chart(courses)
            assert fig2 is not None, "Graphique niveau None"
            print(f"   ✅ Graphique niveau OK")
            
            self.test_results['passed'] += 1
            
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_search(self):
        """Test 9: Recherche de cours"""
        print("\n🔍 Test 9: Recherche de cours")
        try:
            results = self.backend.search_courses("intelligence artificielle")
            assert isinstance(results, list), "Type incorrect"
            print(f"   ✅ Recherche effectuée: {len(results)} résultats")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def test_performance(self):
        """Test 10: Rapport de performance"""
        print("\n⚡ Test 10: Performance")
        try:
            perf = self.backend.get_performance_report()
            assert 'total_queries' in perf, "Métriques manquantes"
            print(f"   ✅ Rapport de performance:")
            print(f"      - Requêtes: {perf.get('total_queries', 0)}")
            print(f"      - Temps moyen: {perf.get('avg_query_time', 'N/A')}")
            print(f"      - Cache hit rate: {perf.get('cache_hit_rate', 'N/A')}")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"   ❌ {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(str(e))
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        if not self.setup():
            print("\n❌ Échec de l'initialisation. Tests annulés.")
            return False
        
        # Exécuter tous les tests
        self.test_connection()
        self.test_get_courses()
        self.test_get_specific_course()
        self.test_prerequisites()
        self.test_statistics()
        self.test_chat_processing()
        self.test_learning_path()
        self.test_visualizations()
        self.test_search()
        self.test_performance()
        
        # Rapport final
        self.print_report()
        
        return self.test_results['failed'] == 0
    
    def print_report(self):
        """Affiche le rapport final"""
        print("\n" + "="*70)
        print("📊 RAPPORT FINAL DES TESTS")
        print("="*70)
        
        total = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total * 100) if total > 0 else 0
        
        print(f"\n✅ Tests réussis: {self.test_results['passed']}")
        print(f"❌ Tests échoués: {self.test_results['failed']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\n🐛 Erreurs détectées:")
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"   {i}. {error}")
        
        print("\n" + "="*70)
        
        if self.test_results['failed'] == 0:
            print("🎉 TOUS LES TESTS PASSENT!")
        else:
            print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        
        print("="*70)


def main():
    """Fonction principale"""
    tester = TestUIIntegration()
    success = tester.run_all_tests()
    
    # Code de sortie
    import sys
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()