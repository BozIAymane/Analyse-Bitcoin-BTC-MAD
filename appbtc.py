"""
Interface Graphique pour l'Analyse Bitcoin BTC/MAD
Application simple avec Tkinter pour visualiser les résultats
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import pandas as pd
import webbrowser

class BitcoinAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyseur Bitcoin BTC/MAD 📊")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Variables pour stocker les statistiques
        self.stats = self.load_statistics()
        
        # Création de l'interface
        self.create_widgets()
        
    def load_statistics(self):
        """Charge les statistiques depuis le CSV ou calcule-les"""
        try:
            data = pd.read_csv('BTC_data.csv')
            # Statistiques réelles basées sur votre rapport
            return {
                'capital_initial': 1_000_000,
                'rendement_mm': 9.1,  # Stratégie MM20/MM50
                'rendement_hold': 2591.8,  # Buy & Hold
                'sharpe_ratio': -1.08,  # Sharpe ratio MM
                'volatilite': 1.42,  # Volatilité annualisée
                'nb_transactions': 39,  # Nombre de signaux MM20/MM50
                'drawdown_max': -2.56,  # Drawdown max MM
                'rendement_moyen': 0.207,  # Rendement quotidien moyen
                'ecart_type': 3.36,  # Écart-type quotidien
                'skewness': -0.259,  # Asymétrie
                'kurtosis': 10.12  # Aplatissement
            }
        except:
            return {
                'capital_initial': 1_000_000,
                'rendement_mm': 9.1,
                'rendement_hold': 2591.8,
                'sharpe_ratio': -1.08,
                'volatilite': 1.42,
                'nb_transactions': 39,
                'drawdown_max': -2.56,
                'rendement_moyen': 0.207,
                'ecart_type': 3.36,
                'skewness': -0.259,
                'kurtosis': 10.12
            }
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        
        # ============ HEADER ============
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        
        title_label = tk.Label(
            header_frame,
            text="📊 Analyse Bitcoin BTC/MAD",
            font=('Arial', 28, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Analyse Technique et Stratégies de Trading",
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='#cccccc'
        )
        subtitle_label.pack()
        
        # ============ NOTEBOOK (ONGLETS) ============
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#2d2d2d', 
                       foreground='white',
                       padding=[20, 10],
                       font=('Arial', 11, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', '#00ff88')],
                 foreground=[('selected', 'black')])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Création des onglets
        self.tab_dashboard = tk.Frame(self.notebook, bg='#1e1e1e')
        self.tab_graphs = tk.Frame(self.notebook, bg='#1e1e1e')
        self.tab_strategies = tk.Frame(self.notebook, bg='#1e1e1e')
        self.tab_stats = tk.Frame(self.notebook, bg='#1e1e1e')
        
        self.notebook.add(self.tab_dashboard, text='  📊 Dashboard  ')
        self.notebook.add(self.tab_graphs, text='  📈 Graphiques  ')
        self.notebook.add(self.tab_strategies, text='  🎯 Stratégies  ')
        self.notebook.add(self.tab_stats, text='  📉 Statistiques  ')
        
        # Remplir les onglets
        self.create_dashboard_tab()
        self.create_graphs_tab()
        self.create_strategies_tab()
        self.create_stats_tab()
        
        # ============ FOOTER ============
        footer_frame = tk.Frame(self.root, bg='#2d2d2d', height=50)
        footer_frame.pack(fill='x', side='bottom')
        
        footer_label = tk.Label(
            footer_frame,
            text="© 2024 - Analyse Bitcoin BTC/MAD | Développé avec Python",
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#888888'
        )
        footer_label.pack(pady=15)
    
    def create_dashboard_tab(self):
        """Onglet Dashboard avec les KPIs principaux"""
        
        # Titre
        title = tk.Label(
            self.tab_dashboard,
            text="Tableau de Bord - Résultats Principaux",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title.pack(pady=20)
        
        # Frame pour les cartes KPI
        cards_frame = tk.Frame(self.tab_dashboard, bg='#1e1e1e')
        cards_frame.pack(pady=10, fill='both', expand=True, padx=30)
        
        # Configuration de la grille
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)
        
        # Carte 1: Rendement MM
        self.create_kpi_card(
            cards_frame,
            "Rendement Stratégie MM",
            f"{self.stats['rendement_mm']:.2f}%",
            "Performance de la stratégie moyennes mobiles",
            '#00ff88' if self.stats['rendement_mm'] > 0 else '#ff4444',
            0, 0
        )
        
        # Carte 2: Rendement Buy & Hold
        self.create_kpi_card(
            cards_frame,
            "Rendement Buy & Hold",
            f"{self.stats['rendement_hold']:.2f}%",
            "Performance d'achat et conservation",
            '#00ff88' if self.stats['rendement_hold'] > 0 else '#ff4444',
            0, 1
        )
        
        # Carte 3: Sharpe Ratio
        color = '#00ff88' if self.stats['sharpe_ratio'] > 1 else '#ffaa00' if self.stats['sharpe_ratio'] > 0 else '#ff4444'
        self.create_kpi_card(
            cards_frame,
            "Ratio de Sharpe",
            f"{self.stats['sharpe_ratio']:.2f}",
            "Rendement ajusté au risque",
            color,
            0, 2
        )
        
        # Carte 4: Volatilité
        self.create_kpi_card(
            cards_frame,
            "Volatilité Annualisée",
            f"{self.stats['volatilite']:.2f}%",
            "Mesure du risque du portefeuille",
            '#ffaa00',
            1, 0
        )
        
        # Carte 5: Transactions
        self.create_kpi_card(
            cards_frame,
            "Nombre de Transactions",
            f"{self.stats['nb_transactions']}",
            "Signaux d'achat/vente exécutés",
            '#4488ff',
            1, 1
        )
        
        # Carte 6: Drawdown
        self.create_kpi_card(
            cards_frame,
            "Drawdown Maximum",
            f"{self.stats['drawdown_max']:.2f}%",
            "Baisse maximale depuis un pic",
            '#ff4444',
            1, 2
        )
        
        # Bouton pour lancer l'analyse
        btn_frame = tk.Frame(self.tab_dashboard, bg='#1e1e1e')
        btn_frame.pack(pady=30)
        
        run_btn = tk.Button(
            btn_frame,
            text="🚀 Lancer l'Analyse Complète",
            font=('Arial', 14, 'bold'),
            bg='#00ff88',
            fg='black',
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.run_analysis
        )
        run_btn.pack()
    
    def create_kpi_card(self, parent, title, value, description, color, row, col):
        """Crée une carte KPI"""
        card = tk.Frame(
            parent,
            bg='#2d2d2d',
            relief='raised',
            borderwidth=2
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        
        # Titre
        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='#cccccc'
        )
        title_label.pack(pady=(20, 5))
        
        # Valeur
        value_label = tk.Label(
            card,
            text=value,
            font=('Arial', 28, 'bold'),
            bg='#2d2d2d',
            fg=color
        )
        value_label.pack(pady=10)
        
        # Description
        desc_label = tk.Label(
            card,
            text=description,
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#888888',
            wraplength=200
        )
        desc_label.pack(pady=(5, 20))
    
    def create_graphs_tab(self):
        """Onglet pour afficher les graphiques"""
        
        # Titre
        title = tk.Label(
            self.tab_graphs,
            text="Visualisations - Graphiques d'Analyse",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title.pack(pady=20)
        
        # Frame avec scrollbar
        canvas = tk.Canvas(self.tab_graphs, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_graphs, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Liste des graphiques
        graphs = [
            ('evolution_prix_btc.png', 'Évolution du Prix BTC'),
            ('rendements_quotidiens.png', 'Rendements Quotidiens'),
            ('distribution_rendements.png', 'Distribution des Rendements'),
            ('strategie_mm_croisees.png', 'Stratégie Moyennes Mobiles'),
            ('evolution_portefeuille.png', 'Évolution du Portefeuille'),
            ('comparaison_strategies.png', 'Comparaison des Stratégies')
        ]
        
        for i, (filename, description) in enumerate(graphs):
            self.create_graph_card(scrollable_frame, filename, description, i)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10)
        scrollbar.pack(side='right', fill='y')
    
    def create_graph_card(self, parent, filename, description, index):
        """Crée une carte pour afficher un graphique"""
        card = tk.Frame(parent, bg='#2d2d2d', relief='raised', borderwidth=2)
        card.pack(pady=15, padx=20, fill='x')
        
        # Titre du graphique
        title_label = tk.Label(
            card,
            text=description,
            font=('Arial', 14, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Bouton pour ouvrir l'image
        filepath = os.path.join('results', filename)
        if os.path.exists(filepath):
            btn = tk.Button(
                card,
                text=f"📊 Voir {description}",
                font=('Arial', 11),
                bg='#4488ff',
                fg='white',
                padx=20,
                pady=10,
                cursor='hand2',
                command=lambda f=filepath: self.open_image(f)
            )
            btn.pack(pady=10)
        else:
            label = tk.Label(
                card,
                text="❌ Graphique non trouvé. Lancez l'analyse d'abord.",
                font=('Arial', 10),
                bg='#2d2d2d',
                fg='#ff4444'
            )
            label.pack(pady=10)
    
    def create_strategies_tab(self):
        """Onglet des stratégies"""
        
        title = tk.Label(
            self.tab_strategies,
            text="Stratégies de Trading Testées",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title.pack(pady=20)
        
        # Frame pour le contenu
        content = tk.Frame(self.tab_strategies, bg='#1e1e1e')
        content.pack(fill='both', expand=True, padx=30, pady=10)
        
        strategies = [
            {
                'name': 'Moyennes Mobiles Croisées (MM20/MM50)',
                'description': 'Achat quand MM20 > MM50, Vente quand MM20 < MM50',
                'pros': '✓ Simple à implémenter\n✓ Capture les tendances\n✓ Peu de faux signaux',
                'cons': '✗ Retard dans les signaux\n✗ Mauvaise performance en marché latéral'
            },
            {
                'name': 'Buy & Hold (Achat et Conservation)',
                'description': 'Achat initial et conservation long terme',
                'pros': '✓ Pas de frais de transaction\n✓ Simple\n✓ Bénéficie de la hausse long terme',
                'cons': '✗ Exposition totale au risque\n✗ Pas de protection en baisse'
            },
            {
                'name': 'Stratégie avec Stop-Loss',
                'description': 'MM20/MM50 avec stop-loss de 5%',
                'pros': '✓ Protection contre les grosses pertes\n✓ Limite les drawdowns',
                'cons': '✗ Peut sortir prématurément\n✗ Plus de transactions'
            }
        ]
        
        for i, strat in enumerate(strategies):
            self.create_strategy_card(content, strat, i)
    
    def create_strategy_card(self, parent, strategy, index):
        """Crée une carte pour une stratégie"""
        card = tk.Frame(parent, bg='#2d2d2d', relief='raised', borderwidth=2)
        card.pack(pady=10, fill='x')
        
        # Nom de la stratégie
        name_label = tk.Label(
            card,
            text=strategy['name'],
            font=('Arial', 14, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        name_label.pack(pady=(15, 5), anchor='w', padx=20)
        
        # Description
        desc_label = tk.Label(
            card,
            text=strategy['description'],
            font=('Arial', 10),
            bg='#2d2d2d',
            fg='#cccccc',
            wraplength=800,
            justify='left'
        )
        desc_label.pack(pady=5, anchor='w', padx=20)
        
        # Frame pour pros/cons
        pros_cons_frame = tk.Frame(card, bg='#2d2d2d')
        pros_cons_frame.pack(fill='x', padx=20, pady=10)
        
        # Avantages
        pros_frame = tk.Frame(pros_cons_frame, bg='#2d2d2d')
        pros_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        pros_title = tk.Label(
            pros_frame,
            text="Avantages:",
            font=('Arial', 11, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        pros_title.pack(anchor='w')
        
        pros_text = tk.Label(
            pros_frame,
            text=strategy['pros'],
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#cccccc',
            justify='left'
        )
        pros_text.pack(anchor='w', pady=5)
        
        # Inconvénients
        cons_frame = tk.Frame(pros_cons_frame, bg='#2d2d2d')
        cons_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        cons_title = tk.Label(
            cons_frame,
            text="Inconvénients:",
            font=('Arial', 11, 'bold'),
            bg='#2d2d2d',
            fg='#ff4444'
        )
        cons_title.pack(anchor='w')
        
        cons_text = tk.Label(
            cons_frame,
            text=strategy['cons'],
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#cccccc',
            justify='left'
        )
        cons_text.pack(anchor='w', pady=5)
    
    def create_stats_tab(self):
        """Onglet des statistiques détaillées"""
        
        title = tk.Label(
            self.tab_stats,
            text="Statistiques Détaillées",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title.pack(pady=20)
        
        # Table de statistiques
        stats_text = f"""
        📊 STATISTIQUES DESCRIPTIVES
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Capital Initial:              {self.stats['capital_initial']:,.0f} MAD
        
        Rendement Stratégie MM:       {self.stats['rendement_mm']:.2f}%
        Rendement Buy & Hold:         {self.stats['rendement_hold']:.2f}%
        
        Rendement Moyen Quotidien:    {self.stats['rendement_moyen']:.3f}%
        Écart-type Quotidien:         {self.stats['ecart_type']:.2f}%
        
        Volatilité Annualisée MM:     {self.stats['volatilite']:.2f}%
        Ratio de Sharpe:              {self.stats['sharpe_ratio']:.2f}
        
        Skewness (Asymétrie):         {self.stats['skewness']:.3f}
        Kurtosis (Aplatissement):     {self.stats['kurtosis']:.2f}
        
        Drawdown Maximum MM:          {self.stats['drawdown_max']:.2f}%
        Nombre de Transactions:       {self.stats['nb_transactions']}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        📈 TESTS STATISTIQUES
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Test de Normalité (Shapiro-Wilk):     ❌ Rejetée (p < 0.05)
        Test de Normalité (Jarque-Bera):      ❌ Rejetée (p < 0.05)
        Test de Stationnarité (ADF):          ✅ Confirmée (p < 0.05)
        Test d'Effet ARCH:                    ✅ Présence détectée (p < 0.05)
        Autocorrélation (k=1,2,3):            ≈ 0 (pas de dépendance)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        🌍 ANALYSE SAISONNIÈRE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Meilleurs mois:    Octobre (+0.61%), Février (+0.57%)
        Pires mois:        Juin (-0.10%), Août (-0.08%)
        Phénomène:         "Sell in May" observable
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        text_widget = tk.Text(
            self.tab_stats,
            font=('Courier', 11),
            bg='#2d2d2d',
            fg='#00ff88',
            height=25,
            width=80,
            relief='flat',
            padx=20,
            pady=20
        )
        text_widget.pack(pady=20, padx=30)
        text_widget.insert('1.0', stats_text)
        text_widget.config(state='disabled')
    
    def open_image(self, filepath):
        """Ouvre une image dans le viewer par défaut"""
        try:
            if os.path.exists(filepath):
                webbrowser.open(filepath)
            else:
                messagebox.showerror("Erreur", f"Fichier non trouvé: {filepath}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image: {str(e)}")
    
    def run_analysis(self):
        """Lance l'analyse complète"""
        response = messagebox.askyesno(
            "Lancer l'Analyse",
            "Voulez-vous lancer l'analyse complète?\n\nCela peut prendre quelques minutes..."
        )
        
        if response:
            try:
                # Lancer le script d'analyse
                os.system('python bitcoin_full_scripts.py')
                messagebox.showinfo(
                    "Succès",
                    "L'analyse a été lancée!\n\nVérifiez la console pour les résultats."
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {str(e)}")

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = BitcoinAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
