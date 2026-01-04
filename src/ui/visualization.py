"""
Module de visualisation pour l'interface
"""

from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import tempfile
import os


def create_prerequisites_graph(courses, prerequisites):
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
        directed=True
    )
    
    # Configuration physique
    net.barnes_hut(
        gravity=-10000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001
    )
    
    # Couleurs par niveau
    color_map = {
        'Débutant': '#4CAF50',      # Vert
        'Intermédiaire': '#FFC107',  # Jaune
        'Avancé': '#F44336'          # Rouge
    }
    
    # Ajouter les nœuds (cours)
    for course in courses:
        color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
        # Tooltip riche
        title = f"""
        <div style='font-family: Arial; max-width: 300px;'>
            <h3>{course['nom']}</h3>
            <p><strong>Code:</strong> {course['code']}</p>
            <p><strong>Niveau:</strong> {course.get('niveau', 'N/A')}</p>
            <p><strong>Crédits:</strong> {course.get('credits', 'N/A')}</p>
            <p><strong>Durée:</strong> {course.get('duree', 'N/A')}h</p>
            <hr>
            <p style='font-size: 0.9em;'>{course.get('description', '')[:150]}...</p>
        </div>
        """
        
        net.add_node(
            course['code'],
            label=course['code'],
            title=title,
            color=color,
            size=30,
            font={'size': 16, 'face': 'Arial'},
            shape='dot'
        )
    
    # Ajouter les arêtes (prérequis)
    for target, source in prerequisites:
        net.add_edge(
            source,
            target,
            arrows='to',
            width=2,
            color='#888888'
        )
    
    # Options avancées
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -10000,
                "centralGravity": 0.3,
                "springLength": 250,
                "springConstant": 0.001,
                "damping": 0.09,
                "avoidOverlap": 0.5
            },
            "stabilization": {
                "enabled": true,
                "iterations": 1000
            }
        },
        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "tooltipDelay": 100
        }
    }
    """)
    
    # Sauvegarder temporairement
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode='w',
        encoding='utf-8'
    )
    net.save_graph(temp_file.name)
    
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # os.unlink(temp_file.name)
    return html_content


def create_domain_chart(courses):
    """Graphique en barres de la répartition par domaine"""
    import pandas as pd
    
    df = pd.DataFrame(courses)
    domain_counts = df['domaine'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=domain_counts.index,
            y=domain_counts.values,
            marker_color='#4CAF50',
            text=domain_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Répartition des cours par domaine",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Domaine",
        yaxis_title="Nombre de cours",
        template="plotly_dark",
        hovermode='x unified'
    )
    
    return fig


def create_level_pie_chart(courses):
    """Camembert de la répartition par niveau"""
    import pandas as pd
    
    df = pd.DataFrame(courses)
    level_counts = df['niveau'].value_counts()
    
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=level_counts.index,
            values=level_counts.values,
            marker=dict(colors=colors),
            hole=0.3
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Répartition par niveau de difficulté",
            'x': 0.5,
            'xanchor': 'center'
        },
        template="plotly_dark"
    )
    
    return fig


def create_credits_distribution(courses):
    """Histogramme de distribution des crédits"""
    import pandas as pd
    
    df = pd.DataFrame(courses)
    
    fig = go.Figure(data=[
        go.Histogram(
            x=df['credits'],
            marker_color='#2196F3',
            nbinsx=10
        )
    ])
    
    fig.update_layout(
        title="Distribution des crédits ECTS",
        xaxis_title="Crédits",
        yaxis_title="Nombre de cours",
        template="plotly_dark"
    )
    
    return fig


def create_learning_path_viz(path_courses):
    """
    Visualisation d'un parcours d'apprentissage linéaire
    
    Args:
        path_courses: Liste ordonnée de cours
    """
    if not path_courses or len(path_courses) == 0:
        return None
    
    net = Network(
        height="400px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=True
    )
    
    color_map = {
        'Débutant': '#4CAF50',
        'Intermédiaire': '#FFC107',
        'Avancé': '#F44336'
    }
    
    # Ajouter les nœuds
    for i, course in enumerate(path_courses):
        color = color_map.get(course.get('niveau', 'Débutant'), '#999999')
        
        net.add_node(
            i,
            label=course['code'],
            title=f"<b>{course['nom']}</b><br>{course.get('niveau', 'N/A')}",
            color=color,
            size=35,
            x=i * 200,
            y=0,
            physics=False
        )
        
        # Connecter au nœud précédent
        if i > 0:
            net.add_edge(i-1, i, arrows='to', width=3, color='#888888')
    
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode='w',
        encoding='utf-8'
    )
    net.save_graph(temp_file.name)
    
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # os.unlink(temp_file.name)
    return html_content