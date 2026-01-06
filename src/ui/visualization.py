"""
Module de visualisation pour l'interface Streamlit
Membre 4 : Interface & Visualisation
"""

import os
import tempfile
import random
import string
from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from typing import List, Dict

# ==================== GRAPHES DE PRÉREQUIS ====================

def generate_unique_temp_filename() -> str:
    """Génère un nom de fichier temporaire unique"""
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return os.path.join(tempfile.gettempdir(), f"tmp_{random_str}.html")

def create_prerequisites_graph(courses: List[Dict], prerequisites: List[tuple]) -> str:
    """
    Crée un graphe interactif des prérequis avec PyVis
    
    Args:
        courses: Liste de dicts avec 'code', 'nom', 'niveau', 'description'
        prerequisites: Liste de tuples (cours_cible, prerequis)
    
    Returns:
        str: HTML du graphe
    """
    net = Network(
        height="650px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=True,
        notebook=False
    )
    
    # Configuration physique pour un meilleur layout
    net.barnes_hut(
        gravity=-15000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001,
        damping=0.09
    )
    
    # Couleurs par niveau
    color_map = {
        'Débutant': '#4CAF50',      # Vert
        'Intermédiaire': '#FFC107',  # Jaune/Orange
        'Avancé': '#F44336'          # Rouge
    }
    
    # Ajouter les nœuds (cours)
    for course in courses:
        color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
        # Créer un tooltip HTML riche
        title_html = f"""
        <div style='font-family: Arial; max-width: 300px; padding: 10px;'>
            <h3 style='margin: 0 0 10px 0; color: {color};'>{course['nom']}</h3>
            <hr style='margin: 10px 0;'>
            <p><strong>📚 Code:</strong> {course['code']}</p>
            <p><strong>🎯 Niveau:</strong> {course.get('niveau', 'N/A')}</p>
            <p><strong>⭐ Crédits:</strong> {course.get('credits', 'N/A')}</p>
            <p><strong>⏱️ Durée:</strong> {course.get('duree', 'N/A')}h</p>
            <p><strong>📈 Difficulté:</strong> {course.get('difficulte', 'N/A')}/5</p>
            <hr style='margin: 10px 0;'>
            <p style='font-size: 0.9em; color: #ccc;'>{course.get('description', '')[:150]}...</p>
        </div>
        """
        
        net.add_node(
            course['code'],
            label=course['code'],
            title=title_html,
            color=color,
            size=30,
            font={'size': 16, 'face': 'Arial', 'bold': True},
            shape='dot',
            borderWidth=2,
            borderWidthSelected=4
        )
    
    # Ajouter les arêtes (prérequis)
    for target, source in prerequisites:
        net.add_edge(
            source,
            target,
            arrows='to',
            width=2,
            color={'color': '#888888', 'highlight': '#4CAF50'},
            smooth={'type': 'curvedCW', 'roundness': 0.2}
        )
    
    # Options avancées du graphe
    net.set_options(""" 
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -15000,
                "centralGravity": 0.3,
                "springLength": 250,
                "springConstant": 0.001,
                "damping": 0.09,
                "avoidOverlap": 0.5
            },
            "stabilization": {
                "enabled": true,
                "iterations": 2000,
                "fit": true
            }
        },
        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": {
                "enabled": true
            },
            "tooltipDelay": 100,
            "zoomView": true,
            "dragView": true
        },
        "edges": {
            "smooth": {
                "type": "curvedCW",
                "roundness": 0.2
            }
        }
    }
    """)
    
    # Créer un fichier temporaire avec un nom unique
    temp_file_name = generate_unique_temp_filename()
    
    # Sauvegarder temporairement et lire
    net.save_graph(temp_file_name)
    
    # Lire le contenu du fichier HTML généré
    with open(temp_file_name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Nettoyer en supprimant le fichier temporaire
    os.unlink(temp_file_name)
    
    return html_content


# ==================== GRAPHIQUES STATISTIQUES ====================

def create_domain_chart(courses: List[Dict]) -> go.Figure:
    """Graphique en barres de la répartition par domaine"""
    df = pd.DataFrame(courses)
    domain_counts = df['domaine'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=domain_counts.index,
            y=domain_counts.values,
            marker_color='#4CAF50',
            text=domain_counts.values,
            textposition='auto',
            textfont=dict(size=14, color='white'),
            hovertemplate='<b>%{x}</b><br>Cours: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Répartition des cours par domaine",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Domaine",
        yaxis_title="Nombre de cours",
        template="plotly_dark",
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_level_pie_chart(courses: List[Dict]) -> go.Figure:
    """Camembert de la répartition par niveau"""
    df = pd.DataFrame(courses)
    level_counts = df['niveau'].value_counts()
    
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=level_counts.index,
            values=level_counts.values,
            marker=dict(colors=colors, line=dict(color='#000000', width=2)),
            hole=0.3,
            textinfo='label+percent',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>Cours: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Répartition par niveau de difficulté",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        template="plotly_dark",
        height=400
    )
    
    return fig


def create_credits_distribution(courses: List[Dict]) -> go.Figure:
    """Histogramme de distribution des crédits"""
    df = pd.DataFrame(courses)
    
    fig = go.Figure(data=[
        go.Histogram(
            x=df['credits'],
            marker_color='#2196F3',
            nbinsx=10,
            hovertemplate='Crédits: %{x}<br>Nombre de cours: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Distribution des crédits ECTS",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Crédits ECTS",
        yaxis_title="Nombre de cours",
        template="plotly_dark",
        height=400
    )
    
    return fig


def create_difficulty_heatmap(courses: List[Dict]) -> go.Figure:
    """Heatmap difficulté par domaine"""
    df = pd.DataFrame(courses)
    
    # Créer une matrice domaine x difficulté
    heatmap_data = df.groupby(['domaine', 'difficulte']).size().unstack(fill_value=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        text=heatmap_data.values,
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='Domaine: %{y}<br>Difficulté: %{x}<br>Cours: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Matrice Domaine × Difficulté",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Niveau de difficulté",
        yaxis_title="Domaine",
        template="plotly_dark",
        height=500
    )
    
    return fig


# ==================== PARCOURS D'APPRENTISSAGE ====================

def create_learning_path_viz(path_courses: List[Dict]) -> str:
    """
    Visualisation d'un parcours d'apprentissage linéaire
    
    Args:
        path_courses: Liste ordonnée de cours
        
    Returns:
        HTML du graphe
    """
    if not path_courses or len(path_courses) == 0:
        return "<p>Aucun parcours à afficher</p>"
    
    net = Network(
        height="400px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=True,
        notebook=False
    )
    
    color_map = {
        'Débutant': '#4CAF50',
        'Intermédiaire': '#FFC107',
        'Avancé': '#F44336'
    }
    
    # Ajouter les nœuds en ligne
    for i, course in enumerate(path_courses):
        color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
        title_html = f"""
        <div style='padding: 10px;'>
            <h4>{course['nom']}</h4>
            <p>Étape {i+1}/{len(path_courses)}</p>
            <p>Niveau: {course.get('niveau', 'N/A')}</p>
            <p>Crédits: {course.get('credits', 'N/A')}</p>
        </div>
        """
        
        net.add_node(
            i,
            label=f"{i+1}. {course['code']}",
            title=title_html,
            color=color,
            size=35,
            x=i * 250,
            y=0,
            physics=False,
            font={'size': 14, 'bold': True}
        )
        
        # Connecter au nœud précédent
        if i > 0:
            net.add_edge(
                i-1,
                i,
                arrows='to',
                width=3,
                color={'color': '#4CAF50', 'highlight': '#8BC34A'}
            )
    
    # Désactiver la physique pour garder le layout linéaire
    net.toggle_physics(False)
    
    # Sauvegarder
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode='w',
        encoding='utf-8'
    )
    net.save_graph(temp_file.name)
    
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    os.unlink(temp_file.name)
    
    return html_content


# ==================== GRAPHIQUES AVANCÉS ====================

def create_credits_by_domain(courses: List[Dict]) -> go.Figure:
    """Graphique des crédits totaux par domaine"""
    df = pd.DataFrame(courses)
    credits_by_domain = df.groupby('domaine')['credits'].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[
        go.Bar(
            x=credits_by_domain.index,
            y=credits_by_domain.values,
            marker_color='#9C27B0',
            text=credits_by_domain.values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Crédits totaux: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Crédits totaux par domaine",
        xaxis_title="Domaine",
        yaxis_title="Crédits ECTS",
        template="plotly_dark",
        height=400
    )
    
    return fig


def create_course_complexity_scatter(courses: List[Dict]) -> go.Figure:
    """Nuage de points crédits vs difficulté"""
    df = pd.DataFrame(courses)
    
    fig = px.scatter(
        df,
        x='credits',
        y='difficulte',
        color='domaine',
        size='duree',
        hover_data=['code', 'nom'],
        title="Complexité des cours (Crédits × Difficulté)",
        labels={
            'credits': 'Crédits ECTS',
            'difficulte': 'Niveau de difficulté',
            'domaine': 'Domaine'
        },
        template='plotly_dark',
        height=500
    )
    
    return fig


def create_network_metrics_viz(courses: List[Dict], prerequisites: List[tuple]) -> Dict[str, go.Figure]:
    """Crée plusieurs visualisations de métriques réseau"""
    
    # Construire le graphe NetworkX
    G = nx.DiGraph()
    
    for course in courses:
        G.add_node(course['code'], **course)
    
    for target, source in prerequisites:
        G.add_edge(source, target)
    
    # Métriques
    figures = {}
    
    # 1. Distribution des degrés
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name='Prérequis reçus',
        x=list(in_degrees.keys()),
        y=list(in_degrees.values()),
        marker_color='#FF5722'
    ))
    fig1.add_trace(go.Bar(
        name='Prérequis donnés',
        x=list(out_degrees.keys()),
        y=list(out_degrees.values()),
        marker_color='#4CAF50'
    ))
    
    fig1.update_layout(
        title="Analyse des connexions de prérequis",
        xaxis_title="Cours",
        yaxis_title="Nombre de connexions",
        template="plotly_dark",
        barmode='group',
        height=400
    )
    
    figures['degrees'] = fig1
    
    # 2. Betweenness centrality (cours "pont")
    if len(G.edges()) > 0:
        betweenness = nx.betweenness_centrality(G)
        top_10 = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig2 = go.Figure(data=[
            go.Bar(
                x=[x[0] for x in top_10],
                y=[x[1] for x in top_10],
                marker_color='#03A9F4',
                text=[f"{x[1]:.3f}" for x in top_10],
                textposition='auto'
            )
        ])
        
        fig2.update_layout(
            title="Cours 'Pont' (Betweenness Centrality)",
            xaxis_title="Cours",
            yaxis_title="Centralité",
            template="plotly_dark",
            height=400
        )
        
        figures['betweenness'] = fig2
    
    return figures


# ==================== TEST ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎨 TEST DU MODULE VISUALIZATION")
    print("="*70)
    
    # Données de test
    test_courses = [
        {'code': 'IA-101', 'nom': 'Intro IA', 'niveau': 'Débutant', 
         'credits': 4, 'duree': 45, 'difficulte': 2, 
         'domaine': 'Intelligence Artificielle', 'description': 'Test'},
        {'code': 'IA-201', 'nom': 'ML', 'niveau': 'Intermédiaire', 
         'credits': 6, 'duree': 60, 'difficulte': 3,
         'domaine': 'Intelligence Artificielle', 'description': 'Test'},
        {'code': 'WEB-101', 'nom': 'HTML/CSS', 'niveau': 'Débutant', 
         'credits': 3, 'duree': 30, 'difficulte': 1,
         'domaine': 'Développement Web', 'description': 'Test'}
    ]
    
    test_prereqs = [('IA-201', 'IA-101')]
    
    # Test 1: Graphe prérequis
    print("\n✅ Test 1: Création du graphe de prérequis")
    graph_html = create_prerequisites_graph(test_courses, test_prereqs)
    print(f"   HTML généré: {len(graph_html)} caractères")
    
    # Test 2: Graphiques statistiques
    print("\n✅ Test 2: Graphiques statistiques")
    fig_domain = create_domain_chart(test_courses)
    print(f"   Graphique domaine créé")
    
    fig_level = create_level_pie_chart(test_courses)
    print(f"   Graphique niveau créé")
    
    fig_credits = create_credits_distribution(test_courses)
    print(f"   Graphique crédits créé")
    
    # Test 3: Parcours
    print("\n✅ Test 3: Visualisation parcours")
    path_html = create_learning_path_viz(test_courses)
    print(f"   Parcours HTML: {len(path_html)} caractères")
    
    print("\n" + "="*70)
    print("✅ Tous les tests passent!")
    print("="*70)
# """
# Module de visualisation pour l'interface
# """

# from pyvis.network import Network
# import plotly.graph_objects as go
# import plotly.express as px
# import networkx as nx
# import tempfile
# import os


# def create_prerequisites_graph(courses, prerequisites):
#     """
#     Crée un graphe interactif des prérequis avec PyVis
    
#     Args:
#         courses: Liste de dicts avec 'code', 'nom', 'niveau', 'description'
#         prerequisites: Liste de tuples (cours_cible, prerequis)
    
#     Returns:
#         str: HTML du graphe
#     """
#     net = Network(
#         height="650px",
#         width="100%",
#         bgcolor="#1e1e1e",
#         font_color="white",
#         directed=True
#     )
    
#     # Configuration physique
#     net.barnes_hut(
#         gravity=-10000,
#         central_gravity=0.3,
#         spring_length=250,
#         spring_strength=0.001
#     )
    
#     # Couleurs par niveau
#     color_map = {
#         'Débutant': '#4CAF50',      # Vert
#         'Intermédiaire': '#FFC107',  # Jaune
#         'Avancé': '#F44336'          # Rouge
#     }
    
#     # Ajouter les nœuds (cours)
#     for course in courses:
#         color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
#         # Tooltip riche
#         title = f"""
#         <div style='font-family: Arial; max-width: 300px;'>
#             <h3>{course['nom']}</h3>
#             <p><strong>Code:</strong> {course['code']}</p>
#             <p><strong>Niveau:</strong> {course.get('niveau', 'N/A')}</p>
#             <p><strong>Crédits:</strong> {course.get('credits', 'N/A')}</p>
#             <p><strong>Durée:</strong> {course.get('duree', 'N/A')}h</p>
#             <hr>
#             <p style='font-size: 0.9em;'>{course.get('description', '')[:150]}...</p>
#         </div>
#         """
        
#         net.add_node(
#             course['code'],
#             label=course['code'],
#             title=title,
#             color=color,
#             size=30,
#             font={'size': 16, 'face': 'Arial'},
#             shape='dot'
#         )
    
#     # Ajouter les arêtes (prérequis)
#     for target, source in prerequisites:
#         net.add_edge(
#             source,
#             target,
#             arrows='to',
#             width=2,
#             color='#888888'
#         )
    
#     # Options avancées
#     net.set_options("""
#     {
#         "physics": {
#             "enabled": true,
#             "barnesHut": {
#                 "gravitationalConstant": -10000,
#                 "centralGravity": 0.3,
#                 "springLength": 250,
#                 "springConstant": 0.001,
#                 "damping": 0.09,
#                 "avoidOverlap": 0.5
#             },
#             "stabilization": {
#                 "enabled": true,
#                 "iterations": 1000
#             }
#         },
#         "interaction": {
#             "hover": true,
#             "navigationButtons": true,
#             "keyboard": true,
#             "tooltipDelay": 100
#         }
#     }
#     """)
    
#     # Sauvegarder temporairement
#     temp_file = tempfile.NamedTemporaryFile(
#         delete=False,
#         suffix=".html",
#         mode='w',
#         encoding='utf-8'
#     )
#     net.save_graph(temp_file.name)
    
#     with open(temp_file.name, 'r', encoding='utf-8') as f:
#         html_content = f.read()
    
#     # os.unlink(temp_file.name)
#     return html_content


# def create_domain_chart(courses):
#     """Graphique en barres de la répartition par domaine"""
#     import pandas as pd
    
#     df = pd.DataFrame(courses)
#     domain_counts = df['domaine'].value_counts()
    
#     fig = go.Figure(data=[
#         go.Bar(
#             x=domain_counts.index,
#             y=domain_counts.values,
#             marker_color='#4CAF50',
#             text=domain_counts.values,
#             textposition='auto',
#         )
#     ])
    
#     fig.update_layout(
#         title={
#             'text': "Répartition des cours par domaine",
#             'x': 0.5,
#             'xanchor': 'center'
#         },
#         xaxis_title="Domaine",
#         yaxis_title="Nombre de cours",
#         template="plotly_dark",
#         hovermode='x unified'
#     )
    
#     return fig


# def create_level_pie_chart(courses):
#     """Camembert de la répartition par niveau"""
#     import pandas as pd
    
#     df = pd.DataFrame(courses)
#     level_counts = df['niveau'].value_counts()
    
#     colors = ['#4CAF50', '#FFC107', '#F44336']
    
#     fig = go.Figure(data=[
#         go.Pie(
#             labels=level_counts.index,
#             values=level_counts.values,
#             marker=dict(colors=colors),
#             hole=0.3
#         )
#     ])
    
#     fig.update_layout(
#         title={
#             'text': "Répartition par niveau de difficulté",
#             'x': 0.5,
#             'xanchor': 'center'
#         },
#         template="plotly_dark"
#     )
    
#     return fig


# def create_credits_distribution(courses):
#     """Histogramme de distribution des crédits"""
#     import pandas as pd
    
#     df = pd.DataFrame(courses)
    
#     fig = go.Figure(data=[
#         go.Histogram(
#             x=df['credits'],
#             marker_color='#2196F3',
#             nbinsx=10
#         )
#     ])
    
#     fig.update_layout(
#         title="Distribution des crédits ECTS",
#         xaxis_title="Crédits",
#         yaxis_title="Nombre de cours",
#         template="plotly_dark"
#     )
    
#     return fig


# def create_learning_path_viz(path_courses):
#     """
#     Visualisation d'un parcours d'apprentissage linéaire
    
#     Args:
#         path_courses: Liste ordonnée de cours
#     """
#     if not path_courses or len(path_courses) == 0:
#         return None
    
#     net = Network(
#         height="400px",
#         width="100%",
#         bgcolor="#1e1e1e",
#         font_color="white",
#         directed=True
#     )
    
#     color_map = {
#         'Débutant': '#4CAF50',
#         'Intermédiaire': '#FFC107',
#         'Avancé': '#F44336'
#     }
    
#     # Ajouter les nœuds
#     for i, course in enumerate(path_courses):
#         color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
#         net.add_node(
#             i,
#             label=course['code'],
#             title=f"<b>{course['nom']}</b><br>{course.get('niveau', 'N/A')}",
#             color=color,
#             size=35,
#             x=i * 200,
#             y=0,
#             physics=False
#         )
        
#         # Connecter au nœud précédent
#         if i > 0:
#             net.add_edge(i-1, i, arrows='to', width=3, color='#888888')
    
#     temp_file = tempfile.NamedTemporaryFile(
#         delete=False,
#         suffix=".html",
#         mode='w',
#         encoding='utf-8'
#     )
#     net.save_graph(temp_file.name)
    
#     with open(temp_file.name, 'r', encoding='utf-8') as f:
#         html_content = f.read()
    
#     # os.unlink(temp_file.name)
#     return html_content