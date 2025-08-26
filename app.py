import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import io
import xlsxwriter

# Configuration de la page
st.set_page_config(
    page_title="Plan Financier Familial X",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS CUSTOM
# ============================================================================

def load_css():
    st.markdown("""
    <style>
    /* Import des fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Variables CSS */
    :root {
        --color-primary: rgba(33, 128, 141, 1);
        --color-success: rgba(33, 128, 141, 1);
        --color-error: rgba(192, 21, 47, 1);
        --color-warning: rgba(168, 75, 47, 1);
        --color-info: rgba(98, 108, 113, 1);
        --color-background: rgba(252, 252, 249, 1);
        --color-surface: rgba(255, 255, 253, 1);
        --color-text: rgba(19, 52, 59, 1);
    }

    /* Reset Streamlit */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: none;
        background-color: var(--color-background);
    }

    /* Kanban Cards */
    .kanban-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .kanban-card.en-retard {
        border-left: 4px solid #ff4444;
        background: #fff5f5;
    }

    .kanban-card.a-risque {
        border-left: 4px solid #ff8800;
        background: #fff8f0;
    }

    .kanban-card.en-avance {
        border-left: 4px solid #00aa00;
        background: #f0fff0;
    }

    .kanban-card.en-cours {
        border-left: 4px solid #007bff;
        background: #f0f8ff;
    }

    .kanban-card.bloque {
        border-left: 4px solid #666666;
        background: #f5f5f5;
    }

    .admin-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DONNÉES ET LOGIQUE METIER
# ============================================================================

def initialize_session_state():
    """Initialise les données de session avec TOUS les champs requis"""
    if 'projets' not in st.session_state:
        st.session_state.projets = [
            {
                'id': 1,
                'nom': 'Titre foncier Mejeuh',
                'type': 'Actif générateur',
                'montant_total': 2815000,
                'budget_alloue_mensuel': 200000,
                'montant_utilise_reel': 50000,
                'cash_flow_mensuel': 0,
                'statut': 'En cours',
                'echeance': date(2025, 6, 30),
                'roi_attendu': 12,
                'priorite': 'Haute',
                'description': 'Acquisition terrain pour location future',
                'source_financement': 'Salaire William',
                'responsable': 'Alix',
                'date_creation': datetime(2025, 1, 15),
                'date_modification': datetime(2025, 2, 10),
                'suivi_mensuel': [
                    {'mois': '2025-01', 'prevu': 200000, 'reel': 50000}
                ]
            },
            {
                'id': 2,
                'nom': 'Voyage enfants Suisse',
                'type': 'Passif',
                'montant_total': 8189592,
                'budget_alloue_mensuel': 680000,
                'montant_utilise_reel': 0,
                'cash_flow_mensuel': -680000,
                'statut': 'Planifié',
                'echeance': date(2025, 8, 15),
                'roi_attendu': 0,
                'priorite': 'Moyenne',
                'description': 'Voyage familial cohésion',
                'source_financement': 'Salaire William',
                'responsable': 'William',
                'date_creation': datetime(2025, 1, 20),
                'date_modification': datetime(2025, 1, 20),
                'suivi_mensuel': []
            },
            {
                'id': 3,
                'nom': 'Scolarité enfants',
                'type': 'Investissement formation',
                'montant_total': 6500000,
                'budget_alloue_mensuel': 542000,
                'montant_utilise_reel': 1084000,
                'cash_flow_mensuel': -542000,
                'statut': 'En cours',
                'echeance': date(2025, 12, 31),
                'roi_attendu': 25,
                'priorite': 'Critique',
                'description': 'Éducation Uriel, Naelle, Nell-Henri',
                'source_financement': 'Revenus IIBA',
                'responsable': 'Alix',
                'date_creation': datetime(2024, 12, 1),
                'date_modification': datetime(2025, 2, 15),
                'suivi_mensuel': [
                    {'mois': '2025-01', 'prevu': 542000, 'reel': 542000},
                    {'mois': '2025-02', 'prevu': 542000, 'reel': 542000}
                ]
            },
            {
                'id': 4,
                'nom': 'Projet IIBA',
                'type': 'Actif générateur',
                'montant_total': 2786480,
                'budget_alloue_mensuel': 100000,
                'montant_utilise_reel': 150000,
                'cash_flow_mensuel': 232000,
                'statut': 'Développement',
                'echeance': date(2025, 3, 30),
                'roi_attendu': 18,
                'priorite': 'Critique',
                'description': 'Business génération revenus passifs',
                'source_financement': 'Épargne',
                'responsable': 'William',
                'date_creation': datetime(2024, 11, 10),
                'date_modification': datetime(2025, 2, 8),
                'suivi_mensuel': [
                    {'mois': '2025-01', 'prevu': 100000, 'reel': 75000},
                    {'mois': '2025-02', 'prevu': 100000, 'reel': 75000}
                ]
            }
        ]

    if 'revenus_variables' not in st.session_state:
        st.session_state.revenus_variables = [
            {
                'id': 1,
                'nom': 'Salaire William',
                'montant_mensuel': 800000,
                'type': 'Salaire',
                'regulier': True,
                'responsable': 'William',
                'date_creation': datetime(2024, 12, 1),
                'date_modification': datetime(2025, 1, 1)
            },
            {
                'id': 2,
                'nom': 'Revenus IIBA',
                'montant_mensuel': 232000,
                'type': 'Business',
                'regulier': False,
                'responsable': 'William',
                'date_creation': datetime(2025, 1, 15),
                'date_modification': datetime(2025, 2, 1)
            },
            {
                'id': 3,
                'nom': 'Épargne',
                'montant_mensuel': 50000,
                'type': 'Épargne',
                'regulier': True,
                'responsable': 'Alix',
                'date_creation': datetime(2024, 12, 1),
                'date_modification': datetime(2024, 12, 1)
            }
        ]

    # Configuration Admin
    if 'admin_config' not in st.session_state:
        st.session_state.admin_config = {
            'kpis_config': {
                'objectif_cash_flow': 500000,
                'objectif_ratio_actifs': 40,
                'objectif_revenus_passifs': 30,
                'objectif_fonds_urgence': 6
            },
            'listes_config': {
                'types_projet': ['Actif générateur', 'Passif', 'Investissement formation'],
                'statuts_projet': ['Planifié', 'En cours', 'Développement', 'Réalisé', 'Suspendu'],
                'priorites': ['Critique', 'Haute', 'Moyenne', 'Faible'],
                'types_revenu': ['Salaire', 'Business', 'Loyer', 'Investissement', 'Autre'],
                'responsables': ['Alix', 'William', 'Famille']
            },
            'mentors_conseils': {
                'Kiyosaki': {
                    'Actif générateur': 'Excellent ! Cet actif génère des revenus passifs et vous rapproche du quadrant I (Investisseur).',
                    'Passif': 'Ce passif retire de l argent de votre poche. Est-il vraiment nécessaire ?',
                    'Investissement formation': 'L éducation est un actif qui génère des revenus futurs plus élevés.'
                },
                'Buffett': {
                    'Actif générateur': 'Assurez-vous de comprendre parfaitement ce business et son potentiel long terme.',
                    'Passif': 'Quel est le coût d opportunité ? Cet argent pourrait-il être mieux investi ?',
                    'Investissement formation': 'Le meilleur investissement est en vous-même et votre famille.'
                },
                'Ramsey': {
                    'Actif générateur': 'Si ce projet ne vous endette pas excessivement, c est excellent pour votre indépendance.',
                    'Passif': 'Vérifiez que cet investissement respecte votre budget 50/30/20.',
                    'Investissement formation': 'L éducation est toujours rentable à long terme.'
                }
            }
        }

    # Filtre global mois/année avec option "Tout"
    if 'filter_month' not in st.session_state:
        st.session_state.filter_month = "Tout"

    if 'filter_year' not in st.session_state:
        st.session_state.filter_year = "Tout"

def safe_get(dict_obj, key, default='N/A'):
    """Récupère une valeur de dictionnaire de manière sécurisée"""
    return dict_obj.get(key, default)

def filter_data_by_period(data_list, date_field):
    """Filtre les données selon la période sélectionnée"""
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        return data_list

    filtered_data = []
    for item in data_list:
        item_date = safe_get(item, date_field)
        if isinstance(item_date, str):
            try:
                item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
            except:
                item_date = datetime.now().date()
        elif isinstance(item_date, datetime):
            item_date = item_date.date()
        elif not isinstance(item_date, date):
            item_date = datetime.now().date()

        # Filtrage par année
        if st.session_state.filter_year != "Tout":
            if item_date.year != st.session_state.filter_year:
                continue

        # Filtrage par mois
        if st.session_state.filter_month != "Tout":
            if item_date.month != st.session_state.filter_month:
                continue

        filtered_data.append(item)

    return filtered_data

def calculer_kpis():
    """Calcule les KPIs en temps réel avec filtrage par période"""
    # Filtrer projets et revenus selon la période
    projets = filter_data_by_period(st.session_state.projets, 'date_creation')
    revenus = filter_data_by_period(st.session_state.revenus_variables, 'date_creation')

    # Revenus totaux
    revenus_mensuels = sum(r['montant_mensuel'] for r in revenus)

    # Cash flow mensuel total
    cash_flow_mensuel = sum(p['cash_flow_mensuel'] for p in projets)

    # Totaux par type
    total_actifs = sum(p['montant_total'] for p in projets if p['type'] == 'Actif générateur')
    total_passifs = sum(p['montant_total'] for p in projets if p['type'] == 'Passif')
    total_formation = sum(p['montant_total'] for p in projets if p['type'] == 'Investissement formation')
    total_global = total_actifs + total_passifs + total_formation

    # Ratios
    ratio_actifs_passifs = (total_actifs / total_global * 100) if total_global > 0 else 0

    # Revenus passifs
    revenus_passifs = sum(p['cash_flow_mensuel'] for p in projets if p['type'] == 'Actif générateur' and p['cash_flow_mensuel'] > 0)
    revenus_passifs_pct = (revenus_passifs / revenus_mensuels * 100) if revenus_mensuels > 0 else 0

    # Nombre d'actifs générateurs
    nombre_actifs = len([p for p in projets if p['type'] == 'Actif générateur'])

    # Phase financière
    if cash_flow_mensuel < 0 or revenus_passifs_pct < 10:
        phase_actuelle = 'Stabilisation'
    elif cash_flow_mensuel >= 0 and 10 <= revenus_passifs_pct < 30:
        phase_actuelle = 'Transition'  
    else:
        phase_actuelle = 'Expansion'

    return {
        'revenus_mensuels': revenus_mensuels,
        'cash_flow_mensuel': cash_flow_mensuel,
        'ratio_actifs_passifs': ratio_actifs_passifs,
        'revenus_passifs_pct': revenus_passifs_pct,
        'nombre_actifs': nombre_actifs,
        'phase_actuelle': phase_actuelle,
        'fonds_urgence_mois': 0,
        'baby_step_actuel': 1,
        'depenses_mensuelles': abs(sum(p['cash_flow_mensuel'] for p in projets if p['cash_flow_mensuel'] < 0)),
        'total_actifs': total_actifs,
        'total_passifs': total_passifs,
        'total_formation': total_formation
    }

def format_currency(amount):
    """Formate un montant en FCFA"""
    return f"{amount:,.0f} FCFA".replace(",", " ")

def categorize_project(projet):
    """Catégorise un projet selon son état"""
    aujourd_hui = date.today()
    echeance = projet['echeance']

    # Calcul progression
    progression = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0

    # Jours jusqu'à échéance
    jours_restants = (echeance - aujourd_hui).days

    # Logique de catégorisation
    if echeance < aujourd_hui:
        return 'en-retard', 'En Retard', '#ff4444'
    elif jours_restants <= 30 and progression < 70:
        return 'a-risque', 'À Risque', '#ff8800'
    elif progression > 90:
        return 'en-avance', 'En Avance', '#00aa00'
    elif projet['montant_utilise_reel'] >= projet['montant_total']:
        return 'bloque', 'Budget Épuisé', '#666666'
    else:
        return 'en-cours', 'En Cours', '#007bff'

def get_sources_financement():
    """Retourne la liste des sources de financement disponibles"""
    revenus = st.session_state.revenus_variables
    return [r['nom'] for r in revenus] + ['Épargne', 'Crédit']

def export_to_excel():
    """Exporte toutes les données vers Excel"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Onglet Projets
        df_projets = pd.DataFrame(st.session_state.projets)
        if not df_projets.empty:
            df_projets['date_creation'] = pd.to_datetime(df_projets['date_creation']).dt.strftime('%Y-%m-%d %H:%M')
            df_projets['date_modification'] = pd.to_datetime(df_projets['date_modification']).dt.strftime('%Y-%m-%d %H:%M')
            df_projets['echeance'] = pd.to_datetime(df_projets['echeance']).dt.strftime('%Y-%m-%d')
        df_projets.to_excel(writer, sheet_name='Projets', index=False)

        # Onglet Revenus
        df_revenus = pd.DataFrame(st.session_state.revenus_variables)
        if not df_revenus.empty:
            df_revenus['date_creation'] = pd.to_datetime(df_revenus['date_creation']).dt.strftime('%Y-%m-%d %H:%M')
            df_revenus['date_modification'] = pd.to_datetime(df_revenus['date_modification']).dt.strftime('%Y-%m-%d %H:%M')
        df_revenus.to_excel(writer, sheet_name='Revenus', index=False)

        # Onglet KPIs
        kpis = calculer_kpis()
        df_kpis = pd.DataFrame([kpis])
        df_kpis.to_excel(writer, sheet_name='KPIs', index=False)

        # Onglet Configuration
        df_config = pd.DataFrame([st.session_state.admin_config])
        df_config.to_excel(writer, sheet_name='Configuration', index=False)

        # Onglet Suivi détaillé
        suivi_data = []
        for projet in st.session_state.projets:
            if projet.get('suivi_mensuel'):
                for suivi in projet['suivi_mensuel']:
                    suivi_data.append({
                        'projet_id': projet['id'],
                        'projet_nom': projet['nom'],
                        'mois': suivi['mois'],
                        'prevu': suivi['prevu'],
                        'reel': suivi['reel'],
                        'ecart': suivi['reel'] - suivi['prevu']
                    })

        if suivi_data:
            df_suivi = pd.DataFrame(suivi_data)
            df_suivi.to_excel(writer, sheet_name='Suivi_Mensuel', index=False)

    return output.getvalue()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar():
    """Affiche la sidebar avec navigation radio et filtre global amélioré"""
    with st.sidebar:
        st.markdown("### 💰 Plan Financier Familial")
        st.markdown("*Alix & William - Vers l'Indépendance 2030*")

        # Filtre global mois/année avec option "Tout"
        st.markdown("---")
        st.markdown("### 📅 Filtre Global")

        col1, col2 = st.columns(2)

        with col1:
            mois_options = ["Tout"] + [datetime(2025, x, 1).strftime('%B') for x in range(1, 13)]
            mois_index = 0
            if st.session_state.filter_month != "Tout":
                try:
                    mois_index = st.session_state.filter_month
                except:
                    mois_index = 0

            selected_mois = st.selectbox("Mois", mois_options, index=mois_index)

            if selected_mois == "Tout":
                st.session_state.filter_month = "Tout"
            else:
                st.session_state.filter_month = mois_options.index(selected_mois)

        with col2:
            annee_options = ["Tout"] + [2024, 2025, 2026, 2027, 2028]
            annee_index = 0
            if st.session_state.filter_year != "Tout":
                try:
                    annee_index = annee_options.index(st.session_state.filter_year)
                except:
                    annee_index = 0

            selected_annee = st.selectbox("Année", annee_options, index=annee_index)
            st.session_state.filter_year = selected_annee

        # Affichage période
        if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
            st.markdown("**📊 Période active:** Toutes les données")
        elif st.session_state.filter_month == "Tout":
            st.markdown(f"**📊 Période active:** Année {st.session_state.filter_year}")
        elif st.session_state.filter_year == "Tout":
            mois_nom = datetime(2025, st.session_state.filter_month, 1).strftime('%B')
            st.markdown(f"**📊 Période active:** {mois_nom} (toutes années)")
        else:
            mois_nom = datetime(2025, st.session_state.filter_month, 1).strftime('%B')
            st.markdown(f"**📊 Période active:** {mois_nom} {st.session_state.filter_year}")

        # Navigation avec radio buttons
        st.markdown("---")
        pages = [
            "📊 Dashboard Principal",
            "📋 Vue Kanban Projets",
            "💼 Gestion Projets", 
            "💰 Revenus Variables",
            "🎯 Conseils 3 Mentors",
            "📈 Analytics & KPIs",
            "🚀 Progression Familiale", 
            "👨‍👩‍👧‍👦 Éducation Enfants",
            "🔮 Vision 2030",
            "⚙️ Administration"
        ]

        selected_page = st.radio(
            "Navigation",
            pages,
            key="nav_radio",
            label_visibility="collapsed"
        )

        # Phase actuelle
        kpis = calculer_kpis()
        phase = kpis['phase_actuelle']

        st.markdown("---")
        st.markdown(f"**🎯 Phase:** {phase}")
        st.markdown(f"**💰 Revenus:** {format_currency(kpis['revenus_mensuels'])}")
        st.markdown(f"**📊 Cash Flow:** {format_currency(kpis['cash_flow_mensuel'])}")

    return selected_page

# ============================================================================
# PAGES DE L'APPLICATION (avec filtrage amélioré)
# ============================================================================

def show_dashboard():
    """Page Dashboard Principal avec filtrage"""
    st.title("📊 Dashboard Principal")

    # Affichage période active
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # KPIs avec données filtrées
    kpis = calculer_kpis()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_color = "normal" if kpis['cash_flow_mensuel'] >= 0 else "inverse"
        st.metric(
            "💸 Cash Flow Mensuel", 
            format_currency(kpis['cash_flow_mensuel']), 
            delta=f"Objectif: {format_currency(st.session_state.admin_config['kpis_config']['objectif_cash_flow'])}",
            delta_color=delta_color
        )

    with col2:
        st.metric(
            "⚖️ Ratio Actifs/Passifs", 
            f"{kpis['ratio_actifs_passifs']:.1f}%", 
            delta=f"Objectif: >{st.session_state.admin_config['kpis_config']['objectif_ratio_actifs']}%"
        )

    with col3:
        st.metric(
            "💰 Revenus Passifs", 
            f"{kpis['revenus_passifs_pct']:.1f}%", 
            delta=f"Objectif: {st.session_state.admin_config['kpis_config']['objectif_revenus_passifs']}%"
        )

    with col4:
        st.metric(
            "🎯 Phase", 
            kpis['phase_actuelle'],
            delta=f"Baby Step {kpis['baby_step_actuel']}/7"
        )

    # Graphiques avec données filtrées
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Évolution Cash Flow")

        import numpy as np
        mois = pd.date_range(start='2024-01-01', end='2024-12-01', freq='MS')
        cash_flow_evolution = np.random.normal(kpis['cash_flow_mensuel'], 500000, len(mois))

        fig = px.line(
            x=mois, 
            y=cash_flow_evolution,
            title="Cash Flow Mensuel (FCFA)"
        )
        fig.add_hline(y=0, line_dash="dash", annotation_text="Équilibre")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 Répartition Investissements")

        if kpis['total_actifs'] + kpis['total_passifs'] + kpis['total_formation'] > 0:
            fig = px.pie(
                values=[kpis['total_actifs'], kpis['total_passifs'], kpis['total_formation']],
                names=['Actifs Générateurs', 'Passifs', 'Formation'],
                color_discrete_map={
                    'Actifs Générateurs': '#1FB8CD',
                    'Passifs': '#B4413C', 
                    'Formation': '#FFC185'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

def show_kanban_view():
    """Vue Kanban des projets avec catégorisation avancée et filtrage"""
    st.title("📋 Vue Kanban - Gestion Visuelle des Projets")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Filtrer projets selon période
    projets_filtered = filter_data_by_period(st.session_state.projets, 'date_creation')

    # Catégorisation des projets filtrés
    categories = {
        'en-retard': {'projets': [], 'titre': '🔴 En Retard', 'couleur': '#ff4444'},
        'a-risque': {'projets': [], 'titre': '🟡 À Risque', 'couleur': '#ff8800'},
        'en-cours': {'projets': [], 'titre': '🔵 En Cours', 'couleur': '#007bff'},
        'en-avance': {'projets': [], 'titre': '🟢 En Avance', 'couleur': '#00aa00'},
        'bloque': {'projets': [], 'titre': '⚫ Bloqué', 'couleur': '#666666'}
    }

    # Répartition des projets
    for projet in projets_filtered:
        categorie, _, _ = categorize_project(projet)
        if categorie in categories:
            categories[categorie]['projets'].append(projet)
        else:
            categories['en-cours']['projets'].append(projet)

    # Affichage en colonnes
    colonnes = st.columns(len(categories))

    for i, (cat_key, cat_data) in enumerate(categories.items()):
        with colonnes[i]:
            st.markdown(f"### {cat_data['titre']} ({len(cat_data['projets'])})")

            if cat_data['projets']:
                for projet in cat_data['projets']:
                    show_kanban_card(projet, cat_data['couleur'], cat_key)
            else:
                st.info("Aucun projet dans cette catégorie")

    # Statistiques avec données filtrées
    st.markdown("---")
    st.subheader("📊 Statistiques Projet")

    col1, col2, col3, col4 = st.columns(4)

    total_projets = len(projets_filtered)

    with col1:
        st.metric("Total Projets", total_projets)

    with col2:
        en_retard = len(categories['en-retard']['projets'])
        st.metric("En Retard", en_retard, delta=f"{(en_retard/total_projets*100):.0f}%" if total_projets > 0 else "0%")

    with col3:
        a_risque = len(categories['a-risque']['projets'])
        st.metric("À Risque", a_risque, delta=f"{(a_risque/total_projets*100):.0f}%" if total_projets > 0 else "0%")

    with col4:
        en_avance = len(categories['en-avance']['projets'])
        st.metric("En Avance", en_avance, delta=f"{(en_avance/total_projets*100):.0f}%" if total_projets > 0 else "0%")

def show_kanban_card(projet, couleur, categorie):
    """Affiche une carte Kanban pour un projet avec gestion sécurisée des champs"""
    progression = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0

    # Calcul jours restants
    jours_restants = (projet['echeance'] - date.today()).days

    # CSS class pour la catégorie
    with st.container():
        # En-tête carte
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{projet['nom']}**")

        with col2:
            # Type badge
            type_colors = {
                'Actif générateur': '🟢',
                'Passif': '🔴',
                'Investissement formation': '🔵'
            }
            st.markdown(f"{type_colors.get(projet['type'], '⚪')} {projet['type'][:8]}...")

        # Infos projet
        st.markdown(f"💰 **Budget:** {format_currency(projet['montant_total'])}")
        st.markdown(f"💸 **Utilisé:** {format_currency(projet['montant_utilise_reel'])}")
        st.markdown(f"📅 **Échéance:** {projet['echeance'].strftime('%d/%m/%Y')}")
        st.markdown(f"⏰ **Jours restants:** {jours_restants}")
        st.markdown(f"👤 **Responsable:** {safe_get(projet, 'responsable', 'Non défini')}")

        # Barre de progression
        st.progress(progression / 100)
        st.markdown(f"📊 **Progression:** {progression:.1f}%")

        # Source financement (gestion sécurisée)
        source_financement = safe_get(projet, 'source_financement', 'Non défini')
        st.markdown(f"🏦 **Financement:** {source_financement}")

        # Actions
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ Modifier", key=f"kanban_edit_{projet['id']}"):
                st.session_state.edit_project_id = projet['id']
                st.session_state.current_page = "💼 Gestion Projets"
                st.rerun()

        with col2:
            if st.button("📊 Détails", key=f"kanban_details_{projet['id']}"):
                st.session_state.show_details_id = projet['id']

        st.markdown("---")

        # Modal détails
        if st.session_state.get('show_details_id') == projet['id']:
            show_project_details_modal(projet)

def show_project_details_modal(projet):
    """Affiche les détails d'un projet dans un expander"""
    with st.expander(f"📊 Détails: {projet['nom']}", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 💰 Informations Financières")
            st.write(f"**Budget Total:** {format_currency(projet['montant_total'])}")
            st.write(f"**Budget Mensuel:** {format_currency(projet['budget_alloue_mensuel'])}")
            st.write(f"**Utilisé Réel:** {format_currency(projet['montant_utilise_reel'])}")
            st.write(f"**Cash Flow/Mois:** {format_currency(projet['cash_flow_mensuel'])}")
            st.write(f"**ROI Attendu:** {projet['roi_attendu']}%")

        with col2:
            st.markdown("### 📋 Informations Projet")
            st.write(f"**Statut:** {projet['statut']}")
            st.write(f"**Priorité:** {safe_get(projet, 'priorite', 'Non définie')}")
            st.write(f"**Échéance:** {projet['echeance'].strftime('%d/%m/%Y')}")
            st.write(f"**Responsable:** {safe_get(projet, 'responsable', 'Non défini')}")
            st.write(f"**Source Financement:** {safe_get(projet, 'source_financement', 'Non définie')}")

        # Dates de gestion
        st.markdown("### 📅 Gestion")
        col1, col2 = st.columns(2)
        with col1:
            date_creation = safe_get(projet, 'date_creation', datetime.now())
            if isinstance(date_creation, str):
                date_creation = datetime.strptime(date_creation, '%Y-%m-%d %H:%M:%S')
            st.write(f"**Créé le:** {date_creation.strftime('%d/%m/%Y %H:%M')}")

        with col2:
            date_modification = safe_get(projet, 'date_modification', datetime.now())
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%Y-%m-%d %H:%M:%S')
            st.write(f"**Modifié le:** {date_modification.strftime('%d/%m/%Y %H:%M')}")

        st.markdown("### 📝 Description")
        st.write(projet['description'])

        # Bouton fermer
        if st.button("❌ Fermer", key=f"close_details_{projet['id']}"):
            if 'show_details_id' in st.session_state:
                del st.session_state.show_details_id
            st.rerun()

def show_project_management():
    """Page Gestion Projets CRUD complète avec filtrage"""
    st.title("💼 Gestion des Projets")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Actions principales
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nouveau Projet", type="primary"):
            st.session_state.show_add_form = True

    # Gestion des modals
    if st.session_state.get('show_add_form', False):
        show_add_project_form()

    if st.session_state.get('edit_project_id'):
        show_edit_project_form()

    # Filtres
    st.subheader("🔍 Filtres")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filter_type = st.selectbox(
            "Type", 
            ["Tous"] + st.session_state.admin_config['listes_config']['types_projet']
        )

    with col2:
        filter_status = st.selectbox(
            "Statut",
            ["Tous"] + st.session_state.admin_config['listes_config']['statuts_projet']
        )

    with col3:
        filter_priority = st.selectbox(
            "Priorité",
            ["Toutes"] + st.session_state.admin_config['listes_config']['priorites']
        )

    with col4:
        sort_by = st.selectbox(
            "Trier par",
            ["Nom", "Montant", "Échéance", "ROI", "Type", "Date création"]
        )

    # Application des filtres avec filtrage par période
    projets_base = filter_data_by_period(st.session_state.projets, 'date_creation')
    projets_filtered = filter_projects(projets_base, filter_type, filter_status, filter_priority, sort_by)

    # Affichage des projets
    st.subheader(f"📋 Projets ({len(projets_filtered)})")

    if projets_filtered:
        for projet in projets_filtered:
            show_project_card_native(projet)
    else:
        st.info("Aucun projet ne correspond aux filtres sélectionnés.")

def show_project_card_native(projet):
    """Affiche une carte projet avec composants Streamlit natifs"""

    # Calculs
    delta_budget = projet['montant_total'] - projet['montant_utilise_reel']
    progress = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0

    # Container principal
    with st.container():
        # En-tête avec nom et type
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.subheader(f"🎯 {projet['nom']}")
            st.caption(f"👤 {safe_get(projet, 'responsable', 'Non défini')}")

        with col2:
            # Badge type
            type_colors = {
                'Actif générateur': '🟢',
                'Passif': '🔴',
                'Investissement formation': '🔵'
            }
            st.markdown(f"{type_colors.get(projet['type'], '⚪')} **{projet['type']}**")

        with col3:
            # Badge statut
            status_colors = {
                'Planifié': '🔵',
                'En cours': '🟡', 
                'Développement': '🟠',
                'Réalisé': '🟢',
                'Suspendu': '🔴'
            }
            st.markdown(f"{status_colors.get(projet['statut'], '⚪')} {projet['statut']}")

        # Métriques financières
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💰 Budget Total", format_currency(projet['montant_total']))

        with col2:
            st.metric("💸 Utilisé", format_currency(projet['montant_utilise_reel']))

        with col3:
            st.metric("📊 Delta", format_currency(delta_budget))

        with col4:
            cash_flow_color = "normal" if projet['cash_flow_mensuel'] >= 0 else "inverse"
            st.metric(
                "💵 Cash Flow/Mois", 
                format_currency(projet['cash_flow_mensuel']),
                delta_color=cash_flow_color
            )

        # Barre de progression
        st.write(f"**Progression: {progress:.1f}%**")
        st.progress(progress / 100)

        # Description
        st.write(f"**Description:** {projet['description']}")

        # Infos supplémentaires
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"📅 **Échéance:** {projet['echeance'].strftime('%d/%m/%Y')}")

        with col2:
            st.write(f"📊 **ROI:** {projet['roi_attendu']}%")

        with col3:
            # Gestion sécurisée du financement
            source_financement = safe_get(projet, 'source_financement', 'Non défini')
            st.write(f"🏦 **Financement:** {source_financement}")

        # Dates de gestion
        col1, col2 = st.columns(2)
        with col1:
            date_creation = safe_get(projet, 'date_creation', datetime.now())
            if isinstance(date_creation, str):
                date_creation = datetime.strptime(date_creation, '%Y-%m-%d %H:%M:%S')
            st.caption(f"📅 Créé: {date_creation.strftime('%d/%m/%Y %H:%M')}")

        with col2:
            date_modification = safe_get(projet, 'date_modification', datetime.now())
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%Y-%m-%d %H:%M:%S')
            st.caption(f"🔄 Modifié: {date_modification.strftime('%d/%m/%Y %H:%M')}")

        # Actions
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✏️ Modifier", key=f"edit_{projet['id']}"):
                st.session_state.edit_project_id = projet['id']
                st.rerun()

        with col2:
            if st.button("🗑️ Supprimer", key=f"delete_{projet['id']}"):
                if st.session_state.get(f"confirm_delete_{projet['id']}", False):
                    # Suppression confirmée
                    st.session_state.projets = [p for p in st.session_state.projets if p['id'] != projet['id']]
                    st.success(f"Projet '{projet['nom']}' supprimé.")
                    if f"confirm_delete_{projet['id']}" in st.session_state:
                        del st.session_state[f"confirm_delete_{projet['id']}"]
                    st.rerun()
                else:
                    # Demande de confirmation
                    st.session_state[f"confirm_delete_{projet['id']}"] = True
                    st.warning("Cliquez à nouveau pour confirmer la suppression.")

        with col3:
            if st.button("📊 Suivi", key=f"suivi_{projet['id']}"):
                st.session_state.show_suivi_id = projet['id']

        with col4:
            if st.button("🎯 Conseils", key=f"advice_{projet['id']}"):
                st.session_state.show_advice_id = projet['id']

    # Affichage conditionnel du suivi
    if st.session_state.get('show_suivi_id') == projet['id']:
        show_project_tracking(projet)

    # Affichage conditionnel des conseils
    if st.session_state.get('show_advice_id') == projet['id']:
        show_project_advice(projet)

    st.markdown("---")

def show_project_tracking(projet):
    """Affiche le suivi mensuel d'un projet"""
    with st.expander(f"📊 Suivi Mensuel: {projet['nom']}", expanded=True):

        # Filtre par mois/année sélectionnée
        filtered_suivi = []
        if st.session_state.filter_year != "Tout" and st.session_state.filter_month != "Tout":
            target_month = f"{st.session_state.filter_year}-{st.session_state.filter_month:02d}"

            if projet['suivi_mensuel']:
                filtered_suivi = [s for s in projet['suivi_mensuel'] if s['mois'].startswith(target_month[:7])]
        else:
            filtered_suivi = projet.get('suivi_mensuel', [])

        if filtered_suivi:
            df_suivi = pd.DataFrame(filtered_suivi)
            df_suivi['écart'] = df_suivi['reel'] - df_suivi['prevu']
            df_suivi['% écart'] = (df_suivi['écart'] / df_suivi['prevu'] * 100).round(1)

            st.dataframe(df_suivi, use_container_width=True)

            # Graphique évolution
            fig = px.bar(
                df_suivi,
                x='mois',
                y=['prevu', 'reel'],
                title=f"Prévisionnel vs Réel",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun suivi pour la période sélectionnée.")

        # Ajouter une entrée de suivi
        if st.session_state.filter_year != "Tout" and st.session_state.filter_month != "Tout":
            st.subheader(f"➕ Ajouter Suivi pour {datetime(st.session_state.filter_year, st.session_state.filter_month, 1).strftime('%B %Y')}")

            with st.form(f"suivi_form_{projet['id']}"):
                col1, col2 = st.columns(2)

                with col1:
                    montant_prevu = st.number_input("Montant Prévu (FCFA)", min_value=0, step=10000, value=projet['budget_alloue_mensuel'])

                with col2:
                    montant_reel = st.number_input("Montant Réel (FCFA)", min_value=0, step=10000)

                if st.form_submit_button("💾 Ajouter Suivi"):
                    # Trouver le projet et ajouter le suivi
                    for i, p in enumerate(st.session_state.projets):
                        if p['id'] == projet['id']:
                            if 'suivi_mensuel' not in st.session_state.projets[i]:
                                st.session_state.projets[i]['suivi_mensuel'] = []

                            mois_cible = f"{st.session_state.filter_year}-{st.session_state.filter_month:02d}"

                            # Vérifier si le suivi existe déjà pour ce mois
                            existing_suivi = [s for s in st.session_state.projets[i]['suivi_mensuel'] if s['mois'] == mois_cible]

                            if existing_suivi:
                                # Mettre à jour
                                for s in st.session_state.projets[i]['suivi_mensuel']:
                                    if s['mois'] == mois_cible:
                                        s['prevu'] = montant_prevu
                                        s['reel'] = montant_reel
                            else:
                                # Ajouter nouveau
                                st.session_state.projets[i]['suivi_mensuel'].append({
                                    'mois': mois_cible,
                                    'prevu': montant_prevu,
                                    'reel': montant_reel
                                })

                            # Mettre à jour le montant utilisé réel et date modification
                            total_reel = sum(s['reel'] for s in st.session_state.projets[i]['suivi_mensuel'])
                            st.session_state.projets[i]['montant_utilise_reel'] = total_reel
                            st.session_state.projets[i]['date_modification'] = datetime.now()

                            st.success(f"Suivi ajouté pour {datetime(st.session_state.filter_year, st.session_state.filter_month, 1).strftime('%B %Y')}!")
                            st.rerun()
        else:
            st.info("Sélectionnez un mois et une année spécifiques pour ajouter un suivi.")

        # Bouton fermer
        if st.button("❌ Fermer Suivi", key=f"close_suivi_{projet['id']}"):
            if 'show_suivi_id' in st.session_state:
                del st.session_state.show_suivi_id
            st.rerun()

def show_project_advice(projet):
    """Affiche les conseils des 3 mentors pour un projet avec configuration dynamique"""
    with st.expander(f"🎯 Conseils des 3 Mentors: {projet['nom']}", expanded=True):

        col1, col2, col3 = st.columns(3)

        mentors_config = st.session_state.admin_config['mentors_conseils']

        with col1:
            st.markdown("#### 🏢 Robert Kiyosaki")
            st.markdown("*Père Riche, Père Pauvre*")

            conseil = mentors_config['Kiyosaki'].get(projet['type'], 'Conseil non configuré')
            if projet['type'] == 'Actif générateur':
                st.success(f"✅ {conseil}")
            elif projet['type'] == 'Passif':
                st.warning(f"⚠️ {conseil}")
            else:
                st.info(f"📚 {conseil}")

        with col2:
            st.markdown("#### 💎 Warren Buffett")
            st.markdown("*L'Oracle d'Omaha*")

            conseil = mentors_config['Buffett'].get(projet['type'], 'Conseil non configuré')
            if projet['type'] == 'Actif générateur':
                st.success(f"🔍 {conseil}")
            elif projet['type'] == 'Passif':
                st.warning(f"🤔 {conseil}")
            else:
                st.info(f"🎯 {conseil}")

        with col3:
            st.markdown("#### 💪 Dave Ramsey")
            st.markdown("*Total Money Makeover*")

            conseil = mentors_config['Ramsey'].get(projet['type'], 'Conseil non configuré')
            if projet['type'] == 'Actif générateur':
                st.success(f"💰 {conseil}")
            elif projet['type'] == 'Passif':
                st.warning(f"🚨 {conseil}")
            else:
                st.info(f"✅ {conseil}")

        # Bouton fermer
        if st.button("❌ Fermer Conseils", key=f"close_advice_{projet['id']}"):
            if 'show_advice_id' in st.session_state:
                del st.session_state.show_advice_id
            st.rerun()

def show_add_project_form():
    """Formulaire d'ajout de projet avec dates et responsable"""
    with st.expander("➕ Nouveau Projet", expanded=True):
        with st.form("add_project_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom du projet*", placeholder="ex: Groupe électrogène meublés")
                type_projet = st.selectbox(
                    "Type selon Kiyosaki*",
                    st.session_state.admin_config['listes_config']['types_projet'],
                    help="Actif = génère revenus, Passif = coûte de l'argent, Formation = capital humain"
                )
                montant_total = st.number_input("Budget total nécessaire (FCFA)*",
                    min_value=0,
                    value=int(projet.get("montant_total", 0) or 0),
                    step=10000)
                roi_attendu = st.number_input("ROI attendu (%)", min_value=0.0, max_value=100.0, step=0.1)
                priorite = st.selectbox("Priorité", st.session_state.admin_config['listes_config']['priorites'])
                responsable = st.selectbox("Responsable*", st.session_state.admin_config['listes_config']['responsables'])

            with col2:
                statut = st.selectbox(
                    "Statut", 
                    st.session_state.admin_config['listes_config']['statuts_projet']
                )
                echeance = st.date_input("Échéance prévue", min_value=date.today())
                budget_mensuel = st.number_input("Budget alloué/mois (FCFA)",
                    min_value=0,
                    value=int(projet.get("budget_alloue_mensuel", 0) or 0),
                    step=10000)
                cash_flow_mensuel = st.number_input(
                    "Cash flow mensuel estimé (FCFA)", 
                    help="Positif pour revenus, négatif pour dépenses",
                    value=int(projet.get("cash_flow_mensuel", 0) or 0),
                    step=10000
                )
                source_financement = st.selectbox(
                    "Source de financement",
                    get_sources_financement()
                )

            description = st.text_area("Description détaillée", height=100)

            col1, col2 = st.columns(2)

            with col1:
                submitted = st.form_submit_button("✅ Créer Projet", type="primary")

            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_add_form = False
                    st.rerun()

            if submitted:
                if nom and type_projet and montant_total > 0 and responsable:
                    # Créer nouveau projet
                    new_id = max([p['id'] for p in st.session_state.projets]) + 1 if st.session_state.projets else 1

                    nouveau_projet = {
                        'id': new_id,
                        'nom': nom,
                        'type': type_projet,
                        'montant_total': montant_total,
                        'budget_alloue_mensuel': budget_mensuel,
                        'montant_utilise_reel': 0,
                        'cash_flow_mensuel': cash_flow_mensuel,
                        'statut': statut,
                        'echeance': echeance,
                        'roi_attendu': roi_attendu,
                        'priorite': priorite,
                        'description': description,
                        'source_financement': source_financement,
                        'responsable': responsable,
                        'date_creation': datetime.now(),
                        'date_modification': datetime.now(),
                        'suivi_mensuel': []
                    }

                    st.session_state.projets.append(nouveau_projet)
                    st.session_state.show_add_form = False
                    st.success(f"✅ Projet '{nom}' créé avec succès !")
                    st.rerun()
                else:
                    st.error("⚠️ Veuillez remplir tous les champs obligatoires.")

def show_edit_project_form():
    """Formulaire de modification de projet avec dates"""
    project_id = st.session_state.edit_project_id
    projet = next((p for p in st.session_state.projets if p['id'] == project_id), None)

    if not projet:
        st.error("Projet introuvable")
        st.session_state.edit_project_id = None
        return

    with st.expander(f"✏️ Modifier: {projet['nom']}", expanded=True):
        with st.form("edit_project_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom du projet*", value=projet['nom'])
                type_projet = st.selectbox(
                    "Type selon Kiyosaki*",
                    st.session_state.admin_config['listes_config']['types_projet'],
                    index=st.session_state.admin_config['listes_config']['types_projet'].index(projet['type'])
                )
                montant_total = st.number_input("Budget total nécessaire (FCFA)*", value=projet['montant_total'], step=10000)
                roi_attendu = st.number_input("ROI attendu (%)", value=float(safe_get(projet, 'roi_attendu', 0.0)), format="%.1f", step=0.1)
                priorite = st.selectbox(
                    "Priorité", 
                    st.session_state.admin_config['listes_config']['priorites'],
                    index=st.session_state.admin_config['listes_config']['priorites'].index(safe_get(projet, 'priorite', 'Moyenne'))
                )
                responsable = st.selectbox(
                    "Responsable*", 
                    st.session_state.admin_config['listes_config']['responsables'],
                    index=st.session_state.admin_config['listes_config']['responsables'].index(safe_get(projet, 'responsable', 'Alix'))
                )

            with col2:
                statut = st.selectbox(
                    "Statut",
                    st.session_state.admin_config['listes_config']['statuts_projet'],
                    index=st.session_state.admin_config['listes_config']['statuts_projet'].index(projet['statut'])
                )
                echeance = st.date_input("Échéance prévue", value=projet['echeance'])
                budget_mensuel = st.number_input("Budget alloué/mois (FCFA)", value=projet['budget_alloue_mensuel'], step=10000)
                cash_flow_mensuel = st.number_input("Cash flow mensuel estimé (FCFA)", value=projet['cash_flow_mensuel'], step=10000)

                sources_list = get_sources_financement()
                current_source = safe_get(projet, 'source_financement', sources_list[0])
                source_index = sources_list.index(current_source) if current_source in sources_list else 0

                source_financement = st.selectbox(
                    "Source de financement",
                    sources_list,
                    index=source_index
                )

            description = st.text_area("Description détaillée", value=projet['description'])

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("💾 Sauvegarder", type="primary"):
                    # Mettre à jour le projet
                    index = next(i for i, p in enumerate(st.session_state.projets) if p['id'] == project_id)

                    st.session_state.projets[index].update({
                        'nom': nom,
                        'type': type_projet,
                        'montant_total': montant_total,
                        'budget_alloue_mensuel': budget_mensuel,
                        'cash_flow_mensuel': cash_flow_mensuel,
                        'statut': statut,
                        'echeance': echeance,
                        'roi_attendu': roi_attendu,
                        'priorite': priorite,
                        'description': description,
                        'source_financement': source_financement,
                        'responsable': responsable,
                        'date_modification': datetime.now()
                    })

                    st.session_state.edit_project_id = None
                    st.success("Projet modifié!")
                    st.rerun()
                
                _ = st.form_submit_button(
                    "✅ Valider (secours)",
                    help="Bouton de secours pour garantir l'envoi du formulaire"
                )

            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.edit_project_id = None
                    st.rerun()

def filter_projects(projets, filter_type, filter_status, filter_priority, sort_by):
    """Filtre et trie les projets"""

    # Filtrage
    if filter_type != "Tous":
        projets = [p for p in projets if p['type'] == filter_type]

    if filter_status != "Tous":
        projets = [p for p in projets if p['statut'] == filter_status]

    if filter_priority != "Toutes":
        projets = [p for p in projets if safe_get(p, 'priorite', 'Moyenne') == filter_priority]

    # Tri
    if sort_by == "Nom":
        projets.sort(key=lambda x: x['nom'])
    elif sort_by == "Montant":
        projets.sort(key=lambda x: x['montant_total'], reverse=True)
    elif sort_by == "Échéance":
        projets.sort(key=lambda x: x['echeance'])
    elif sort_by == "ROI":
        projets.sort(key=lambda x: x['roi_attendu'], reverse=True)
    elif sort_by == "Type":
        projets.sort(key=lambda x: x['type'])
    elif sort_by == "Date création":
        projets.sort(key=lambda x: safe_get(x, 'date_creation', datetime.now()), reverse=True)

    return projets

def show_revenue_management():
    """Page Gestion des Revenus Variables avec filtrage et dates"""
    st.title("💰 Gestion des Revenus Variables")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    st.markdown("""
    Cette section permet de gérer les revenus qui fluctuent chaque mois 
    (salaires supplémentaires, revenus business IIBA, loyers, etc.)
    """)

    # Actions principales
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Ajouter Revenu", type="primary"):
            st.session_state.show_add_revenue_form = True

    # Formulaire d'ajout
    if st.session_state.get('show_add_revenue_form', False):
        show_add_revenue_form()

    # Formulaire de modification
    if st.session_state.get('edit_revenue_id'):
        show_edit_revenue_form()

    # Affichage revenus actuels avec filtrage
    st.subheader("💼 Revenus Mensuels Actuels")

    revenus_filtered = filter_data_by_period(st.session_state.revenus_variables, 'date_creation')

    if revenus_filtered:
        for revenu in revenus_filtered:
            show_revenue_card(revenu)

        # Total
        total_revenus = sum(r['montant_mensuel'] for r in revenus_filtered)
        st.markdown(f"### **Total Revenus: {format_currency(total_revenus)}**")

    else:
        st.info("Aucun revenu variable pour la période sélectionnée.")

    # Graphique évolution filtré par période
    st.subheader("📈 Évolution des Revenus")

    if revenus_filtered:
        # Simulation données historiques pour la période sélectionnée
        import numpy as np

        # Générer données
        if st.session_state.filter_year != "Tout":
            end_date = date(st.session_state.filter_year, 12, 1)
        else:
            end_date = date.today().replace(day=1)

        mois = pd.date_range(end=end_date, periods=12, freq='MS')

        revenus_data = []
        for revenu in revenus_filtered:
            if revenu['regulier']:
                revenus_data.append([revenu['montant_mensuel']] * len(mois))
            else:
                # Simulation variation pour revenus variables
                base = revenu['montant_mensuel'] 
                variation = np.random.normal(base, base*0.2, len(mois))
                variation = np.maximum(variation, 0)  # Pas de revenus négatifs
                revenus_data.append(variation)

        if revenus_data:
            df_revenus = pd.DataFrame({
                revenu['nom']: evolution 
                for revenu, evolution in zip(revenus_filtered, revenus_data)
            }, index=mois)

            fig = px.line(df_revenus, title="Évolution des Revenus par Source")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def show_revenue_card(revenu):
    """Affiche une carte de revenu avec possibilité de modification et informations de gestion"""
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        with col1:
            st.write(f"**{revenu['nom']}**")
            st.caption(f"👤 {safe_get(revenu, 'responsable', 'Non défini')}")

        with col2:
            st.write(revenu['type'])

        with col3:
            st.write(format_currency(revenu['montant_mensuel']))

        with col4:
            st.write("🔄 Régulier" if revenu['regulier'] else "📊 Variable")

        with col5:
            col_edit, col_delete = st.columns(2)

            # Utilisation sécurisée de l'ID
            revenu_id = safe_get(revenu, 'id', f"rev_{revenu['nom'].replace(' ', '_')}")

            with col_edit:
                if st.button("✏️", key=f"edit_rev_{revenu_id}"):
                    st.session_state.edit_revenue_id = revenu_id
                    st.rerun()

            with col_delete:
                if st.button("🗑️", key=f"del_rev_{revenu_id}"):
                    if st.session_state.get(f"confirm_delete_rev_{revenu_id}", False):
                        # Suppression confirmée
                        st.session_state.revenus_variables = [r for r in st.session_state.revenus_variables if safe_get(r, 'id', f"rev_{r['nom'].replace(' ', '_')}") != revenu_id]
                        st.success(f"Revenu '{revenu['nom']}' supprimé.")
                        if f"confirm_delete_rev_{revenu_id}" in st.session_state:
                            del st.session_state[f"confirm_delete_rev_{revenu_id}"]
                        st.rerun()
                    else:
                        # Demande de confirmation
                        st.session_state[f"confirm_delete_rev_{revenu_id}"] = True
                        st.warning("Cliquez à nouveau pour confirmer.")

        # Affichage dates de gestion
        col1, col2 = st.columns(2)
        with col1:
            date_creation = safe_get(revenu, 'date_creation', datetime.now())
            if isinstance(date_creation, str):
                date_creation = datetime.strptime(date_creation, '%Y-%m-%d %H:%M:%S')
            st.caption(f"📅 Créé: {date_creation.strftime('%d/%m/%Y %H:%M')}")

        with col2:
            date_modification = safe_get(revenu, 'date_modification', datetime.now())
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%Y-%m-%d %H:%M:%S')
            st.caption(f"🔄 Modifié: {date_modification.strftime('%d/%m/%Y %H:%M')}")

    st.markdown("---")

def show_add_revenue_form():
    """Formulaire d'ajout de revenu avec responsable et dates"""
    with st.expander("➕ Ajouter un Revenu Variable", expanded=True):
        with st.form("add_revenue_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom_revenu = st.text_input("Nom du revenu*", placeholder="ex: Bonus William")
                type_revenu = st.selectbox("Type", st.session_state.admin_config['listes_config']['types_revenu'])
                responsable = st.selectbox("Responsable*", st.session_state.admin_config['listes_config']['responsables'])

            with col2:
                montant_mensuel = st.number_input("Montant ce mois (FCFA)*", min_value=0, step=10000)
                regulier = st.checkbox("Revenu régulier ?", help="Cocher si le montant est prévisible chaque mois")

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("✅ Ajouter Revenu", type="primary"):
                    if nom_revenu and montant_mensuel > 0 and responsable:
                        # Créer ID unique
                        existing_ids = [safe_get(r, 'id', 0) for r in st.session_state.revenus_variables]
                        numeric_ids = [id for id in existing_ids if isinstance(id, int)]
                        new_id = max(numeric_ids) + 1 if numeric_ids else 1

                        nouveau_revenu = {
                            'id': new_id,
                            'nom': nom_revenu,
                            'montant_mensuel': montant_mensuel,
                            'type': type_revenu,
                            'regulier': regulier,
                            'responsable': responsable,
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now()
                        }
                        st.session_state.revenus_variables.append(nouveau_revenu)
                        st.session_state.show_add_revenue_form = False
                        st.success(f"Revenu '{nom_revenu}' ajouté !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs obligatoires.")

            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_add_revenue_form = False
                    st.rerun()

def show_edit_revenue_form():
    """Formulaire de modification de revenu avec dates"""
    revenue_id = st.session_state.edit_revenue_id

    # Trouver le revenu avec gestion sécurisée des IDs
    revenu = None
    for r in st.session_state.revenus_variables:
        r_id = safe_get(r, 'id', f"rev_{r['nom'].replace(' ', '_')}")
        if r_id == revenue_id:
            revenu = r
            break

    if not revenu:
        st.error("Revenu introuvable")
        st.session_state.edit_revenue_id = None
        return

    with st.expander(f"✏️ Modifier: {revenu['nom']}", expanded=True):
        with st.form("edit_revenue_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom_revenu = st.text_input("Nom du revenu*", value=revenu['nom'])
                type_revenu = st.selectbox(
                    "Type", 
                    st.session_state.admin_config['listes_config']['types_revenu'],
                    index=st.session_state.admin_config['listes_config']['types_revenu'].index(revenu['type'])
                )
                responsable = st.selectbox(
                    "Responsable*", 
                    st.session_state.admin_config['listes_config']['responsables'],
                    index=st.session_state.admin_config['listes_config']['responsables'].index(safe_get(revenu, 'responsable', 'Alix'))
                )

            with col2:
                montant_mensuel = st.number_input("Montant ce mois (FCFA)*", value=revenu['montant_mensuel'], step=10000)
                regulier = st.checkbox("Revenu régulier ?", value=revenu['regulier'])

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("💾 Sauvegarder", type="primary"):
                    # Mettre à jour le revenu
                    for i, r in enumerate(st.session_state.revenus_variables):
                        r_id = safe_get(r, 'id', f"rev_{r['nom'].replace(' ', '_')}")
                        if r_id == revenue_id:
                            st.session_state.revenus_variables[i].update({
                                'nom': nom_revenu,
                                'montant_mensuel': montant_mensuel,
                                'type': type_revenu,
                                'regulier': regulier,
                                'responsable': responsable,
                                'date_modification': datetime.now()
                            })
                            break

                    st.session_state.edit_revenue_id = None
                    st.success("Revenu modifié!")
                    st.rerun()

            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.edit_revenue_id = None
                    st.rerun()

# ============================================================================
# PAGES COMPLÈTES AVEC FILTRAGE
# ============================================================================

def show_mentor_advice():
    """Page Conseils des 3 Mentors avec filtrage des projets"""
    st.title("🎯 Conseil des 3 Mentors Financiers")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Sélection d'un projet avec filtrage
    projets_filtered = filter_data_by_period(st.session_state.projets, 'date_creation')
    project_names = [p['nom'] for p in projets_filtered]

    if project_names:
        selected_project_name = st.selectbox("Choisir un projet pour conseil détaillé", project_names)

        if selected_project_name:
            project = next(p for p in projets_filtered if p['nom'] == selected_project_name)
            show_project_advice(project)
    else:
        st.info("Aucun projet disponible pour la période sélectionnée. Ajoutez des projets ou modifiez le filtre.")

def show_analytics():
    """Page Analytics & KPIs Avancés avec filtrage complet"""
    st.title("📈 Analytics & KPIs Avancés")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Données filtrées
    projets_filtered = filter_data_by_period(st.session_state.projets, 'date_creation')
    kpis = calculer_kpis()  # Déjà filtré dans la fonction

    # KPIs détaillés pour la période sélectionnée
    col1, col2, col3 = st.columns(3)

    with col1:
        total_investissement = sum(p['montant_total'] for p in projets_filtered)
        st.metric("💰 Total Investissement", format_currency(total_investissement))

    with col2:
        total_utilise = sum(p['montant_utilise_reel'] for p in projets_filtered)
        st.metric("💸 Utilisé Réel", format_currency(total_utilise))

    with col3:
        utilisation_pct = (total_utilise / total_investissement * 100) if total_investissement > 0 else 0
        st.metric("📊 Taux Utilisation", f"{utilisation_pct:.1f}%")

    # Graphique détaillé par projet pour la période
    st.subheader("📊 Performance des Projets par Période")

    if projets_filtered:
        df_projets = pd.DataFrame([
            {
                'Nom': p['nom'],
                'Type': p['type'],
                'Responsable': safe_get(p, 'responsable', 'Non défini'),
                'Budget Total': p['montant_total'],
                'Utilisé': p['montant_utilise_reel'],
                'Progression %': (p['montant_utilise_reel'] / p['montant_total'] * 100) if p['montant_total'] > 0 else 0,
                'Cash Flow': p['cash_flow_mensuel'],
                'ROI %': p['roi_attendu']
            }
            for p in projets_filtered
        ])

        fig = px.scatter(
            df_projets, 
            x='Budget Total', 
            y='Cash Flow',
            size='Progression %',
            color='Type',
            hover_name='Nom',
            hover_data=['Responsable', 'ROI %'],
            title="Analyse Investissements",
            labels={'Budget Total': 'Budget Total (FCFA)', 'Cash Flow': 'Cash Flow Mensuel (FCFA)'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Table détaillée
        st.subheader("📋 Détail par Projet")
        st.dataframe(df_projets, use_container_width=True, hide_index=True)

        # Analyse par responsable
        st.subheader("📊 Répartition par Responsable")

        responsable_stats = {}
        for projet in projets_filtered:
            resp = safe_get(projet, 'responsable', 'Non défini')
            if resp not in responsable_stats:
                responsable_stats[resp] = {'projets': 0, 'budget_total': 0, 'cash_flow': 0}
            responsable_stats[resp]['projets'] += 1
            responsable_stats[resp]['budget_total'] += projet['montant_total']
            responsable_stats[resp]['cash_flow'] += projet['cash_flow_mensuel']

        if responsable_stats:
            df_resp = pd.DataFrame(responsable_stats).T
            df_resp.index.name = 'Responsable'
            st.dataframe(df_resp, use_container_width=True)
    else:
        st.info("Aucune donnée pour la période sélectionnée.")

def show_progression():
    """Page Progression Familiale avec filtrage"""
    st.title("🚀 Progression Familiale vers l'Indépendance")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Baby Steps Dave Ramsey avec progression par période
    st.subheader("👶 Baby Steps Dave Ramsey - Progression")

    baby_steps = [
        ("Fonds d'urgence starter 665k FCFA", 1, "💰"),
        ("Éliminer toutes dettes (sauf immobilier)", 2, "🚫"),  
        ("Fonds d'urgence complet 3-6 mois", 3, "🏦"),
        ("Investir 15% revenus pour retraite", 4, "📈"),
        ("Épargne université enfants", 5, "🎓"),
        ("Rembourser hypothèque anticipé", 6, "🏠"),
        ("Construire richesse et donner", 7, "💎")
    ]

    kpis = calculer_kpis()
    current_step = kpis['baby_step_actuel']

    for step_desc, step_num, emoji in baby_steps:
        if step_num < current_step:
            st.success(f"✅ {emoji} **Étape {step_num}:** {step_desc}")
        elif step_num == current_step:
            st.warning(f"🔄 {emoji} **Étape {step_num} (ACTUELLE):** {step_desc}")
        else:
            st.info(f"⏳ {emoji} **Étape {step_num}:** {step_desc}")

    # Graphique progression temporelle basé sur période filtrée
    st.subheader("📈 Évolution par Période")

    # Simulation progression sur 24 mois
    if st.session_state.filter_year != "Tout" and st.session_state.filter_month != "Tout":
        start_date = date(st.session_state.filter_year, st.session_state.filter_month, 1)
    else:
        start_date = date.today().replace(day=1)

    mois_futurs = pd.date_range(start=start_date, periods=24, freq='MS')

    progression_simulation = []
    for i, mois in enumerate(mois_futurs):
        progression_simulation.append({
            'Mois': mois,
            'Revenus Passifs %': min(kpis['revenus_passifs_pct'] + (i * 1.2), 50),  # Progression graduelle
            'Cash Flow': kpis['cash_flow_mensuel'] + (i * 120000),  # Amélioration graduelle
            'Baby Step': min(current_step + (i // 6), 7)  # Progression par étapes
        })

    df_progression = pd.DataFrame(progression_simulation)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            df_progression, 
            x='Mois', 
            y='Revenus Passifs %',
            title="Projection Revenus Passifs"
        )
        fig.add_hline(y=st.session_state.admin_config['kpis_config']['objectif_revenus_passifs'], 
                      line_dash="dash", 
                      annotation_text=f"Objectif {st.session_state.admin_config['kpis_config']['objectif_revenus_passifs']}%")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            df_progression, 
            x='Mois', 
            y='Cash Flow',
            title="Projection Cash Flow"
        )
        fig.add_hline(y=0, line_dash="dash", annotation_text="Équilibre")
        fig.add_hline(y=st.session_state.admin_config['kpis_config']['objectif_cash_flow'], 
                      line_dash="dot", 
                      annotation_text="Objectif")
        st.plotly_chart(fig, use_container_width=True)

def show_children_education():
    """Page Éducation Financière des Enfants avec adaptation à la période"""
    st.title("👨‍👩‍👧‍👦 Éducation Financière des Enfants")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        st.markdown("**📅 Période:** Toutes les données")
    else:
        periode_str = ""
        if st.session_state.filter_month != "Tout":
            periode_str += datetime(2025, st.session_state.filter_month, 1).strftime('%B')
        if st.session_state.filter_year != "Tout":
            if periode_str:
                periode_str += f" {st.session_state.filter_year}"
            else:
                periode_str = f"Année {st.session_state.filter_year}"
        st.markdown(f"**📅 Période:** {periode_str}")

    # Adaptation des âges selon l'année filtrée
    annee_base = 2025
    if st.session_state.filter_year != "Tout":
        diff_annee = st.session_state.filter_year - annee_base
    else:
        diff_annee = 0

    enfants = [
        {
            'nom': 'Uriel',
            'age': 14 + diff_annee,
            'emoji': '👦',
            'niveau': 'Adolescent - Concepts avancés',
            'objectifs_mois': [
                f'Analyser un projet familial',
                'Créer son budget mensuel personnel',
                'Comprendre les quadrants E-S-B-I'
            ],
            'activites': [
                'Participation à la révision mensuelle des KPIs',
                'Analyse d un investissement familial',
                'Création d un mini-business plan'
            ]
        },
        {
            'nom': 'Naelle', 
            'age': 7 + diff_annee,
            'emoji': '👧',
            'niveau': 'Enfant - Concepts fondamentaux',
            'objectifs_mois': [
                'Épargner 500 FCFA ce mois',
                'Différencier 3 "actifs" et 3 "passifs"',
                'Comprendre les "projets" des parents'
            ],
            'activites': [
                'Jeu de tri "Actif ou Passif?"',
                'Tirelire mensuelle avec objectif visuel',
                'Histoire du "Petit Cochon Financier"'
            ]
        },
        {
            'nom': 'Nell-Henri',
            'age': 5 + diff_annee,
            'emoji': '👶',
            'niveau': 'Petit enfant - Concepts simples',
            'objectifs_mois': [
                'Reconnaître pièces et billets FCFA',
                'Comprendre "garder" vs "dépenser"',
                'Aider à compter l argent'
            ],
            'activites': [
                'Jeu "Marchande" avec vraie monnaie',
                'Comptine "Les Sous qui Dorment"',
                'Dessin "Ma Tirelire Magique"'
            ]
        }
    ]

    # Affichage des enfants avec planning personnalisé
    for enfant in enfants:
        with st.container():
            st.markdown(f"## {enfant['emoji']} {enfant['nom']} ({enfant['age']} ans)")
            st.markdown(f"**Niveau:** {enfant['niveau']}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### 🎯 Objectifs")
                for objectif in enfant['objectifs_mois']:
                    st.write(f"• {objectif}")

            with col2:
                st.markdown(f"### 🎮 Activités")
                for activite in enfant['activites']:
                    st.write(f"• {activite}")

            # Suivi progression selon période
            if st.session_state.filter_month != "Tout":
                progress_value = min((st.session_state.filter_month / 12) * 100, 100)
                st.progress(progress_value / 100)
                st.markdown(f"**Progression annuelle:** {progress_value:.0f}%")

            st.markdown("---")

    # Planning familial
    st.subheader("👨‍👩‍👧‍👦 Planning Familial")

    if st.session_state.filter_month != "Tout":
        planning_mensuel = {
            1: "Nouvelle année financière - Objectifs famille",
            2: "Mois de l épargne - Challenge tirelires",
            3: "Trimestre bilan - Réunion famille",
            4: "Mois des projets - Planification ensemble",
            5: "Préparation été - Budget vacances",
            6: "Bilan mi-année - Célébration réussites",
            7: "Vacances éducatives - Jeux financiers",
            8: "Préparation rentrée - Budget scolaire",
            9: "Rentrée - Nouveaux objectifs",
            10: "Mois Halloween - Épargne bonbons",
            11: "Préparation fêtes - Budget cadeaux",
            12: "Bilan annuel - Récompenses famille"
        }

        activite_mois = planning_mensuel.get(st.session_state.filter_month, "Développement continu")
        st.success(f"**🎯 Activité principale ce mois :** {activite_mois}")
    else:
        st.info("Sélectionnez un mois spécifique pour voir l'activité recommandée.")

def show_vision_2030():
    """Page Vision Familiale 2030 avec calculs basés sur période actuelle"""
    st.title("🔮 Vision Familiale 2030")

    # Affichage période
    if st.session_state.filter_month == "Tout" and st.session_state.filter_year == "Tout":
        current_date = date.today()
        st.markdown(f"**📅 Période actuelle:** {current_date.strftime('%B %Y')}")
    else:
        if st.session_state.filter_year != "Tout" and st.session_state.filter_month != "Tout":
            current_date = date(st.session_state.filter_year, st.session_state.filter_month, 1)
            st.markdown(f"**📅 Période actuelle:** {current_date.strftime('%B %Y')}")
        else:
            current_date = date.today()
            st.markdown("**📅 Période actuelle:** Date actuelle (filtre partiel)")

    st.subheader("🇨🇭 Objectif: Toute la famille en Suisse avec indépendance financière")

    # Progression vers 2030 basée sur la période actuelle
    target_date = date(2030, 1, 1)
    jours_restants = (target_date - current_date).days
    mois_restants = jours_restants // 30

    st.metric("⏰ Temps Restant", f"{mois_restants} mois", delta=f"{jours_restants} jours")

    # Milestones avec dates précises
    st.markdown("### 📅 Roadmap Stratégique vers 2030")

    milestones = [
        {'annee': 2025, 'titre': 'Stabilisation', 'description': 'Finaliser actifs Cameroun + cash flow positif', 'statut': 'en-cours'},
        {'annee': 2026, 'titre': 'Transition', 'description': 'Développement revenus passifs 15%+', 'statut': 'planifie'},
        {'annee': 2027, 'titre': 'Expansion', 'description': 'Multiplication actifs générateurs', 'statut': 'futur'},
        {'annee': 2028, 'titre': 'Préparation', 'description': 'Déménagement famille - visa/scolarité', 'statut': 'futur'},
        {'annee': 2029, 'titre': 'Installation', 'description': 'Installation progressive en Suisse', 'statut': 'futur'},
        {'annee': 2030, 'titre': 'Indépendance', 'description': 'Indépendance financière complète', 'statut': 'objectif'}
    ]

    annee_reference = st.session_state.filter_year if st.session_state.filter_year != "Tout" else current_date.year

    for milestone in milestones:
        annee = milestone['annee']
        progress = max(0, min(100, ((annee - 2025) / 5) * 100))

        if annee <= annee_reference:
            if milestone['statut'] == 'en-cours':
                st.success(f"🔄 **{annee} - EN COURS:** {milestone['titre']} - {milestone['description']}")
            else:
                st.success(f"✅ **{annee} - RÉALISÉ:** {milestone['titre']} - {milestone['description']}")
        elif annee == annee_reference + 1:
            st.warning(f"🎯 **{annee} - PROCHAINE ÉTAPE:** {milestone['titre']} - {milestone['description']}")
        else:
            st.info(f"⏳ **{annee} - FUTUR:** {milestone['titre']} - {milestone['description']}")

        st.progress(progress / 100)

    # Calculs financiers actualisés
    st.markdown("### 💰 Exigences Financières Actualisées")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Situation Actuelle")
        kpis = calculer_kpis()

        st.metric("Cash Flow Mensuel", format_currency(kpis['cash_flow_mensuel']))
        st.metric("Revenus Passifs", f"{kpis['revenus_passifs_pct']:.1f}%")
        st.metric("Actifs Générateurs", f"{kpis['nombre_actifs']} projets")

    with col2:
        st.markdown("#### 🎯 Objectifs 2030")

        # Calculs pour 2030
        cout_enfants_2030_chf = 280000  # CHF
        cout_famille_2030_chf = 150000  # CHF logement + vie
        cout_total_chf = cout_enfants_2030_chf + cout_famille_2030_chf
        cout_total_fcfa = cout_total_chf * 665  # Taux approximatif

        st.metric("Coût Total Suisse", f"{cout_total_chf:,} CHF/an")
        st.metric("Équivalent FCFA", f"{cout_total_fcfa:,.0f} FCFA/an")

        revenus_passifs_requis = cout_total_fcfa * 1.3  # Marge sécurité
        revenus_passifs_mensuels = revenus_passifs_requis / 12

        st.metric("Revenus Passifs Requis", f"{revenus_passifs_mensuels:,.0f} FCFA/mois")

    # Progression mensuelle vers objectif
    st.markdown("### 📈 Progression Mensuelle vers Objectif")

    # Calculer progression basée sur période actuelle
    mois_ecoules = (annee_reference - 2025) * 12
    if st.session_state.filter_month != "Tout":
        mois_ecoules += st.session_state.filter_month
    else:
        mois_ecoules += current_date.month

    progression_actuelle = min(mois_ecoules / 60 * 100, 100)  # 60 mois jusqu'à 2030

    st.progress(progression_actuelle / 100)
    st.markdown(f"**Progression générale:** {progression_actuelle:.1f}% vers objectif 2030")

    # Actions prioritaires pour la période actuelle
    st.markdown(f"### 🎯 Actions Prioritaires")

    if annee_reference == 2025:
        actions = [
            "✅ Finaliser titre foncier Mejeuh",
            "📈 Développer IIBA pour 500k FCFA/mois",
            "💰 Atteindre cash flow mensuel positif",
            "🏦 Constituer fonds d urgence 6 mois"
        ]
    elif annee_reference == 2026:
        actions = [
            "🏠 Acquérir 2ème propriété locative",
            "💼 William: développer side-business",
            "📊 Atteindre 20% revenus passifs",
            "🎓 Formation investissement Alix"
        ]
    else:
        actions = [
            "🌍 Préparer dossiers immigration Suisse",
            "🏫 Rechercher écoles enfants Suisse",
            "💰 Optimiser transferts Cameroun-Suisse",
            "🎯 Diversifier revenus passifs"
        ]

    for action in actions:
        st.write(f"• {action}")

# ============================================================================
# NOUVELLE PAGE ADMINISTRATION
# ============================================================================

def show_admin():
    """Page Administration complète"""
    st.title("⚙️ Administration du Système")
    st.markdown("Configuration avancée des paramètres, listes et conseils des mentors")

    # Navigation admin
    admin_tabs = st.tabs([
        "🎯 KPIs & Objectifs", 
        "📋 Listes & Vocabulaire", 
        "🧠 Conseils Mentors",
        "📊 Export/Import Données",
        "📈 Statistiques Système"
    ])

    with admin_tabs[0]:
        show_admin_kpis()

    with admin_tabs[1]:
        show_admin_listes()

    with admin_tabs[2]:
        show_admin_mentors()

    with admin_tabs[3]:
        show_admin_export_import()

    with admin_tabs[4]:
        show_admin_stats()

def show_admin_kpis():
    """Configuration des KPIs et objectifs"""
    st.subheader("🎯 Configuration des KPIs et Objectifs")

    with st.form("admin_kpis_form"):
        st.markdown("### 💰 Objectifs Financiers")

        col1, col2 = st.columns(2)

        with col1:
            objectif_cash_flow = st.number_input(
                "Objectif Cash Flow Mensuel (FCFA)",
                value=st.session_state.admin_config['kpis_config']['objectif_cash_flow'],
                step=100000
            )

            objectif_ratio_actifs = st.number_input(
                "Objectif Ratio Actifs/Total (%)",
                value=st.session_state.admin_config['kpis_config']['objectif_ratio_actifs'],
                min_value=0,
                max_value=100
            )

        with col2:
            objectif_revenus_passifs = st.number_input(
                "Objectif Revenus Passifs (%)",
                value=st.session_state.admin_config['kpis_config']['objectif_revenus_passifs'],
                min_value=0,
                max_value=100
            )

            objectif_fonds_urgence = st.number_input(
                "Objectif Fonds d'Urgence (mois)",
                value=st.session_state.admin_config['kpis_config']['objectif_fonds_urgence'],
                min_value=0,
                max_value=12
            )

        if st.form_submit_button("💾 Sauvegarder KPIs", type="primary"):
            st.session_state.admin_config['kpis_config'].update({
                'objectif_cash_flow': objectif_cash_flow,
                'objectif_ratio_actifs': objectif_ratio_actifs,
                'objectif_revenus_passifs': objectif_revenus_passifs,
                'objectif_fonds_urgence': objectif_fonds_urgence
            })
            st.success("✅ Configuration KPIs sauvegardée!")
            st.rerun()

def show_admin_listes():
    """Configuration des listes et vocabulaire"""
    st.subheader("📋 Configuration des Listes et Vocabulaire")

    # Types de projet
    with st.expander("🏗️ Types de Projets", expanded=False):
        with st.form("admin_types_form"):
            types_actuels = st.session_state.admin_config['listes_config']['types_projet']

            st.write("**Types actuels:**")
            for i, type_p in enumerate(types_actuels):
                st.write(f"• {type_p}")

            nouveau_type = st.text_input("Ajouter un nouveau type")
            type_a_supprimer = st.selectbox("Supprimer un type", ["Aucun"] + types_actuels)

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("➕ Ajouter"):
                    if nouveau_type and nouveau_type not in types_actuels:
                        st.session_state.admin_config['listes_config']['types_projet'].append(nouveau_type)
                        st.success(f"Type '{nouveau_type}' ajouté!")
                        st.rerun()

            with col2:
                if st.form_submit_button("🗑️ Supprimer"):
                    if type_a_supprimer != "Aucun":
                        st.session_state.admin_config['listes_config']['types_projet'].remove(type_a_supprimer)
                        st.success(f"Type '{type_a_supprimer}' supprimé!")
                        st.rerun()

    # Statuts de projet
    with st.expander("📊 Statuts de Projets", expanded=False):
        with st.form("admin_statuts_form"):
            statuts_actuels = st.session_state.admin_config['listes_config']['statuts_projet']

            st.write("**Statuts actuels:**")
            for statut in statuts_actuels:
                st.write(f"• {statut}")

            nouveau_statut = st.text_input("Ajouter un nouveau statut")
            statut_a_supprimer = st.selectbox("Supprimer un statut", ["Aucun"] + statuts_actuels)

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("➕ Ajouter"):
                    if nouveau_statut and nouveau_statut not in statuts_actuels:
                        st.session_state.admin_config['listes_config']['statuts_projet'].append(nouveau_statut)
                        st.success(f"Statut '{nouveau_statut}' ajouté!")
                        st.rerun()

            with col2:
                if st.form_submit_button("🗑️ Supprimer"):
                    if statut_a_supprimer != "Aucun":
                        st.session_state.admin_config['listes_config']['statuts_projet'].remove(statut_a_supprimer)
                        st.success(f"Statut '{statut_a_supprimer}' supprimé!")
                        st.rerun()

    # Responsables
    with st.expander("👤 Responsables", expanded=False):
        with st.form("admin_responsables_form"):
            responsables_actuels = st.session_state.admin_config['listes_config']['responsables']

            st.write("**Responsables actuels:**")
            for resp in responsables_actuels:
                st.write(f"• {resp}")

            nouveau_responsable = st.text_input("Ajouter un nouveau responsable")
            responsable_a_supprimer = st.selectbox("Supprimer un responsable", ["Aucun"] + responsables_actuels)

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("➕ Ajouter"):
                    if nouveau_responsable and nouveau_responsable not in responsables_actuels:
                        st.session_state.admin_config['listes_config']['responsables'].append(nouveau_responsable)
                        st.success(f"Responsable '{nouveau_responsable}' ajouté!")
                        st.rerun()

            with col2:
                if st.form_submit_button("🗑️ Supprimer"):
                    if responsable_a_supprimer != "Aucun":
                        st.session_state.admin_config['listes_config']['responsables'].remove(responsable_a_supprimer)
                        st.success(f"Responsable '{responsable_a_supprimer}' supprimé!")
                        st.rerun()

def show_admin_mentors():
    """Configuration des conseils des mentors"""
    st.subheader("🧠 Configuration des Conseils des Mentors")

    mentors = ["Kiyosaki", "Buffett", "Ramsey"]
    types_projet = st.session_state.admin_config['listes_config']['types_projet']

    for mentor in mentors:
        with st.expander(f"🎯 {mentor}", expanded=False):
            st.markdown(f"### Conseils de {mentor}")

            with st.form(f"admin_mentor_{mentor}_form"):
                conseils_actuels = st.session_state.admin_config['mentors_conseils'][mentor]

                for type_projet in types_projet:
                    conseil_actuel = conseils_actuels.get(type_projet, "")
                    nouveau_conseil = st.text_area(
                        f"Conseil pour '{type_projet}'",
                        value=conseil_actuel,
                        height=100,
                        key=f"{mentor}_{type_projet}"
                    )

                    # Mise à jour immédiate
                    st.session_state.admin_config['mentors_conseils'][mentor][type_projet] = nouveau_conseil

                if st.form_submit_button(f"💾 Sauvegarder conseils {mentor}", type="primary"):
                    st.success(f"✅ Conseils de {mentor} sauvegardés!")
                    st.rerun()

def show_admin_export_import():
    """Export/Import des données"""
    st.subheader("📊 Export/Import des Données")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Exporter les Données")

        if st.button("📊 Générer Export Excel", type="primary"):
            try:
                excel_data = export_to_excel()

                # Nom du fichier avec timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"Plan_Financier_Familial_{timestamp}.xlsx"

                st.download_button(
                    label="💾 Télécharger Excel",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

                st.success("✅ Export Excel généré avec succès!")

            except Exception as e:
                st.error(f"❌ Erreur lors de l'export: {str(e)}")

        # Statistiques export
        st.markdown("### 📈 Contenu de l'Export")
        st.write(f"• **{len(st.session_state.projets)}** projets")
        st.write(f"• **{len(st.session_state.revenus_variables)}** revenus")
        st.write("• **Configuration** complète")
        st.write("• **KPIs** calculés")
        st.write("• **Suivi mensuel** détaillé")

    with col2:
        st.markdown("### 📥 Importer des Données")

        st.info("""
        **🔄 Fonctionnalité Import**

        L'import de données sera disponible dans une future version.

        Pour l'instant, vous pouvez :
        1. Exporter vos données actuelles
        2. Les modifier dans Excel
        3. Les réimporter manuellement via l'interface
        """)

        uploaded_file = st.file_uploader(
            "Choisir un fichier Excel",
            type=['xlsx'],
            help="Fonctionnalité en développement"
        )

        if uploaded_file:
            st.warning("⚠️ Import automatique pas encore disponible")

    # Sauvegarde JSON
    st.markdown("### 💾 Sauvegarde Configuration")

    if st.button("📋 Générer Sauvegarde JSON"):
        backup_data = {
            'projets': st.session_state.projets,
            'revenus_variables': st.session_state.revenus_variables,
            'admin_config': st.session_state.admin_config,
            'timestamp': datetime.now().isoformat()
        }

        # Convertir les dates en strings pour JSON
        for projet in backup_data['projets']:
            if 'echeance' in projet:
                projet['echeance'] = projet['echeance'].isoformat()
            if 'date_creation' in projet:
                projet['date_creation'] = projet['date_creation'].isoformat()
            if 'date_modification' in projet:
                projet['date_modification'] = projet['date_modification'].isoformat()

        for revenu in backup_data['revenus_variables']:
            if 'date_creation' in revenu:
                revenu['date_creation'] = revenu['date_creation'].isoformat()
            if 'date_modification' in revenu:
                revenu['date_modification'] = revenu['date_modification'].isoformat()

        json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)

        st.download_button(
            label="💾 Télécharger Sauvegarde JSON",
            data=json_data,
            file_name=f"sauvegarde_plan_financier_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

def show_admin_stats():
    """Statistiques système"""
    st.subheader("📈 Statistiques du Système")

    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total Projets", len(st.session_state.projets))

    with col2:
        st.metric("💰 Total Revenus", len(st.session_state.revenus_variables))

    with col3:
        total_suivi = sum(len(p.get('suivi_mensuel', [])) for p in st.session_state.projets)
        st.metric("📋 Entrées Suivi", total_suivi)

    with col4:
        total_budget = sum(p['montant_total'] for p in st.session_state.projets)
        st.metric("💸 Budget Total", format_currency(total_budget))

    # Graphiques statistiques
    st.markdown("### 📊 Répartitions")

    col1, col2 = st.columns(2)

    with col1:
        # Répartition par type
        type_counts = {}
        for projet in st.session_state.projets:
            type_p = projet['type']
            type_counts[type_p] = type_counts.get(type_p, 0) + 1

        if type_counts:
            fig = px.pie(
                values=list(type_counts.values()),
                names=list(type_counts.keys()),
                title="Répartition des Projets par Type"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Répartition par responsable
        resp_counts = {}
        for projet in st.session_state.projets:
            resp = safe_get(projet, 'responsable', 'Non défini')
            resp_counts[resp] = resp_counts.get(resp, 0) + 1

        if resp_counts:
            fig = px.bar(
                x=list(resp_counts.keys()),
                y=list(resp_counts.values()),
                title="Nombre de Projets par Responsable",
                labels={'x': 'Responsable', 'y': 'Nombre de projets'}
            )
            st.plotly_chart(fig, use_container_width=True)

    # Historique des modifications
    st.markdown("### 📅 Activité Récente")

    # Combine projets et revenus avec leurs dates de modification
    activites = []

    for projet in st.session_state.projets:
        date_modif = safe_get(projet, 'date_modification', datetime.now())
        if isinstance(date_modif, str):
            date_modif = datetime.fromisoformat(date_modif)
        activites.append({
            'type': 'Projet',
            'nom': projet['nom'],
            'date': date_modif,
            'responsable': safe_get(projet, 'responsable', 'Non défini')
        })

    for revenu in st.session_state.revenus_variables:
        date_modif = safe_get(revenu, 'date_modification', datetime.now())
        if isinstance(date_modif, str):
            date_modif = datetime.fromisoformat(date_modif)
        activites.append({
            'type': 'Revenu',
            'nom': revenu['nom'],
            'date': date_modif,
            'responsable': safe_get(revenu, 'responsable', 'Non défini')
        })

    # Trier par date de modification (plus récent d'abord)
    activites.sort(key=lambda x: x['date'], reverse=True)

    # Afficher les 10 plus récentes
    if activites:
        df_activites = pd.DataFrame(activites[:10])
        df_activites['date'] = df_activites['date'].dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df_activites, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune activité récente")

# ============================================================================
# FONCTION PRINCIPALE AVEC NOUVELLE PAGE ADMIN
# ============================================================================

def main():
    # Chargement CSS
    load_css()

    # Initialisation session state
    initialize_session_state()

    # Sidebar navigation
    selected_page = render_sidebar()

    # Routing des pages
    if selected_page == "📊 Dashboard Principal":
        show_dashboard()
    elif selected_page == "📋 Vue Kanban Projets":
        show_kanban_view()
    elif selected_page == "💼 Gestion Projets":
        show_project_management()
    elif selected_page == "💰 Revenus Variables":
        show_revenue_management()
    elif selected_page == "🎯 Conseils 3 Mentors":
        show_mentor_advice()
    elif selected_page == "📈 Analytics & KPIs":
        show_analytics()
    elif selected_page == "🚀 Progression Familiale":
        show_progression()
    elif selected_page == "👨‍👩‍👧‍👦 Éducation Enfants":
        show_children_education()
    elif selected_page == "🔮 Vision 2030":
        show_vision_2030()
    elif selected_page == "⚙️ Administration":
        show_admin()

if __name__ == "__main__":
    main()
