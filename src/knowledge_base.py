"""
Module de gestion de la base de connaissance RDF avec Apache Jena Fuseki
"""
from SPARQLWrapper import SPARQLWrapper, JSON, POST
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import logging
from typing import List, Dict, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Classe pour interagir avec la base de connaissance RDF (Fuseki)
    """
    
    def __init__(self, fuseki_url: str = "http://localhost:3030", 
                 dataset_name: str = "university",
                 username: str = "admin",
                 password: str = "admin123"):
        """
        Initialise la connexion à Fuseki
        
        Args:
            fuseki_url: URL du serveur Fuseki
            dataset_name: Nom du dataset dans Fuseki
            username: Nom d'utilisateur Fuseki
            password: Mot de passe Fuseki
        """
        self.fuseki_url = fuseki_url
        self.dataset_name = dataset_name
        
        # Endpoints SPARQL
        self.query_endpoint = f"{fuseki_url}/{dataset_name}/query"
        self.update_endpoint = f"{fuseki_url}/{dataset_name}/update"
        
        # Configuration SPARQLWrapper pour les requêtes
        self.sparql_query = SPARQLWrapper(self.query_endpoint)
        self.sparql_query.setReturnFormat(JSON)
        self.sparql_query.setCredentials(username, password)
        
        # Configuration pour les updates
        self.sparql_update = SPARQLWrapper(self.update_endpoint)
        self.sparql_update.setMethod(POST)
        self.sparql_update.setCredentials(username, password)
            
        # Namespace de l'ontologie
        self.ns = Namespace("http://www.university.edu/ontology/courses#")
        
        logger.info(f"✅ KnowledgeBase initialisée : {self.query_endpoint}")
    
    
    def execute_query(self, sparql_query: str) -> List[Dict]:
        """
        Exécute une requête SPARQL SELECT
        
        Args:
            sparql_query: La requête SPARQL
            
        Returns:
            Liste de dictionnaires avec les résultats
        """
        try:
            self.sparql_query.setQuery(sparql_query)
            results = self.sparql_query.query().convert()
            
            # Convertir les résultats en format simple
            bindings = results["results"]["bindings"]
            return bindings
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de la requête : {e}")
            return []
    
    
    def execute_update(self, sparql_update: str) -> bool:
        """
        Exécute une requête SPARQL UPDATE (INSERT, DELETE)
        
        Args:
            sparql_update: La requête SPARQL UPDATE
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.sparql_update.setQuery(sparql_update)
            self.sparql_update.query()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'update : {e}")
            return False
    
    
    def get_all_courses(self) -> List[Dict]:
        """
        Récupère tous les cours de la base
        
        Returns:
            Liste de tous les cours
        """
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?cours ?nom ?code ?credits ?duree ?description
        WHERE {
            ?cours a ?t .
            ?t rdfs:subClassOf* course:Course .

            OPTIONAL { ?cours course:nomCours ?nom }
            OPTIONAL { ?cours course:codeCours ?code }
            OPTIONAL { ?cours course:credits ?credits }
            OPTIONAL { ?cours course:duree ?duree }
            OPTIONAL { ?cours course:description ?description }
        }
        ORDER BY ?code
        """
        return self.execute_query(query)
    
    
    def get_course_by_code(self, code_cours: str) -> Optional[Dict]:
        """
        Récupère un cours par son code
        
        Args:
            code_cours: Code du cours (ex: "IA-401")
            
        Returns:
            Dictionnaire avec les infos du cours ou None
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?cours ?code ?nom ?credits ?duree ?description ?difficulte
        WHERE {{
            ?cours course:codeCours "{code_cours}" .
            BIND("{code_cours}" AS ?code)
            OPTIONAL {{ ?cours course:nomCours ?nom }}
            OPTIONAL {{ ?cours course:credits ?credits }}
            OPTIONAL {{ ?cours course:duree ?duree }}
            OPTIONAL {{ ?cours course:description ?description }}
            OPTIONAL {{ ?cours course:difficulte ?difficulte }}
        }}
        LIMIT 1
        """
        results = self.execute_query(query)
        return results[0] if results else None
    
    
    def get_prerequisites(self, code_cours: str) -> List[Dict]:
        """
        Récupère tous les prérequis d'un cours
        
        Args:
            code_cours: Code du cours
            
        Returns:
            Liste des cours prérequis
        """
        query = f"""
        PREFIX course: <http://www.university.edu/ontology/courses#>
        
        SELECT ?prerequis ?nomPrerequis ?codePrerequis
        WHERE {{
            ?cours course:codeCours "{code_cours}" .
            ?cours course:aPrerequis ?prerequis .
            ?prerequis course:nomCours ?nomPrerequis .
            ?prerequis course:codeCours ?codePrerequis .
        }}
        """
        return self.execute_query(query)
    
    
    def test_connection(self) -> bool:
        """
        Test la connexion à Fuseki
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
            self.execute_query(query)
            logger.info("✅ Connexion à Fuseki OK")
            return True
        except Exception as e:
            logger.error(f"❌ Impossible de se connecter à Fuseki: {e}")
            return False


# Fonction utilitaire
def create_knowledge_base() -> KnowledgeBase:
    """Crée et retourne une instance de KnowledgeBase"""
    return KnowledgeBase()


# Test du module
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DE KNOWLEDGE_BASE.PY")
    print("="*60)
    
    kb = create_knowledge_base()
    
    if kb.test_connection():
        print("\n✅ Connexion réussie !")
        
        # Test : Compter les triplets
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        results = kb.execute_query(query)
        if results:
            count = results[0]['count']['value']
            print(f"📊 Nombre de triplets dans la base : {count}")
        
        # Test : Récupérer quelques cours
        print("\n📚 Quelques cours dans la base:")
        courses = kb.get_all_courses()
        for course in courses[:5]:
            code = course.get('code', {}).get('value', 'N/A')
            nom = course.get('nom', {}).get('value', 'N/A')
            print(f"   - {code}: {nom}")
    else:
        print("\n❌ Connexion échouée. Vérifie que Fuseki tourne !")
        print("\n💡 Pour démarrer Fuseki:")
        print("   docker-compose up -d fuseki")