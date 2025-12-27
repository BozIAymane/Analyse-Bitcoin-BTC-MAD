# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de démarrer avec le projet en **5 minutes** !

## ⚡ Installation Ultra-Rapide

### Option 1 : Pour les débutants

```bash
# 1. Téléchargez le projet
# Cliquez sur "Code" > "Download ZIP" sur GitHub
# Décompressez le dossier

# 2. Ouvrez un terminal dans le dossier
cd Analyse-Bitcoin-BTC-MAD

# 3. Installez les dépendances
pip install -r requirements.txt

# 4. Lancez l'analyse
python bitcoin_full_scripts.py
```

### Option 2 : Avec Git (recommandé)

```bash
# 1. Clonez le projet
git clone https://github.com/BozlAymane/Analyse-Bitcoin-BTC-MAD.git
cd Analyse-Bitcoin-BTC-MAD

# 2. Créez un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# 3. Installez les dépendances
pip install -r requirements.txt

# 4. Lancez l'analyse
python bitcoin_full_scripts.py
```

## 📊 Utilisation

### Lancer l'analyse complète

```bash
python bitcoin_full_scripts.py
```

**Ce qui va se passer :**
- ✅ Chargement des données BTC
- ✅ Analyse statistique complète
- ✅ Génération de 15+ graphiques
- ✅ Backtesting des stratégies
- ✅ Résultats affichés dans le terminal

**Durée estimée :** 2-3 minutes

### Lancer l'interface graphique

```bash
python appbtc.py
```

**Vous verrez :**
- 📊 Dashboard avec KPIs
- 📈 Tous les graphiques
- 🎯 Explications des stratégies
- 📉 Statistiques détaillées

## 📁 Fichiers Générés

Après l'exécution, vous trouverez dans le dossier `results/` :

```
results/
├── evolution_prix_btc.png              # Prix dans le temps
├── rendements_quotidiens.png           # Rendements journaliers
├── distribution_rendements.png         # Distribution
├── rendements_mensuels.png             # Saisonnalité
├── autocorrelation.png                 # Autocorrélation
├── strategie_mm_croisees.png           # Signaux trading
├── evolution_portefeuille.png          # Performance
├── comparaison_strategies.png          # Comparaison
├── rendements_annuels.png              # Par année
├── optimisation_mm_comparaison.png     # Optimisation
├── analyse_drawdowns.png               # Drawdowns
├── impact_halvings.png                 # Halvings
└── performances_par_contexte.png       # Contextes
```

## 🎯 Résultats Clés à Regarder

### 1. Performance Globale

```
Stratégie Moyennes Mobiles (MM20/MM50)
├── Rendement : 9.1%
├── Sharpe : -1.08
└── Drawdown : -2.56%

Buy & Hold
├── Rendement : 2591.8% 🚀
└── Drawdown : -73.57%

Placement sans risque (3%)
└── Rendement : 19.4%
```

### 2. Meilleure Combinaison MM

```
MM10/MM30
├── Rendement : 1943.60%
├── Sharpe : 1.08
└── Transactions : 82
```

### 3. Analyse Saisonnière

```
Meilleurs mois : Octobre (+0.61%), Février (+0.57%)
Pires mois : Juin (-0.10%), Août (-0.08%)
```

## 🔧 Personnalisation Rapide

### Changer les paramètres de la stratégie

Ouvrez `bitcoin_full_scripts.py` et modifiez :

```python
# Ligne ~200
data['MMC'] = data['Fermeture_MAD'].rolling(window=20).mean()  # Changez 20
data['MML'] = data['Fermeture_MAD'].rolling(window=50).mean()  # Changez 50
```

### Changer le capital initial

```python
# Ligne ~250
capital_initial = 1_000_000  # Changez cette valeur
```

### Tester d'autres combinaisons MM

```python
# Ligne ~450
mm_pairs = [(5, 20), (10, 30), (20, 50), (50, 100), (100, 200)]
# Ajoutez vos combinaisons ici
```

## 📖 Exemples d'Utilisation

### Exemple 1 : Analyse basique

```python
import pandas as pd

# Charger les données
data = pd.read_csv('BTC_data.csv')

# Afficher les premières lignes
print(data.head())

# Statistiques de base
print(data['Fermeture'].describe())
```

### Exemple 2 : Calculer les rendements

```python
# Rendements quotidiens
data['Rendement'] = data['Fermeture'].pct_change() * 100

# Rendement moyen
print(f"Rendement moyen : {data['Rendement'].mean():.2f}%")

# Volatilité
print(f"Volatilité : {data['Rendement'].std():.2f}%")
```

### Exemple 3 : Tester une stratégie simple

```python
# Moyennes mobiles
data['MM20'] = data['Fermeture'].rolling(20).mean()
data['MM50'] = data['Fermeture'].rolling(50).mean()

# Signaux
data['Signal'] = 0
data.loc[data['MM20'] > data['MM50'], 'Signal'] = 1  # Achat
data.loc[data['MM20'] < data['MM50'], 'Signal'] = -1  # Vente

# Compter les signaux
print(f"Signaux d'achat : {(data['Signal'] == 1).sum()}")
print(f"Signaux de vente : {(data['Signal'] == -1).sum()}")
```

## ❓ FAQ

**Q: L'analyse prend trop de temps**  
R: Normal, le script génère 15+ graphiques. Soyez patient (2-3 minutes).

**Q: J'ai une erreur "Module not found"**  
R: Installez les dépendances : `pip install -r requirements.txt`

**Q: Les graphiques ne s'affichent pas**  
R: Vérifiez que matplotlib est installé : `pip install matplotlib`

**Q: Je veux modifier les données**  
R: Remplacez `BTC_data.csv` par vos données (même format)

**Q: Comment exporter les résultats ?**  
R: Les graphiques sont automatiquement sauvegardés dans `results/`

## 🆘 Besoin d'Aide ?

1. **Consultez le README principal** : Plus de détails
2. **Ouvrez une Issue** : Sur GitHub
3. **Lisez le rapport complet** : `docs/BTC_projetVF.docx`

## 🎓 Prochaines Étapes

Une fois l'analyse terminée :

1. ✅ Explorez tous les graphiques dans `results/`
2. ✅ Lisez les conclusions dans le terminal
3. ✅ Testez l'interface graphique (`python appbtc.py`)
4. ✅ Modifiez les paramètres selon vos besoins
5. ✅ Partagez vos résultats !

---

**Temps total estimé : 5 minutes** ⏱️

Bon courage ! 🚀
