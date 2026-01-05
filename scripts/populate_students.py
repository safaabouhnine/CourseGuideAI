"""
Script pour peupler la base avec des données étudiants
Version corrigée compatible avec students.csv
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
import csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREFIX = "http://www.university.edu/ontology/courses#"


def clean_uri_name(text):
    """Nettoie un texte pour en faire un nom d'URI valide"""
    return (text.replace(' ', '')
                .replace('é', 'e')
                .replace('è', 'e')
                .replace('à', 'a')
                .replace('ê', 'e')
                .replace('ô', 'o'))


def populate_students_from_csv(kb: KnowledgeBase, csv_file: str):
    """
    Peuple la base avec des étudiants depuis un CSV
    
    Format CSV attendu:
    student_id,nom,prenom,interets,competences,cours_suivis
    STU-001,Dupont,Marie,"IA,Math","Python,Algèbre","PROG-101,MATH-101"
    """
    print("\n" + "="*70)
    print("👥 POPULATION DES ÉTUDIANTS")
    print("="*70)
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier {csv_file} introuvable!")
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            students_data = list(reader)
        
        print(f"📊 {len(students_data)} étudiants à ajouter\n")
        
        for student in students_data:
            student_id = student['student_id'].strip()
            nom = student['nom'].strip()
            prenom = student['prenom'].strip()
            
            # URI de l'étudiant (utiliser student_id tel quel)
            student_uri = f"{PREFIX}{student_id}"
            
            # ===== 1. Créer l'étudiant =====
            update_student = f"""
            PREFIX course: <{PREFIX}>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            INSERT DATA {{
                <{student_uri}> a course:Student ;
                    course:nomEtudiant "{nom}" ;
                    course:prenomEtudiant "{prenom}" ;
                    course:studentId "{student_id}" ;
                    rdfs:label "{prenom} {nom}"@fr .
            }}
            """
            
            if kb.execute_update(update_student):
                print(f"✅ Étudiant créé: {prenom} {nom} ({student_id})")
            else:
                print(f"❌ Erreur pour {student_id}")
                continue
            
            # ===== 2. Ajouter les intérêts (domaines) =====
            if student.get('interets'):
                interets = [i.strip() for i in student['interets'].split(',')]
                
                for interet in interets:
                    if not interet:
                        continue
                    
                    # Nettoyer pour URI (ex: "Intelligence Artificielle" -> "IntelligenceArtificielle")
                    interet_uri_name = clean_uri_name(interet)
                    interet_uri = f"{PREFIX}{interet_uri_name}"
                    
                    # Créer le domaine s'il n'existe pas
                    update_domain = f"""
                    PREFIX course: <{PREFIX}>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
                    INSERT {{
                        <{interet_uri}> a course:Domain ;
                            rdfs:label "{interet}"@fr .
                    }}
                    WHERE {{
                        FILTER NOT EXISTS {{ <{interet_uri}> a course:Domain }}
                    }}
                    """
                    kb.execute_update(update_domain)
                    
                    # Lier l'étudiant au domaine
                    update_interet = f"""
                    PREFIX course: <{PREFIX}>
                    
                    INSERT DATA {{
                        <{student_uri}> course:intéresséPar <{interet_uri}> .
                    }}
                    """
                    kb.execute_update(update_interet)
                
                print(f"   📚 Intérêts: {', '.join(interets)}")
            
            # ===== 3. Ajouter les compétences =====
            if student.get('competences'):
                competences = [c.strip() for c in student['competences'].split(',')]
                
                for comp in competences:
                    if not comp:
                        continue
                    
                    comp_uri_name = clean_uri_name(comp)
                    comp_uri = f"{PREFIX}{comp_uri_name}"
                    
                    # Créer la compétence si elle n'existe pas
                    update_skill = f"""
                    PREFIX course: <{PREFIX}>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
                    INSERT {{
                        <{comp_uri}> a course:Skill ;
                            rdfs:label "{comp}"@fr .
                    }}
                    WHERE {{
                        FILTER NOT EXISTS {{ <{comp_uri}> a course:Skill }}
                    }}
                    """
                    kb.execute_update(update_skill)
                    
                    # Lier l'étudiant à la compétence
                    update_comp = f"""
                    PREFIX course: <{PREFIX}>
                    
                    INSERT DATA {{
                        <{student_uri}> course:possèdeCompetence <{comp_uri}> .
                    }}
                    """
                    kb.execute_update(update_comp)
                
                print(f"   🎓 Compétences: {', '.join(competences)}")
            
            # ===== 4. Ajouter les cours suivis =====
            if student.get('cours_suivis'):
                cours_list = [c.strip() for c in student['cours_suivis'].split(',')]
                cours_ajoutes = []
                
                for code_cours in cours_list:
                    if not code_cours:
                        continue
                    
                    # Trouver le cours par son code
                    query_cours = f"""
                    PREFIX course: <{PREFIX}>
                    
                    SELECT ?cours
                    WHERE {{
                        ?cours course:codeCours "{code_cours}" .
                    }}
                    LIMIT 1
                    """
                    
                    result = kb.execute_query(query_cours)
                    
                    if result:
                        cours_uri = result[0]['cours']['value']
                        
                        # Lier l'étudiant au cours
                        update_suivi = f"""
                        PREFIX course: <{PREFIX}>
                        
                        INSERT DATA {{
                            <{student_uri}> course:aSuivi <{cours_uri}> .
                        }}
                        """
                        
                        if kb.execute_update(update_suivi):
                            cours_ajoutes.append(code_cours)
                    else:
                        print(f"      ⚠️ Cours {code_cours} introuvable dans la base")
                
                if cours_ajoutes:
                    print(f"   📖 Cours suivis: {', '.join(cours_ajoutes)}")
            
            print()
        
        print("="*70)
        print("✅ POPULATION TERMINÉE")
        print("="*70)
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {csv_file}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


def verify_students(kb: KnowledgeBase):
    """Vérifie que les étudiants ont bien été ajoutés"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION DES ÉTUDIANTS")
    print("="*70)
    
    # Compter les étudiants
    query_count = f"""
    PREFIX course: <{PREFIX}>
    
    SELECT (COUNT(DISTINCT ?student) as ?count)
    WHERE {{
        ?student a course:Student .
    }}
    """
    
    result = kb.execute_query(query_count)
    count = result[0]['count']['value'] if result else "0"
    print(f"\n✅ {count} étudiants dans la base")
    
    # Lister les étudiants avec détails
    query_details = f"""
    PREFIX course: <{PREFIX}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?student ?label 
           (COUNT(DISTINCT ?interet) as ?interetCount)
           (COUNT(DISTINCT ?comp) as ?compCount)
           (COUNT(DISTINCT ?cours) as ?coursCount)
    WHERE {{
        ?student a course:Student .
        OPTIONAL {{ ?student rdfs:label ?label }}
        OPTIONAL {{ ?student course:intéresséPar ?interet }}
        OPTIONAL {{ ?student course:possèdeCompetence ?comp }}
        OPTIONAL {{ ?student course:aSuivi ?cours }}
    }}
    GROUP BY ?student ?label
    ORDER BY ?label
    """
    
    results = kb.execute_query(query_details)
    
    if results:
        print(f"\n📋 Détails des étudiants:\n")
        for r in results:
            label = r.get('label', {}).get('value', 'Sans nom')
            uri = r.get('student', {}).get('value', 'N/A')
            interets = r.get('interetCount', {}).get('value', '0')
            comps = r.get('compCount', {}).get('value', '0')
            cours = r.get('coursCount', {}).get('value', '0')
            
            print(f"   👤 {label}")
            print(f"      URI: {uri}")
            print(f"      📚 {interets} intérêts | 🎓 {comps} compétences | 📖 {cours} cours")
            print()
    
    # Afficher un profil complet d'exemple
    if results:
        print("\n" + "-"*70)
        print("📊 PROFIL DÉTAILLÉ D'UN ÉTUDIANT (exemple)")
        print("-"*70)
        
        first_student = results[0]['student']['value']
        
        query_profile = f"""
        PREFIX course: <{PREFIX}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?nom ?prenom
               (GROUP_CONCAT(DISTINCT ?interetLabel; separator=", ") as ?interets)
               (GROUP_CONCAT(DISTINCT ?compLabel; separator=", ") as ?competences)
               (GROUP_CONCAT(DISTINCT ?coursCode; separator=", ") as ?cours)
        WHERE {{
            <{first_student}> course:nomEtudiant ?nom ;
                              course:prenomEtudiant ?prenom .
            
            OPTIONAL {{
                <{first_student}> course:intéresséPar ?interet .
                ?interet rdfs:label ?interetLabel .
            }}
            
            OPTIONAL {{
                <{first_student}> course:possèdeCompetence ?comp .
                ?comp rdfs:label ?compLabel .
            }}
            
            OPTIONAL {{
                <{first_student}> course:aSuivi ?coursObj .
                ?coursObj course:codeCours ?coursCode .
            }}
        }}
        GROUP BY ?nom ?prenom
        """
        
        profile = kb.execute_query(query_profile)
        
        if profile:
            p = profile[0]
            print(f"\n   👤 {p.get('prenom', {}).get('value', '')} {p.get('nom', {}).get('value', '')}")
            print(f"   URI: {first_student}")
            print(f"\n   📚 Intérêts: {p.get('interets', {}).get('value', 'Aucun')}")
            print(f"   🎓 Compétences: {p.get('competences', {}).get('value', 'Aucune')}")
            print(f"   📖 Cours: {p.get('cours', {}).get('value', 'Aucun')}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 SCRIPT DE POPULATION DES ÉTUDIANTS")
    print("="*70)
    
    # Connexion à la base
    kb = KnowledgeBase()
    
    if not kb.test_connection():
        print("❌ Impossible de se connecter à Fuseki")
        print("💡 Lancez d'abord: docker-compose up -d fuseki")
        exit(1)
    
    # Peupler les étudiants
    csv_file = "data/students.csv"
    populate_students_from_csv(kb, csv_file)
    
    # Vérifier
    verify_students(kb)
    
    print("\n" + "="*70)
    print("✅ SCRIPT TERMINÉ!")
    print("="*70)
    print("\n💡 Prochaines étapes:")
    print("   1. Testez: python -m tests.test_reasoner_agent")
    print("   2. Utilisez l'URI: http://www.university.edu/ontology/courses#STU-001")