"""
Script pour peupler la base de connaissance avec des données de cours
"""
import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).parent.parent))

from src.knowledge_base import KnowledgeBase


class KnowledgeBasePopulator:
    """
    Classe pour peupler la base de connaissance depuis des fichiers CSV
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.course_uris = {}  # Mapping code → URI
        
    
    def populate_domains(self):
        """
        Crée les domaines dans la base de connaissance
        """
        print("\n📚 Création des domaines...")
        
        domains = [
            ("IntelligenceArtificielle", "Intelligence Artificielle"),
            ("DeveloppementWeb", "Développement Web"),
            ("BaseDeDonnees", "Bases de Données"),
            ("Informatique", "Informatique"),
            ("Mathematiques", "Mathématiques")
        ]
        
        for domain_id, domain_name in domains:
            domain_uri = f"http://www.university.edu/ontology/courses#{domain_id}"
            
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            INSERT DATA {{
                <{domain_uri}> rdf:type course:Domain ;
                    course:nomDomaine "{domain_name}" .
            }}
            """
            
            if self.kb.execute_update(query):
                print(f"  ✅ Domaine créé : {domain_name}")
            else:
                print(f"  ❌ Erreur création domaine : {domain_name}")
    
    
    def populate_levels(self):
        """
        Crée les niveaux dans la base de connaissance
        """
        print("\n📊 Création des niveaux...")
        
        levels = ["Debutant", "Intermediaire", "Avance"]
        
        for level in levels:
            level_uri = f"http://www.university.edu/ontology/courses#{level}"
            
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            INSERT DATA {{
                <{level_uri}> rdf:type course:Level .
            }}
            """
            
            if self.kb.execute_update(query):
                print(f"  ✅ Niveau créé : {level}")
            else:
                print(f"  ❌ Erreur création niveau : {level}")
    
    
    def populate_courses(self, csv_path: str):
        """
        Peuple les cours depuis un fichier CSV
        
        Args:
            csv_path: Chemin vers le fichier cours.csv
        """
        print("\n📘 Import des cours...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"  📄 {len(df)} cours à importer")
        except FileNotFoundError:
            print(f"  ❌ Fichier non trouvé : {csv_path}")
            return
        
        for idx, row in df.iterrows():
            code = row['code']
            course_uri = f"http://www.university.edu/ontology/courses#{code}"
            self.course_uris[code] = course_uri
            
            # Déterminer le type de cours
            if 'IA' in code:
                course_type = "CourseIA"
            elif 'WEB' in code:
                course_type = "CourseWeb"
            elif 'BDD' in code:
                course_type = "CourseBDD"
            elif 'MATH' in code:
                course_type = "CourseMathematiques"
            else:
                course_type = "CourseInformatique"
            
            # Échapper les guillemets dans la description
            description = str(row['description']).replace('"', '\\"')
            nom = str(row['nom']).replace('"', '\\"')
            
            # Créer le cours
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            INSERT DATA {{
                <{course_uri}> rdf:type course:Course , course:{course_type} ;
                    course:codeCours "{code}" ;
                    course:nomCours "{nom}" ;
                    course:credits "{row['credits']}"^^xsd:integer ;
                    course:duree "{row['duree']}"^^xsd:integer ;
                    course:difficulte "{row['difficulte']}"^^xsd:integer ;
                    course:description "{description}" ;
                    course:appartientADomaine course:{row['domaine']} ;
                    course:aNiveau course:{row['niveau']} .
            }}
            """
            
            if self.kb.execute_update(query):
                print(f"  ✅ Cours {idx+1}/{len(df)} : {code} - {row['nom']}")
            else:
                print(f"  ❌ Erreur cours : {code}")
    
    
    def populate_prerequisites(self, csv_path: str):
        """
        Ajoute les relations de prérequis
        
        Args:
            csv_path: Chemin vers le fichier prerequis.csv
        """
        print("\n🔗 Ajout des prérequis...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"  📄 {len(df)} relations de prérequis à créer")
        except FileNotFoundError:
            print(f"  ❌ Fichier non trouvé : {csv_path}")
            return
        
        for idx, row in df.iterrows():
            cours_code = row['cours']
            prerequis_code = row['prerequis']
            
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            
            INSERT DATA {{
                course:{cours_code} course:aPrerequis course:{prerequis_code} .
            }}
            """
            
            if self.kb.execute_update(query):
                print(f"  ✅ Prérequis {idx+1}/{len(df)} : {cours_code} → {prerequis_code}")
            else:
                print(f"  ❌ Erreur prérequis : {cours_code} → {prerequis_code}")
    
    
    def populate_skills(self, csv_path: str):
        """
        Crée les compétences et les lie aux cours
        
        Args:
            csv_path: Chemin vers le fichier competences.csv
        """
        print("\n🎯 Import des compétences...")
        
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"  ❌ Fichier non trouvé : {csv_path}")
            return
        
        # Récupérer toutes les compétences uniques
        skills = df['competence'].unique()
        print(f"  📄 {len(skills)} compétences uniques à créer")
        
        # Créer les compétences
        for skill in skills:
            skill_id = skill.replace(' ', '_').replace('/', '_').replace('.', '_')
            skill_uri = f"http://www.university.edu/ontology/courses#Skill_{skill_id}"
            
            # Échapper les guillemets
            skill_escaped = skill.replace('"', '\\"')
            
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            INSERT DATA {{
                <{skill_uri}> rdf:type course:Skill ;
                    course:nomCompetence "{skill_escaped}" .
            }}
            """
            
            self.kb.execute_update(query)
        
        print(f"  ✅ {len(skills)} compétences créées")
        
        # Lier les compétences aux cours
        print("\n🔗 Liaison cours-compétences...")
        for idx, row in df.iterrows():
            cours_code = row['cours']
            skill = row['competence']
            skill_id = skill.replace(' ', '_').replace('/', '_').replace('.', '_')
            
            query = f"""
            PREFIX course: <http://www.university.edu/ontology/courses#>
            
            INSERT DATA {{
                course:{cours_code} course:enseigneCompetence course:Skill_{skill_id} .
            }}
            """
            
            self.kb.execute_update(query)
            
            if (idx + 1) % 10 == 0:
                print(f"  ✅ {idx + 1}/{len(df)} liaisons créées...")
        
        print(f"  ✅ Toutes les liaisons cours-compétences créées")
    
    
    def run_full_population(self, data_dir: Path):
        """
        Exécute la population complète de la base de connaissance
        
        Args:
            data_dir: Répertoire contenant les fichiers CSV
        """
        print("="*70)
        print("🚀 DÉBUT DE LA POPULATION DE LA BASE DE CONNAISSANCE")
        print("="*70)
        
        try:
            # 1. Domaines et niveaux
            self.populate_domains()
            self.populate_levels()
            
            # 2. Cours
            self.populate_courses(data_dir / "cours.csv")
            
            # 3. Prérequis
            self.populate_prerequisites(data_dir / "prerequis.csv")
            
            # 4. Compétences
            self.populate_skills(data_dir / "competences.csv")
            
            print("\n" + "="*70)
            print("✅ POPULATION TERMINÉE AVEC SUCCÈS !")
            print("="*70)
            
            # Afficher des statistiques
            self.print_statistics()
            
        except Exception as e:
            print(f"\n❌ ERREUR GÉNÉRALE : {e}")
            import traceback
            traceback.print_exc()
    
    
    def print_statistics(self):
        """
        Affiche des statistiques sur la base de connaissance
        """
        print("\n📊 STATISTIQUES DE LA BASE DE CONNAISSANCE :")
        print("-" * 70)
        
        # Nombre total de triplets
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        results = self.kb.execute_query(query)
        if results:
            count = results[0]['count']['value']
            print(f"  📦 Nombre total de triplets : {count}")
        
        # Nombre de cours
        courses = self.kb.get_all_courses()
        print(f"  📚 Nombre de cours : {len(courses)}")
        
        # Nombre de prérequis
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        SELECT (COUNT(*) as ?count) WHERE {
            ?c course:aPrerequis ?p .
        }
        """
        results = self.kb.execute_query(query)
        if results:
            count = results[0]['count']['value']
            print(f"  🔗 Nombre de relations de prérequis : {count}")
        
        # Nombre de compétences
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
            ?s a course:Skill .
        }
        """
        results = self.kb.execute_query(query)
        if results:
            count = results[0]['count']['value']
            print(f"  🎯 Nombre de compétences : {count}")
        
        # Nombre de domaines
        query = """
        PREFIX course: <http://www.university.edu/ontology/courses#>
        SELECT (COUNT(*) as ?count) WHERE {
            ?d a course:Domain .
        }
        """
        results = self.kb.execute_query(query)
        if results:
            count = results[0]['count']['value']
            print(f"  📂 Nombre de domaines : {count}")
        
        print("-" * 70)


def main():
    """
    Fonction principale
    """
    print("\n" + "="*70)
    print("🎓 SCRIPT DE POPULATION DE LA BASE DE CONNAISSANCE UNIVERSITAIRE")
    print("="*70 + "\n")
    
    # Créer la connexion à la base de connaissance
    print("🔌 Connexion à Fuseki...")
    kb = KnowledgeBase()
    
    # Tester la connexion
    if not kb.test_connection():
        print("\n❌ ERREUR : Impossible de se connecter à Fuseki")
        print("💡 Vérifications à faire :")
        print("   1. Fuseki est-il démarré ? → docker-compose ps")
        print("   2. Le port 3030 est-il accessible ? → http://localhost:3030")
        print("   3. Le dataset 'university' existe-t-il dans Fuseki ?")
        return
    
    print("✅ Connexion établie !\n")
    
    # Définir le répertoire des données
    data_dir = Path(__file__).parent.parent / "data"
    
    # Vérifier que les fichiers CSV existent
    required_files = ["cours.csv", "prerequis.csv", "competences.csv"]
    missing_files = []
    
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ERREUR : Fichiers CSV manquants dans {data_dir} :")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Crée ces fichiers avant de relancer le script.")
        return
    
    print("✅ Tous les fichiers CSV sont présents\n")
    
    # Créer le populator
    populator = KnowledgeBasePopulator(kb)
    
    # Lancer la population
    populator.run_full_population(data_dir)
    
    print("\n" + "="*70)
    print("🎉 SCRIPT TERMINÉ !")
    print("="*70)
    print("\n💡 Prochaines étapes :")
    print("   1. Vérifie les données dans Fuseki : http://localhost:3030")
    print("   2. Teste des requêtes SPARQL dans l'interface web")
    print("   3. Partage knowledge_base.py avec les autres membres de l'équipe\n")


if __name__ == "__main__":
    main()