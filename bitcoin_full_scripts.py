"""
Script d'analyse technique et financière du Bitcoin
Ce script analyse les données historiques du Bitcoin, calcule différentes métriques,
teste des stratégies d'investissement et produit des visualisations pertinentes.
"""
#############################################
# PARTIE 1: CONFIGURATION ET CHARGEMENT DES DONNÉES
#############################################

# Import des bibliothèques nécessaires
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import acf
import matplotlib.dates as mdates
from datetime import datetime

# Téléchargement des données
print("Téléchargement des données...")
ticky = 'BTC-EUR'
data = yf.download(ticky, start='2019-01-01', end='2025-01-01', interval='1d')

# Gestion des multi-index potentiels (yfinance récent)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# Reset index pour avoir la date en colonne
data.reset_index(inplace=True)

# Sauvegarder en CSV
data.to_csv("BTC_data.csv", index=False)

# Chargement des données
data = pd.read_csv('BTC_data.csv')

# Affichage pour vérification des premières lignes
print("Aperçu des données brutes:")
print(data.head())

# Renommage des colonnes pour cohérence et utilisation en français
# Adaptation pour accepter 'Date' ou 'Price' selon la source
rename_dict = {
    'Date': 'date',               # Format yfinance standard
    'Price': 'date',              # Format alternatif
    'Adj Close': 'Fermeture_Ajustee',
    'Close': 'Fermeture',
    'High': 'Maximum',
    'Low': 'Minimum',
    'Open': 'Ouverture',
    'Volume': 'Volume'
}

data = data.rename(columns=rename_dict)

# Vérification si la colonne date existe bien
if 'date' not in data.columns:
    # Tentative de récupération si index
    if data.index.name == 'Date':
        data.reset_index(inplace=True)
        data = data.rename(columns={'Date': 'date'})

# Suppression des deux premières lignes inutiles (seulement ci nécessaire)
# data.drop(data.index[0:2], inplace=True) 
# Note: Avec yfinance propre, ce n'est généralement pas nécessaire. 
# Je le commente pour éviter de perdre des données valides.

# Réinitialisation de l'index après suppression
data.reset_index(drop=True, inplace=True)

# Conversion des colonnes numériques (pour s'assurer que les types sont corrects)
colonnes_numeriques = ['Fermeture_Ajustee', 'Fermeture', 'Maximum', 'Minimum', 'Ouverture', 'Volume']
for col in colonnes_numeriques:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

# Conversion de la colonne 'date' en format datetime
data['date'] = pd.to_datetime(data['date'])

# Vérification finale de la structure des données
print("\nInformations sur le dataset après nettoyage:")
print(data.info())

# Vérification des valeurs manquantes
missing_values = data.isnull().sum()
print("\nValeurs manquantes par colonne:")
print(missing_values)

#############################################
# PARTIE 2: ANALYSE DESCRIPTIVE DE BASE
#############################################

# Calcul de la fourchette quotidienne (différence entre prix max et min)
data['Daily Range'] = data['Maximum'] - data['Minimum']

# Calcul de la fourchette moyenne quotidienne - indicateur de volatilité
average_daily_range = data['Daily Range'].mean()
print(f"\nFourchette moyenne quotidienne : {average_daily_range:.2f} EUR")

# Conversion en MAD (Dirham marocain) pour analyse en devise locale
TAUX_EUR_MAD = 10.8  # Taux de conversion EUR vers MAD

# Conversion des colonnes de prix en MAD
for col in colonnes_numeriques[:-1]:  # Exclure le Volume
    if col in data.columns:
        data[f"{col}_MAD"] = data[col] * TAUX_EUR_MAD

#############################################
# PARTIE 3: VISUALISATIONS DE BASE
#############################################

# Graphique 1: Évolution du prix de fermeture en MAD
plt.figure(figsize=(10, 6))
plt.plot(data['date'], data['Fermeture_MAD'], label="Prix de Fermeture (MAD)", color='red')
plt.title("Évolution du Prix de Fermeture du Bitcoin (MAD)")
plt.xlabel("Date")
plt.ylabel("Prix (MAD)")
plt.legend()

# Formatage de l'axe des dates pour meilleure lisibilité
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('evolution_prix_btc.png')
# plt.show() # Commenté pour éviter blocage en mode script non-interactif

#############################################
# PARTIE 4: ANALYSE DES RENDEMENTS
#############################################

# Calcul des deux types de rendements
# 1. Rendement pourcentage (variation relative)
data['Rendement_%'] = (data['Fermeture_MAD'].pct_change()) * 100

# 2. Rendement logarithmique (utilisé en finance pour ses propriétés statistiques)
data['Rendement_log'] = np.log(data['Fermeture_MAD'] / data['Fermeture_MAD'].shift(1))

# Visualisation des rendements quotidiens
plt.figure(figsize=(10, 6))
plt.plot(data['date'], data['Rendement_%'], label='Rendement (%)', color='green')
plt.title('Rendements journaliers du Bitcoin en MAD')
plt.xlabel('Date')
plt.ylabel('Rendement (%)')
plt.grid(True, alpha=0.3)
plt.legend()

# Ajout d'une ligne horizontale à zéro pour référence
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)

# Formatage de l'axe des dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('rendements_quotidiens.png')
# plt.show()

# Statistiques descriptives des rendements
from scipy.stats import skew, kurtosis
print("\nStatistiques descriptives des rendements quotidiens:")
print(f"Moyenne : {data['Rendement_%'].mean():.4f}%")
print(f"Écart-type : {data['Rendement_%'].std():.4f}%")
print(f"Skewness (asymétrie) : {skew(data['Rendement_%'].dropna()):.4f}")
print(f"Kurtosis (aplatissement) : {kurtosis(data['Rendement_%'].dropna()):.4f}")

# Test de normalité de Shapiro-Wilk
from scipy.stats import shapiro
shapiro_test = shapiro(data['Rendement_%'].dropna())
print("\nTest de normalité Shapiro-Wilk:")
print(f"Statistique : {shapiro_test.statistic:.4f}")
print(f"p-value : {shapiro_test.pvalue:.6f}")
print(f"Interprétation: {'Les rendements ne suivent PAS une distribution normale (p<0.05)' if shapiro_test.pvalue < 0.05 else 'Les rendements suivent une distribution normale (p>0.05)'}")

# Visualisation de la distribution des rendements
plt.figure(figsize=(12, 6))
# Création d'un histogramme avec courbe de densité superposée
sns.histplot(data['Rendement_%'].dropna(), bins=100, kde=True, color='purple')
plt.title('Distribution des rendements journaliers (%)')
plt.xlabel('Rendement (%)')
plt.ylabel('Fréquence')

# Ajout de lignes verticales pour la moyenne et médiane
plt.axvline(x=data['Rendement_%'].mean(), color='red', linestyle='--', 
            label=f'Moyenne: {data["Rendement_%"].mean():.2f}%')
plt.axvline(x=data['Rendement_%'].median(), color='green', linestyle='--', 
            label=f'Médiane: {data["Rendement_%"].median():.2f}%')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('distribution_rendements.png')
# plt.show()

#############################################
# PARTIE 5: ANALYSE SAISONNIÈRE
#############################################

# Ajout de colonnes temporelles pour le mois et l'année
data['Mois'] = data['date'].dt.month
data['Année'] = data['date'].dt.year

# Calcul des rendements moyens par mois
rendement_mensuel = data.groupby('Mois')['Rendement_%'].mean()

# Visualisation des rendements mensuels moyens
plt.figure(figsize=(12, 6))
bars = rendement_mensuel.plot(kind='bar', figsize=(12, 6), color='skyblue')
plt.title("Rendements moyens mensuels du Bitcoin", fontsize=14)
plt.xlabel("Mois", fontsize=12)
plt.ylabel("Rendement moyen (%)", fontsize=12)

# Ajout des valeurs sur chaque barre
for i, v in enumerate(rendement_mensuel):
    plt.text(i, v + 0.1 if v > 0 else v - 0.5, f"{v:.2f}%", 
             ha='center', va='bottom' if v > 0 else 'top', fontweight='bold')

# Renommer les mois en format texte
mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
# S'assurer qu'on ne dépasse pas l'index si moins de mois
plt.xticks(range(len(rendement_mensuel)), [mois_noms[i-1] for i in rendement_mensuel.index], rotation=45)

plt.grid(True, axis='y', alpha=0.3)
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)  # Ligne horizontale à 0
plt.tight_layout()
plt.savefig('rendements_mensuels.png')
# plt.show()

#############################################
# PARTIE 6: ANALYSE D'AUTOCORRÉLATION
#############################################

# Calcul des autocorrélations pour les retards k=1,2,3
print("\nAnalyse d'autocorrélation des rendements:")
for k in range(1, 4):
    autocorr = data['Rendement_%'].autocorr(lag=k)
    print(f"Autocorrélation (k={k}) : {autocorr:.4f}")

# Visualisation de l'autocorrélogramme
from statsmodels.graphics.tsaplots import plot_acf
plt.figure(figsize=(12, 6))
plot_acf(data['Rendement_%'].dropna(), lags=20, alpha=0.05, ax=plt.gca())
plt.title("Autocorrélogramme des rendements BTC en MAD", fontsize=14)
plt.xlabel("Retard (jours)", fontsize=12)
plt.ylabel("Autocorrélation", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('autocorrelation.png')
# plt.show()

#############################################
# PARTIE 7: STRATÉGIE DE TRADING - MOYENNES MOBILES CROISÉES
#############################################

# Calcul des moyennes mobiles
data['MMC'] = data['Fermeture_MAD'].rolling(window=20).mean()  # Moyenne mobile courte (20 jours)
data['MML'] = data['Fermeture_MAD'].rolling(window=50).mean()  # Moyenne mobile longue (50 jours)

# Génération des signaux d'achat/vente basés sur le croisement des moyennes mobiles
data['Signal'] = 0

# Signal d'achat: MMC croise MML par le haut
data.loc[(data['MMC'] > data['MML']) & (data['MMC'].shift(1) <= data['MML'].shift(1)), 'Signal'] = 1

# Signal de vente: MMC croise MML par le bas
data.loc[(data['MMC'] < data['MML']) & (data['MMC'].shift(1) >= data['MML'].shift(1)), 'Signal'] = -1

# Visualisation de la stratégie
plt.figure(figsize=(14, 8))
# Tracé du prix
plt.plot(data['date'], data['Fermeture_MAD'], label='Prix BTC-MAD', alpha=0.5, color='gray')
# Tracé des moyennes mobiles
plt.plot(data['date'], data['MMC'], label='Moyenne mobile 20 jours', linestyle='--', color='blue', linewidth=1.5)
plt.plot(data['date'], data['MML'], label='Moyenne mobile 50 jours', linestyle='--', color='red', linewidth=1.5)

# Marquage des signaux d'achat/vente
plt.plot(data[data['Signal'] == 1]['date'], 
         data[data['Signal'] == 1]['Fermeture_MAD'], 
         '^', markersize=10, color='g', label='Signal Achat')
plt.plot(data[data['Signal'] == -1]['date'], 
         data[data['Signal'] == -1]['Fermeture_MAD'], 
         'v', markersize=10, color='r', label='Signal Vente')

plt.title('Stratégie de Croisement des Moyennes Mobiles - BTC/MAD', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Prix (MAD)', fontsize=12)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)

# Formatage de l'axe des dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('strategie_mm_croisees.png')
# plt.show()

#############################################
# PARTIE 8: SIMULATION DE PORTEFEUILLE AVEC STRATÉGIE MM
#############################################

# Initialisation des paramètres de simulation
capital_initial = 1_000_000  # Capital initial en MAD
btc_held = 0                 # Quantité de BTC détenue initialement
cash = capital_initial       # Liquidités disponibles initialement
portfolio_values = []        # Liste pour stocker l'évolution de la valeur du portefeuille

# Simulation de trading jour par jour
for i, row in data.iterrows():
    price = row['Fermeture_MAD']  # Prix du jour
    signal = row['Signal']        # Signal de trading du jour

    # Sécurité pour prix manquant
    if pd.isna(price):
        portfolio_values.append(cash + btc_held * (portfolio_values[-1] if portfolio_values else price))
        continue
    
    # Logique d'achat: acheter 0.1 BTC si signal d'achat et liquidités suffisantes
    if signal == 1 and cash >= price * 0.1:
        btc_held += 0.1           # Achat de 0.1 BTC
        cash -= price * 0.1       # Réduction des liquidités
    
    # Logique de vente: vendre 0.1 BTC si signal de vente et BTC suffisants
    elif signal == -1 and btc_held >= 0.1:
        btc_held -= 0.1           # Vente de 0.1 BTC
        cash += price * 0.1       # Augmentation des liquidités
    
    # Calcul de la valeur totale du portefeuille (liquidités + valeur BTC)
    valeur_totale = cash + btc_held * price
    portfolio_values.append(valeur_totale)

# Ajout des valeurs de portefeuille au dataframe
data['Valeur_Portefeuille'] = portfolio_values

# Visualisation de l'évolution du portefeuille
plt.figure(figsize=(12, 6))
plt.plot(data['date'], data['Valeur_Portefeuille'], label='Valeur du Portefeuille', color='blue', linewidth=2)
plt.title('Évolution de la Valeur du Portefeuille BTC-MAD avec Stratégie MM', fontsize=14)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Valeur (MAD)', fontsize=12)

# Ajout d'une ligne horizontale pour le capital initial
plt.axhline(y=capital_initial, color='red', linestyle='--', label=f'Capital initial: {capital_initial:,} MAD')
plt.grid(True, alpha=0.3)
plt.legend()

# Formatage de l'axe des dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)

# Formatage de l'axe des valeurs en milliers/millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x/1000)}K" if x < 1000000 else f"{x/1000000:.1f}M"))
plt.tight_layout()
plt.savefig('evolution_portefeuille.png')
# plt.show()

#############################################
# PARTIE 9: COMPARAISON DES STRATÉGIES D'INVESTISSEMENT
#############################################

# Calcul du nombre de BTC achetés au début (stratégie Buy & Hold)
if len(data) > 0 and not pd.isna(data['Fermeture_MAD'].iloc[0]):
    btc_initial = capital_initial / data['Fermeture_MAD'].iloc[0]  # Achat unique au premier jour
else:
    btc_initial = 0

# Valeur finale du portefeuille Buy & Hold à la fin de la période
valeur_finale_hold = btc_initial * data['Fermeture_MAD'].iloc[-1]  # Nombre de BTC × prix final

# Calcul du nombre de jours écoulés entre le début et la fin
nb_jours = (data['date'].iloc[-1] - data['date'].iloc[0]).days  # Utile pour annualiser les rendements

# Valeur finale d'un placement sans risque à 3% d'intérêt composé annuel
valeur_finale_risque = capital_initial * (1 + 0.03) ** (nb_jours / 365)  # Intérêt composé sur nb_jours

# Calcul des rendements pour chaque stratégie
rendement_strategie = (data['Valeur_Portefeuille'].iloc[-1]/capital_initial - 1)*100  # Stratégie MM
rendement_hold = (valeur_finale_hold/capital_initial - 1)*100                        # Buy & Hold
rendement_sans_risque = (valeur_finale_risque/capital_initial - 1)*100               # Sans risque

# Calcul des métriques de risque
data['Rendement_Portefeuille'] = data['Valeur_Portefeuille'].pct_change()
volatilite = data['Rendement_Portefeuille'].std() * (252**0.5)  # Volatilité annualisée

# Calcul du ratio de Sharpe (rendement ajusté au risque)
rendement_annuelise = ((1 + rendement_strategie/100)**(365/nb_jours if nb_jours > 0 else 1) - 1)*100
sharpe_ratio = (rendement_annuelise/100 - 0.03)/volatilite if volatilite > 0 else 0  # (Rendement - Taux sans risque) / Volatilité

# Affichage des résultats sous forme de tableau
print("\nComparaison des stratégies d'investissement:")
print(f"| Métrique          | Stratégie MM | Buy & Hold | Sans Risque |")
print(f"|-------------------|--------------|------------|-------------|")
print(f"| Rendement Total   | {rendement_strategie:.1f}%    | {rendement_hold:.1f}%   | {rendement_sans_risque:.1f}%    |")
print(f"| Volatilité        | {volatilite:.2%}     | -          | -           |")
print(f"| Sharpe Ratio      | {sharpe_ratio:.2f}       | -          | -           |")

# Visualisation comparative des stratégies
plt.figure(figsize=(12, 7))
# Création des séries temporelles pour chaque stratégie
mm_values = data['Valeur_Portefeuille']
hold_values = btc_initial * data['Fermeture_MAD']
risk_free_values = [capital_initial * (1 + 0.03)**(i/365) for i in range(len(data))]

# Tracé de chaque stratégie
plt.plot(data['date'], mm_values, label='Stratégie MM', lw=2, color='blue')
plt.plot(data['date'], hold_values, label='Buy & Hold', lw=2, color='green')
plt.plot(data['date'], risk_free_values, label='Placement 3%', lw=2, color='red')

plt.title("Performance Comparative des Stratégies d'Investissement", fontsize=16)
plt.ylabel("Valeur du Portefeuille (MAD)", fontsize=12)
plt.xlabel("Date", fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left')

# Formatage de l'axe des dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)

# Formatage de l'axe des valeurs en millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000000:.1f}M"))
plt.tight_layout()
plt.savefig('comparaison_strategies.png')
# plt.show()

#############################################
# PARTIE 10: TESTS STATISTIQUES AVANCÉS
#############################################

from scipy.stats import jarque_bera

# Test de Jarque-Bera pour la normalité des rendements
# Suppression des valeurs manquantes
rendements = data['Rendement_%'].dropna()

# Test de Jarque-Bera
jb_stat, jb_pvalue = jarque_bera(rendements)
print("\nTest de normalité Jarque-Bera:")
print(f"Statistique Jarque-Bera : {jb_stat:.2f}")
print(f"p-value : {jb_pvalue:.4f}")

# Interprétation
if jb_pvalue < 0.05:
    print("❌ Les rendements ne suivent pas une distribution normale (p<0.05).")
else:
    print("✅ Les rendements suivent une distribution normale (p>0.05).")

from statsmodels.tsa.stattools import adfuller

# Test de Dickey-Fuller Augmenté (ADF) pour la stationnarité
adf_result = adfuller(rendements)
print("\nTest de stationnarité Dickey-Fuller Augmenté:")
print(f"Statistique du test ADF : {adf_result[0]:.3f}")
print(f"p-value : {adf_result[1]:.4f}")

# Interprétation
if adf_result[1] < 0.05:
    print("✅ La série est stationnaire (p<0.05).")
else:
    print("❌ La série n'est pas stationnaire (p>0.05).")

from statsmodels.stats.diagnostic import het_arch

# Test d'effet ARCH (hétéroscédasticité conditionnelle autorégressive)
arch_stat, arch_pvalue, _, _ = het_arch(rendements)
print("\nTest d'effet ARCH (volatilité conditionnelle):")
print(f"Statistique LM (ARCH) : {arch_stat:.2f}")
print(f"p-value : {arch_pvalue:.4f}")

# Interprétation
if arch_pvalue < 0.05:
    print("✅ Présence d'un effet ARCH significatif (volatilité conditionnelle, p<0.05).")
else:
    print("❌ Pas d'effet ARCH détecté (p>0.05).")

#############################################
# PARTIE 11: STATISTIQUES ANNUELLES
#############################################

# Calcul des statistiques par année
data['Année'] = data['date'].dt.year
stats_annuelles = data.groupby('Année')['Rendement_%'].agg([
    ('Rendement moyen (%)', 'mean'),
    ('Écart-type (%)', 'std'),
    ('Minimum (%)', 'min'),
    ('Maximum (%)', 'max')
]).round(3)

# Calcul du Sharpe Ratio annuel (taux sans risque de 0% pour simplification)
stats_annuelles['Sharpe Ratio'] = (stats_annuelles['Rendement moyen (%)'] / stats_annuelles['Écart-type (%)']).round(2)

print("\nStatistiques annuelles des rendements:")
print(stats_annuelles)

# Visualisation des rendements annuels moyens
plt.figure(figsize=(12, 6))
stats_annuelles['Rendement moyen (%)'].plot(kind='bar', color='orange')
plt.title("Rendement moyen annuel du Bitcoin", fontsize=14)
plt.xlabel("Année", fontsize=12)
plt.ylabel("Rendement moyen (%)", fontsize=12)

# Ajout des valeurs sur chaque barre
for i, v in enumerate(stats_annuelles['Rendement moyen (%)']):
    plt.text(i, v + 0.1 if v > 0 else v - 0.5, f"{v:.2f}%", 
             ha='center', va='bottom' if v > 0 else 'top', fontweight='bold')

plt.grid(True, axis='y', alpha=0.3)
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.tight_layout()
plt.savefig('rendements_annuels.png')
# plt.show()

#############################################
# PARTIE 12: OPTIMISATION DES PARAMÈTRES DE STRATÉGIE
#############################################

# Test de différentes combinaisons de moyennes mobiles pour trouver la meilleure
# Nous testons 5 combinaisons différentes de périodes courtes/longues

# -------------------------------------------
# Assurez-vous que vos données sont prêtes
data['date'] = pd.to_datetime(data['date'])
# Attention: set_index modifié uniquement pour la copie ou l'usage local ici
# data.set_index('date', inplace=True) 
# Le code d'origine faisait set_index mais cela peut casser la suite si 'date' est encore utilisé comme colonne

capital_initial = 100000
rendements_resultats = []

# Liste des paires (courte, longue) à tester
mm_pairs = [(5, 20), (10, 30), (20, 50), (50, 100), (100, 200)]

for short_win, long_win in mm_pairs:
    # Créer une copie des données pour éviter de modifier les originales
    df = data.copy()
    if 'date' in df.columns:
        df.set_index('date', inplace=True)

    # Calcul des moyennes mobiles pour cette combinaison
    df['MM_courte'] = df['Fermeture_MAD'].rolling(window=short_win).mean()
    df['MM_longue'] = df['Fermeture_MAD'].rolling(window=long_win).mean()

    # Génération du signal de trading:
    # 1 = signal d'achat
    # -1 = signal de vente
    df['Signal'] = 0
    df.loc[(df['MM_courte'] > df['MM_longue']) & (df['MM_courte'].shift(1) <= df['MM_longue'].shift(1)), 'Signal'] = 1
    df.loc[(df['MM_courte'] < df['MM_longue']) & (df['MM_courte'].shift(1) >= df['MM_longue'].shift(1)), 'Signal'] = -1
    
    # Conversion des signaux en positions continues (maintien de la dernière position)
    df['Position'] = df['Signal'].replace(0).ffill().fillna(0) # Correction deprecation method='ffill'
    
    # Simulation du portefeuille
    btc, cash = 0, capital_initial
    portefeuille = []
    
    # Exécution des ordres pour chaque jour de la période
    for i in range(len(df)):
        prix = df['Fermeture_MAD'].iloc[i]
        signal = df['Signal'].iloc[i]
        
        # Sécurité prix manquant
        if pd.isna(prix):
            portefeuille.append(cash + btc * (portefeuille[-1] if portefeuille else 1.0))
            continue

        # Stratégie: achat total au signal d'achat, vente totale au signal de vente
        if signal == 1 and cash > 0 and prix > 0:
            btc = cash / prix  # Conversion de tout le cash en BTC
            cash = 0
        elif signal == -1 and btc > 0 and prix > 0:
            cash = btc * prix  # Conversion de tout le BTC en cash
            btc = 0
            
        # Valeur totale du portefeuille chaque jour
        portefeuille.append(cash + btc * prix)
    
    # Stockage des valeurs de portefeuille et calcul des rendements quotidiens
    df['Portefeuille'] = portefeuille
    df['Rendement'] = df['Portefeuille'].pct_change()
    
    # Calcul des métriques de performance
    # 1. Rendement total sur la période
    rendement_total = (df['Portefeuille'].iloc[-1] / capital_initial - 1) * 100
    
    # 2. Volatilité annualisée du portefeuille
    volatilite = df['Rendement'].std() * np.sqrt(252) * 100  # Annualisation avec √252 jours de trading
    
    # 3. Ratio de Sharpe (rendement ajusté au risque)
    # Hypothèse: taux sans risque = 0 pour simplifier
    sharpe = ((df['Rendement'].mean() * 252) / (df['Rendement'].std() * np.sqrt(252))) if df['Rendement'].std() > 0 else np.nan
    
    # 4. Nombre de transactions effectuées
    nb_transactions = df['Signal'].abs().sum()
    
    # Enregistrement des résultats pour cette combinaison
    rendements_resultats.append({
        'Combinaison MM': f'MM{short_win}/MM{long_win}',
        'Rendement total (%)': round(rendement_total, 2),
        'Volatilité (%)': round(volatilite, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Nb. transactions': int(nb_transactions)
    })

# Conversion en DataFrame pour affichage plus clair
resultats_df = pd.DataFrame(rendements_resultats)
print(resultats_df)

# Visualisation des performances par combinaison de MM
plt.figure(figsize=(12, 8))

# Graphique à barres pour le rendement total
ax1 = plt.subplot(2, 2, 1)
sns.barplot(x='Combinaison MM', y='Rendement total (%)', data=resultats_df, palette='viridis', ax=ax1)
ax1.set_title('Rendement Total par Combinaison', fontsize=12)
ax1.set_ylabel('Rendement (%)')
ax1.tick_params(axis='x', rotation=45)

# Graphique à barres pour le ratio de Sharpe
ax2 = plt.subplot(2, 2, 2)
sns.barplot(x='Combinaison MM', y='Sharpe Ratio', data=resultats_df, palette='viridis', ax=ax2)
ax2.set_title('Ratio de Sharpe par Combinaison', fontsize=12)
ax2.tick_params(axis='x', rotation=45)

# Graphique à barres pour la volatilité
ax3 = plt.subplot(2, 2, 3)
sns.barplot(x='Combinaison MM', y='Volatilité (%)', data=resultats_df, palette='viridis', ax=ax3)
ax3.set_title('Volatilité par Combinaison', fontsize=12)
ax3.set_ylabel('Volatilité annualisée (%)')
ax3.tick_params(axis='x', rotation=45)

# Graphique à barres pour le nombre de transactions
ax4 = plt.subplot(2, 2, 4)
sns.barplot(x='Combinaison MM', y='Nb. transactions', data=resultats_df, palette='viridis', ax=ax4)
ax4.set_title('Nombre de Transactions par Combinaison', fontsize=12)
ax4.set_ylabel('Nombre de trades')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.suptitle('Comparaison des Performances par Combinaison de Moyennes Mobiles', fontsize=14, y=1.02)
plt.savefig('optimisation_mm_comparaison.png', dpi=300, bbox_inches='tight')
# plt.show()

# -------------------------------------------
# ANALYSE DES DRAWDOWNS PAR STRATÉGIE
# -------------------------------------------
# Le drawdown mesure la baisse maximale depuis un pic précédent
# C'est un indicateur important du risque d'une stratégie
# -------------------------------------------

# Fonction pour calculer la série de drawdowns
def calcul_drawdown(serie):
    pic = serie.cummax()  # Série des maximums cumulatifs (pics historiques)
    # Eviter division par zero
    pic = pic.replace(0, np.nan) 
    drawdown = (serie - pic) / pic  # Calcul du drawdown relatif
    return drawdown

# Fonction pour extraire les métriques de drawdown
def analyse_drawdown(serie):
    dd = calcul_drawdown(serie)
    max_dd = dd.min() * 100  # Drawdown maximum en %
    
    # Identifier les phases de drawdown individuelles
    en_dd = dd < 0  # Série booléenne: True quand en drawdown
    durées, récups = [], []
    i = 0
    
    # Parcours de la série pour identifier chaque période de drawdown
    while i < len(en_dd):
        if en_dd.iloc[i]:  # Si nous sommes en drawdown
            start = i  # Début de la période de drawdown
            
            # Trouver la fin de cette période de drawdown
            while i < len(en_dd) and en_dd.iloc[i]:
                i += 1
            end = i
            
            # Enregistrer la durée du drawdown
            durées.append(end - start)
            
            # Calculer le temps de récupération (jusqu'à nouveau pic)
            try:
                # Index du premier point où la valeur dépasse celle du début du drawdown
                recup = np.where(serie.iloc[end:] >= serie.iloc[start])[0][0]
            except IndexError:
                # Pas de récupération complète dans la série
                recup = np.nan
            récups.append(recup)
        else:
            i += 1
            
    # Calcul des moyennes
    durée_moyenne = np.mean(durées) if durées else 0
    recup_moyenne = np.nanmean(récups) if récups else 0
    
    return round(max_dd, 2), round(durée_moyenne), round(recup_moyenne)

# Préparer les séries de valeur des trois stratégies
val_mm = data['Valeur_Portefeuille']  # Notre stratégie de moyennes mobiles
val_hold = (data['Fermeture_MAD'] / data['Fermeture_MAD'].iloc[0]) * 100000 if not data['Fermeture_MAD'].empty else pd.Series() # Buy & Hold
val_risk_free = [100000 * (1 + 0.02) ** (i / 365) for i in range(len(data))]  # Placement sans risque à 2%

# Appliquer l'analyse de drawdown à chaque stratégie
if not val_mm.empty:
    dd_mm = analyse_drawdown(val_mm)
    dd_hold = analyse_drawdown(val_hold)
    dd_risk = analyse_drawdown(pd.Series(val_risk_free))

    # Résumé en tableau
    drawdown_df = pd.DataFrame([
        {"Stratégie": "MM Croisées", "Drawdown maximum (%)": dd_mm[0], "Durée moyenne (jours)": dd_mm[1], "Temps moyen de récupération (jours)": dd_mm[2]},
        {"Stratégie": "Buy & Hold", "Drawdown maximum (%)": dd_hold[0], "Durée moyenne (jours)": dd_hold[1], "Temps moyen de récupération (jours)": dd_hold[2]},
        {"Stratégie": "Sans risque", "Drawdown maximum (%)": dd_risk[0], "Durée moyenne (jours)": dd_risk[1], "Temps moyen de récupération (jours)": dd_risk[2]},
    ])
    print(drawdown_df)

    # Visualisation des drawdowns pour chaque stratégie
    plt.figure(figsize=(14, 10))
    # Sous-graphique 1: Évolution des valeurs de portefeuille
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(data.index, val_mm, label='Moyennes Mobiles', color='blue')
    ax1.plot(data.index, val_hold, label='Buy & Hold', color='green')
    ax1.plot(data.index, val_risk_free, label='Sans risque (2%)', color='gray', linestyle='--')
    ax1.set_title('Évolution de la Valeur des Portefeuilles', fontsize=14)
    ax1.set_ylabel('Valeur (MAD)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Sous-graphique 2: Drawdowns
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(data.index, calcul_drawdown(val_mm)*100, label='Drawdown MM', color='blue')
    ax2.plot(data.index, calcul_drawdown(val_hold)*100, label='Drawdown B&H', color='green')
    ax2.set_title('Drawdowns au fil du temps', fontsize=14)
    ax2.set_ylabel('Drawdown (%)')
    try:
        ax2.set_ylim(bottom=min(dd_mm[0], dd_hold[0])*1.1, top=5)  # Ajuster l'échelle
    except:
        pass
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('analyse_drawdowns.png', dpi=300, bbox_inches='tight')
    # plt.show()

# -------------------------------------------
# ANALYSE DE L'IMPACT DES HALVINGS SUR LE BITCOIN
# -------------------------------------------
# Les halvings sont des événements où la récompense de minage est divisée par deux
# Ils ont historiquement un impact important sur le prix du Bitcoin
# -------------------------------------------

from matplotlib.patches import Rectangle

# Assurez-vous que data['date'] est bien en datetime
# (Déjà fait plus haut, mais bon rappel)

# Création d'une copie indexée par date pour cette analyse
data_indexed = data.copy()
if 'date' in data_indexed.columns:
    data_indexed.set_index('date', inplace=True)

# Dates approximatives des halvings de Bitcoin
halving_dates = {
    'Halving 2020': '2020-05-11',
    'Halving 2024': '2024-04-20'
}

# Fenêtre d'analyse (60 jours avant et après)
window = 60

# Liste pour stocker les résultats
results = []

# Création d'une figure pour visualiser l'impact des halvings
plt.figure(figsize=(14, 10))

# Pour chaque halving, analyser les rendements avant/après
for i, (label, halving_date) in enumerate(halving_dates.items()):
    halving_date = pd.to_datetime(halving_date)
    
    # Définir les périodes avant et après le halving
    try:
        avant = data_indexed.loc[halving_date - pd.Timedelta(days=window):halving_date - pd.Timedelta(days=1)].copy()
        apres = data_indexed.loc[halving_date + pd.Timedelta(days=1):halving_date + pd.Timedelta(days=window)].copy()
        
        if avant.empty or apres.empty:
            continue

        # Calcul des rendements quotidiens
        avant['rendement'] = avant['Fermeture_MAD'].pct_change()
        apres['rendement'] = apres['Fermeture_MAD'].pct_change()
        
        # Calcul des statistiques
        rendement_avant = avant['rendement'].mean() * 100
        rendement_apres = apres['rendement'].mean() * 100
        vol_avant = avant['rendement'].std() * np.sqrt(252) * 100  # Volatilité annualisée
        vol_apres = apres['rendement'].std() * np.sqrt(252) * 100  # Volatilité annualisée
        
        # Stocker les résultats
        results.append({
            'Période': label,
            'Rendement moyen avant halving (60j)': round(rendement_avant, 2),
            'Rendement moyen après halving (60j)': round(rendement_apres, 2),
            'Volatilité avant (%)': round(vol_avant, 2),
            'Volatilité après (%)': round(vol_apres, 2)
        })
        
        # Sous-graphique pour ce halving
        ax = plt.subplot(2, 1, i+1)
        
        # Obtenir la période complète (avant et après)
        periode_complete = data_indexed.loc[halving_date - pd.Timedelta(days=window):halving_date + pd.Timedelta(days=window)]
        
        # Tracer le prix
        ax.plot(periode_complete.index, periode_complete['Fermeture_MAD'], label='Prix BTC (MAD)')
        
        # Marquer le jour du halving
        ax.axvline(x=halving_date, color='red', linestyle='--', label='Date du halving')
        
        # Ajouter un rectangle coloré pour la période avant/après
        ax.add_patch(Rectangle((mdates.date2num(halving_date - pd.Timedelta(days=window)), ax.get_ylim()[0]),
                             mdates.date2num(halving_date) - mdates.date2num(halving_date - pd.Timedelta(days=window)),
                             ax.get_ylim()[1] - ax.get_ylim()[0],
                             alpha=0.1, color='blue', label='Avant halving'))
        
        ax.add_patch(Rectangle((mdates.date2num(halving_date), ax.get_ylim()[0]),
                             mdates.date2num(halving_date + pd.Timedelta(days=window)) - mdates.date2num(halving_date),
                             ax.get_ylim()[1] - ax.get_ylim()[0],
                             alpha=0.1, color='green', label='Après halving'))
        
        # Annotations
        ax.set_title(f'Impact du {label} sur le prix du Bitcoin', fontsize=14)
        ax.set_ylabel('Prix (MAD)')
        ax.text(halving_date + pd.Timedelta(days=5), ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0])*0.9,
               f"Rendement moyen: {round(rendement_apres, 2)}% vs {round(rendement_avant, 2)}% avant",
               fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
        ax.grid(True, alpha=0.3)
        ax.legend()
    except Exception as e:
        print(f"Skipping halving analysis for {label}: {e}")

plt.tight_layout()
plt.savefig('impact_halvings.png', dpi=300, bbox_inches='tight')
# plt.show()

# Affichage des résultats sous forme de tableau
halving_df = pd.DataFrame(results)
print(halving_df)

# -------------------------------------------
# ANALYSE PAR SOUS-PÉRIODES DE MARCHÉ
# -------------------------------------------
# Le BTC traverse différentes phases de marché (haussier, baissier, latéral)
# Cette analyse évalue comment se comporte notre stratégie dans chaque contexte
# -------------------------------------------

# Fonction de calcul des performances pour une sous-période donnée
def analyse_performance(df, capital_initial=100000, short_win=20, long_win=50):
    df = df.copy()
    # Calcul des moyennes mobiles
    df['MM_courte'] = df['Fermeture_MAD'].rolling(window=short_win).mean()
    df['MM_longue'] = df['Fermeture_MAD'].rolling(window=long_win).mean()
    
    # Génération des signaux de trading
    df['Signal'] = 0
    df.loc[(df['MM_courte'] > df['MM_longue']) & (df['MM_courte'].shift(1) <= df['MM_longue'].shift(1)), 'Signal'] = 1
    df.loc[(df['MM_courte'] < df['MM_longue']) & (df['MM_courte'].shift(1) >= df['MM_longue'].shift(1)), 'Signal'] = -1
    
    df['Position'] = df['Signal'].replace(0).ffill().fillna(0)
    
    # Simulation du portefeuille
    cash, btc = capital_initial, 0
    portefeuille = []
    
    for i in range(len(df)):
        prix = df['Fermeture_MAD'].iloc[i]
        signal = df['Signal'].iloc[i]
        
        if signal == 1 and cash > 0:
            btc = cash / prix
            cash = 0
        elif signal == -1 and btc > 0:
            cash = btc * prix
            btc = 0
        portefeuille.append(cash + btc * prix)
        
    # Calcul des métriques de performance
    df['Portefeuille'] = portefeuille
    rendement_mm = (df['Portefeuille'].iloc[-1] / capital_initial - 1) * 100
    df['Rendement_MM'] = df['Portefeuille'].pct_change()
    sharpe = (df['Rendement_MM'].mean() * 252) / (df['Rendement_MM'].std() * np.sqrt(252)) if df['Rendement_MM'].std() > 0 else np.nan
    
    # Rendement Buy & Hold pour la même période
    prix_initial = df['Fermeture_MAD'].iloc[0]
    prix_final = df['Fermeture_MAD'].iloc[-1]
    rendement_hold = ((prix_final / prix_initial) - 1) * 100
    
    return round(rendement_mm, 2), round(rendement_hold, 2), round(sharpe, 2)

# Liste des sous-périodes à analyser avec leur contexte de marché
sous_periodes = [
    ('2019-01-01', '2020-12-31', 'Haussier modéré'),
    ('2021-01-01', '2021-12-31', 'Fortement haussier'),
    ('2022-01-01', '2022-12-31', 'Baissier'),
    ('2023-01-01', '2024-12-31', 'Latéral puis haussier')
]

# Résultats pour chaque sous-période
resultats = []

# Préparation d'une figure pour visualiser les performances par sous-période
plt.figure(figsize=(16, 12))

# Pour chaque sous-période définie
for i, (debut, fin, contexte) in enumerate(sous_periodes):
    # Extraire les données pour cette sous-période dans la copie indexée
    subset = data_indexed[(data_indexed.index >= debut) & (data_indexed.index <= fin)]
    
    # Vérifier qu'il y a des données dans cette période
    if len(subset) > 0:
        # Calculer les performances
        try:
            r_mm, r_hold, sharpe = analyse_performance(subset)
            
            # Stocker les résultats
            resultats.append({
                'Sous-période': f'{debut[:4]}-{fin[:4]}',
                'Contexte de marché': contexte,
                'Rendement MM': f'{r_mm}%',
                'Rendement B&H': f'{r_hold}%',
                'Sharpe MM': sharpe
            })
            
            # Créer un sous-graphique pour cette période
            ax = plt.subplot(2, 2, i+1)
            
            # Tracer le prix et les moyennes mobiles
            ax.plot(subset.index, subset['Fermeture_MAD'], label='Prix BTC', alpha=0.7)
            ax.plot(subset.index, subset['Fermeture_MAD'].rolling(window=20).mean(), label='MM20', linestyle='--')
            ax.plot(subset.index, subset['Fermeture_MAD'].rolling(window=50).mean(), label='MM50', linestyle='--')
            
            # Annotations et formatage
            ax.set_title(f'{contexte} ({debut[:4]}-{fin[:4]})', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylabel('Prix (MAD)')
            
            # Afficher les rendements en annotation
            ax.text(0.05, 0.95, f"MM: {r_mm}% | B&H: {r_hold}%", 
                    transform=ax.transAxes, fontsize=10, 
                    bbox=dict(facecolor='white', alpha=0.5))
            
            if i == 0:  # Seulement pour le premier graphique
                ax.legend()
        except Exception as e:
            print(f"Erreur analyse période {debut}-{fin}: {e}")

plt.tight_layout()
plt.suptitle('Performances par contexte de marché', fontsize=16, y=1.02)
plt.savefig('performances_par_contexte.png', dpi=300, bbox_inches='tight')
# plt.show()

# Résumé en DataFrame
sous_periodes_df = pd.DataFrame(resultats)
print(sous_periodes_df)

# -------------------------------------------
# GESTION DES RISQUES ET OPTIMISATION DE LA STRATÉGIE
# -------------------------------------------
# Nous testons différentes règles de gestion des risques pour améliorer la stratégie:
# - Stop-loss
# - Take-profit
# - Position sizing dynamique
# -------------------------------------------

# Paramètres de base
capital_initial = 100000
stop_loss_pct = 0.05  # 5% de perte maximum
take_profit_pct = 0.15  # 15% de gain cible

# Fonction de simulation avec options de gestion des risques
def backtest_risk_strategy(data, stop_loss=False, take_profit=False, dynamic_position=False):
    df = data.copy()
    
    # Calcul des moyennes mobiles
    df['MM20'] = df['Fermeture_MAD'].rolling(20).mean()
    df['MM50'] = df['Fermeture_MAD'].rolling(50).mean()
    
    # Génération des signaux de trading comme précédemment
    df['Signal'] = 0
    df.loc[(df['MM20'] > df['MM50']) & (df['MM20'].shift(1) <= df['MM50'].shift(1)), 'Signal'] = 1
    df.loc[(df['MM20'] < df['MM50']) & (df['MM20'].shift(1) >= df['MM50'].shift(1)), 'Signal'] = -1
    
    # Variables pour la simulation
    cash = capital_initial
    btc = 0
    portefeuille = []
    prix_achat = 0  # Prix auquel le BTC a été acheté (pour stop-loss/take-profit)
    
    # Simulation jour par jour
    for i in range(len(df)):
        prix = df['Fermeture_MAD'].iloc[i]
        signal = df['Signal'].iloc[i]
        
        if pd.isna(prix):
             portefeuille.append(cash + btc * (portefeuille[-1] if portefeuille else 1.0))
             continue

        # Traitement des signaux d'achat/vente
        if signal == 1 and cash > 0:
            # Si position sizing dynamique, n'investir qu'une partie du capital
            montant_investi = cash if not dynamic_position else cash * 0.5
            btc = montant_investi / prix
            cash -= montant_investi
            prix_achat = prix  # Enregistrer le prix d'achat pour SL/TP
            
        elif signal == -1 and btc > 0:
            # Vendre toute la position au signal de vente
            cash += btc * prix
            btc = 0
            prix_achat = 0
            
        # Gestion du stop-loss ou take-profit si activés
        if btc > 0 and prix_achat > 0:
            # Calculer la variation en % depuis l'achat
            variation = (prix - prix_achat) / prix_achat
            
            # Stop-loss: vendre si la perte dépasse le seuil
            if stop_loss and variation <= -stop_loss_pct:
                cash += btc * prix
                btc = 0
                
            # Take-profit: vendre si le gain dépasse le seuil
            elif take_profit and variation >= take_profit_pct:
                cash += btc * prix
                btc = 0
        
        # Enregistrer la valeur du portefeuille chaque jour
        portefeuille.append(cash + btc * prix)
        
    # Stockage des valeurs et calcul des rendements
    df['Portefeuille'] = portefeuille
    df['Rendement'] = df['Portefeuille'].pct_change()
    
    # Calcul des métriques de performance
    rendement = (df['Portefeuille'].iloc[-1] / capital_initial - 1) * 100
    volatilite = df['Rendement'].std() * np.sqrt(252) * 100
    sharpe = (df['Rendement'].mean() * 252) / (df['Rendement'].std() * np.sqrt(252)) if df['Rendement'].std() > 0 else np.nan
    drawdown = ((df['Portefeuille'] / df['Portefeuille'].cummax()) - 1).min() * 100
    
    return round(rendement, 2), round(volatilite, 2), round(sharpe, 2), round(drawdown, 2), df['Portefeuille']

# Définition des scénarios à tester
scenarios = [
    ("Base (MM20/MM50)", False, False, False),
    ("+ Stop-loss 5%", True, False, False),
    ("+ Take-profit 15%", False, True, False),
    ("+ Position sizing dynamique", False, False, True)
]

# Exécution des scénarios et collecte des résultats
results = []
portfolios = {}

# S'assurer que data est prêt (si nettoyé au début)
for label, sl, tp, dyn in scenarios:
    r, v, s, d, portfolio = backtest_risk_strategy(data, stop_loss=sl, take_profit=tp, dynamic_position=dyn)
    results.append({
        'Règle appliquée': label,
        'Rendement (%)': r,
        'Volatilité (%)': v,
        'Sharpe': s,
        'Drawdown max (%)': d
    })
    portfolios[label] = portfolio

# Création du DataFrame de résultats
df_results = pd.DataFrame(results)
print(df_results)