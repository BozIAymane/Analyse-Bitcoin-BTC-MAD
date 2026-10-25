"""
indicators.py - Calcul des indicateurs techniques financiers.
"""
import pandas as pd
import numpy as np

def compute_indicators(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    """
    Calcule l'ensemble des indicateurs techniques sur la série temporelle BTC/MAD.
    """
    df = df.copy()
    price_col = 'close_mad' if 'close_mad' in df.columns else 'close'

    # Rendements quotidiens arithmétiques et logarithmiques
    df['return_pct'] = df[price_col].pct_change() * 100
    df['return_simple'] = df[price_col].pct_change()
    df['return_log'] = np.log(df[price_col] / df[price_col].shift(1))

    # Moyennes mobiles simples (SMA)
    df[f'SMA_{short_window}'] = df[price_col].rolling(window=short_window).mean()
    df[f'SMA_{long_window}'] = df[price_col].rolling(window=long_window).mean()
    df['SMA_200'] = df[price_col].rolling(window=200).mean()

    # Moyennes mobiles exponentielles (EMA)
    df['EMA_12'] = df[price_col].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df[price_col].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # RSI (Relative Strength Index 14)
    delta = df[price_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50)

    # Bandes de Bollinger (20 jours, 2 écarts-types)
    bb_window = 20
    df['BB_Mid'] = df[price_col].rolling(window=bb_window).mean()
    bb_std = df[price_col].rolling(window=bb_window).std()
    df['BB_Upper'] = df['BB_Mid'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Mid'] - (bb_std * 2)

    # Volatilité historique roulante (annualisée 365 jours pour crypto)
    df['Volatility_30d'] = df['return_simple'].rolling(window=30).std() * np.sqrt(365) * 100

    # Drawdown historique Buy & Hold
    cummax = df[price_col].cummax()
    df['Drawdown'] = ((df[price_col] - cummax) / cummax) * 100

    return df
