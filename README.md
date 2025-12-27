# 📊 Analyse Technique et Financière du Bitcoin (BTC/MAD)

## 📋 Description

Cette étude présente une **analyse quantitative approfondie** de l'évolution du cours du Bitcoin (BTC) entre le **1er janvier 2019** et le **1er janvier 2025**. En tant qu'analyste financier, diverses méthodes mathématiques et statistiques ont été appliquées pour extraire des insights actionnables concernant cette cryptomonnaie.

### 🎯 Période d'étude
- **Début** : 1er janvier 2019
- **Fin** : 1er janvier 2025
- **Fréquence** : Données quotidiennes
- **Source** : Yahoo Finance (BTC/EUR)
- **Conversion** : EUR → MAD (taux : 10.8)

## 🎯 Objectifs du Projet

Notre méthodologie comprend :
- ✅ **Acquisition et traitement** des données historiques depuis Yahoo Finance
- ✅ **Conversion des prix** en Dirhams marocains (MAD)
- ✅ **Analyse des rendements** quotidiens et leur distribution statistique
- ✅ **Étude de la saisonnalité** et des auto-corrélations
- ✅ **Backtesting** d'une stratégie basée sur le croisement de moyennes mobiles (20 et 50 jours)
- ✅ **Analyse comparative** de différentes stratégies d'investissement
- ✅ **Étude de l'impact des halvings** sur le prix du Bitcoin
- ✅ **Gestion des risques** (stop-loss, take-profit, position sizing)

## 📈 Résultats Clés

### Statistiques Descriptives
- **Fourchette moyenne quotidienne** : Calculée pour mesurer la volatilité intrajournalière
- **Rendement moyen quotidien** : 0.207% (tendance globale haussière)
- **Écart-type** : 3.36% (forte volatilité caractéristique des cryptomonnaies)
- **Skewness (Asymétrie)** : -0.259 (légèrement négative, pertes extrêmes plus fréquentes)
- **Kurtosis (Aplatissement)** : 10.12 (distribution leptokurtique avec queues épaisses)

### Tests Statistiques
| Test | Résultat | Interprétation |
|------|----------|----------------|
| **Shapiro-Wilk (normalité)** | p < 0.05 | ❌ Distribution non normale |
| **Jarque-Bera (normalité)** | p < 0.05 | ❌ Rejette l'hypothèse de normalité |
| **ADF (stationnarité)** | p < 0.05 | ✅ Série stationnaire |
| **Test ARCH** | p < 0.05 | ✅ Présence de volatilité conditionnelle |
| **Autocorrélation (k=1,2,3)** | ≈ 0 | Pas de dépendance temporelle significative |

### Performance des Stratégies (Capital initial : 1 000 000 MAD)

| Stratégie | Rendement Total | Volatilité | Sharpe Ratio | Drawdown Max |
|-----------|----------------|------------|--------------|--------------|
| **Moyennes Mobiles (MM20/MM50)** | **9.1%** | 1.42% | -1.08 | -2.56% |
| **Buy & Hold** | **2591.8%** | - | - | -73.57% |
| **Placement sans risque (3%)** | **19.4%** | 0% | - | 0% |

### Analyse Saisonnière (Rendements moyens mensuels)

| Mois | Rendement Moyen | Observation |
|------|----------------|-------------|
| **Octobre** | **+0.61%** | 🔥 Meilleur mois |
| **Février** | **+0.57%** | 📈 Très performant |
| **Juin** | **-0.10%** | 📉 Mois négatif |
| **Août** | **-0.08%** | 📉 Période faible |
| **Septembre** | **-0.04%** | 📉 Tendance baissière |

**Phénomène observé** : "Sell in May" avec déclin progressif de mai à septembre

### Impact des Halvings

| Halving | Rendement avant (60j) | Rendement après (60j) | Volatilité avant | Volatilité après |
|---------|----------------------|---------------------|-----------------|-----------------|
| **2020** | 1.14% | 0.05% | 81.44% | 38.92% |
| **2024** | 0.43% | 0.02% | 57.95% | 36.61% |

**Conclusion** : Le halving entraîne une forte baisse du rendement moyen car l'effet haussier est largement anticipé.

### Optimisation des Paramètres MM

| Combinaison | Rendement | Volatilité | Sharpe | Transactions |
|-------------|-----------|------------|--------|--------------|
| MM5/MM20 | 1162.77% | 38.28% | 0.95 | 120 |
| **MM10/MM30** | **1943.60%** | 38.94% | **1.08** | 82 |
| MM20/MM50 | 1897.38% | 39.63% | 1.07 | 39 |
| MM50/MM100 | 185.12% | 38.99% | 0.51 | 22 |
| MM100/MM200 | 503.78% | 35.69% | 0.76 | 14 |

**Meilleure combinaison** : MM10/MM30 avec un rendement de 1943.60% et un Sharpe de 1.08

### Performance par Contexte de Marché

| Période | Contexte | Rendement MM | Rendement B&H | Sharpe MM |
|---------|----------|--------------|---------------|-----------|
| 2019-2020 | Haussier modéré | 428.55% | 607.97% | 1.55 |
| 2021 | Fortement haussier | 17.84% | 68.47% | 0.54 |
| 2022 | Baissier | -26.35% | -63.21% | -0.85 |
| 2023-2024 | Latéral puis haussier | 120.29% | 473.34% | 1.02 |

**Observation** : La stratégie MM limite les pertes en marché baissier (-26% vs -63%)

## 🛠️ Technologies Utilisées

```
Python 3.8+
├── pandas 2.0.0        # Manipulation de données
├── numpy 1.24.0        # Calculs numériques
├── matplotlib 3.7.0    # Visualisations
├── seaborn 0.12.0      # Visualisations statistiques
├── scipy 1.10.0        # Tests statistiques
└── statsmodels 0.14.0  # Modèles de séries temporelles
```

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)
- Git

### Étapes d'installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/BozlAymane/Analyse-Bitcoin-BTC-MAD.git
cd Analyse-Bitcoin-BTC-MAD
```

2. **Créer un environnement virtuel (recommandé)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Analyse complète
```bash
python bitcoin_full_scripts.py
```

### Interface graphique
```bash
python appbtc.py
```

Le script génère automatiquement :
- 📊 Tous les graphiques d'analyse
- 📈 Les statistiques détaillées
- 💹 Les résultats de backtesting
- 📉 Les comparaisons de stratégies

## 📊 Visualisations Générées

Le script produit 15+ graphiques d'analyse :

| Graphique | Description | Insights |
|-----------|-------------|----------|
| `evolution_prix_btc.png` | Évolution du prix BTC en MAD | Tendance générale, pics, corrections |
| `rendements_quotidiens.png` | Rendements journaliers | Volatilité, périodes de crise |
| `distribution_rendements.png` | Histogramme et densité | Distribution non normale |
| `rendements_mensuels.png` | Analyse saisonnière | Octobre et février = meilleurs mois |
| `autocorrelation.png` | Autocorrélogramme | Pas de dépendance temporelle |
| `strategie_mm_croisees.png` | Signaux achat/vente | Points d'entrée/sortie |
| `evolution_portefeuille.png` | Performance dans le temps | Croissance du capital |
| `comparaison_strategies.png` | MM vs B&H vs Sans risque | Buy & Hold domine |
| `rendements_annuels.png` | Performance par année | 2020-2021 = meilleures années |
| `optimisation_mm_comparaison.png` | Test de 5 combinaisons MM | MM10/MM30 = optimal |
| `analyse_drawdowns.png` | Baisses maximales | MM limite les pertes |
| `impact_halvings.png` | Effet des halvings 2020/2024 | Anticipation du marché |
| `performances_par_contexte.png` | 4 contextes de marché | MM défensif en baisse |

### Exemples de Visualisations

Les graphiques montrent clairement :
- 📈 **Forte hausse 2020-2021** : Bull run historique
- 📉 **Correction 2022** : Crise économique mondiale
- 🔄 **Reprise 2023-2024** : Halving et regain d'intérêt

## 📁 Structure du Projet

```
Analyse-Bitcoin-BTC-MAD/
│
├── README.md                          # Ce fichier
├── requirements.txt                   # Dépendances Python
├── LICENSE                            # Licence MIT
├── .gitignore                         # Fichiers à ignorer
│
├── bitcoin_full_scripts.py            # Script principal d'analyse
├── appbtc.py                          # Interface graphique
├── BTC_data.csv                       # Données historiques Bitcoin
│
├── results/                           # Graphiques générés
│   ├── evolution_prix_btc.png
│   ├── rendements_quotidiens.png
│   ├── distribution_rendements.png
│   ├── strategie_mm_croisees.png
│   ├── comparaison_strategies.png
│   └── ... (15+ visualisations)
```

## 🔬 Méthodologie Détaillée

### 1. Acquisition et Préparation des Données
- Téléchargement depuis Yahoo Finance (BTC/EUR)
- Nettoyage : suppression des métadonnées
- Conversion EUR → MAD (taux : 10.8)
- Vérification des valeurs manquantes : ✅ Aucune

### 2. Analyse Statistique Complète
```python
# Tests réalisés
- Shapiro-Wilk : Normalité
- Jarque-Bera : Normalité (confirmation)
- ADF : Stationnarité
- ARCH : Volatilité conditionnelle
- Autocorrélation : Dépendances temporelles
```

### 3. Stratégie de Trading
**Croisement de Moyennes Mobiles**
- MM courte : 20 jours
- MM longue : 50 jours
- Signal d'achat : MM20 > MM50
- Signal de vente : MM20 < MM50

**Règles de gestion**
- Capital initial : 1 000 000 MAD
- Taille de position : 0.1 BTC par signal
- Stop-loss optionnel : 5%
- Take-profit optionnel : 15%

### 4. Backtesting Rigoureux
- Simulation jour par jour
- Prise en compte des coûts (simplifiés)
- Calcul du Sharpe ratio
- Analyse des drawdowns
- Comparaison avec benchmarks

## 🎓 Conclusions Principales

### 📌 Points Clés

1. **Rendements non normaux** : Distribution avec queues épaisses (kurtosis = 10.12)
2. **Forte volatilité** : Écart-type de 3.36% quotidien
3. **Pas de mémoire** : Autocorrélations ≈ 0 (marché efficient)
4. **Saisonnalité** : Octobre (+0.61%) et février (+0.57%) sont les meilleurs mois
5. **Buy & Hold domine** : 2591.8% vs 9.1% pour MM20/MM50
6. **MM protège en baisse** : -26% vs -63% en 2022
7. **Halvings anticipés** : Baisse des rendements post-halving

### ⚠️ Limites et Améliorations

**Limites identifiées :**
- Stratégie MM simple ne capture pas les grands mouvements
- Sharpe ratio négatif (-1.08) pour MM20/MM50
- Pas de prise en compte des frais de transaction

**Pistes d'amélioration :**
- [ ] Ajouter des filtres de volatilité
- [ ] Optimiser les périodes MM (MM10/MM30 semble meilleur)
- [ ] Implémenter stop-loss et take-profit
- [ ] Tester des stratégies ML (LSTM, Random Forest)
- [ ] Ajouter des indicateurs (RSI, MACD, Bollinger)
- [ ] Position sizing dynamique basé sur la volatilité

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add: nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 TODO / Roadmap

- [x] Analyse descriptive complète
- [x] Tests statistiques avancés
- [x] Stratégie moyennes mobiles
- [x] Analyse des halvings
- [x] Optimisation des paramètres
- [ ] Ajouter d'autres cryptomonnaies (ETH, BNB, SOL)
- [ ] Implémenter stratégies ML (LSTM)
- [ ] Interface web interactive (Streamlit/Dash)
- [ ] API REST pour données en temps réel
- [ ] Système d'alertes automatiques
- [ ] Backtesting avec frais réels

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Aymane Bozian** (à personnaliser)
- GitHub: [@BozIAymane](https://github.com/BozIAymane)
- LinkedIn: [Aymane Bozian](https://www.linkedin.com/in/aymane-bozian/))
- Email: aymanebozian@gmail.com

## 🙏 Remerciements

- **Yahoo Finance** pour les données historiques
- **Communauté Python** pour les excellentes bibliothèques
- **Anthropic** pour les outils d'analyse

## 📚 Références

1. Hull, John C. (2018). *Options, Futures and Other Derivatives*. 10e édition, Pearson.
2. Tsay, Ruey S. (2010). *Analysis of Financial Time Series*. 3rd edition, Wiley.
3. Fama, E. F. (1970). "Efficient Capital Markets: A Review of Theory and Empirical Work"
4. Sharpe, W. F. (1966). "Mutual Fund Performance"
5. Engle, R. F. (1982). "Autoregressive Conditional Heteroscedasticity"

## 📞 Support

Pour toute question ou problème :
- 🐛 Ouvrez une [Issue](https://github.com/BozIAymane/Analyse-Bitcoin-BTC-MAD/issues)
- 💬 Démarrez une [Discussion](https://github.com/BozIAymane/Analyse-Bitcoin-BTC-MAD/discussions)
- 📧 Contactez-moi par email

---

⭐ **Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !**

📊 **Données mises à jour** : 1er janvier 2025  
🔄 **Dernière mise à jour du code** : Décembre 2024
