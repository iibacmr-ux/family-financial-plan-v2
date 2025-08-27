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
    page_title="Plan Financier Familial",
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
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #ffffff 100%);
    }
    .main-header {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .project-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .allocation-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DONNÉES ET LOGIQUE METIER AMÉLIORÉE
# ============================================================================
def initialize_session_state():
    """Initialise les données de session avec TOUS les champs requis et allocation dynamique"""
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
                ],
                'allocations_recues': []  # Nouveau champ pour les allocations
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
                'suivi_mensuel': [],
                'allocations_recues': []
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
                ],
                'allocations_recues': []
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
                ],
                'allocations_recues': []
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
                'date_modification': datetime(2025, 1, 1),
                'allocations': []  # Nouveau champ pour les allocations
            },
            {
                'id': 2,
                'nom': 'Revenus IIBA',
                'montant_mensuel': 232000,
                'type': 'Business',
                'regulier': False,
                'responsable': 'William',
                'date_creation': datetime(2025, 1, 15),
                'date_modification': datetime(2025, 2, 1),
                'allocations': []
            },
            {
                'id': 3,
                'nom': 'Épargne',
                'montant_mensuel': 50000,
                'type': 'Épargne',
                'regulier': True,
                'responsable': 'Alix',
                'date_creation': datetime(2024, 12, 1),
                'date_modification': datetime(2024, 12, 1),
                'allocations': []
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
                    'Passif': 'Ce passif retire de l\'argent de votre poche. Est-il vraiment nécessaire ?',
                    'Investissement formation': 'L\'éducation est un actif qui génère des revenus futurs plus élevés.'
                },
                'Buffett': {
                    'Actif générateur': 'Assurez-vous de comprendre parfaitement ce business et son potentiel long terme.',
                    'Passif': 'Quel est le coût d\'opportunité ? Cet argent pourrait-il être mieux investi ?',
                    'Investissement formation': 'Le meilleur investissement est en vous-même et votre famille.'
                },
                'Ramsey': {
                    'Actif générateur': 'Si ce projet ne vous endette pas excessivement, c\'est excellent pour votre indépendance.',
                    'Passif': 'Vérifiez que cet investissement respecte votre budget 50/30/20.',
                    'Investissement formation': 'L\'éducation est toujours rentable à long terme.'
                }
            },
            'education_module_active': False  # Module éducation enfants désactivé par défaut
        }

def safe_get(dict_obj, key, default='N/A'):
    """Récupère une valeur de dictionnaire de manière sécurisée"""
    return dict_obj.get(key, default)

def calculer_kpis():
    """Calcule les KPIs en temps réel"""
    projets = st.session_state.projets
    revenus = st.session_state.revenus_variables
    
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

def filter_by_date(projets):
    year = st.session_state.filters_date['year']
    month = st.session_state.filters_date['month']

    def visible(p):
        start_year = p['date_creation'].year
        # Supposons date fin = échéance, ou date_modification
        end_date = p.get('echeance', p.get('date_modification', datetime.now()))
        if year != "Tous" and start_year != int(year):
            return False
        if month != "Tous":
            # vérifier mois dans la plage date_creation à date fin
            start = p['date_creation']
            end = end_date if isinstance(end_date, date) else end_date.date()
            filter_m = int(month)
            return (start.month <= filter_m <= end.month) if (start.year == end.year) else True
        return True

    return [p for p in projets if visible(p)]


# ============================================================================
# FONCTIONS D'ALLOCATION DYNAMIQUE
# ============================================================================
def allouer_revenu_aux_projets(revenu_id, allocations_list):
    """Alloue un revenu à plusieurs projets avec validation"""
    # Trouver le revenu
    revenu = next((r for r in st.session_state.revenus_variables if r['id'] == revenu_id), None)
    if not revenu:
        return False, "Revenu introuvable"
    
    # Validation du total
    total_alloue = sum(alloc['montant'] for alloc in allocations_list)
    if total_alloue > revenu['montant_mensuel']:
        return False, f"Total alloué ({format_currency(total_alloue)}) dépasse le revenu disponible ({format_currency(revenu['montant_mensuel'])})"
    
    # Mettre à jour le revenu
    revenu['allocations'] = allocations_list
    revenu['date_modification'] = datetime.now()
    
    # Mettre à jour les projets concernés
    for allocation in allocations_list:
        projet = next((p for p in st.session_state.projets if p['id'] == allocation['projet_id']), None)
        if projet:
            if 'allocations_recues' not in projet:
                projet['allocations_recues'] = []
            
            # Ajouter l'allocation reçue
            projet['allocations_recues'].append({
                'revenu_id': revenu_id,
                'revenu_nom': revenu['nom'],
                'montant': allocation['montant'],
                'mois': allocation['mois'],
                'date_allocation': datetime.now()
            })
            projet['date_modification'] = datetime.now()
    
    return True, "Allocation réalisée avec succès"

def calculer_velocite_projet(projet):
    """Calcule la vélocité mensuelle d'un projet"""
    if not projet.get('suivi_mensuel'):
        return 0
    
    suivis = projet['suivi_mensuel']
    if len(suivis) < 2:
        return 0
    
    # Prendre les 3 derniers mois pour la vélocité
    recent_suivis = sorted(suivis, key=lambda x: x['mois'])[-3:]
    velocites = []
    
    for suivi in recent_suivis:
        velocites.append(suivi['reel'])
    
    return sum(velocites) / len(velocites) if velocites else 0

def calculer_probabilite_reussite(projet):
    """Calcule la probabilité de réussite d'un projet"""
    # Facteurs de calcul
    progression = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0
    jours_restants = (projet['echeance'] - date.today()).days
    velocite = calculer_velocite_projet(projet)
    
    # Score basé sur différents critères
    score = 50  # Score de base
    
    # Bonus progression
    if progression > 75:
        score += 20
    elif progression > 50:
        score += 10
    elif progression < 10:
        score -= 20
    
    # Bonus temps
    if jours_restants > 90:
        score += 15
    elif jours_restants < 30:
        score -= 25
    
    # Bonus vélocité
    if velocite > projet['budget_alloue_mensuel'] * 0.8:
        score += 15
    elif velocite < projet['budget_alloue_mensuel'] * 0.3:
        score -= 15
    
    return max(0, min(100, score))

# ============================================================================
# NOUVELLE SIDEBAR NAVIGATION (5 ONGLETS)
# ============================================================================
def render_sidebar():
    """Affiche la sidebar avec navigation optimisée UX 2025"""
    with st.sidebar:
        st.markdown("### 💰 Plan Financier Familial")
        st.markdown("*Alix & William - Vers l'Indépendance 2030*")
        
        # Navigation avec 5 onglets optimisés UX
        st.markdown("---")
        pages = [
            "🏠 Tableau de Bord",
            "💼 Projets & Revenus", 
            "📊 Analytics",
            "🎯 Vision & Objectifs",
            "⚙️ Paramètres"
        ]
        
        selected_page = st.radio(
            "Navigation",
            pages,
            key="nav_radio",
            label_visibility="collapsed"
        )
        
        # Ajout d’un filtre global avec "Mois", "Année" et "Tous" dans la sidebar gauche
        st.markdown("### 📅 Filtre Global par Date") 
        filter_year = st.selectbox("Année", ["Tous"] + sorted(set([p['date_creation'].year for p in st.session_state.projets])), index=0)
        filter_month = st.selectbox("Mois", ["Tous"] + [f"{i:02d}" for i in range(1,13)], index=0) 
        st.session_state.filters_date = {'year': filter_year, 'month': filter_month}
        
        # Phase actuelle
        kpis = calculer_kpis()
        phase = kpis['phase_actuelle']
        # Calcul du total budget projet filtré 
        filtered_projets = filter_by_date(st.session_state.projets) 
        total_budget_filtre = sum(p['montant_total'] for p in filtered_projets)
        st.markdown("---")
        st.markdown(f"**🎯 Phase:** {phase}")
        st.markdown(f"**💰 Revenus:** {format_currency(kpis['revenus_mensuels'])}")
        st.markdown(f"**💼 Budget Total Filtré:** {format_currency(total_budget_filtre)}")
        st.markdown(f"**📊 Cash Flow:** {format_currency(kpis['cash_flow_mensuel'])}")        
        
        return selected_page

# ============================================================================
# 1. TABLEAU DE BORD - HUB CENTRAL UNIFIÉ
# ============================================================================
def show_tableau_de_bord():
    """Hub central unifié - Dashboard + KPIs + Actions rapides"""
    st.title("🏠 Tableau de Bord Central")
    
    # Actions rapides en haut
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Nouveau Projet", type="primary"):
            st.session_state.show_quick_add_project = True
    with col2:
        if st.button("💰 Ajouter Revenu"):
            st.session_state.show_quick_add_revenue = True
    with col3:
        if st.button("📊 Voir Analytics"):
            st.session_state.nav_radio = "📊 Analytics"
            st.rerun()
    with col4:
        if st.button("🎯 Voir Objectifs"):
            st.session_state.nav_radio = "🎯 Vision & Objectifs"
            st.rerun()
    
    # KPIs principaux
    kpis = calculer_kpis()
    
    st.markdown("### 📈 KPIs Essentiels")
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
            "🎯 Phase Actuelle",
            kpis['phase_actuelle'],
            delta=f"Baby Step {kpis['baby_step_actuel']}/7"
        )
    
    # Graphiques essentiels
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution Cash Flow")
        # Simulation données
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
    
    # Résumé des projets critiques
    st.subheader("⚠️ Projets Nécessitant Attention")
    projets_critiques = []
    for projet in st.session_state.projets:
        categorie, titre, _ = categorize_project(projet)
        if categorie in ['en-retard', 'a-risque', 'bloque']:
            projets_critiques.append({
                'nom': projet['nom'],
                'statut': titre,
                'progression': f"{(projet['montant_utilise_reel']/projet['montant_total']*100):.1f}%" if projet['montant_total'] > 0 else "0%",
                'jours_restants': (projet['echeance'] - date.today()).days
            })
    
    if projets_critiques:
        df_critiques = pd.DataFrame(projets_critiques)
        st.dataframe(df_critiques, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Tous les projets sont sur la bonne voie !")
    
    # Modals d'ajout rapide
    if st.session_state.get('show_quick_add_project'):
        show_quick_add_project_modal()
    
    if st.session_state.get('show_quick_add_revenue'):
        show_quick_add_revenue_modal()

def show_quick_add_project_modal():
    """Modal d'ajout rapide de projet"""
    with st.expander("➕ Ajout Rapide - Nouveau Projet", expanded=True):
        with st.form("quick_add_project"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom du projet*")
                type_projet = st.selectbox("Type", st.session_state.admin_config['listes_config']['types_projet'])
                montant_total = st.number_input("Budget total (FCFA)*", min_value=0, step=10000)
            
            with col2:
                responsable = st.selectbox("Responsable*", st.session_state.admin_config['listes_config']['responsables'])
                echeance = st.date_input("Échéance", min_value=date.today())
                priorite = st.selectbox("Priorité", st.session_state.admin_config['listes_config']['priorites'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer", type="primary"):
                    if nom and montant_total > 0:
                        new_id = max([p['id'] for p in st.session_state.projets]) + 1 if st.session_state.projets else 1
                        nouveau_projet = {
                            'id': new_id,
                            'nom': nom,
                            'type': type_projet,
                            'montant_total': montant_total,
                            'budget_alloue_mensuel': montant_total // 12,  # Répartition sur 12 mois par défaut
                            'montant_utilise_reel': 0,
                            'cash_flow_mensuel': 0 if type_projet != 'Passif' else -montant_total//12,
                            'statut': 'Planifié',
                            'echeance': echeance,
                            'roi_attendu': 0,
                            'priorite': priorite,
                            'description': f'Projet {type_projet.lower()} créé rapidement',
                            'source_financement': 'À définir',
                            'responsable': responsable,
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now(),
                            'suivi_mensuel': [],
                            'allocations_recues': [],
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now(),
                            'created_by': 'William',  # Exemple à remplacer par utilisateur courant
                            'updated_by': 'William',
                        }
                        st.session_state.projets.append(nouveau_projet)
                        st.success(f"✅ Projet '{nom}' créé !")
                        st.session_state.show_quick_add_project = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_quick_add_project = False
                    st.rerun()

def show_quick_add_revenue_modal():
    """Modal d'ajout rapide de revenu"""
    with st.expander("💰 Ajout Rapide - Nouveau Revenu", expanded=True):
        with st.form("quick_add_revenue"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom du revenu*")
                montant = st.number_input("Montant mensuel (FCFA)*", min_value=0, step=10000)
            
            with col2:
                type_revenu = st.selectbox("Type", st.session_state.admin_config['listes_config']['types_revenu'])
                responsable = st.selectbox("Responsable*", st.session_state.admin_config['listes_config']['responsables'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer", type="primary"):
                    # À l'intérieur du formulaire de création de revenu
                    date_disponibilite = st.date_input("Date de mise à disposition", value=date.today())
                    if nom and montant > 0:
                        existing_ids = [r['id'] for r in st.session_state.revenus_variables]
                        new_id = max(existing_ids) + 1 if existing_ids else 1
                        # Lors de la création du revenu
                        nouveau_revenu = {
                            'id': new_id,
                            'nom': nom,
                            'montant_mensuel': montant,
                            'type': type_revenu,
                            'regulier': True,
                            'responsable': responsable,
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now(),
                            'date_disponibilite': date_disponibilite,
                            'allocations': []
                        }
                        st.session_state.revenus_variables.append(nouveau_revenu)
                        st.success(f"✅ Revenu '{nom}' ajouté !")
                        st.session_state.show_quick_add_revenue = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_quick_add_revenue = False
                    st.rerun()

# ============================================================================
# 2. PROJETS & REVENUS - WORKFLOW FINANCIER COMPLET
# ============================================================================
def show_projets_revenus():
    """Page unifiée Projets & Revenus avec allocation dynamique"""
    st.title("💼 Projets & Revenus")
    
    # Toggle entre vues
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste Projets", "📊 Vue Kanban", "💰 Revenus", "🔄 Allocations"])
    
    with tab1:
        show_projets_liste()
    
    with tab2:
        show_projets_kanban()
    
    with tab3:
        show_revenus_avec_allocation()
    
    with tab4:
        show_allocations_dashboard()

def show_projets_liste():
    """Affichage liste des projets avec actions"""
    # Actions principales
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nouveau Projet", type="primary"):
            st.session_state.show_add_project_form = True
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_type = st.selectbox("Type", ["Tous"] + st.session_state.admin_config['listes_config']['types_projet'])
    with col2:
        filter_status = st.selectbox("Statut", ["Tous"] + st.session_state.admin_config['listes_config']['statuts_projet'])
    with col3:
        filter_priority = st.selectbox("Priorité", ["Toutes"] + st.session_state.admin_config['listes_config']['priorites'])
    with col4:
        sort_by = st.selectbox("Trier par", ["Nom", "Montant", "Échéance", "ROI", "Type", "Date création"])
    
    # Application des filtres
    projets_filtered = filter_projects(st.session_state.projets, filter_type, filter_status, filter_priority, sort_by)
    
    # Affichage des projets
    st.subheader(f"📋 Projets ({len(projets_filtered)})")
    
    if projets_filtered:
        for projet in projets_filtered:
            show_project_card_enhanced(projet)
    else:
        st.info("Aucun projet ne correspond aux filtres sélectionnés.")
    
    # Formulaire d'ajout
    if st.session_state.get('show_add_project_form'):
        show_add_project_form_complete()

def show_edit_project_form():
    if st.session_state.get('show_edit_project_form') and st.session_state.get('edit_project_id'):
        projet = next((p for p in st.session_state.projets if p['id'] == st.session_state.edit_project_id), None)
        if projet:
            with st.expander(f"✏️ Modifier Projet: {projet['nom']}", expanded=True):
                with st.form("edit_project_form"):
                    nom = st.text_input("Nom du projet", value=projet['nom'])
                    # Ajoutez ici tous les champs à modifier, préremplis avec projet
                    # Ex:
                    montant_total = st.number_input("Budget total (FCFA)", value=projet['montant_total'])
                    # ...
                    if st.form_submit_button("✅ Enregistrer"):
                        projet['nom'] = nom
                        projet['montant_total'] = montant_total
                        projet['date_modification'] = datetime.now()
                        st.session_state.show_edit_project_form = False
                        st.success(f"Projet '{nom}' modifié !")
                        st.experimental_rerun()
                    if st.form_submit_button("❌ Annuler"):
                        st.session_state.show_edit_project_form = False
                        st.experimental_rerun()


def show_project_card_enhanced(projet):
    """Affiche une carte projet améliorée avec vélocité et probabilité"""
    with st.container():
        # En-tête
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"🎯 {projet['nom']}")
            st.caption(f"👤 {safe_get(projet, 'responsable', 'Non défini')}")
            if st.button("✏️ Modifier", key=f"edit_{projet['id']}"):
                st.session_state.edit_project_id = projet['id']
                st.session_state.show_edit_project_form = True  # Ajout flag pour afficher form
                st.experimental_rerun()
        
        with col2:
            type_colors = {
                'Actif générateur': '🟢',
                'Passif': '🔴',
                'Investissement formation': '🔵'
            }
            st.markdown(f"{type_colors.get(projet['type'], '⚪')} **{projet['type']}**")
        
        with col3:
            status_colors = {
                'Planifié': '🔵', 'En cours': '🟡', 'Développement': '🟠',
                'Réalisé': '🟢', 'Suspendu': '🔴'
            }
            st.markdown(f"{status_colors.get(projet['statut'], '⚪')} {projet['statut']}")
        
        # Métriques principales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💰 Budget Total", format_currency(projet['montant_total']))
        
        with col2:
            st.metric("💸 Utilisé", format_currency(projet['montant_utilise_reel']))
        
        with col3:
            progress = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0
            st.metric("📊 Progression", f"{progress:.1f}%")
        
        with col4:
            velocite = calculer_velocite_projet(projet)
            st.metric("⚡ Vélocité", format_currency(velocite))
        
        with col5:
            probabilite = calculer_probabilite_reussite(projet)
            st.metric("🎯 Probabilité", f"{probabilite:.0f}%")
        
        # Barre de progression
        st.progress(progress / 100)
        
        # Informations supplémentaires
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"📅 **Échéance:** {projet['echeance'].strftime('%d/%m/%Y')}")
            jours_restants = (projet['echeance'] - date.today()).days
            st.write(f"⏰ **Jours restants:** {jours_restants}")
        
        with col2:
            st.write(f"📊 **ROI attendu:** {projet['roi_attendu']}%")
            st.write(f"💵 **Cash Flow/Mois:** {format_currency(projet['cash_flow_mensuel'])}")
        
        with col3:
            st.write(f"🔴 **Priorité:** {safe_get(projet, 'priorite', 'Moyenne')}")
            source_financement = safe_get(projet, 'source_financement', 'Non défini')
            st.write(f"🏦 **Financement:** {source_financement}")
        
        # Description
        st.write(f"**Description:** {projet['description']}")
        
        # Allocations reçues
        if projet.get('allocations_recues'):
            with st.expander(f"💰 Allocations reçues ({len(projet['allocations_recues'])})"):
                for alloc in projet['allocations_recues']:
                    st.write(f"• **{alloc['revenu_nom']}** - {format_currency(alloc['montant'])} - {alloc['mois']}")
        
        # Actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Modifier", key=f"edit_{projet['id']}"):
                st.session_state.edit_project_id = projet['id']
                st.rerun()
        
        with col2:
            if st.button("🗑️ Supprimer", key=f"delete_{projet['id']}"):
                if st.session_state.get(f"confirm_delete_{projet['id']}", False):
                    st.session_state.projets = [p for p in st.session_state.projets if p['id'] != projet['id']]
                    st.success(f"Projet '{projet['nom']}' supprimé.")
                    if f"confirm_delete_{projet['id']}" in st.session_state:
                        del st.session_state[f"confirm_delete_{projet['id']}"]
                    st.rerun()
                else:
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
            show_project_tracking_enhanced(projet)
        
        # Affichage conditionnel des conseils
        if st.session_state.get('show_advice_id') == projet['id']:
            show_project_advice_inline(projet)
        
        st.markdown("---")

def show_project_tracking_enhanced(projet):
    """Affiche le suivi mensuel amélioré d'un projet"""
    with st.expander(f"📊 Suivi Mensuel: {projet['nom']}", expanded=True):
        if projet.get('suivi_mensuel'):
            df_suivi = pd.DataFrame(projet['suivi_mensuel'])
            df_suivi['écart'] = df_suivi['reel'] - df_suivi['prevu']
            df_suivi['% écart'] = (df_suivi['écart'] / df_suivi['prevu'] * 100).round(1)
            
            st.dataframe(df_suivi, use_container_width=True)
            
            # Graphique évolution
            fig = px.bar(
                df_suivi,
                x='mois',
                y=['prevu', 'reel'],
                title="Prévisionnel vs Réel",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun suivi mensuel enregistré.")
        
        # Ajouter une entrée de suivi
        st.subheader("➕ Ajouter un Suivi")
        with st.form(f"suivi_form_{projet['id']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                mois_suivi = st.text_input("Mois (YYYY-MM)", value=datetime.now().strftime('%Y-%m'))
            
            with col2:
                montant_prevu = st.number_input("Montant Prévu (FCFA)", min_value=0, step=10000, value=projet['budget_alloue_mensuel'])
            
            with col3:
                montant_reel = st.number_input("Montant Réel (FCFA)", min_value=0, step=10000)
            
            if st.form_submit_button("💾 Ajouter Suivi"):
                # Trouver le projet et ajouter le suivi
                for i, p in enumerate(st.session_state.projets):
                    if p['id'] == projet['id']:
                        if 'suivi_mensuel' not in st.session_state.projets[i]:
                            st.session_state.projets[i]['suivi_mensuel'] = []
                        
                        # Vérifier si le suivi existe déjà pour ce mois
                        existing_suivi = [s for s in st.session_state.projets[i]['suivi_mensuel'] if s['mois'] == mois_suivi]
                        
                        if existing_suivi:
                            # Mettre à jour
                            for s in st.session_state.projets[i]['suivi_mensuel']:
                                if s['mois'] == mois_suivi:
                                    s['prevu'] = montant_prevu
                                    s['reel'] = montant_reel
                        else:
                            # Ajouter nouveau
                            st.session_state.projets[i]['suivi_mensuel'].append({
                                'mois': mois_suivi,
                                'prevu': montant_prevu,
                                'reel': montant_reel
                            })
                        
                        # Mettre à jour le montant utilisé réel et date modification
                        total_reel = sum(s['reel'] for s in st.session_state.projets[i]['suivi_mensuel'])
                        st.session_state.projets[i]['montant_utilise_reel'] = total_reel
                        st.session_state.projets[i]['date_modification'] = datetime.now()
                        
                        st.success(f"Suivi ajouté pour {mois_suivi}!")
                        st.rerun()
        
        # Bouton fermer
        if st.button("❌ Fermer Suivi", key=f"close_suivi_{projet['id']}"):
            if 'show_suivi_id' in st.session_state:
                del st.session_state.show_suivi_id
            st.rerun()

def show_project_advice_inline(projet):
    """Affiche les conseils des 3 mentors inline"""
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

def show_projets_kanban():
    """Vue Kanban des projets avec catégorisation avancée"""
    st.subheader("📋 Vue Kanban - Gestion Visuelle")
    
    # Catégorisation des projets
    categories = {
        'en-retard': {'projets': [], 'titre': '🔴 En Retard', 'couleur': '#ff4444'},
        'a-risque': {'projets': [], 'titre': '🟡 À Risque', 'couleur': '#ff8800'},
        'en-cours': {'projets': [], 'titre': '🔵 En Cours', 'couleur': '#007bff'},
        'en-avance': {'projets': [], 'titre': '🟢 En Avance', 'couleur': '#00aa00'},
        'bloque': {'projets': [], 'titre': '⚫ Bloqué', 'couleur': '#666666'}
    }
    
    # Répartition des projets
    for projet in st.session_state.projets:
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
                    show_kanban_card_compact(projet, cat_data['couleur'])
            else:
                st.info("Aucun projet")

def show_kanban_card_compact(projet, couleur):
    """Affiche une carte Kanban compacte"""
    progression = (projet['montant_utilise_reel'] / projet['montant_total']) * 100 if projet['montant_total'] > 0 else 0
    
    with st.container():
        st.markdown(f"**{projet['nom']}**")
        st.markdown(f"💰 {format_currency(projet['montant_total'])}")
        st.markdown(f"👤 {safe_get(projet, 'responsable', 'Non défini')}")
        
        # Barre de progression
        st.progress(progression / 100)
        st.markdown(f"📊 {progression:.1f}%")
        
        # Actions compactes
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️", key=f"kanban_edit_{projet['id']}", help="Modifier"):
                st.session_state.edit_project_id = projet['id']
                st.rerun()
        
        with col2:
            if st.button("📊", key=f"kanban_details_{projet['id']}", help="Détails"):
                st.session_state.show_details_id = projet['id']
        
        st.markdown("---")

def show_revenus_avec_allocation():
    """Gestion des revenus avec allocation dynamique"""
    st.subheader("💰 Revenus Variables avec Allocation")
    
    # Actions principales
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Ajouter Revenu", type="primary"):
            st.session_state.show_add_revenue_form = True
    
    # Affichage des revenus avec allocations
    if st.session_state.revenus_variables:
        for revenu in st.session_state.revenus_variables:
            show_revenue_card_with_allocation(revenu)
        
        # Total
        total_revenus = sum(r['montant_mensuel'] for r in st.session_state.revenus_variables)
        st.markdown(f"### **Total Revenus: {format_currency(total_revenus)}**")
    else:
        st.info("Aucun revenu variable enregistré.")
    
    # Formulaire d'ajout
    if st.session_state.get('show_add_revenue_form'):
        show_add_revenue_form_with_allocation()

def show_revenue_card_with_allocation(revenu):
    """Affiche une carte de revenu avec ses allocations"""
    with st.container():
        # En-tête revenu
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**💰 {revenu['nom']}**")
            st.caption(f"👤 {safe_get(revenu, 'responsable', 'Non défini')}")
        
        with col2:
            st.write(revenu['type'])
        
        with col3:
            st.write(format_currency(revenu['montant_mensuel']))
        
        with col4:
            st.write("🔄 Régulier" if revenu['regulier'] else "📊 Variable")
        
        with col5:
            col_edit, col_delete = st.columns(2)
            
            with col_edit:
                if st.button("✏️", key=f"edit_rev_{revenu['id']}"):
                    st.session_state.edit_revenue_id = revenu['id']
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️", key=f"del_rev_{revenu['id']}"):
                    if st.session_state.get(f"confirm_delete_rev_{revenu['id']}", False):
                        st.session_state.revenus_variables = [r for r in st.session_state.revenus_variables if r['id'] != revenu['id']]
                        st.success(f"Revenu '{revenu['nom']}' supprimé.")
                        if f"confirm_delete_rev_{revenu['id']}" in st.session_state:
                            del st.session_state[f"confirm_delete_rev_{revenu['id']}"]
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_rev_{revenu['id']}"] = True
                        st.warning("Cliquez à nouveau pour confirmer.")
        
        # Allocations actuelles
        if revenu.get('allocations'):
            total_alloue = sum(alloc['montant'] for alloc in revenu['allocations'])
            non_alloue = revenu['montant_mensuel'] - total_alloue
            
            st.markdown("**🔄 Allocations:**")
            for allocation in revenu['allocations']:
                projet = next((p for p in st.session_state.projets if p['id'] == allocation['projet_id']), None)
                projet_nom = projet['nom'] if projet else "Projet supprimé"
                st.write(f"• **{projet_nom}** - {format_currency(allocation['montant'])} ({allocation['mois']})")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Alloué", format_currency(total_alloue))
            with col2:
                st.metric("Disponible", format_currency(non_alloue))
        else:
            st.info("Aucune allocation définie")
        
        # Bouton pour gérer les allocations
        if st.button(f"🔄 Gérer Allocations", key=f"alloc_{revenu['id']}"):
            st.session_state.manage_allocation_id = revenu['id']
            st.rerun()
        
        # Modal de gestion des allocations
        if st.session_state.get('manage_allocation_id') == revenu['id']:
            show_allocation_management_modal(revenu)
        
        st.markdown("---")

def show_allocation_management_modal(revenu):
    """Modal de gestion des allocations d'un revenu"""
    with st.expander(f"🔄 Allocation: {revenu['nom']}", expanded=True):
        st.markdown(f"**Montant disponible:** {format_currency(revenu['montant_mensuel'])}")
        
        # Allocations existantes
        current_allocations = revenu.get('allocations', [])
        total_alloue = sum(alloc['montant'] for alloc in current_allocations)
        restant = revenu['montant_mensuel'] - total_alloue
        
        if current_allocations:
            st.markdown("**Allocations actuelles:**")
            for i, allocation in enumerate(current_allocations):
                projet = next((p for p in st.session_state.projets if p['id'] == allocation['projet_id']), None)
                projet_nom = projet['nom'] if projet else "Projet supprimé"
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(projet_nom)
                with col2:
                    st.write(format_currency(allocation['montant']))
                with col3:
                    st.write(allocation['mois'])
                with col4:
                    if st.button("🗑️", key=f"del_alloc_{revenu['id']}_{i}"):
                        current_allocations.pop(i)
                        revenu['allocations'] = current_allocations
                        st.rerun()
        
        st.markdown(f"**Montant restant:** {format_currency(restant)}")
        
        # Formulaire nouvelle allocation
        if restant > 0:
            st.markdown("**➕ Nouvelle Allocation:**")
            with st.form(f"allocation_form_{revenu['id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    projets_options = [(p['id'], p['nom']) for p in st.session_state.projets]
                    if projets_options:
                        selected_projet = st.selectbox(
                            "Projet",
                            options=[p[0] for p in projets_options],
                            format_func=lambda x: next(p[1] for p in projets_options if p[0] == x)
                        )
                    else:
                        st.warning("Aucun projet disponible")
                        selected_projet = None
                
                with col2:
                    montant_allocation = st.number_input(
                        "Montant (FCFA)",
                        min_value=0,
                        max_value=restant,
                        step=10000,
                        value=min(50000, restant)
                    )
                
                with col3:
                    mois_allocation = st.text_input("Mois (YYYY-MM)", value=datetime.now().strftime('%Y-%m'))
                
                if st.form_submit_button("➕ Ajouter Allocation") and selected_projet:
                    # Ajouter la nouvelle allocation
                    nouvelle_allocation = {
                        'projet_id': selected_projet,
                        'montant': montant_allocation,
                        'mois': mois_allocation
                    }
                    
                    if 'allocations' not in revenu:
                        revenu['allocations'] = []
                    revenu['allocations'].append(nouvelle_allocation)
                    
                    # Appeler la fonction d'allocation
                    success, message = allouer_revenu_aux_projets(revenu['id'], revenu['allocations'])
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                    
                    st.rerun()
        
        # Bouton fermer
        if st.button("❌ Fermer", key=f"close_alloc_{revenu['id']}"):
            if 'manage_allocation_id' in st.session_state:
                del st.session_state.manage_allocation_id
            st.rerun()

def show_allocations_dashboard():
    """Dashboard des allocations globales"""
    st.subheader("🔄 Dashboard des Allocations")
    
    # Statistiques globales
    total_revenus = sum(r['montant_mensuel'] for r in st.session_state.revenus_variables)
    total_alloue = 0
    
    for revenu in st.session_state.revenus_variables:
        if revenu.get('allocations'):
            total_alloue += sum(alloc['montant'] for alloc in revenu['allocations'])
    
    total_non_alloue = total_revenus - total_alloue
    pourcentage_alloue = (total_alloue / total_revenus * 100) if total_revenus > 0 else 0
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Revenus", format_currency(total_revenus))
    
    with col2:
        st.metric("🔄 Total Alloué", format_currency(total_alloue))
    
    with col3:
        st.metric("💸 Non Alloué", format_currency(total_non_alloue))
    
    with col4:
        st.metric("📊 % Alloué", f"{pourcentage_alloue:.1f}%")
    
    # Graphique répartition
    if total_alloue > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique par revenu
            revenus_data = []
            for revenu in st.session_state.revenus_variables:
                if revenu.get('allocations'):
                    alloue_revenu = sum(alloc['montant'] for alloc in revenu['allocations'])
                    revenus_data.append({
                        'Revenu': revenu['nom'],
                        'Alloué': alloue_revenu,
                        'Non Alloué': revenu['montant_mensuel'] - alloue_revenu
                    })
            
            if revenus_data:
                df_revenus = pd.DataFrame(revenus_data)
                fig = px.bar(
                    df_revenus,
                    x='Revenu',
                    y=['Alloué', 'Non Alloué'],
                    title="Allocation par Revenu",
                    barmode='stack'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Graphique par projet
            projets_allocations = {}
            for revenu in st.session_state.revenus_variables:
                if revenu.get('allocations'):
                    for alloc in revenu['allocations']:
                        projet = next((p for p in st.session_state.projets if p['id'] == alloc['projet_id']), None)
                        if projet:
                            if projet['nom'] not in projets_allocations:
                                projets_allocations[projet['nom']] = 0
                            projets_allocations[projet['nom']] += alloc['montant']
            
            if projets_allocations:
                fig = px.pie(
                    values=list(projets_allocations.values()),
                    names=list(projets_allocations.keys()),
                    title="Allocation par Projet"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Table détaillée des allocations
    st.subheader("📋 Détail des Allocations")
    
    allocations_detail = []
    for revenu in st.session_state.revenus_variables:
        if revenu.get('allocations'):
            for alloc in revenu['allocations']:
                projet = next((p for p in st.session_state.projets if p['id'] == alloc['projet_id']), None)
                allocations_detail.append({
                    'Revenu': revenu['nom'],
                    'Projet': projet['nom'] if projet else 'Projet supprimé',
                    'Montant': format_currency(alloc['montant']),
                    'Mois': alloc['mois'],
                    'Type Projet': projet['type'] if projet else 'N/A'
                })
    
    if allocations_detail:
        df_allocations = pd.DataFrame(allocations_detail)
        st.dataframe(df_allocations, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune allocation définie.")

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

def show_add_project_form_complete():
    """Formulaire d'ajout de projet complet"""
    with st.expander("➕ Nouveau Projet Complet", expanded=True):
        with st.form("add_project_complete_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom du projet*", placeholder="ex: Groupe électrogène meublés")
                type_projet = st.selectbox(
                    "Type selon Kiyosaki*",
                    st.session_state.admin_config['listes_config']['types_projet'],
                    help="Actif = génère revenus, Passif = coûte de l'argent, Formation = capital humain"
                )
                montant_total = st.number_input("Budget total nécessaire (FCFA)*", min_value=0, step=10000)
                roi_attendu = st.number_input("ROI attendu (%)", min_value=0.0, max_value=100.0, step=0.1)
                priorite = st.selectbox("Priorité", st.session_state.admin_config['listes_config']['priorites'])
                responsable = st.selectbox("Responsable*", st.session_state.admin_config['listes_config']['responsables'])
            
            with col2:
                statut = st.selectbox("Statut", st.session_state.admin_config['listes_config']['statuts_projet'])
                echeance = st.date_input("Échéance prévue", min_value=date.today())
                budget_mensuel = st.number_input("Budget alloué/mois (FCFA)", min_value=0, step=10000)
                cash_flow_mensuel = st.number_input(
                    "Cash flow mensuel estimé (FCFA)",
                    help="Positif pour revenus, négatif pour dépenses",
                    step=10000
                )
                source_financement = st.selectbox(
                    "Source de financement",
                    ["Salaire William", "Revenus IIBA", "Épargne", "Crédit", "Autre"]
                )
            
            description = st.text_area("Description détaillée", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer Projet", type="primary"):
                    if nom and type_projet and montant_total > 0 and responsable:
                        new_id = max([p['id'] for p in st.session_state.projets]) + 1 if st.session_state.projets else 1
                        nouveau_projet = {
                            'id': new_id,
                            'nom': nom,
                            'type': type_projet,
                            'montant_total': montant_total,
                            'budget_alloue_mensuel': budget_mensuel or montant_total // 12,
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
                            'suivi_mensuel': [],
                            'allocations_recues': [],
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now(),
                            'created_by': 'William',  # Exemple à remplacer par utilisateur courant
                            'updated_by': 'William',
                        }
                        st.session_state.projets.append(nouveau_projet)
                        st.session_state.show_add_project_form = False
                        st.success(f"✅ Projet '{nom}' créé avec succès !")
                        st.rerun()
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs obligatoires.")
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_add_project_form = False
                    st.rerun()

def show_add_revenue_form_with_allocation():
    """Formulaire d'ajout de revenu avec allocation"""
    with st.expander("💰 Ajouter un Revenu Variable", expanded=True):
        with st.form("add_revenue_allocation_form"):
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
                    # À l'intérieur du formulaire de création de revenu
                    date_disponibilite = st.date_input("Date de mise à disposition", value=date.today())
                    if nom_revenu and montant_mensuel > 0 and responsable:
                        existing_ids = [r['id'] for r in st.session_state.revenus_variables]
                        new_id = max(existing_ids) + 1 if existing_ids else 1
                        # Lors de la création du revenu
                        nouveau_revenu = {
                            'id': new_id,
                            'nom': nom_revenu,
                            'montant_mensuel': montant_mensuel,
                            'type': type_revenu,
                            'regulier': regulier,
                            'responsable': responsable,
                            'date_creation': datetime.now(),
                            'date_modification': datetime.now(),
                            'date_disponibilite': date_disponibilite,
                            'allocations': []
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




# ============================================================================
# 3. ANALYTICS - BUSINESS INTELLIGENCE
# ============================================================================
def show_analytics():
    """Analytics et KPIs avancés"""
    st.title("📊 Analytics & Business Intelligence")
    
    kpis = calculer_kpis()
    
    # KPIs avancés
    st.markdown("### 📈 KPIs Avancés")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_investissement = sum(p['montant_total'] for p in st.session_state.projets)
        st.metric("💰 Total Investissement", format_currency(total_investissement))
    
    with col2:
        total_utilise = sum(p['montant_utilise_reel'] for p in st.session_state.projets)
        st.metric("💸 Utilisé Réel", format_currency(total_utilise))
    
    with col3:
        utilisation_pct = (total_utilise / total_investissement * 100) if total_investissement > 0 else 0
        st.metric("📊 Taux Utilisation", f"{utilisation_pct:.1f}%")
    
    with col4:
        velocite_moyenne = sum(calculer_velocite_projet(p) for p in st.session_state.projets) / len(st.session_state.projets) if st.session_state.projets else 0
        st.metric("⚡ Vélocité Moyenne", format_currency(velocite_moyenne))
    
    # Graphiques avancés
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Performance des Projets")
        if st.session_state.projets:
            df_projets = pd.DataFrame([
                {
                    'Nom': p['nom'],
                    'Type': p['type'],
                    'Responsable': safe_get(p, 'responsable', 'Non défini'),
                    'Budget Total': p['montant_total'],
                    'Utilisé': p['montant_utilise_reel'],
                    'Progression %': (p['montant_utilise_reel'] / p['montant_total'] * 100) if p['montant_total'] > 0 else 0,
                    'Cash Flow': p['cash_flow_mensuel'],
                    'ROI %': p['roi_attendu'],
                    'Vélocité': calculer_velocite_projet(p),
                    'Probabilité %': calculer_probabilite_reussite(p)
                }
                for p in st.session_state.projets
            ])
            
            fig = px.scatter(
                df_projets,
                x='Budget Total',
                y='Cash Flow',
                size='Progression %',
                color='Type',
                hover_name='Nom',
                hover_data=['Responsable', 'ROI %', 'Vélocité', 'Probabilité %'],
                title="Analyse Investissements vs Cash Flow",
                labels={'Budget Total': 'Budget Total (FCFA)', 'Cash Flow': 'Cash Flow Mensuel (FCFA)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Évolution Probabilités")
        if st.session_state.projets:
            probabilites_data = [
                {
                    'Projet': p['nom'],
                    'Probabilité': calculer_probabilite_reussite(p),
                    'Type': p['type']
                }
                for p in st.session_state.projets
            ]
            
            df_prob = pd.DataFrame(probabilites_data)
            fig = px.bar(
                df_prob,
                x='Projet',
                y='Probabilité',
                color='Type',
                title="Probabilité de Réussite par Projet",
                labels={'Probabilité': 'Probabilité (%)'}
            )
            fig.add_hline(y=50, line_dash="dash", annotation_text="Seuil Critique 50%")
            st.plotly_chart(fig, use_container_width=True)
    
    # Analyse par responsable
    st.subheader("📊 Analyse par Responsable")
    responsable_stats = {}
    for projet in st.session_state.projets:
        resp = safe_get(projet, 'responsable', 'Non défini')
        if resp not in responsable_stats:
            responsable_stats[resp] = {
                'projets': 0,
                'budget_total': 0,
                'cash_flow': 0,
                'velocite_moyenne': 0,
                'probabilite_moyenne': 0
            }
        
        responsable_stats[resp]['projets'] += 1
        responsable_stats[resp]['budget_total'] += projet['montant_total']
        responsable_stats[resp]['cash_flow'] += projet['cash_flow_mensuel']
        responsable_stats[resp]['velocite_moyenne'] += calculer_velocite_projet(projet)
        responsable_stats[resp]['probabilite_moyenne'] += calculer_probabilite_reussite(projet)
    
    # Calculer les moyennes
    for resp, stats in responsable_stats.items():
        if stats['projets'] > 0:
            stats['velocite_moyenne'] = stats['velocite_moyenne'] / stats['projets']
            stats['probabilite_moyenne'] = stats['probabilite_moyenne'] / stats['projets']
    
    if responsable_stats:
        df_resp = pd.DataFrame(responsable_stats).T
        df_resp.index.name = 'Responsable'
        
        # Formater les colonnes
        df_resp['budget_total'] = df_resp['budget_total'].apply(lambda x: format_currency(x))
        df_resp['cash_flow'] = df_resp['cash_flow'].apply(lambda x: format_currency(x))
        df_resp['velocite_moyenne'] = df_resp['velocite_moyenne'].apply(lambda x: format_currency(x))
        df_resp['probabilite_moyenne'] = df_resp['probabilite_moyenne'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(df_resp, use_container_width=True)
    
    # Table détaillée avec métriques avancées
    st.subheader("📋 Détail Complet par Projet")
    if st.session_state.projets:
        df_detail = pd.DataFrame([
            {
                'Nom': p['nom'],
                'Type': p['type'],
                'Budget Total': format_currency(p['montant_total']),
                'Utilisé': format_currency(p['montant_utilise_reel']),
                'Progression': f"{(p['montant_utilise_reel']/p['montant_total']*100):.1f}%" if p['montant_total'] > 0 else "0%",
                'Cash Flow/Mois': format_currency(p['cash_flow_mensuel']),
                'ROI Attendu': f"{p['roi_attendu']}%",
                'Vélocité': format_currency(calculer_velocite_projet(p)),
                'Probabilité': f"{calculer_probabilite_reussite(p):.0f}%",
                'Responsable': safe_get(p, 'responsable', 'Non défini'),
                'Statut': p['statut'],
                'Échéance': p['echeance'].strftime('%d/%m/%Y')
            }
            for p in st.session_state.projets
        ])
        
        total_budget = sum(p['montant_total'] for p in st.session_state.projets)
        total_utilise = sum(p['montant_utilise_reel'] for p in st.session_state.projets)
        total_cashflow = sum(p['cash_flow_mensuel'] for p in st.session_state.projets)
        total_roi = sum(p['roi_attendu'] for p in st.session_state.projets) / len(st.session_state.projets) if st.session_state.projets else 0
        total_progression = (total_utilise / total_budget * 100) if total_budget > 0 else 0

        total_row = {
            'Nom': 'TOTAL',
            'Type': '',
            'Budget Total': format_currency(total_budget),
            'Utilisé': format_currency(total_utilise),
            'Progression': f"{total_progression:.1f}%",
            'Cash Flow/Mois': format_currency(total_cashflow),
            'ROI Attendu': f"{total_roi:.1f}%",
            'Vélocité': '',
            'Probabilité': '',
            'Responsable': '',
            'Statut': '',
            'Échéance': ''
        }
        
        df_detail = df_detail.append(total_row, ignore_index=True)
        st.dataframe(df_detail, use_container_width=True, hide_index=True)
    
    # Recommandations automatiques
    st.subheader("🎯 Recommandations Automatiques")
    
    recommendations = []
    
    # Analyser chaque projet
    for projet in st.session_state.projets:
        probabilite = calculer_probabilite_reussite(projet)
        velocite = calculer_velocite_projet(projet)
        progression = (projet['montant_utilise_reel'] / projet['montant_total'] * 100) if projet['montant_total'] > 0 else 0
        
        if probabilite < 30:
            recommendations.append(f"🔴 **{projet['nom']}** - Probabilité critique ({probabilite:.0f}%). Revoir la stratégie.")
        
        if velocite < projet['budget_alloue_mensuel'] * 0.3:
            recommendations.append(f"🟡 **{projet['nom']}** - Vélocité faible. Augmenter les allocations.")
        
        if progression > 90 and projet['statut'] != 'Réalisé':
            recommendations.append(f"🟢 **{projet['nom']}** - Projet quasi terminé. Planifier la finalisation.")
        
        if (projet['echeance'] - date.today()).days < 30 and progression < 70:
            recommendations.append(f"⚠️ **{projet['nom']}** - Échéance proche avec progression insuffisante.")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("✅ Tous les projets sont dans les paramètres normaux !")

# ============================================================================
# 4. VISION & OBJECTIFS - PLANIFICATION STRATÉGIQUE
# ============================================================================
def show_vision_objectifs():
    """Vision 2030 + Progression + Baby Steps"""
    st.title("🎯 Vision & Objectifs Strategiques")
    
    # Tabs pour organiser le contenu
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 Vision 2030", "👶 Baby Steps", "🚀 Progression", "🎯 Objectifs"])
    
    with tab1:
        show_vision_2030_consolidated()
    
    with tab2:
        show_baby_steps_progression()
    
    with tab3:
        show_progression_familiale()
    
    with tab4:
        show_objectifs_smart()

def show_vision_2030_consolidated():
    """Vision 2030 consolidée"""
    st.subheader("🔮 Vision Familiale 2030")
    st.markdown("**Objectif:** Toute la famille en Suisse avec indépendance financière")
    
    # Progression vers 2030
    target_date = date(2030, 1, 1)
    current_date = date.today()
    jours_restants = (target_date - current_date).days
    mois_restants = jours_restants // 30
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏰ Temps Restant", f"{mois_restants} mois", delta=f"{jours_restants} jours")
    
    with col2:
        progression_generale = ((2025 - 2024) / (2030 - 2024)) * 100  # Approximation
        st.metric("📈 Progression", f"{progression_generale:.1f}%")
    
    with col3:
        kpis = calculer_kpis()
        if kpis['revenus_passifs_pct'] >= 30:
            phase_2030 = "Prêt"
        elif kpis['revenus_passifs_pct'] >= 15:
            phase_2030 = "En route"
        else:
            phase_2030 = "Préparation"
        st.metric("🎯 Phase 2030", phase_2030)
    
    # Roadmap vers 2030
    st.markdown("### 📅 Roadmap Stratégique")
    
    milestones = [
        {'annee': 2025, 'titre': 'Stabilisation', 'description': 'Finaliser actifs Cameroun + cash flow positif'},
        {'annee': 2026, 'titre': 'Transition', 'description': 'Développement revenus passifs 15%+'},
        {'annee': 2027, 'titre': 'Expansion', 'description': 'Multiplication actifs générateurs'},
        {'annee': 2028, 'titre': 'Préparation', 'description': 'Déménagement famille - visa/scolarité'},
        {'annee': 2029, 'titre': 'Installation', 'description': 'Installation progressive en Suisse'},
        {'annee': 2030, 'titre': 'Indépendance', 'description': 'Indépendance financière complète'}
    ]
    
    for milestone in milestones:
        annee = milestone['annee']
        progress = max(0, min(100, ((annee - 2024) / 6) * 100))
        
        if annee <= current_date.year:
            st.success(f"✅ **{annee} - {milestone['titre']}:** {milestone['description']}")
        elif annee == current_date.year + 1:
            st.warning(f"🎯 **{annee} - PROCHAINE ÉTAPE:** {milestone['titre']} - {milestone['description']}")
        else:
            st.info(f"⏳ **{annee} - FUTUR:** {milestone['titre']} - {milestone['description']}")
        
        st.progress(progress / 100)
    
    # Calculs financiers pour la Suisse
    st.markdown("### 💰 Exigences Financières Suisse")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Situation Actuelle")
        kpis = calculer_kpis()
        st.metric("Cash Flow Mensuel", format_currency(kpis['cash_flow_mensuel']))
        st.metric("Revenus Passifs", f"{kpis['revenus_passifs_pct']:.1f}%")
        st.metric("Actifs Générateurs", f"{kpis['nombre_actifs']} projets")
    
    with col2:
        st.markdown("#### 🎯 Objectifs 2030 Suisse")
        # Calculs réalistes pour la Suisse
        cout_enfants_2030_chf = 280000  # CHF par an pour 3 enfants
        cout_famille_2030_chf = 150000  # CHF logement + vie
        cout_total_chf = cout_enfants_2030_chf + cout_famille_2030_chf
        cout_total_fcfa = cout_total_chf * 665  # Taux approximatif CHF/FCFA
        
        st.metric("Coût Total Suisse", f"{cout_total_chf:,} CHF/an")
        st.metric("Équivalent FCFA", f"{cout_total_fcfa:,.0f} FCFA/an")
        
        revenus_passifs_requis = cout_total_fcfa * 1.3  # Marge sécurité 30%
        revenus_passifs_mensuels = revenus_passifs_requis / 12
        st.metric("Revenus Passifs Requis", f"{revenus_passifs_mensuels:,.0f} FCFA/mois")

def show_baby_steps_progression():
    """Baby Steps Dave Ramsey avec progression"""
    st.subheader("👶 Baby Steps Dave Ramsey")
    
    baby_steps = [
        ("Fonds d'urgence starter 665k FCFA", 1, "💰", "Urgence immédiate pour petites crises"),
        ("Éliminer toutes dettes (sauf immobilier)", 2, "🚫", "Méthode boule de neige"),
        ("Fonds d'urgence complet 3-6 mois", 3, "🏦", "Sécurité financière totale"),
        ("Investir 15% revenus pour retraite", 4, "📈", "Croissance long terme"),
        ("Épargne université enfants", 5, "🎓", "Éducation des 3 enfants"),
        ("Rembourser hypothèque anticipé", 6, "🏠", "Liberté immobilière"),
        ("Construire richesse et donner", 7, "💎", "Indépendance et générosité")
    ]
    
    kpis = calculer_kpis()
    current_step = kpis['baby_step_actuel']
    
    for step_desc, step_num, emoji, detail in baby_steps:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            if step_num < current_step:
                st.success(f"✅ {emoji}")
            elif step_num == current_step:
                st.warning(f"🔄 {emoji}")
            else:
                st.info(f"⏳ {emoji}")
        
        with col2:
            st.markdown(f"**Étape {step_num}:** {step_desc}")
            st.caption(detail)
        
        with col3:
            # Calcul progression pour cette étape
            if step_num == 1:  # Fonds urgence starter
                progression = min(100, (kpis.get('fonds_urgence_mois', 0) / 1) * 100)
            elif step_num == 3:  # Fonds urgence complet
                progression = min(100, (kpis.get('fonds_urgence_mois', 0) / 6) * 100)
            elif step_num == 4:  # Investissement 15%
                progression = min(100, (kpis['revenus_passifs_pct'] / 15) * 100)
            else:
                progression = 0 if step_num > current_step else 100
            
            st.progress(progression / 100)
            st.caption(f"{progression:.0f}%")
    
    # Actions pour l'étape actuelle
    st.markdown(f"### 🎯 Actions pour l'Étape {current_step}")
    
    if current_step == 1:
        st.markdown("""
        **Objectif:** Constituer 665 000 FCFA d'urgence
        - Ouvrir un compte épargne dédié
        - Économiser 100 000 FCFA/mois pendant 6-7 mois
        - Utiliser uniquement pour de vraies urgences
        """)
    elif current_step == 2:
        st.markdown("""
        **Objectif:** Éliminer toutes les dettes
        - Lister toutes les dettes par ordre croissant
        - Payer les minimums partout
        - Concentrer l'excédent sur la plus petite dette
        """)
    elif current_step == 3:
        st.markdown("""
        **Objectif:** 3-6 mois d'épargne d'urgence
        - Calculer les dépenses mensuelles réelles
        - Viser 6 mois de dépenses en épargne
        - Placer dans un compte facilement accessible
        """)

def show_progression_familiale():
    """Progression familiale vers l'indépendance"""
    st.subheader("🚀 Progression Familiale")
    
    # Simulation progression sur 24 mois
    kpis = calculer_kpis()
    current_step = kpis['baby_step_actuel']
    
    mois_futurs = pd.date_range(start=date.today(), periods=24, freq='MS')
    progression_simulation = []
    
    for i, mois in enumerate(mois_futurs):
        # Simulation d'une progression graduelle
        progression_simulation.append({
            'Mois': mois,
            'Revenus Passifs %': min(kpis['revenus_passifs_pct'] + (i * 1.2), 50),
            'Cash Flow': kpis['cash_flow_mensuel'] + (i * 120000),
            'Baby Step': min(current_step + (i // 6), 7),
            'Total Actifs': kpis['total_actifs'] + (i * 500000)
        })
    
    df_progression = pd.DataFrame(progression_simulation)
    
    # Graphiques de progression
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            df_progression,
            x='Mois',
            y='Revenus Passifs %',
            title="Projection Revenus Passifs"
        )
        fig.add_hline(
            y=st.session_state.admin_config['kpis_config']['objectif_revenus_passifs'],
            line_dash="dash",
            annotation_text=f"Objectif {st.session_state.admin_config['kpis_config']['objectif_revenus_passifs']}%"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            df_progression,
            x='Mois',
            y='Cash Flow',
            title="Projection Cash Flow"
        )
        fig.add_hline(y=0, line_dash="dash", annotation_text="Équilibre")
        fig.add_hline(
            y=st.session_state.admin_config['kpis_config']['objectif_cash_flow'],
            line_dash="dot",
            annotation_text="Objectif"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Évolution des Baby Steps
    fig = px.line(
        df_progression,
        x='Mois',
        y='Baby Step',
        title="Progression Baby Steps",
        range_y=[0, 8]
    )
    st.plotly_chart(fig, use_container_width=True)

def show_objectifs_smart():
    """Objectifs SMART configurables"""
    st.subheader("🎯 Objectifs SMART")
    
    # Configuration des objectifs
    if 'objectifs_smart' not in st.session_state:
        st.session_state.objectifs_smart = [
            {
                'id': 1,
                'nom': 'Cash Flow Positif',
                'description': 'Atteindre un cash flow mensuel positif et stable',
                'critere_mesure': 'Cash flow > 0 FCFA pendant 3 mois consécutifs',
                'date_limite': date(2025, 6, 30),
                'responsable': 'William',
                'statut': 'En cours',
                'progression': 60
            },
            {
                'id': 2,
                'nom': '20% Revenus Passifs',
                'description': 'Atteindre 20% de revenus passifs',
                'critere_mesure': 'Revenus passifs / Revenus totaux >= 20%',
                'date_limite': date(2025, 12, 31),
                'responsable': 'Alix',
                'statut': 'Planifié',
                'progression': 25
            },
            {
                'id': 3,
                'nom': 'Finaliser Titre Foncier',
                'description': 'Completion du projet titre foncier Mejeuh',
                'critere_mesure': '100% du budget utilisé et propriété acquise',
                'date_limite': date(2025, 6, 30),
                'responsable': 'Alix',
                'statut': 'En cours',
                'progression': 80
            }
        ]
    
    # Affichage des objectifs
    for objectif in st.session_state.objectifs_smart:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**🎯 {objectif['nom']}**")
                st.caption(objectif['description'])
                st.write(f"**Mesure:** {objectif['critere_mesure']}")
            
            with col2:
                jours_restants = (objectif['date_limite'] - date.today()).days
                st.metric("📅 Échéance", objectif['date_limite'].strftime('%d/%m/%Y'))
                st.metric("⏰ Jours restants", jours_restants)
            
            with col3:
                st.metric("👤 Responsable", objectif['responsable'])
                st.metric("📊 Progression", f"{objectif['progression']}%")
            
            # Barre de progression
            st.progress(objectif['progression'] / 100)
            
            # Statut
            if objectif['statut'] == 'En cours':
                st.info(f"🔄 En cours")
            elif objectif['statut'] == 'Réalisé':
                st.success(f"✅ Réalisé")
            else:
                st.warning(f"⏳ {objectif['statut']}")
            
            st.markdown("---")
    
    # Ajouter un nouvel objectif
    if st.button("➕ Nouvel Objectif SMART"):
        st.session_state.show_add_objectif_form = True
    
    if st.session_state.get('show_add_objectif_form'):
        show_add_objectif_smart_form()

def show_add_objectif_smart_form():
    """Formulaire d'ajout d'objectif SMART"""
    with st.expander("➕ Nouvel Objectif SMART", expanded=True):
        with st.form("add_objectif_smart"):
            nom = st.text_input("Nom de l'objectif*")
            description = st.text_area("Description détaillée")
            critere_mesure = st.text_input("Critère de mesure*")
            
            col1, col2 = st.columns(2)
            with col1:
                date_limite = st.date_input("Date limite", min_value=date.today())
                responsable = st.selectbox("Responsable", st.session_state.admin_config['listes_config']['responsables'])
            
            with col2:
                statut = st.selectbox("Statut initial", ["Planifié", "En cours", "Suspendu"])
                progression = st.slider("Progression initiale (%)", 0, 100, 0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer Objectif", type="primary"):
                    if nom and critere_mesure:
                        new_id = max([obj['id'] for obj in st.session_state.objectifs_smart]) + 1 if st.session_state.objectifs_smart else 1
                        nouvel_objectif = {
                            'id': new_id,
                            'nom': nom,
                            'description': description,
                            'critere_mesure': critere_mesure,
                            'date_limite': date_limite,
                            'responsable': responsable,
                            'statut': statut,
                            'progression': progression
                        }
                        st.session_state.objectifs_smart.append(nouvel_objectif)
                        st.session_state.show_add_objectif_form = False
                        st.success(f"Objectif '{nom}' créé !")
                        st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_add_objectif_form = False
                    st.rerun()

# ============================================================================
# 5. PARAMÈTRES - CONFIGURATION ET OUTILS
# ============================================================================
def show_parametres():
    """Configuration et administration"""
    st.title("⚙️ Paramètres & Administration")
    
    # Tabs pour organiser les paramètres
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 KPIs & Objectifs", 
        "📋 Listes & Vocabulaire", 
        "🧠 Conseils Mentors", 
        "📊 Export/Import", 
        "👨👩👧👦 Module Enfants"
    ])
    
    with tab1:
        show_admin_kpis()
    
    with tab2:
        show_admin_listes()
    
    with tab3:
        show_admin_mentors()
    
    with tab4:
        show_admin_export_import()
    
    with tab5:
        show_module_enfants()

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
            for type_p in types_actuels:
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
                # Création des données d'export
                export_data = {
                    'projets': st.session_state.projets,
                    'revenus_variables': st.session_state.revenus_variables,
                    'admin_config': st.session_state.admin_config,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Conversion en JSON pour téléchargement
                json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
                
                st.download_button(
                    label="💾 Télécharger Sauvegarde JSON",
                    data=json_data,
                    file_name=f"plan_financier_familial_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    type="primary"
                )
                
                st.success("✅ Export généré avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur lors de l'export: {str(e)}")
        
        # Statistiques export
        st.markdown("### 📈 Contenu de l'Export")
        st.write(f"• **{len(st.session_state.projets)}** projets")
        st.write(f"• **{len(st.session_state.revenus_variables)}** revenus")
        st.write("• **Configuration** complète")
        st.write("• **Allocations** dynamiques")
    
    with col2:
        st.markdown("### 📥 Importer des Données")
        
        uploaded_file = st.file_uploader(
            "Choisir un fichier JSON",
            type=['json'],
            help="Importer une sauvegarde précédente"
        )
        
        if uploaded_file:
            try:
                # Lecture du fichier
                import_data = json.loads(uploaded_file.read())
                
                st.json(import_data, expanded=False)
                
                if st.button("🔄 Confirmer Import", type="primary"):
                    # Backup actuel
                    backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    # Import des données
                    if 'projets' in import_data:
                        st.session_state.projets = import_data['projets']
                    if 'revenus_variables' in import_data:
                        st.session_state.revenus_variables = import_data['revenus_variables']
                    if 'admin_config' in import_data:
                        st.session_state.admin_config = import_data['admin_config']
                    
                    st.success("✅ Import réalisé avec succès!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de l'import: {str(e)}")

def show_module_enfants():
    """Module éducation enfants optionnel"""
    st.subheader("👨👩👧👦 Module Éducation Enfants")
    
    # Toggle pour activer/désactiver le module
    module_active = st.toggle(
        "Activer le module d'éducation financière des enfants",
        value=st.session_state.admin_config.get('education_module_active', False)
    )
    
    st.session_state.admin_config['education_module_active'] = module_active
    
    if module_active:
        st.success("✅ Module éducation enfants activé")
        
        # Adaptation des âges selon l'année
        annee_base = 2025
        current_year = datetime.now().year
        diff_annee = current_year - annee_base
        
        enfants = [
            {
                'nom': 'Uriel',
                'age': 14 + diff_annee,
                'emoji': '👦',
                'niveau': 'Adolescent - Concepts avancés',
                'objectifs_mois': [
                    'Analyser un projet familial',
                    'Créer son budget mensuel personnel',
                    'Comprendre les quadrants E-S-B-I'
                ],
                'activites': [
                    'Participation à la révision mensuelle des KPIs',
                    'Analyse d\'un investissement familial',
                    'Création d\'un mini-business plan'
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
                    'Aider à compter l\'argent'
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
                    st.markdown("### 🎯 Objectifs du Mois")
                    for objectif in enfant['objectifs_mois']:
                        st.write(f"• {objectif}")
                
                with col2:
                    st.markdown("### 🎮 Activités Recommandées")
                    for activite in enfant['activites']:
                        st.write(f"• {activite}")
                
                # Progression mensuelle
                current_month = datetime.now().month
                progress_value = min((current_month / 12) * 100, 100)
                st.progress(progress_value / 100)
                st.caption(f"Progression annuelle: {progress_value:.0f}%")
                
                st.markdown("---")
        
        # Planning familial mensuel
        st.subheader("👨👩👧👦 Planning Familial Mensuel")
        
        planning_mensuel = {
            1: "Nouvelle année financière - Objectifs famille",
            2: "Mois de l'épargne - Challenge tirelires",
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
        
        current_month = datetime.now().month
        activite_mois = planning_mensuel.get(current_month, "Développement continu")
        
        st.success(f"**🎯 Activité principale ce mois :** {activite_mois}")
        
    else:
        st.info("Module éducation enfants désactivé. Activez-le pour accéder aux fonctionnalités d'éducation financière.")

# ============================================================================
# FONCTION PRINCIPALE AVEC NAVIGATION OPTIMISÉE
# ============================================================================
def main():
    # Chargement CSS
    load_css()
    
    # Initialisation session state
    initialize_session_state()
    
    # Sidebar navigation optimisée
    selected_page = render_sidebar()
    
    # Routing optimisé vers 5 pages principales
    if selected_page == "🏠 Tableau de Bord":
        show_tableau_de_bord()
    elif selected_page == "💼 Projets & Revenus":
        show_projets_revenus()
    elif selected_page == "📊 Analytics":
        show_analytics()
    elif selected_page == "🎯 Vision & Objectifs":
        show_vision_objectifs()
    elif selected_page == "⚙️ Paramètres":
        show_parametres()

if __name__ == "__main__":
    main()
