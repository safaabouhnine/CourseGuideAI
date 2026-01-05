"""
Moniteur de performance pour le système de recommandation
"""

import logging
import time
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Moniteur de performance pour tracer les métriques système
    """
    
    def __init__(self):
        """Initialise le moniteur"""
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_query_time': 0.0,
            'recommendations_generated': 0,
            'start_time': datetime.now()
        }
        logger.info("📊 PerformanceMonitor initialisé")
    
    
    def record_query(self, query_time: float, from_cache: bool = False):
        """
        Enregistre une requête
        
        Args:
            query_time: Temps d'exécution
            from_cache: Si résultat du cache
        """
        self.metrics['total_queries'] += 1
        self.metrics['total_query_time'] += query_time
        
        if from_cache:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
    
    
    def record_recommendation(self):
        """Enregistre une recommandation générée"""
        self.metrics['recommendations_generated'] += 1
    
    
    def get_report(self) -> Dict:
        """
        Génère un rapport de performance
        
        Returns:
            Rapport avec toutes les métriques
        """
        uptime = (datetime.now() - self.metrics['start_time']).total_seconds()
        
        cache_hit_rate = 0
        if self.metrics['total_queries'] > 0:
            cache_hit_rate = (self.metrics['cache_hits'] / 
                            self.metrics['total_queries'] * 100)
        
        avg_query_time = 0
        if self.metrics['total_queries'] > 0:
            avg_query_time = (self.metrics['total_query_time'] / 
                            self.metrics['total_queries'])
        
        return {
            'uptime_seconds': uptime,
            'total_queries': self.metrics['total_queries'],
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'avg_query_time': f"{avg_query_time:.3f}s",
            'recommendations_generated': self.metrics['recommendations_generated'],
            'queries_per_second': self.metrics['total_queries'] / uptime if uptime > 0 else 0
        }
    
    
    def print_report(self):
        """Affiche le rapport de performance"""
        report = self.get_report()
        
        print("\n" + "="*60)
        print("📊 RAPPORT DE PERFORMANCE")
        print("="*60)
        print(f"Uptime: {report['uptime_seconds']:.0f}s")
        print(f"Requêtes totales: {report['total_queries']}")
        print(f"Taux de cache hit: {report['cache_hit_rate']}")
        print(f"Temps moyen par requête: {report['avg_query_time']}")
        print(f"Recommandations générées: {report['recommendations_generated']}")
        print(f"Requêtes/seconde: {report['queries_per_second']:.2f}")
        print("="*60)


# Instance globale
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Retourne l'instance globale du moniteur"""
    return _monitor