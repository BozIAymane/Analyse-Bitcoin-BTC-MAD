"""
statistics.py - Tests statistiques économétriques avancés et analyse saisonnière.
"""
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf
from statsmodels.stats.diagnostic import het_arch

def compute_descriptive_stats(returns: pd.Series) -> dict:
    """Calcule les statistiques descriptives complètes d'une série de rendements."""
    clean_returns = returns.dropna()
    return {
        "count": int(clean_returns.count()),
        "mean_daily_pct": float(clean_returns.mean()),
        "std_daily_pct": float(clean_returns.std()),
        "annualized_return_pct": float(clean_returns.mean() * 365),
        "annualized_volatility_pct": float(clean_returns.std() * np.sqrt(365)),
        "skewness": float(stats.skew(clean_returns)),
        "kurtosis": float(stats.kurtosis(clean_returns)),  # excess kurtosis
        "min_pct": float(clean_returns.min()),
        "max_pct": float(clean_returns.max()),
        "median_pct": float(clean_returns.median()),
    }

def run_statistical_tests(returns: pd.Series) -> dict:
    """
    Exécute les tests formels :
    - Stationnarité (Augmented Dickey-Fuller)
    - Normalité (Shapiro-Wilk et Jarque-Bera)
    - Hétéroscédasticité conditionnelle (Effet ARCH d'Engle)
    """
    clean = returns.dropna()
    results = {}

    # 1. ADF Test (Stationnarité)
    try:
        adf_res = adfuller(clean, autolag='AIC')
        results["adf"] = {
            "statistic": float(adf_res[0]),
            "p_value": float(adf_res[1]),
            "is_stationary": bool(adf_res[1] < 0.05),
            "critical_values": adf_res[4]
        }
    except Exception as e:
        results["adf"] = {"error": str(e)}

    # 2. Shapiro-Wilk (échantillon sous-jacent max 5000)
    try:
        sample = clean.iloc[-4000:] if len(clean) > 4000 else clean
        shapiro_stat, shapiro_p = stats.shapiro(sample)
        results["shapiro"] = {
            "statistic": float(shapiro_stat),
            "p_value": float(shapiro_p),
            "is_normal": bool(shapiro_p > 0.05)
        }
    except Exception as e:
        results["shapiro"] = {"error": str(e)}

    # 3. Jarque-Bera
    try:
        jb_stat, jb_p = stats.jarque_bera(clean)
        results["jarque_bera"] = {
            "statistic": float(jb_stat),
            "p_value": float(jb_p),
            "is_normal": bool(jb_p > 0.05)
        }
    except Exception as e:
        results["jarque_bera"] = {"error": str(e)}

    # 4. Test d'effet ARCH (Engle)
    try:
        arch_test = het_arch(clean)
        results["arch"] = {
            "lm_statistic": float(arch_test[0]),
            "p_value": float(arch_test[1]),
            "has_arch_effect": bool(arch_test[1] < 0.05)
        }
    except Exception as e:
        results["arch"] = {"error": str(e)}

    return results

def compute_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la saisonnalité moyenne mensuelle."""
    df_copy = df.copy()
    if 'date' in df_copy.columns:
        df_copy['month'] = df_copy['date'].dt.month
        df_copy['month_name'] = df_copy['date'].dt.strftime('%B')
        df_copy['year'] = df_copy['date'].dt.year
    else:
        return pd.DataFrame()

    monthly = df_copy.groupby(['month', 'month_name'])['return_pct'].agg(['mean', 'median', 'std', 'count']).reset_index()
    monthly = monthly.sort_values('month').reset_index(drop=True)
    return monthly

def compute_halving_impact(df: pd.DataFrame, window_days: int = 60) -> list:
    """
    Analyse l'impact des halvings du Bitcoin (2020 et 2024).
    """
    halvings = [
        {"name": "Halving Mai 2020", "date": pd.Timestamp("2020-05-11")},
        {"name": "Halving Avril 2024", "date": pd.Timestamp("2024-04-19")}
    ]
    price_col = 'close_mad' if 'close_mad' in df.columns else 'close'
    impact_results = []

    for h in halvings:
        h_date = h["date"]
        before = df[(df['date'] >= h_date - pd.Timedelta(days=window_days)) & (df['date'] < h_date)]
        after = df[(df['date'] > h_date) & (df['date'] <= h_date + pd.Timedelta(days=window_days))]

        if len(before) > 0 and len(after) > 0:
            ret_before = before['return_pct'].mean()
            ret_after = after['return_pct'].mean()
            vol_before = before['return_pct'].std() * np.sqrt(365)
            vol_after = after['return_pct'].std() * np.sqrt(365)

            p_start_before = before[price_col].iloc[0]
            p_end_before = before[price_col].iloc[-1]
            tot_ret_before = ((p_end_before / p_start_before) - 1) * 100

            p_start_after = after[price_col].iloc[0]
            p_end_after = after[price_col].iloc[-1]
            tot_ret_after = ((p_end_after / p_start_after) - 1) * 100

            impact_results.append({
                "halving": h["name"],
                "date": h_date.strftime("%Y-%m-%d"),
                "ret_daily_before": round(ret_before, 2),
                "ret_daily_after": round(ret_after, 2),
                "tot_ret_before": round(tot_ret_before, 2),
                "tot_ret_after": round(tot_ret_after, 2),
                "vol_annual_before": round(vol_before, 2),
                "vol_annual_after": round(vol_after, 2),
            })

    return impact_results
