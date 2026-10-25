"""
app.py - Application Web Interactive d'Analyse Bitcoin BTC/MAD
Développée avec Streamlit et Plotly.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Import des modules métiers
from src.data_loader import load_btc_data
from src.indicators import compute_indicators
from src.statistics import (
    compute_descriptive_stats,
    run_statistical_tests,
    compute_monthly_seasonality,
    compute_halving_impact,
)
from src.backtest import run_backtest_ma, run_dca_backtest, run_comparison

# ── Configuration de la page Streamlit ────────────────────────────
st.set_page_config(
    page_title="Bitcoin Analytics | BTC/MAD",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Design ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* En-tête gradient */
    .hero-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #064e3b 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .badge-mad {
        background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
        color: #000;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        display: inline-block;
        margin-left: 8px;
    }
    
    /* Cartes KPI */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #10b981;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-val {
        font-size: 1.9rem;
        font-weight: 800;
        margin: 8px 0;
        color: #f1f5f9;
    }
    .kpi-desc {
        font-size: 0.8rem;
        color: #64748b;
    }
    .positive { color: #10b981 !important; }
    .negative { color: #ef4444 !important; }
    .neutral { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar : Paramètres ──────────────────────────────────────────
with st.sidebar:
    st.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=032", width=60)
    st.title("⚙️ Paramètres")
    st.caption("Contrôle du Moteur d'Analyse & Backtest")

    st.subheader("💰 Capital & Frais")
    initial_cap = st.number_input(
        "Capital Initial (MAD)",
        min_value=1_000.0,
        max_value=100_000_000.0,
        value=1_000_000.0,
        step=50_000.0,
        format="%.0f"
    )

    fee_pct = st.slider("Frais de transaction par trade (%)", 0.0, 1.0, 0.1, 0.05) / 100.0
    risk_free = st.slider("Taux sans risque annuel - Bank Al-Maghrib (%)", 0.0, 8.0, 3.0, 0.25) / 100.0

    st.subheader("🎯 Paramètres Moyennes Mobiles")
    col_ma1, col_ma2 = st.columns(2)
    with col_ma1:
        ma_short = st.number_input("MM Courte (jours)", min_value=3, max_value=50, value=20, step=1)
    with col_ma2:
        ma_long = st.number_input("MM Longue (jours)", min_value=10, max_value=250, value=50, step=5)

    st.subheader("🛡️ Gestion des Risques")
    use_sl = st.checkbox("Activer Stop-Loss", value=False)
    sl_val = st.slider("Seuil Stop-Loss (%)", 1.0, 20.0, 5.0, 0.5) / 100.0 if use_sl else None

    use_tp = st.checkbox("Activer Take-Profit", value=False)
    tp_val = st.slider("Seuil Take-Profit (%)", 5.0, 50.0, 15.0, 1.0) / 100.0 if use_tp else None

    st.markdown("---")
    force_refresh = st.button("🔄 Actualiser les données en ligne", use_container_width=True)
    st.caption("Source : Yahoo Finance (BTC-USD + USD/MAD) converti en temps réel.")

# ── Chargement des données ────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Chargement des données de marché...")
def get_data(refresh=False):
    return load_btc_data(force_download=refresh)

try:
    df_raw = get_data(refresh=force_refresh)
    df = compute_indicators(df_raw, short_window=ma_short, long_window=ma_long)
except Exception as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.stop()

# ── Hero Banner ───────────────────────────────────────────────────
latest_date = df['date'].iloc[-1].strftime("%d/%m/%Y")
latest_price = df['close_mad'].iloc[-1]
first_price = df['close_mad'].iloc[0]
total_market_ret = ((latest_price / first_price) - 1.0) * 100.0

st.markdown(f"""
<div class="hero-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <h1 class="hero-title">Bitcoin Analytics — BTC/MAD <span class="badge-mad">Dirham Marocain</span></h1>
            <p class="hero-sub">Plateforme d'analyse technique, économétrique et de backtesting quantitatif (2019 — {latest_date})</p>
        </div>
        <div style="text-align: right; margin-top: 10px;">
            <div style="font-size: 0.85rem; color: #94a3b8;">Dernier cours BTC/MAD</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #10b981;">{latest_price:,.0f} MAD</div>
            <div style="font-size: 0.85rem; color: #38bdf8;">Croissance globale : +{total_market_ret:,.1f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Exécution du Backtest ─────────────────────────────────────────
backtest_res = run_backtest_ma(
    df,
    initial_capital=initial_cap,
    short_window=ma_short,
    long_window=ma_long,
    fee_rate=fee_pct,
    stop_loss_pct=sl_val,
    take_profit_pct=tp_val,
    risk_free_rate=risk_free,
)

# ── Onglets Principaux ────────────────────────────────────────────
tabs = st.tabs([
    "📊 Tableau de Bord & KPIs",
    "📈 Analyse Technique & Chandeliers",
    "🎯 Comparaison des Stratégies",
    "📉 Tests Statistiques & Distribution",
    "📅 Saisonnalité & Halvings",
])

# ══════════════════════════════════════════════════════════════════
# ONGLET 1 : TABLEAU DE BORD & KPIS
# ══════════════════════════════════════════════════════════════════
with tabs[0]:
    # Métriques Clés
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Capital Final</div>
            <div class="kpi-val {'positive' if backtest_res['final_value'] > initial_cap else 'negative'}">{backtest_res['final_value']:,.0f} <span style="font-size:1rem;">MAD</span></div>
            <div class="kpi-desc">Initial: {initial_cap:,.0f} MAD</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Rendement Total</div>
            <div class="kpi-val {'positive' if backtest_res['total_return_pct'] > 0 else 'negative'}">{backtest_res['total_return_pct']:+.1f}%</div>
            <div class="kpi-desc">CAGR Annuel: {backtest_res['cagr_pct']:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Ratio de Sharpe</div>
            <div class="kpi-val {'positive' if backtest_res['sharpe_ratio'] > 1 else 'neutral' if backtest_res['sharpe_ratio'] > 0 else 'negative'}">{backtest_res['sharpe_ratio']:.2f}</div>
            <div class="kpi-desc">Taux sans risque: {risk_free*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Drawdown Maximum</div>
            <div class="kpi-val negative">{backtest_res['max_drawdown_pct']:.2f}%</div>
            <div class="kpi-desc">Baisse max historique</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Trades & Win Rate</div>
            <div class="kpi-val neutral">{backtest_res['nb_trades']} <span style="font-size:1.1rem; color:#94a3b8;">trades</span></div>
            <div class="kpi-desc">Gagnants: {backtest_res['win_rate']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique d'évolution du portefeuille
    st.subheader(f"📈 Évolution de la Valeur du Portefeuille (MM{ma_short}/MM{ma_long} vs Buy & Hold)")

    # Calcul Buy & Hold pour le graphe
    btc_init_units = initial_cap / df['close_mad'].iloc[0]
    hold_series = btc_init_units * df['close_mad']
    
    # Placement sans risque pour le graphe
    days_arr = np.arange(len(df))
    rf_series = initial_cap * ((1.0 + risk_free) ** (days_arr / 365.0))

    fig_port = go.Figure()
    fig_port.add_trace(go.Scatter(
        x=df['date'], y=backtest_res['portfolio_series'],
        name=f"Stratégie MM ({ma_short}/{ma_long})",
        line=dict(color="#10b981", width=2.5)
    ))
    fig_port.add_trace(go.Scatter(
        x=df['date'], y=hold_series,
        name="Buy & Hold (Achat & Conservation)",
        line=dict(color="#f59e0b", width=1.8, dash="dot")
    ))
    fig_port.add_trace(go.Scatter(
        x=df['date'], y=rf_series,
        name=f"Placement Sans Risque ({risk_free*100:.1f}%)",
        line=dict(color="#64748b", width=1.5, dash="dash")
    ))
    fig_port.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=20, b=40),
        yaxis=dict(title="Valeur du Portefeuille (MAD)", type="log"),
        xaxis=dict(title="Date"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_port, use_container_width=True)

    # Graphique Drawdown Underwater
    col_dd1, col_dd2 = st.columns([2, 1])
    with col_dd1:
        st.subheader("📉 Drawdown Historique (% de baisse depuis le pic)")
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=df['date'], y=backtest_res['drawdown_series'],
            fill='tozeroy', name="Drawdown MM", line=dict(color="#ef4444", width=1.5)
        ))
        fig_dd.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            margin=dict(l=40, r=40, t=10, b=30),
            yaxis=dict(title="Drawdown (%)", ticksuffix="%"),
            xaxis=dict(title="Date"),
        )
        st.plotly_chart(fig_dd, use_container_width=True)

    with col_dd2:
        st.subheader("📋 Derniers Signaux Exécutés")
        if backtest_res['trade_logs']:
            trades_df = pd.DataFrame(backtest_res['trade_logs']).tail(10)
            trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
            trades_df['price'] = trades_df['price'].map("{:,.0f} MAD".format)
            trades_df['proceeds'] = trades_df['proceeds'].map("{:,.0f} MAD".format)
            trades_df['return_trade'] = trades_df['return_trade'].map("{:+.1f}%".format)
            st.dataframe(trades_df[['date', 'action', 'price', 'return_trade']], use_container_width=True)
        else:
            st.info("Aucun trade enregistré sur la période.")

# ══════════════════════════════════════════════════════════════════
# ONGLET 2 : ANALYSE TECHNIQUE & CHANDELIERS
# ══════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("🕯️ Graphique Chandelier Japonais & Indicateurs Techniques")

    # Options d'affichage
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_sma_short = st.checkbox(f"Afficher SMA {ma_short}", value=True)
    with c2:
        show_sma_long = st.checkbox(f"Afficher SMA {ma_long}", value=True)
    with c3:
        show_bb = st.checkbox("Bandes de Bollinger (20, 2)", value=False)
    with c4:
        show_sma_200 = st.checkbox("Afficher SMA 200", value=True)

    fig_tech = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Cours BTC/MAD (Bougies)", "Volume d'échange", "RSI (14)")
    )

    # Chandelier
    fig_tech.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open_mad'] if 'open_mad' in df.columns else df['open'],
        high=df['high_mad'] if 'high_mad' in df.columns else df['high'],
        low=df['low_mad'] if 'low_mad' in df.columns else df['low'],
        close=df['close_mad'],
        name="BTC/MAD"
    ), row=1, col=1)

    # Moyennes Mobiles
    if show_sma_short:
        fig_tech.add_trace(go.Scatter(
            x=df['date'], y=df[f'SMA_{ma_short}'],
            name=f"SMA {ma_short}", line=dict(color="#38bdf8", width=1.5)
        ), row=1, col=1)

    if show_sma_long:
        fig_tech.add_trace(go.Scatter(
            x=df['date'], y=df[f'SMA_{ma_long}'],
            name=f"SMA {ma_long}", line=dict(color="#f43f5e", width=1.5)
        ), row=1, col=1)

    if show_sma_200:
        fig_tech.add_trace(go.Scatter(
            x=df['date'], y=df['SMA_200'],
            name="SMA 200", line=dict(color="#a855f7", width=1.8, dash="dash")
        ), row=1, col=1)

    if show_bb:
        fig_tech.add_trace(go.Scatter(
            x=df['date'], y=df['BB_Upper'],
            name="BB Sup", line=dict(color="#94a3b8", width=1, dash="dot")
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df['date'], y=df['BB_Lower'],
            name="BB Inf", line=dict(color="#94a3b8", width=1, dash="dot"),
            fill='tonexty', fillcolor='rgba(148, 163, 184, 0.05)'
        ), row=1, col=1)

    # Volume
    colors_vol = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df['close_mad'], df.get('open_mad', df['close_mad']))]
    fig_tech.add_trace(go.Bar(
        x=df['date'], y=df['volume'],
        name="Volume", marker_color=colors_vol, opacity=0.7
    ), row=2, col=1)

    # RSI
    fig_tech.add_trace(go.Scatter(
        x=df['date'], y=df['RSI'],
        name="RSI 14", line=dict(color="#f59e0b", width=1.5)
    ), row=3, col=1)
    fig_tech.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)
    fig_tech.add_hline(y=30, line_dash="dash", line_color="#10b981", row=3, col=1)

    fig_tech.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        xaxis_rangeslider_visible=False,
        height=850,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1)
    )
    st.plotly_chart(fig_tech, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ONGLET 3 : COMPARAISON DES STRATÉGIES & DCA
# ══════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("🎯 Comparaison Rigoureuse des Stratégies d'Investissement")
    comp_df = run_comparison(
        df,
        initial_capital=initial_cap,
        short_window=ma_short,
        long_window=ma_long,
        risk_free_rate=risk_free
    )
    st.table(comp_df)

    st.markdown("---")

    # Simulateur DCA en MAD
    st.subheader("💡 Simulateur Dollar-Cost Averaging (DCA en Dirham Marocain)")
    st.write("Le DCA consiste à investir une somme fixe chaque mois de façon disciplinée, lissant la volatilité du Bitcoin.")

    col_dca1, col_dca2 = st.columns([1, 2])
    with col_dca1:
        monthly_dca = st.number_input(
            "Versement mensuel régulier (MAD)",
            min_value=100.0,
            max_value=100_000.0,
            value=1_000.0,
            step=100.0
        )
        dca_res = run_dca_backtest(df, monthly_investment=monthly_dca, fee_rate=fee_pct)

        st.metric("Total Fonds Investis", f"{dca_res['total_invested']:,.0f} MAD")
        st.metric("Valeur Finale du Portefeuille", f"{dca_res['final_value']:,.0f} MAD", delta=f"{dca_res['total_return_pct']:+.1f}%")
        st.metric("BTC Cumulés", f"{dca_res['btc_accumulated']:.4f} BTC")

    with col_dca2:
        fig_dca = go.Figure()
        fig_dca.add_trace(go.Scatter(
            x=df['date'], y=dca_res['portfolio_series'],
            name="Valeur du Portefeuille DCA (MAD)", line=dict(color="#10b981", width=2.5)
        ))
        fig_dca.add_trace(go.Scatter(
            x=df['date'], y=dca_res['invested_series'],
            name="Total Investi en MAD", line=dict(color="#94a3b8", width=2, dash="dash")
        ))
        fig_dca.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            margin=dict(l=40, r=40, t=20, b=40),
            yaxis=dict(title="MAD"),
            xaxis=dict(title="Date"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_dca, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ONGLET 4 : TESTS STATISTIQUES & DISTRIBUTION
# ══════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("📉 Propriétés Statistiques & Économétriques des Rendements")

    desc_stats = compute_descriptive_stats(df['return_pct'])
    tests = run_statistical_tests(df['return_pct'])

    c_s1, c_s2 = st.columns([1, 2])

    with c_s1:
        st.markdown("#### Statistiques Descriptives")
        st.write(f"- **Nombre d'observations** : {desc_stats['count']:,}")
        st.write(f"- **Rendement quotidien moyen** : `{desc_stats['mean_daily_pct']:.3f}%`")
        st.write(f"- **Écart-type quotidien** : `{desc_stats['std_daily_pct']:.2f}%`")
        st.write(f"- **Volatilité annualisée (365j)** : `{desc_stats['annualized_volatility_pct']:.2f}%`")
        st.write(f"- **Skewness (Asymétrie)** : `{desc_stats['skewness']:.3f}`")
        st.write(f"- **Kurtosis (Aplatissement)** : `{desc_stats['kurtosis']:.2f}` (Leptokurtique)")
        st.write(f"- **Pire journée** : `{desc_stats['min_pct']:.2f}%`")
        st.write(f"- **Meilleure journée** : `+{desc_stats['max_pct']:.2f}%`")

    with c_s2:
        # Histogramme interactif avec courbe normale
        clean_ret = df['return_pct'].dropna()
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=clean_ret, nbinsx=100, histnorm='probability density',
            name="Rendements Quotidiens", marker_color="#0284c7", opacity=0.75
        ))
        # Courbe Normale théorique
        x_vals = np.linspace(clean_ret.min(), clean_ret.max(), 500)
        norm_vals = (1 / (clean_ret.std() * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_vals - clean_ret.mean()) / clean_ret.std()) ** 2)
        fig_dist.add_trace(go.Scatter(
            x=x_vals, y=norm_vals, name="Loi Normale Théorique", line=dict(color="#ef4444", width=2)
        ))
        fig_dist.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            title="Distribution des Rendements Quotidiens vs Loi Normale",
            margin=dict(l=40, r=40, t=40, b=30),
            xaxis=dict(title="Rendement Quotidien (%)", range=[-15, 15]),
            yaxis=dict(title="Densité"),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("#### Synthèse des Tests Économétriques")
    test_rows = []

    if "adf" in tests and "statistic" in tests["adf"]:
        adf = tests["adf"]
        test_rows.append({
            "Test Économétrique": "Augmented Dickey-Fuller (ADF)",
            "Hypothèse Nulle (H0)": "Présence d'une racine unitaire (Non-stationnaire)",
            "P-Value": f"{adf['p_value']:.4e}",
            "Résultat": "✅ Stationnaire (p < 0.05)" if adf['is_stationary'] else "❌ Non-stationnaire",
            "Interprétation": "Les rendements n'ont pas de tendance de fond et oscillent autour de la moyenne."
        })

    if "shapiro" in tests and "statistic" in tests["shapiro"]:
        shp = tests["shapiro"]
        test_rows.append({
            "Test Économétrique": "Shapiro-Wilk",
            "Hypothèse Nulle (H0)": "Distribution Gaussienne normale",
            "P-Value": f"{shp['p_value']:.4e}",
            "Résultat": "❌ Non normale (p < 0.05)" if not shp['is_normal'] else "✅ Normale",
            "Interprétation": "Rejet ferme de la normalité; queues épaisses (Fat Tails)."
        })

    if "jarque_bera" in tests and "statistic" in tests["jarque_bera"]:
        jb = tests["jarque_bera"]
        test_rows.append({
            "Test Économétrique": "Jarque-Bera",
            "Hypothèse Nulle (H0)": "Symétrie et Kurtosis d'une loi normale",
            "P-Value": f"{jb['p_value']:.4e}",
            "Résultat": "❌ Rejet de la normalité" if not jb['is_normal'] else "✅ Normale",
            "Interprétation": "Excès de kurtosis confirmant le risque d'événements extrêmes (krachs/bull runs)."
        })

    if "arch" in tests and "lm_statistic" in tests["arch"]:
        arch = tests["arch"]
        test_rows.append({
            "Test Économétrique": "Test ARCH d'Engle",
            "Hypothèse Nulle (H0)": "Absence d'effets ARCH (Volatilité constante)",
            "P-Value": f"{arch['p_value']:.4e}",
            "Résultat": "✅ Effet ARCH Confirmé (p < 0.05)" if arch['has_arch_effect'] else "❌ Pas d'effet ARCH",
            "Interprétation": "Clusters de volatilité : les périodes de haute volatilité se regroupent dans le temps."
        })

    st.table(pd.DataFrame(test_rows))

# ══════════════════════════════════════════════════════════════════
# ONGLET 5 : SAISONNALITÉ & HALVINGS
# ══════════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("📅 Analyse de la Saisonnalité Mensuelle")
    
    monthly_df = compute_monthly_seasonality(df)
    if not monthly_df.empty:
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            st.dataframe(monthly_df[['month_name', 'mean', 'median', 'std']].rename(columns={
                'month_name': 'Mois',
                'mean': 'Rendement Moyen (%)',
                'median': 'Médiane (%)',
                'std': 'Écart-type (%)'
            }).style.format({
                'Rendement Moyen (%)': '{:+.2f}%',
                'Médiane (%)': '{:+.2f}%',
                'Écart-type (%)': '{:.2f}%'
            }), use_container_width=True)

        with col_m2:
            colors_m = ['#10b981' if r >= 0 else '#ef4444' for r in monthly_df['mean']]
            fig_m = go.Figure()
            fig_m.add_trace(go.Bar(
                x=monthly_df['month_name'], y=monthly_df['mean'],
                marker_color=colors_m, text=monthly_df['mean'].apply(lambda x: f"{x:+.2f}%"),
                textposition="outside"
            ))
            fig_m.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                title="Rendement Moyen Quotidien par Mois",
                margin=dict(l=40, r=40, t=40, b=40),
                yaxis=dict(title="Rendement Moyen (%)", ticksuffix="%"),
                xaxis=dict(title="Mois")
            )
            st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")
    st.subheader("⚡ Impact des Halvings de Bitcoin (2020 & 2024)")
    st.caption("Comparaison des fenêtres de 60 jours avant vs 60 jours après chaque halving.")
    
    halvings_impact = compute_halving_impact(df, window_days=60)
    if halvings_impact:
        st.dataframe(pd.DataFrame(halvings_impact).rename(columns={
            'halving': 'Événement',
            'date': 'Date',
            'ret_daily_before': 'Rendement Quotidien Avant (60j)',
            'ret_daily_after': 'Rendement Quotidien Après (60j)',
            'tot_ret_before': 'Performance Cumulée Avant (%)',
            'tot_ret_after': 'Performance Cumulée Après (%)',
            'vol_annual_before': 'Volatilité Avant (%)',
            'vol_annual_after': 'Volatilité Après (%)'
        }), use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 30px 0;">
    Bitcoin Analytics — BTC/MAD • Développé avec Streamlit, Plotly & Python • Analyse Quantitative & Économétrique
</div>
""", unsafe_allow_html=True)
