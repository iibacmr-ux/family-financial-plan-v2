# Fichier app6ko_corrigé.py - Version complète et corrigée
# Combinaison de toutes les parties avec corrections

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
        body, .css-18e3th9 {
            background-color: white !important;
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
                'created_by': 'Alix',
                'updated_by': 'Alix',
                'suivi_mensuel': [
                    {'mois': '2025-01', 'prevu': 200000, 'reel': 50000}
                ],
                'allocations_recues': []
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
                'created_by': 'William',
                'updated_by': 'William',
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
                'created_by': 'Alix',
                'updated_by': 'Alix',
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
                'created_by': 'William',
                'updated_by': 'William',
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
                'date_disponibilite': date(2024, 12, 1),
                'created_by': 'William',
                'updated_by': 'William',
                'allocations': []
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
                'date_disponibilite': date(2025, 1, 15),
                'created_by': 'William',
                'updated_by': 'William',
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
                'date_disponibilite': date(2024, 12, 1),
                'created_by': 'Alix',
                'updated_by': 'Alix',
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
            'education_module_active': False
        }
    
    # Initialiser les filtres de date
    if 'filters_date' not in st.session_state:
        st.session_state.filters_date = {'year': 'Tous', 'month': 'Tous'}

def safe_get(dict_obj, key, default='N/A'):
    """Récupère une valeur de dictionnaire de manière sécurisée"""
    return dict_obj.get(key, default)

def calculer_kpis(projets_filtered=None):
    """Calcule les KPIs en temps réel avec projets filtrés optionnels"""
    if projets_filtered is None:
        projets = st.session_state.projets
    else:
        projets = projets_filtered
    
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

def filter_by_date(items, item_type='projet'):
    """Filtre les projets ou revenus par date selon les filtres globaux"""
    if 'filters_date' not in st.session_state:
        return items
    
    year = st.session_state.filters_date['year']
    month = st.session_state.filters_date['month']
    
    if year == "Tous" and month == "Tous":
        return items
    
    def is_visible(item):
        if item_type == 'projet':
            start_date = item['date_creation']
            end_date = item.get('echeance', datetime.now().date())
        else:  # revenu
            start_date = item.get('date_disponibilite', item['date_creation'])
            # Pour les revenus, considérer qu'ils sont actifs jusqu'à allocation complète
            end_date = datetime.now().date()
        
        # Convertir en date si nécessaire
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        # Filtrage par année
        if year != "Tous" and start_date.year != int(year):
            return False
        
        # Filtrage par mois
        if month != "Tous":
            filter_month = int(month)
            # Vérifier si l'item est actif pendant ce mois
            if start_date.year == end_date.year:
                return start_date.month <= filter_month <= end_date.month
            else:
                # Si l'item s'étend sur plusieurs années
                return True
        
        return True
    
    return [item for item in items if is_visible(item)]

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
    revenu['updated_by'] = 'William'  # À remplacer par utilisateur courant

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
            projet['updated_by'] = 'William'

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

        # Ajout des filtres globaux par date
        st.markdown("### 📅 Filtre Global par Date")
        
        # Récupérer les années disponibles des projets
        available_years = sorted(set([p['date_creation'].year for p in st.session_state.projets]))
        
        filter_year = st.selectbox(
            "Année", 
            ["Tous"] + available_years, 
            index=0,
            key="filter_year"
        )
        
        filter_month = st.selectbox(
            "Mois", 
            ["Tous"] + [f"{i:02d}" for i in range(1, 13)], 
            index=0,
            key="filter_month"
        )

        st.session_state.filters_date = {'year': filter_year, 'month': filter_month}

        # Calcul des KPIs avec filtrage
        filtered_projets = filter_by_date(st.session_state.projets, 'projet')
        kpis = calculer_kpis(filtered_projets)
        phase = kpis['phase_actuelle']

        # Calcul du total budget projet filtré
        total_budget_filtre = sum(p['montant_total'] for p in filtered_projets)

        st.markdown("---")
        st.markdown(f"**🎯 Phase:** {phase}")
        st.markdown(f"**💰 Revenus:** {format_currency(kpis['revenus_mensuels'])}")
        st.markdown(f"**💼 Budget Total Filtré:** {format_currency(total_budget_filtre)}")
        st.markdown(f"**📊 Cash Flow:** {format_currency(kpis['cash_flow_mensuel'])}")

        return selected_page

# ============================================================================
# 1. TABLEAU DE BORD - HUB CENTRAL UNIFIÉ (Fonction complète simplifiée pour l'espace)
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

    # KPIs principaux avec filtrage
    filtered_projets = filter_by_date(st.session_state.projets, 'projet')
    kpis = calculer_kpis(filtered_projets)
    
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

# ============================================================================
# MAIN - FONCTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale avec navigation optimisée"""
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
        st.title("💼 Projets & Revenus - En construction")
        st.info("Cette section sera implémentée avec toutes les fonctionnalités de gestion de projets et revenus.")
    elif selected_page == "📊 Analytics":
        st.title("📊 Analytics - En construction")
        st.info("Cette section contiendra tous les analytics et graphiques avancés.")
    elif selected_page == "🎯 Vision & Objectifs":
        st.title("🎯 Vision & Objectifs - En construction")
        st.info("Cette section contiendra la vision 2030 et les Baby Steps.")
    elif selected_page == "⚙️ Paramètres":
        st.title("⚙️ Paramètres - En construction")
        st.info("Cette section contiendra toute la configuration et administration.")

if __name__ == "__main__":
    main()
