"""
backtest.py - Moteur de backtest quantitatif réaliste pour le marché BTC/MAD.
Prend en compte :
- Frais de transaction (Trading fees)
- Pas de look-ahead bias (exécution au prix d'ouverture du lendemain)
- Gestion de risque : Stop-Loss, Take-Profit
- Comparaison : Stratégie MM vs Buy & Hold vs DCA (Dollar-Cost Averaging) vs Placement Sans Risque
"""
import pandas as pd
import numpy as np

def run_backtest_ma(
    df: pd.DataFrame,
    initial_capital: float = 1_000_000.0,
    short_window: int = 20,
    long_window: int = 50,
    fee_rate: float = 0.001,  # 0.1% par trade
    stop_loss_pct: float = None,  # Ex: 0.05 pour 5%
    take_profit_pct: float = None,  # Ex: 0.15 pour 15%
    risk_free_rate: float = 0.03  # 3% annuel (taux directeur Bank Al-Maghrib)
) -> dict:
    """
    Exécute le backtest de croisement de moyennes mobiles avec gestion réaliste des ordres.
    """
    df = df.copy().reset_index(drop=True)
    price_col = 'close_mad' if 'close_mad' in df.columns else 'close'
    open_col = 'open_mad' if 'open_mad' in df.columns else price_col

    # Calcul des MM
    ma_short = df[price_col].rolling(window=short_window).mean()
    ma_long = df[price_col].rolling(window=long_window).mean()

    # Signaux bruts calculés à la fermeture du jour t
    raw_signal = np.where(ma_short > ma_long, 1, 0)
    
    # Exécution réaliste à t+1 à l'ouverture pour éviter le Look-Ahead Bias
    positions = pd.Series(raw_signal, index=df.index).shift(1).fillna(0).values

    cash = initial_capital
    btc_held = 0.0
    portfolio_values = []
    trade_logs = []
    entry_price = 0.0

    for i in range(len(df)):
        current_open = df[open_col].iloc[i]
        current_close = df[price_col].iloc[i]
        target_pos = positions[i]
        date_i = df['date'].iloc[i] if 'date' in df.columns else i

        # Vérification Stop-Loss / Take-Profit si on a une position ouverte
        if btc_held > 0 and entry_price > 0:
            price_change = (current_close - entry_price) / entry_price
            hit_sl = stop_loss_pct and (price_change <= -stop_loss_pct)
            hit_tp = take_profit_pct and (price_change >= take_profit_pct)

            if hit_sl or hit_tp:
                # Vente forcée
                proceeds = btc_held * current_close * (1.0 - fee_rate)
                reason = "Stop-Loss" if hit_sl else "Take-Profit"
                trade_logs.append({
                    "date": date_i,
                    "action": f"SELL ({reason})",
                    "price": current_close,
                    "btc": btc_held,
                    "proceeds": proceeds,
                    "return_trade": price_change * 100
                })
                cash += proceeds
                btc_held = 0.0
                entry_price = 0.0
                target_pos = 0  # Position fermée

        # Exécution normale de signal
        if target_pos == 1 and btc_held == 0.0 and cash > 0:
            # Achat complet
            fee = cash * fee_rate
            invest_cash = cash - fee
            btc_held = invest_cash / current_open
            entry_price = current_open
            trade_logs.append({
                "date": date_i,
                "action": "BUY",
                "price": current_open,
                "btc": btc_held,
                "proceeds": -cash,
                "return_trade": 0.0
            })
            cash = 0.0

        elif target_pos == 0 and btc_held > 0:
            # Vente complète
            gross = btc_held * current_open
            fee = gross * fee_rate
            net_proceeds = gross - fee
            trade_ret = (current_open - entry_price) / entry_price * 100 if entry_price > 0 else 0
            trade_logs.append({
                "date": date_i,
                "action": "SELL (Signal)",
                "price": current_open,
                "btc": btc_held,
                "proceeds": net_proceeds,
                "return_trade": trade_ret
            })
            cash = net_proceeds
            btc_held = 0.0
            entry_price = 0.0

        # Valeur portefeuille fin de journée
        val = cash + (btc_held * current_close)
        portfolio_values.append(val)

    df['Strategy_Value'] = portfolio_values
    df['Strategy_Return'] = df['Strategy_Value'].pct_change()

    # Métriques de performance
    total_days = len(df)
    years = total_days / 365.0 if total_days > 0 else 1.0
    final_value = portfolio_values[-1]
    total_return_pct = ((final_value / initial_capital) - 1.0) * 100.0
    cagr_pct = (((final_value / initial_capital) ** (1.0 / max(years, 0.1))) - 1.0) * 100.0

    # Volatilité annualisée (base 365 jours pour crypto)
    daily_std = df['Strategy_Return'].std()
    annual_vol_pct = daily_std * np.sqrt(365) * 100.0

    # Ratio de Sharpe ajusté au taux sans risque
    excess_return = (cagr_pct / 100.0) - risk_free_rate
    sharpe_ratio = excess_return / (daily_std * np.sqrt(365)) if daily_std > 0 else 0.0

    # Max Drawdown
    cummax_strat = df['Strategy_Value'].cummax()
    drawdown_series = (df['Strategy_Value'] - cummax_strat) / cummax_strat * 100.0
    max_drawdown_pct = float(drawdown_series.min())

    # Statistiques des trades
    nb_trades = len(trade_logs) // 2
    profitable_trades = [t for t in trade_logs if t.get('return_trade', 0) > 0 and 'SELL' in t['action']]
    win_rate = (len(profitable_trades) / max(nb_trades, 1)) * 100.0

    return {
        "final_value": final_value,
        "total_return_pct": total_return_pct,
        "cagr_pct": cagr_pct,
        "annual_vol_pct": annual_vol_pct,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown_pct": max_drawdown_pct,
        "nb_trades": nb_trades,
        "win_rate": win_rate,
        "trade_logs": trade_logs,
        "portfolio_series": df['Strategy_Value'],
        "drawdown_series": drawdown_series
    }

def run_dca_backtest(
    df: pd.DataFrame,
    monthly_investment: float = 1_000.0,
    fee_rate: float = 0.001
) -> dict:
    """
    Stratégie Dollar-Cost Averaging (DCA) :
    Investit une somme fixe en MAD chaque 1er du mois (ou premier jour ouvré du mois).
    """
    df = df.copy().reset_index(drop=True)
    price_col = 'close_mad' if 'close_mad' in df.columns else 'close'

    total_invested = 0.0
    btc_accumulated = 0.0
    portfolio_values = []
    invested_series = []

    current_month = None

    for i in range(len(df)):
        date_i = df['date'].iloc[i] if 'date' in df.columns else None
        price = df[price_col].iloc[i]

        if date_i is not None:
            month_i = (date_i.year, date_i.month)
            if month_i != current_month:
                # Nouvel investissement mensuel
                current_month = month_i
                net_inv = monthly_investment * (1.0 - fee_rate)
                btc_bought = net_inv / price
                btc_accumulated += btc_bought
                total_invested += monthly_investment

        port_val = btc_accumulated * price
        portfolio_values.append(port_val)
        invested_series.append(total_invested)

    final_val = portfolio_values[-1]
    total_ret = ((final_val / max(total_invested, 1.0)) - 1.0) * 100.0

    return {
        "total_invested": total_invested,
        "final_value": final_val,
        "total_return_pct": total_ret,
        "btc_accumulated": btc_accumulated,
        "portfolio_series": pd.Series(portfolio_values, index=df.index),
        "invested_series": pd.Series(invested_series, index=df.index)
    }

def run_comparison(
    df: pd.DataFrame,
    initial_capital: float = 1_000_000.0,
    short_window: int = 20,
    long_window: int = 50,
    risk_free_rate: float = 0.03
) -> pd.DataFrame:
    """
    Compare côte à côte :
    1. Stratégie Moyennes Mobiles
    2. Buy & Hold (Achat et Conservation)
    3. Placement sans risque (Taux garanti 3% annuel)
    """
    price_col = 'close_mad' if 'close_mad' in df.columns else 'close'

    # 1. Stratégie MM
    res_ma = run_backtest_ma(
        df, initial_capital=initial_capital,
        short_window=short_window, long_window=long_window,
        risk_free_rate=risk_free_rate
    )

    # 2. Buy & Hold
    p_start = df[price_col].iloc[0]
    p_end = df[price_col].iloc[-1]
    hold_btc = initial_capital / p_start
    hold_final = hold_btc * p_end
    hold_ret = ((hold_final / initial_capital) - 1.0) * 100.0
    
    hold_daily_ret = df[price_col].pct_change()
    hold_vol = hold_daily_ret.std() * np.sqrt(365) * 100.0
    hold_cummax = (hold_btc * df[price_col]).cummax()
    hold_dd = (((hold_btc * df[price_col]) - hold_cummax) / hold_cummax * 100.0).min()
    years = len(df) / 365.0
    hold_cagr = (((hold_final / initial_capital) ** (1.0 / max(years, 0.1))) - 1.0) * 100.0
    hold_sharpe = ((hold_cagr / 100.0) - risk_free_rate) / (hold_daily_ret.std() * np.sqrt(365)) if hold_daily_ret.std() > 0 else 0

    # 3. Placement sans risque
    risk_free_final = initial_capital * ((1.0 + risk_free_rate) ** years)
    risk_free_ret = ((risk_free_final / initial_capital) - 1.0) * 100.0

    comparison_data = [
        {
            "Stratégie": f"Moyennes Mobiles (MM{short_window}/MM{long_window})",
            "Capital Final (MAD)": f"{res_ma['final_value']:,.0f}",
            "Rendement Total (%)": f"{res_ma['total_return_pct']:+.2f}%",
            "CAGR Annuel (%)": f"{res_ma['cagr_pct']:+.2f}%",
            "Volatilité Annuelle (%)": f"{res_ma['annual_vol_pct']:.2f}%",
            "Ratio de Sharpe": f"{res_ma['sharpe_ratio']:.2f}",
            "Drawdown Max (%)": f"{res_ma['max_drawdown_pct']:.2f}%",
            "Nombre de Trades": f"{res_ma['nb_trades']}"
        },
        {
            "Stratégie": "Buy & Hold (Achat & Conservation)",
            "Capital Final (MAD)": f"{hold_final:,.0f}",
            "Rendement Total (%)": f"{hold_ret:+.2f}%",
            "CAGR Annuel (%)": f"{hold_cagr:+.2f}%",
            "Volatilité Annuelle (%)": f"{hold_vol:.2f}%",
            "Ratio de Sharpe": f"{hold_sharpe:.2f}",
            "Drawdown Max (%)": f"{hold_dd:.2f}%",
            "Nombre de Trades": "1"
        },
        {
            "Stratégie": f"Placement Sans Risque ({risk_free_rate*100:.1f}%)",
            "Capital Final (MAD)": f"{risk_free_final:,.0f}",
            "Rendement Total (%)": f"{risk_free_ret:+.2f}%",
            "CAGR Annuel (%)": f"{risk_free_rate*100:.2f}%",
            "Volatilité Annuelle (%)": "0.00%",
            "Ratio de Sharpe": "0.00",
            "Drawdown Max (%)": "0.00%",
            "Nombre de Trades": "0"
        }
    ]

    return pd.DataFrame(comparison_data)
