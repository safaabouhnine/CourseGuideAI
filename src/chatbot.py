from src.conversation_manager import ConversationManager
import sys


class CourseGuideChatbot:
    def __init__(self):
        """Initialise le chatbot complet"""
        print("🤖 Initialisation de CourseGuideAI...\n")
        self.conversation_manager = ConversationManager()
        self.is_running = False
        print("✅ CourseGuideAI est prêt !\n")
    
    def start(self):
        """Démarre le chatbot en mode interactif"""
        self.is_running = True
        
        # Message de bienvenue
        self._print_welcome_message()
        
        # Boucle de conversation
        while self.is_running:
            try:
                # Lire l'entrée utilisateur
                user_input = input("\n💬 Vous: ").strip()
                
                # Vérifier les commandes spéciales
                if self._handle_special_commands(user_input):
                    continue
                
                # Traiter le message
                if user_input:
                    print("\n🤖 CourseGuideAI: ", end="")
                    response = self.conversation_manager.process_message(user_input)
                    print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Au revoir ! À bientôt !")
                self.is_running = False
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
                print("💡 Tapez 'aide' pour voir les commandes disponibles")
    
    def _print_welcome_message(self):
        """Affiche le message de bienvenue"""
        print("=" * 70)
        print("🎓 Bienvenue sur CourseGuideAI ! 🎓".center(70))
        print("=" * 70)
        print("\nJe suis votre assistant intelligent pour vous guider dans le choix de cours.")
        print("\n📚 Exemples de questions que vous pouvez me poser :")
        print("  • 'Je cherche des cours en intelligence artificielle'")
        print("  • 'Quels sont les prérequis pour IA-401 ?'")
        print("  • 'Je veux devenir expert en Machine Learning'")
        print("  • 'Montre-moi tous les cours disponibles'")
        print("\n💡 Commandes spéciales :")
        print("  • 'aide' - Afficher l'aide")
        print("  • 'historique' - Voir l'historique de conversation")
        print("  • 'contexte' - Voir le contexte actuel")
        print("  • 'reset' - Réinitialiser la conversation")
        print("  • 'quitter' - Quitter le chatbot")
        print("\n" + "=" * 70 + "\n")
    
    def _handle_special_commands(self, command: str) -> bool:
        """
        Gère les commandes spéciales
        
        Args:
            command: Commande entrée par l'utilisateur
            
        Returns:
            True si c'est une commande spéciale, False sinon
        """
        command_lower = command.lower()
        
        if command_lower in ['quitter', 'exit', 'quit', 'q']:
            print("\n👋 Au revoir ! À bientôt !")
            self.is_running = False
            return True
        
        elif command_lower in ['aide', 'help', 'h', '?']:
            self._show_help()
            return True
        
        elif command_lower in ['historique', 'history']:
            self._show_history()
            return True
        
        elif command_lower in ['contexte', 'context']:
            self._show_context()
            return True
        
        elif command_lower in ['reset', 'clear', 'nouveau']:
            self._reset_conversation()
            return True
        
        return False
    
    def _show_help(self):
        """Affiche l'aide complète"""
        print("\n📖 GUIDE D'UTILISATION")
        print("=" * 70)
        print("\n🎯 Types de questions que je comprends :\n")
        
        print("1️⃣ Recherche de cours :")
        print("   • 'Je cherche des cours en [domaine]'")
        print("   • 'Montre-moi des cours de niveau [débutant/intermédiaire/avancé]'")
        print("   • 'Quels cours en intelligence artificielle ?'")
        
        print("\n2️⃣ Vérification de prérequis :")
        print("   • 'Quels sont les prérequis pour [CODE-COURS] ?'")
        print("   • 'Est-ce que je peux suivre IA-401 ?'")
        
        print("\n3️⃣ Parcours d'apprentissage :")
        print("   • 'Je veux devenir expert en [domaine]'")
        print("   • 'Par où commencer pour apprendre le Machine Learning ?'")
        print("   • 'Quel parcours pour maîtriser le développement web ?'")
        
        print("\n4️⃣ Informations sur un cours :")
        print("   • 'C'est quoi le cours [CODE-COURS] ?'")
        print("   • 'Donne-moi des infos sur IA-401'")
        
        print("\n5️⃣ Liste complète :")
        print("   • 'Montre-moi tous les cours'")
        print("   • 'Liste tous les cours disponibles'")
        
        print("\n💡 Commandes spéciales :")
        print("   • aide - Afficher cette aide")
        print("   • historique - Voir l'historique de conversation")
        print("   • contexte - Voir le contexte actuel")
        print("   • reset - Réinitialiser la conversation")
        print("   • quitter - Quitter le chatbot")
        print("\n" + "=" * 70)
    
    def _show_history(self):
        """Affiche l'historique de conversation"""
        history = self.conversation_manager.get_conversation_history()
        
        if not history:
            print("\n📭 Aucun historique pour le moment.")
            return
        
        print("\n📜 HISTORIQUE DE CONVERSATION")
        print("=" * 70)
        
        for i, exchange in enumerate(history, 1):
            print(f"\n💬 Échange {i} - {exchange['timestamp'].strftime('%H:%M:%S')}")
            print(f"👤 Vous: {exchange['user']}")
            print(f"🤖 Bot: {exchange['bot'][:100]}..." if len(exchange['bot']) > 100 else f"🤖 Bot: {exchange['bot']}")
        
        print("\n" + "=" * 70)
    
    def _show_context(self):
        """Affiche le contexte actuel"""
        print("\n" + self.conversation_manager.get_context_summary())
    
    def _reset_conversation(self):
        """Réinitialise la conversation"""
        self.conversation_manager.clear_history()
        print("\n🔄 Conversation réinitialisée. Recommençons depuis le début !")
    
    def chat(self, message: str) -> str:
        """
        Mode API : envoyer un message et recevoir une réponse
        
        Args:
            message: Message de l'utilisateur
            
        Returns:
            Réponse du chatbot
        """
        return self.conversation_manager.process_message(message)
    
    def get_conversation_state(self) -> dict:
        """
        Retourne l'état complet de la conversation
        
        Returns:
            Dictionnaire avec l'historique et le contexte
        """
        return {
            'history': self.conversation_manager.get_conversation_history(),
            'context': self.conversation_manager.context
        }


# Point d'entrée principal
def main():
    """Fonction principale pour lancer le chatbot"""
    chatbot = CourseGuideChatbot()
    chatbot.start()


if __name__ == "__main__":
    main()