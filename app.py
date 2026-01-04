"""
Application Streamlit - Interface du Chatbot de Recommandation de Cours
Membre 4 : Interface & Visualisation
"""
import plotly.graph_objects as go
import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent))

from src.ui.backend_adapter import BackendAdapter
from src.ui.visualization import (
    create_prerequisites_graph,
    create_domain_chart,
    create_level_pie_chart,
    create_credits_distribution,
    create_learning_path_viz
)

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="CourseGuide AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .course-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.75rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    .level-debutant {
        background-color: #4CAF50;
        color: white;
    }
    
    .level-intermediaire {
        background-color: #FFC107;
        color: black;
    }
    
    .level-avance {
        background-color: #F44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALISATION ====================

@st.cache_resource
def init_backend():
    """Initialise le backend adapter"""
    try:
        backend = BackendAdapter()
        return backend
    except Exception as e:
        st.error(f"❌ Erreur initialisation backend: {e}")
        st.info("💡 Vérifiez que Fuseki est démarré: `docker compose up -d`")
        st.stop()

# Charger le backend
backend = init_backend()

# Test de connexion
if not backend.test_connection():
    st.error("❌ Impossible de se connecter à Fuseki")
    st.info("Vérifiez que Fuseki tourne sur http://localhost:3030")
    st.code("docker compose up -d")
    st.stop()

# ==================== FONCTIONS UTILITAIRES ====================

def format_course_badge(niveau):
    """Génère un badge HTML pour le niveau"""
    if niveau == "Débutant":
        return '<span class="level-badge level-debutant">🟢 Débutant</span>'
    elif niveau == "Intermédiaire":
        return '<span class="level-badge level-intermediaire">🟡 Intermédiaire</span>'
    else:
        return '<span class="level-badge level-avance">🔴 Avancé</span>'

# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown("# 🎓 CourseGuide AI")
    st.markdown("*Votre assistant intelligent*")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "📍 Navigation",
        [
            "💬 Chatbot",
            "📊 Dashboard",
            "🔍 Explorer les cours",
            "🗺️ Graphe RDF",
            "📈 Statistiques"
        ],
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    # Statut système
    with st.expander("⚙️ Statut Système", expanded=False):
        stats = backend.get_statistics()
        st.metric("📚 Cours", stats['total_courses'])
        st.metric("🔗 Relations", stats['total_prerequisites'])
        st.metric("🏷️ Domaines", len(stats['domains']))
        st.success("✅ Fuseki connecté")
    
    # Aide rapide
    with st.expander("❓ Aide Rapide"):
        st.markdown("""
        **Exemples de questions:**
        
        - 🔍 *Je cherche des cours en IA*
        - ✅ *Quels sont les prérequis de IA-401?*
        - 🎯 *Je veux devenir expert en ML*
        - 📚 *Parcours débutant en Web*
        - 🗺️ *Cours les plus difficiles*
        """)
    
    st.markdown("---")
    st.caption("v1.0 - Membre 4")

# ==================== PAGE 1: CHATBOT ====================
if page == "💬 Chatbot":
    st.markdown('<p class="main-header">💬 Assistant Intelligent</p>', unsafe_allow_html=True)

    # Initialiser l'historique (une seule fois)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": """👋 **Bonjour !** Je suis votre assistant pour trouver les cours parfaits.

**Je peux vous aider à:**
- 🔍 Rechercher des cours par domaine ou niveau
- ✅ Vérifier les prérequis nécessaires
- 🗺️ Créer un parcours d'apprentissage personnalisé
- 📚 Obtenir des informations détaillées sur les cours

**Posez-moi une question pour commencer !**"""
            }
        ]

    def handle_message(text: str, with_spinner: bool = False):
        """Ajoute un message user, appelle le backend, ajoute la réponse assistant."""
        st.session_state.chat_history.append({"role": "user", "content": text})

        if with_spinner:
            with st.spinner("🤔 Analyse de votre question..."):
                result = backend.process_chat_message(text)
        else:
            result = backend.process_chat_message(text)

        if result.get("success"):
            response = result.get("response", "")
        else:
            response = f"❌ **Erreur:** {result.get('response', 'Erreur inconnue')}\n\nVeuillez réessayer ou reformuler votre question."

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    col1, col2 = st.columns([2, 1])

    # ----- Colonne gauche : conversation -----
    with col1:
        st.markdown("### 💭 Conversation")

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # ----- Colonne droite : actions / suggestions -----
    with col2:
        st.markdown("### 🎯 Actions Rapides")

        if st.button("🧹 Nouvelle conversation", use_container_width=True):
            backend.reset_conversation()
            st.session_state.chat_history = [
                {"role": "assistant", "content": "✨ Conversation réinitialisée. Comment puis-je vous aider ?"}
            ]
            st.rerun()

        if st.button("💾 Sauvegarder conversation", use_container_width=True):
            chat_text = ""
            for msg in st.session_state.chat_history:
                role = "Vous" if msg["role"] == "user" else "Assistant"
                chat_text += f"{role}: {msg['content']}\n\n"

            st.download_button(
                "📥 Télécharger",
                chat_text,
                "conversation.txt",
                "text/plain",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### 💡 Suggestions")

        suggestions = [
            ("🤖", "Cours en Intelligence Artificielle"),
            ("📋", "Prérequis pour IA-401"),
            ("🌐", "Parcours débutant en Web"),
            ("📊", "Cours les plus difficiles"),
            ("🎓", "Cours avec le plus de crédits"),
        ]

        for icon, text in suggestions:
            if st.button(f"{icon} {text}", key=f"sug_{text}", use_container_width=True):
                handle_message(text, with_spinner=False)

    # IMPORTANT : l'input doit être HORS des colonnes
    user_input = st.chat_input("💬 Posez votre question...", key="chat_input")
    if user_input:
        handle_message(user_input, with_spinner=True)

        st.markdown("---")
        st.markdown("### 📊 Statistiques Session")
        if len(st.session_state.chat_history) > 1:
            messages_count = len(st.session_state.chat_history) - 1
            st.metric("Messages échangés", messages_count)

# ==================== PAGE 2: DASHBOARD ====================

elif page == "📊 Dashboard":
    st.markdown('<p class="main-header">📊 Tableau de Bord</p>', unsafe_allow_html=True)
    
    # Récupérer les données
    courses = backend.get_all_courses()
    stats = backend.get_statistics()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 Total Cours",
            value=stats['total_courses'],
            help="Nombre total de cours disponibles dans la base"
        )
    
    with col2:
        st.metric(
            label="🏷️ Domaines",
            value=len(stats['domains']),
            help="Nombre de domaines d'études différents"
        )
    
    with col3:
        beginner = stats['levels'].get('Débutant', 0)
        st.metric(
            label="🟢 Niveau Débutant",
            value=beginner,
            help="Cours accessibles aux débutants"
        )
    
    with col4:
        st.metric(
            label="🔗 Relations",
            value=stats['total_prerequisites'],
            help="Nombre total de relations de prérequis"
        )
    
    st.markdown("---")
    
    # Graphiques détaillés
    tab1, tab2, tab3 = st.tabs(["📊 Par Domaine", "🎯 Par Niveau", "⭐ Par Crédits"])
    
    with tab1:
        st.markdown("### Répartition des cours par domaine")
        fig_domain = create_domain_chart(courses)
        st.plotly_chart(fig_domain, use_container_width=True)
        
        # Détails par domaine
        st.markdown("#### Détails")
        for domain, count in stats['domains'].items():
            percentage = (count / stats['total_courses']) * 100
            st.write(f"**{domain}:** {count} cours ({percentage:.1f}%)")
    
    with tab2:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### Distribution")
            fig_level = create_level_pie_chart(courses)
            st.plotly_chart(fig_level, use_container_width=True)
        
        with col_b:
            st.markdown("### Progression par niveau")
            for level in ['Débutant', 'Intermédiaire', 'Avancé']:
                count = stats['levels'].get(level, 0)
                percentage = (count / stats['total_courses']) * 100
                st.progress(
                    percentage / 100,
                    text=f"{level}: {count} cours ({percentage:.1f}%)"
                )
    
    with tab3:
        st.markdown("### Distribution des crédits ECTS")
        fig_credits = create_credits_distribution(courses)
        st.plotly_chart(fig_credits, use_container_width=True)
        
        # Stats crédits
        df = pd.DataFrame(courses)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Crédits moyen", f"{df['credits'].mean():.1f}")
        with col2:
            st.metric("Maximum", df['credits'].max())
        with col3:
            st.metric("Minimum", df['credits'].min())
    
    st.markdown("---")
    
    # Tableau récapitulatif
    st.markdown("### 📋 Liste Complète des Cours")
    
    # Filtres rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_domain = st.selectbox(
            "Filtrer par domaine",
            ["Tous"] + list(stats['domains'].keys())
        )
    with col2:
        filter_level = st.selectbox(
            "Filtrer par niveau",
            ["Tous", "Débutant", "Intermédiaire", "Avancé"]
        )
    with col3:
        sort_option = st.selectbox(
            "Trier par",
            ["Code", "Nom", "Crédits", "Difficulté"]
        )
    
    # Appliquer filtres
    filtered_courses = courses
    if filter_domain != "Tous":
        filtered_courses = [c for c in filtered_courses if c['domaine'] == filter_domain]
    if filter_level != "Tous":
        filtered_courses = [c for c in filtered_courses if c['niveau'] == filter_level]
    
    # Trier
    sort_key = sort_option.lower()
    filtered_courses = sorted(filtered_courses, key=lambda x: x.get(sort_key, ''))
    
    # Afficher
    df = pd.DataFrame(filtered_courses)
    st.dataframe(
        df[['code', 'nom', 'domaine', 'niveau', 'credits', 'duree', 'difficulte']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "code": "Code",
            "nom": "Nom du cours",
            "domaine": "Domaine",
            "niveau": "Niveau",
            "credits": st.column_config.NumberColumn("Crédits", format="%d ⭐"),
            "duree": st.column_config.NumberColumn("Durée", format="%d h"),
            "difficulte": st.column_config.ProgressColumn("Difficulté", min_value=1, max_value=5)
        }
    )
    
    # Export
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Télécharger en CSV",
        csv,
        "courses_export.csv",
        "text/csv",
        use_container_width=False
    )

# ==================== PAGE 3: EXPLORER ====================

elif page == "🔍 Explorer les cours":
    st.markdown('<p class="main-header">🔍 Explorer les Cours</p>', unsafe_allow_html=True)
    
    courses = backend.get_all_courses()
    
    # Barre de recherche principale
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input(
            "🔎 Rechercher un cours",
            placeholder="Entrez un nom, code ou mot-clé...",
            label_visibility="collapsed"
        )
    
    with col2:
        sort_by = st.selectbox(
            "Trier par",
            ["code", "nom", "credits", "difficulte"],
            label_visibility="collapsed"
        )
    
    # Filtres avancés
    with st.expander("🎛️ Filtres Avancés", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            stats = backend.get_statistics()
            domains = st.multiselect(
                "🏷️ Domaines",
                list(stats['domains'].keys())
            )
        
        with col2:
            levels = st.multiselect(
                "🎯 Niveaux",
                ["Débutant", "Intermédiaire", "Avancé"]
            )
        
        with col3:
            credits = st.slider(
                "⭐ Crédits",
                min_value=0,
                max_value=10,
                value=(0, 10)
            )
        
        with col4:
            difficulte = st.slider(
                "📈 Difficulté",
                min_value=1,
                max_value=5,
                value=(1, 5)
            )
    
    # Appliquer les filtres
    filtered = courses
    
    if search:
        search_lower = search.lower()
        filtered = [c for c in filtered if 
                   search_lower in c['nom'].lower() or 
                   search_lower in c['code'].lower() or
                   search_lower in c.get('description', '').lower()]
    
    if domains:
        filtered = [c for c in filtered if c['domaine'] in domains]
    
    if levels:
        filtered = [c for c in filtered if c['niveau'] in levels]
    
    filtered = [c for c in filtered if 
               credits[0] <= c['credits'] <= credits[1] and
               difficulte[0] <= c['difficulte'] <= difficulte[1]]
    
    # Trier
    filtered = sorted(filtered, key=lambda x: x.get(sort_by, ''))
    
    # Affichage des résultats
    st.markdown(f"### 📊 {len(filtered)} cours trouvés sur {len(courses)}")
    
    if not filtered:
        st.warning("❌ Aucun cours ne correspond à vos critères. Essayez d'élargir votre recherche.")
    else:
        # Mode d'affichage
        view_mode = st.radio(
            "Mode d'affichage",
            ["🎴 Cartes", "📋 Tableau", "📝 Liste détaillée"],
            horizontal=True
        )
        
        if view_mode == "🎴 Cartes":
            # Affichage en cartes (2 colonnes)
            cols_per_row = 2
            rows = [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]
            
            for row in rows:
                cols = st.columns(cols_per_row)
                for idx, course in enumerate(row):
                    with cols[idx]:
                        with st.container():
                            # En-tête de carte
                            level_icons = {'Débutant': '🟢', 'Intermédiaire': '🟡', 'Avancé': '🔴'}
                            st.markdown(f"### {level_icons.get(course['niveau'])} {course['code']}")
                            st.markdown(f"**{course['nom']}**")
                            
                            # Badges
                            st.caption(f"📚 {course['domaine']}")
                            st.caption(f"⭐ {course['credits']} crédits • ⏱️ {course['duree']}h • 📈 Difficulté {course['difficulte']}/5")
                            
                            # Description expandable
                            with st.expander("📄 Plus d'informations"):
                                st.write(course.get('description', 'Pas de description disponible'))
                                
                                # Prérequis
                                prereqs = backend.get_prerequisites_for_course(course['code'])
                                if prereqs:
                                    st.markdown("**📋 Prérequis:**")
                                    for p in prereqs:
                                        st.write(f"→ **{p['code']}**: {p['nom']}")
                                else:
                                    st.success("✅ Aucun prérequis")
                            
                            st.markdown("---")
        
        elif view_mode == "📋 Tableau":
            # Affichage en tableau
            df = pd.DataFrame(filtered)
            st.dataframe(
                df[['code', 'nom', 'domaine', 'niveau', 'credits', 'duree', 'difficulte']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "code": "Code",
                    "nom": "Nom",
                    "domaine": "Domaine",
                    "niveau": "Niveau",
                    "credits": st.column_config.NumberColumn("Crédits", format="%d ⭐"),
                    "duree": st.column_config.NumberColumn("Durée (h)"),
                    "difficulte": st.column_config.ProgressColumn("Difficulté", min_value=1, max_value=5)
                }
            )
        
        else:  # Liste détaillée
            for course in filtered:
                with st.expander(f"**{course['code']}** - {course['nom']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:**")
                        st.write(course.get('description', 'Pas de description'))
                        
                        prereqs = backend.get_prerequisites_for_course(course['code'])
                        if prereqs:
                            st.markdown("**Prérequis:**")
                            for p in prereqs:
                                st.write(f"→ {p['code']}: {p['nom']}")
                    
                    with col2:
                        st.markdown("**Détails:**")
                        st.write(f"🏷️ Domaine: {course['domaine']}")
                        st.write(f"🎯 Niveau: {course['niveau']}")
                        st.write(f"⭐ Crédits: {course['credits']}")
                        st.write(f"⏱️ Durée: {course['duree']}h")
                        st.write(f"📈 Difficulté: {course['difficulte']}/5")

# ==================== PAGE 4: GRAPHE RDF ====================

elif page == "🗺️ Graphe RDF":
    st.markdown('<p class="main-header">🗺️ Graphe des Prérequis</p>', unsafe_allow_html=True)
    
    st.info("📖 **Mode d'emploi:** Cliquez et faites glisser les nœuds pour explorer. Survolez pour voir les détails. Zoomez avec la molette.")
    
    # Légende
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🟢 **Débutant**")
    with col2:
        st.markdown("🟡 **Intermédiaire**")
    with col3:
        st.markdown("🔴 **Avancé**")
    with col4:
        st.markdown("➡️ **Prérequis**")
    
    # Options de filtrage
    with st.expander("⚙️ Options de visualisation", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            stats = backend.get_statistics()
            filter_domain = st.selectbox(
                "Filtrer par domaine",
                ["Tous"] + list(stats['domains'].keys())
            )
        
        with col2:
            show_isolated = st.checkbox(
                "Afficher les cours sans prérequis",
                value=True
            )
    
    # Récupérer données
    courses = backend.get_all_courses()
    prerequisites = backend.get_all_prerequisites()
    
    # Appliquer filtres
    if filter_domain != "Tous":
        courses = [c for c in courses if c['domaine'] == filter_domain]
        course_codes = {c['code'] for c in courses}
        prerequisites = [(t, s) for t, s in prerequisites 
                        if t in course_codes and s in course_codes]
    
    if not show_isolated:
        # Exclure les cours sans prérequis
        courses_with_prereqs = set()
        for target, source in prerequisites:
            courses_with_prereqs.add(target)
            courses_with_prereqs.add(source)
        courses = [c for c in courses if c['code'] in courses_with_prereqs]
    
    # Générer le graphe
    with st.spinner("🎨 Génération du graphe interactif..."):
        graph_html = create_prerequisites_graph(courses, prerequisites)
    
    # Afficher le graphe
    st.components.v1.html(graph_html, height=750)
    
    # Statistiques du graphe
    st.markdown("---")
    st.markdown("### 📊 Analyse du Graphe")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nœuds (Cours)", len(courses))
    
    with col2:
        st.metric("Arêtes (Relations)", len(prerequisites))
    
    with col3:
        # Cours sans prérequis
        courses_with_prereqs = {target for target, _ in prerequisites}
        isolated = len([c for c in courses if c['code'] not in courses_with_prereqs])
        st.metric("Sans prérequis", isolated)
    
    with col4:
        # Cours avec le plus de prérequis
        prereq_count = {}
        for target, _ in prerequisites:
            prereq_count[target] = prereq_count.get(target, 0) + 1
        max_prereqs = max(prereq_count.values()) if prereq_count else 0
        st.metric("Max prérequis", max_prereqs)
    
    # Liste des prérequis
    with st.expander("📋 Liste détaillée des prérequis"):
        if prerequisites:
            prereq_data = []
            for target, source in prerequisites:
                target_course = backend.get_course_by_code(target)
                source_course = backend.get_course_by_code(source)
                if target_course and source_course:
                    prereq_data.append({
                        'Cours': f"{target} - {target_course['nom']}",
                        'Prérequis': f"{source} - {source_course['nom']}"
                    })
            
            df_prereqs = pd.DataFrame(prereq_data)
            st.dataframe(df_prereqs, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun prérequis pour les cours affichés")

# ==================== PAGE 5: STATISTIQUES ====================

elif page == "📈 Statistiques":
    st.markdown('<p class="main-header">📈 Statistiques Avancées</p>', unsafe_allow_html=True)
    
    courses = backend.get_all_courses()
    prerequisites = backend.get_all_prerequisites()
    df = pd.DataFrame(courses)
    
    # Section 1: Analyse de Complexité
    st.markdown("## 🎯 Analyse de Complexité")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution par difficulté
        st.markdown("### Distribution par difficulté")
        diff_counts = df['difficulte'].value_counts().sort_index()
        
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
        fig = go.Figure(data=[
            go.Bar(
                x=[f"Niveau {i}" for i in diff_counts.index],
                y=diff_counts.values,
                marker_color=[colors[i-1] for i in diff_counts.index],
                text=diff_counts.values,
                textposition='auto'
            )
        ])
        fig.update_layout(
            template="plotly_dark",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top cours par crédits
        st.markdown("### 🏆 Top 5 - Crédits")
        top_credits = df.nlargest(5, 'credits')[['code', 'nom', 'credits']]
        for idx, row in top_credits.iterrows():
            st.markdown(f"**{row['code']}** - {row['nom']}")
            st.progress(row['credits'] / 10, text=f"{row['credits']} crédits")
        
        st.markdown("---")
        
        # Top cours difficiles
        st.markdown("### 🔥 Top 5 - Difficulté")
        top_diff = df.nlargest(5, 'difficulte')[['code', 'nom', 'difficulte']]
        for idx, row in top_diff.iterrows():
            st.markdown(f"**{row['code']}** - {row['nom']}")
            st.progress(row['difficulte'] / 5, text=f"{row['difficulte']}/5")
    
    st.markdown("---")
    
    # Section 2: Analyse des Prérequis
    st.markdown("## 🔗 Analyse des Prérequis")
    
    # Calculer statistiques prérequis
    prereq_count = {}
    for target, _ in prerequisites:
        prereq_count[target] = prereq_count.get(target, 0) + 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Cours avec le plus de prérequis")
        sorted_prereqs = sorted(prereq_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if sorted_prereqs:
            for code, count in sorted_prereqs:
                course = backend.get_course_by_code(code)
                if course:
                    st.write(f"**{code}** - {course['nom']}")
                    st.caption(f"→ {count} prérequis nécessaires")
        else:
            st.info("Aucun cours avec prérequis")
    
    with col2:
        st.markdown("### 🎯 Cours sans prérequis (Points d'entrée)")
        courses_with_prereqs = set(prereq_count.keys())
        all_courses = {c['code'] for c in courses}
        no_prereqs = list(all_courses - courses_with_prereqs)[:5]
        
        if no_prereqs:
            for code in no_prereqs:
                course = backend.get_course_by_code(code)
                if course:
                    st.write(f"**{code}** - {course['nom']}")
                    st.caption(f"✅ Accessible directement")
        else:
            st.info("Tous les cours ont des prérequis")
    
    st.markdown("---")
    
    # Section 3: Répartition Globale
    st.markdown("## 📊 Vue d'Ensemble")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Par Domaine")
        for domaine, count in backend.get_statistics()['domains'].items():
            percentage = (count / len(courses)) * 100
            st.write(f"**{domaine}**")
            st.progress(percentage / 100, text=f"{count} cours ({percentage:.1f}%)")
    
    with col2:
        st.markdown("### Par Niveau")
        for niveau, count in backend.get_statistics()['levels'].items():
            percentage = (count / len(courses)) * 100
            st.write(f"**{niveau}**")
            st.progress(percentage / 100, text=f"{count} cours ({percentage:.1f}%)")
    
    with col3:
        st.markdown("### Statistiques Globales")
        st.metric("Crédits moyen", f"{df['credits'].mean():.1f}")
        st.metric("Durée moyenne", f"{df['duree'].mean():.0f}h")
        st.metric("Difficulté moyenne", f"{df['difficulte'].mean():.1f}/5")
    
    st.markdown("---")
    
    # Section 4: Export de données
    st.markdown("## 📥 Export des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export CSV complet
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📊 Télécharger tous les cours (CSV)",
            csv_data,
            "all_courses.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export prérequis
        prereq_df = pd.DataFrame(prerequisites, columns=['Cours', 'Prérequis'])
        prereq_csv = prereq_df.to_csv(index=False)
        st.download_button(
            "🔗 Télécharger les prérequis (CSV)",
            prereq_csv,
            "prerequisites.csv",
            "text/csv",
            use_container_width=True
        )

# ==================== FOOTER ====================
st.sidebar.markdown("---")
st.sidebar.caption("© 2024 CourseGuide AI")
st.sidebar.caption("Développé par Membre 4")
st.sidebar.caption("Interface & Visualisation")