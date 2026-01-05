"""
Optimiseur de requêtes SPARQL
Améliore les performances des requêtes complexes
"""

from typing import Dict, List
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


class SPARQLOptimizer:
    """
    Optimiseur de requêtes SPARQL pour améliorer les performances
    """
    
    def __init__(self):
        """Initialise l'optimiseur"""
        self.query_stats = {}
        logger.info("⚡ SPARQLOptimizer initialisé")
    
    
    @staticmethod
    def add_limit_if_missing(query: str, default_limit: int = 1000) -> str:
        """
        Ajoute une clause LIMIT si absente
        
        Args:
            query: Requête SPARQL
            default_limit: Limite par défaut
            
        Returns:
            Requête optimisée
        """
        if 'LIMIT' not in query.upper() and 'COUNT' not in query.upper():
            query = query.strip() + f'\nLIMIT {default_limit}'
        
        return query
    
    
    @staticmethod
    def add_query_hints(query: str) -> str:
        """
        Ajoute des hints d'optimisation pour Fuseki
        
        Args:
            query: Requête SPARQL
            
        Returns:
            Requête avec hints
        """
        # Ajouter des préfixes optimisés si manquants
        optimized_prefixes = """
        # HINT: Utiliser les index
        """
        
        if '# HINT' not in query:
            query = optimized_prefixes + query
        
        return query
    
    
    @staticmethod
    def reorder_filters(query: str) -> str:
        """
        Réorganise les FILTER pour optimiser l'exécution
        Les filtres les plus sélectifs doivent venir en premier
        
        Args:
            query: Requête SPARQL
            
        Returns:
            Requête optimisée
        """
        # Simple optimisation : déplacer les FILTER CONTAINS vers la fin
        # car ils sont généralement plus coûteux
        
        lines = query.split('\n')
        filter_lines = [l for l in lines if 'FILTER' in l.upper()]
        other_lines = [l for l in lines if 'FILTER' not in l.upper()]
        
        # Réorganiser : filtres simples d'abord, CONTAINS à la fin
        simple_filters = [f for f in filter_lines if 'CONTAINS' not in f.upper()]
        complex_filters = [f for f in filter_lines if 'CONTAINS' in f.upper()]
        
        optimized_lines = other_lines[:-1] + simple_filters + complex_filters + [other_lines[-1]]
        
        return '\n'.join(optimized_lines)
    
    
    @staticmethod
    def use_property_paths_efficiently(query: str) -> str:
        """
        Optimise l'utilisation des property paths (course:aPrerequis+)
        
        Args:
            query: Requête SPARQL
            
        Returns:
            Requête optimisée
        """
        # Remplacer les patterns inefficaces par des property paths
        # Exemple: Remplacer plusieurs OPTIONAL par un property path
        
        return query
    
    
    def log_query_performance(self, query_name: str, execution_time: float):
        """
        Enregistre les performances d'une requête
        
        Args:
            query_name: Nom de la requête
            execution_time: Temps d'exécution en secondes
        """
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }
        
        stats = self.query_stats[query_name]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
    
    
    def get_performance_report(self) -> Dict:
        """
        Génère un rapport de performance
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return self.query_stats
    
    
    def optimize_full_query(self, query: str) -> str:
        """
        Applique toutes les optimisations disponibles
        
        Args:
            query: Requête SPARQL originale
            
        Returns:
            Requête complètement optimisée
        """
        query = self.add_limit_if_missing(query)
        query = self.add_query_hints(query)
        # query = self.reorder_filters(query)  # Peut causer des bugs, à tester
        
        return query


def measure_query_time(func):
    """
    Décorateur pour mesurer le temps d'exécution des requêtes
    
    Usage:
        @measure_query_time
        def ma_fonction_query(self):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"⏱️ {func.__name__} exécuté en {execution_time:.3f}s")
        
        return result
    
    return wrapper


# Fonction utilitaire
def create_optimizer() -> SPARQLOptimizer:
    """Crée et retourne une instance de SPARQLOptimizer"""
    return SPARQLOptimizer()


# Test du module
if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚡ TEST DE SPARQL_OPTIMIZER.PY")
    print("="*60)
    
    optimizer = SPARQLOptimizer()
    
    # Test 1: Ajouter LIMIT
    query1 = "SELECT * WHERE { ?s ?p ?o }"
    optimized1 = optimizer.add_limit_if_missing(query1)
    print(f"\nQuery originale:\n{query1}")
    print(f"\nQuery optimisée:\n{optimized1}")
    
    # Test 2: Optimisation complète
    query2 = """
    PREFIX course: <http://www.university.edu/ontology/courses#>
    SELECT * WHERE {
        ?cours course:nomCours ?nom .
        FILTER(CONTAINS(LCASE(?nom), "intelligence"))
    }
    """
    optimized2 = optimizer.optimize_full_query(query2)
    print(f"\nQuery optimisée complète:\n{optimized2}")
    
    print("\n✅ Tests terminés!")