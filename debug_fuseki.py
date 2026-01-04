"""
Script de debug pour vérifier le contenu de Fuseki
"""

from src.knowledge_base import KnowledgeBase

def test_fuseki_content():
    """Teste différentes requêtes pour voir ce qu'il y a dans Fuseki"""
    
    kb = KnowledgeBase()
    print("🔍 DEBUG : Vérification du contenu de Fuseki\n")
    print("=" * 70)
    
    # Test 1 : Compter tous les triplets
    print("\n📊 Test 1 : Compter tous les triplets")
    query1 = """
    SELECT (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o .
    }
    """
    result1 = kb.execute_query(query1)
    print(f"Résultat : {result1}")
    
    # Test 2 : Lister tous les types de classes
    print("\n📊 Test 2 : Lister tous les types (classes)")
    query2 = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?type (COUNT(?s) as ?count)
    WHERE {
        ?s rdf:type ?type .
    }
    GROUP BY ?type
    """
    result2 = kb.execute_query(query2)
    print(f"Résultat : {result2}")
    
    # Test 3 : Lister quelques instances de cours (peu importe leur type)
    print("\n📊 Test 3 : Lister les 5 premières instances avec rdf:type")
    query3 = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?subject ?type ?label
    WHERE {
        ?subject rdf:type ?type .
        OPTIONAL { ?subject rdfs:label ?label . }
    }
    LIMIT 10
    """
    result3 = kb.execute_query(query3)
    print(f"Résultat : {result3}")
    
    # Test 4 : Chercher spécifiquement course:Course
    print("\n📊 Test 4 : Chercher les cours avec type course:Course")
    query4 = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX course: <http://www.semanticweb.org/ontologies/2024/university#>
    SELECT ?course ?label ?code
    WHERE {
        ?course rdf:type course:Course .
        OPTIONAL { ?course rdfs:label ?label . }
        OPTIONAL { ?course course:codeCours ?code . }
    }
    LIMIT 5
    """
    result4 = kb.execute_query(query4)
    print(f"Résultat : {result4}")
    
    # Test 5 : Lister tous les prédicats utilisés
    print("\n📊 Test 5 : Lister tous les prédicats (propriétés)")
    query5 = """
    SELECT DISTINCT ?predicate (COUNT(?s) as ?count)
    WHERE {
        ?s ?predicate ?o .
    }
    GROUP BY ?predicate
    ORDER BY DESC(?count)
    """
    result5 = kb.execute_query(query5)
    print(f"Résultat : {result5}")
    
    # Test 6 : Chercher n'importe quoi avec "label"
    print("\n📊 Test 6 : Chercher tout ce qui a un label")
    query6 = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?subject ?label
    WHERE {
        ?subject rdfs:label ?label .
    }
    LIMIT 10
    """
    result6 = kb.execute_query(query6)
    print(f"Résultat : {result6}")
    
    # Test 7 : Requête ultra simple
    print("\n📊 Test 7 : Sélectionner les 10 premiers triplets")
    query7 = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    LIMIT 10
    """
    result7 = kb.execute_query(query7)
    print(f"Résultat : {result7}")
    
    print("\n" + "=" * 70)
    print("✅ Tests de debug terminés")
    print("\n💡 ANALYSE :")
    print("   - Si Test 1 montre 0 triplets → La base est vide")
    print("   - Si Test 2 montre des types → Vérifier le namespace")
    print("   - Si Test 4 échoue → Le préfixe 'course:' n'est pas bon")


if __name__ == "__main__":
    test_fuseki_content()