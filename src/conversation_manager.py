"""
Module de gestion de conversation avec contexte et réponses naturelles
Membre 2 : Spécialiste NLP - Conversation Manager
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.sparql_query_builder import SPARQLQueryBuilder
from src.knowledge_base import KnowledgeBase


class ConversationManager:
    def __init__(self):
        """Initialise le gestionnaire de conversation"""
        self.kb = KnowledgeBase()
        self.query_builder = SPARQLQueryBuilder(self.kb)
        
        # Historique de conversation
        self.history: List[Dict[str, Any]] = []
        
        # Contexte de la conversation
        self.context = {
            'last_intent': None,
            'last_entities': {},
            'last_courses': [],
            'user_domain': None,
            'user_level': None
        }
        
        print("✅ ConversationManager initialisé")
    
    def process_message(self, user_message: str) -> str:
        """
        Traite un message utilisateur et retourne une réponse
        
        Args:
            user_message: Message de l'utilisateur
            
        Returns:
            Réponse formatée du chatbot
        """
        # Ajouter à l'historique
        self.history.append({
            'timestamp': datetime.now(),
            'user': user_message,
            'bot': None
        })
        
        # Traiter la requête
        result = self.query_builder.process_user_query(user_message)
        
        # Mettre à jour le contexte
        self._update_context(result)
        
        # Générer une réponse naturelle
        response = self._generate_response(result)
        
        # Ajouter la réponse à l'historique
        self.history[-1]['bot'] = response
        
        return response
    
    def _update_context(self, result: Dict[str, Any]):
        """Met à jour le contexte de conversation"""
        self.context['last_intent'] = result['intent']
        
        # Extraire les entités si présentes
        if 'data' in result and result['data']:
            if isinstance(result['data'], list):
                self.context['last_courses'] = result['data']
            elif isinstance(result['data'], dict):
                if 'domain' in result['data']:
                    self.context['user_domain'] = result['data']['domain']
    
    def _generate_response(self, result: Dict[str, Any]) -> str:
        """
        Génère une réponse naturelle selon l'intention et les données
        
        Args:
            result: Résultat de la requête SPARQL
            
        Returns:
            Réponse formatée
        """
        intent = result['intent']
        data = result['data']
        
        if intent == 'recherche_cours':
            return self._format_course_search_response(data)
        
        elif intent == 'verifier_prerequis':
            return self._format_prerequisites_response(data)
        
        elif intent == 'parcours_apprentissage':
            return self._format_learning_path_response(data)
        
        elif intent == 'info_cours':
            return self._format_course_info_response(data)
        
        elif intent == 'liste_cours':
            return self._format_all_courses_response(data)
        
        else:
            return "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler ?"
    
    def _format_course_search_response(self, courses: List[Dict]) -> str:
        """Formate la réponse pour une recherche de cours"""
        if not courses or len(courses) == 0:
            return ("Je n'ai trouvé aucun cours correspondant à votre recherche. 😔\n\n"
                    "💡 Suggestions :\n"
                    "- Essayez de chercher par domaine : 'cours en web', 'cours en IA'\n"
                    "- Ou demandez la liste complète : 'montre-moi tous les cours'")
        
        response = f"✅ J'ai trouvé **{len(courses)} cours** pour vous !\n\n"
        
        for i, course in enumerate(courses, 1):
            response += f"**{i}. {course['label']}**\n"
            response += f"   📌 Code: {course['code']}\n"
            response += f"   🎓 Crédits: {course['credits']}\n"
            
            if course.get('description'):
                desc = course['description'][:100] + "..." if len(course['description']) > 100 else course['description']
                response += f"   📝 {desc}\n"
            
            response += "\n"
        
        response += "💬 Besoin de plus d'infos ? Demandez-moi les prérequis ou plus de détails sur un cours !"
        
        return response
    
    def _format_prerequisites_response(self, prereqs: Dict) -> str:
        """Formate la réponse pour les prérequis"""
        if not prereqs.get('course'):
            return f"❌ {prereqs.get('message', 'Cours non trouvé')}\n\n💡 Vérifiez le code du cours (ex: IA-401, WEB-301)"
        
        course_name = prereqs['course']
        prereq_list = prereqs['prerequisites']
        
        if not prereq_list:
            return (f"🎉 Bonne nouvelle !\n\n"
                    f"Le cours **{course_name}** ({prereqs['code']}) n'a **aucun prérequis**.\n"
                    f"Vous pouvez le suivre directement ! 🚀")
        
        response = f"📋 Prérequis pour **{course_name}** ({prereqs['code']}) :\n\n"
        
        for i, prereq in enumerate(prereq_list, 1):
            response += f"{i}. **{prereq['label']}** ({prereq['code']})\n"
        
        response += f"\n💡 Vous devez compléter ces {len(prereq_list)} cours avant de pouvoir suivre {course_name}."
        
        return response
    
    def _format_learning_path_response(self, courses: List[Dict]) -> str:
        """Formate la réponse pour un parcours d'apprentissage"""
        if not courses or len(courses) == 0:
            return ("Je n'ai pas trouvé de parcours pour ce domaine. 🤔\n\n"
                    "💡 Essayez : 'parcours en Intelligence Artificielle' ou 'parcours en Web'")
        
        response = "🎯 **Votre parcours d'apprentissage recommandé** :\n\n"
        response += "Suivez ces cours dans l'ordre pour une progression optimale :\n\n"
        
        # Organiser par niveau (basé sur le code)
        beginner = [c for c in courses if '-1' in c['code'] or '-2' in c['code']]
        intermediate = [c for c in courses if '-3' in c['code']]
        advanced = [c for c in courses if '-4' in c['code'] or '-5' in c['code']]
        
        if beginner:
            response += "**🌱 Niveau Débutant :**\n"
            for course in beginner:
                response += f"  → {course['label']} ({course['code']})\n"
            response += "\n"
        
        if intermediate:
            response += "**📈 Niveau Intermédiaire :**\n"
            for course in intermediate:
                response += f"  → {course['label']} ({course['code']})\n"
            response += "\n"
        
        if advanced:
            response += "**🚀 Niveau Avancé :**\n"
            for course in advanced:
                response += f"  → {course['label']} ({course['code']})\n"
            response += "\n"
        
        response += "💬 Voulez-vous plus d'infos sur un cours spécifique ?"
        
        return response
    
    def _format_course_info_response(self, info: Optional[Dict]) -> str:
        """Formate la réponse pour les infos détaillées d'un cours"""
        if not info:
            return "❌ Cours non trouvé. Vérifiez le code (ex: IA-401)"
        
        response = f"📚 **{info['label']}**\n\n"
        response += f"🔖 **Code :** {info['code']}\n"
        response += f"🎓 **Crédits :** {info['credits']}\n\n"
        
        if info.get('description'):
            response += f"📝 **Description :**\n{info['description']}\n\n"
        
        if info.get('skills'):
            response += f"💡 **Compétences enseignées :**\n"
            for skill in info['skills']:
                response += f"  • {skill}\n"
            response += "\n"
        
        response += "💬 Voulez-vous connaître les prérequis de ce cours ?"
        
        return response
    
    def _format_all_courses_response(self, courses: List[Dict]) -> str:
        """Formate la réponse pour la liste de tous les cours"""
        if not courses:
            return "❌ Aucun cours disponible dans la base de données."
        
        response = f"📚 **Catalogue complet : {len(courses)} cours disponibles**\n\n"
        
        # Grouper par domaine (basé sur le code)
        domains = {}
        for course in courses:
            code_prefix = course['code'].split('-')[0] if '-' in course['code'] else 'AUTRE'
            if code_prefix not in domains:
                domains[code_prefix] = []
            domains[code_prefix].append(course)
        
        for domain, domain_courses in domains.items():
            domain_names = {
                'IA': '🤖 Intelligence Artificielle',
                'WEB': '🌐 Développement Web',
                'BDD': '💾 Base de Données',
                'MATH': '📊 Mathématiques',
                'SEC': '🔒 Sécurité'
            }
            
            response += f"**{domain_names.get(domain, domain)} :**\n"
            for course in domain_courses:
                response += f"  • {course['label']} ({course['code']})\n"
            response += "\n"
        
        response += "💬 Dites-moi quel domaine vous intéresse pour des recommandations personnalisées !"
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Retourne l'historique de conversation"""
        return self.history
    
    def clear_history(self):
        """Efface l'historique"""
        self.history = []
        self.context = {
            'last_intent': None,
            'last_entities': {},
            'last_courses': [],
            'user_domain': None,
            'user_level': None
        }
        print("✅ Historique effacé")
    
    def get_context_summary(self) -> str:
        """Retourne un résumé du contexte actuel"""
        summary = "📊 **Contexte de conversation :**\n\n"
        
        if self.context['last_intent']:
            summary += f"Dernière intention : {self.context['last_intent']}\n"
        
        if self.context['user_domain']:
            summary += f"Domaine d'intérêt : {self.context['user_domain']}\n"
        
        if self.context['last_courses']:
            summary += f"Cours en contexte : {len(self.context['last_courses'])}\n"
        
        summary += f"Messages échangés : {len(self.history)}\n"
        
        return summary


# Test du module
if __name__ == "__main__":
    print("🧪 Test du ConversationManager\n")
    
    manager = ConversationManager()
    
    # Scénario de conversation
    test_messages = [
        "Bonjour ! Je cherche des cours en intelligence artificielle",
        "Quels sont les prérequis pour IA-401 ?",
        "Montre-moi tous les cours disponibles"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"👤 Utilisateur: {msg}")
        print(f"{'='*60}")
        
        response = manager.process_message(msg)
        print(f"🤖 Bot:\n{response}\n")
    
    # Afficher le contexte
    print(f"\n{'='*60}")
    print(manager.get_context_summary())