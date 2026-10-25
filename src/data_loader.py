"""
data_loader.py - Module d'acquisition et de traitement des données de marché.
Télécharge l'historique BTC et les taux réels de conversion USD/MAD ou EUR/MAD.
"""
import os
import logging
import pandas as pd
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "BTC_data.csv")

def load_btc_data(start_date="2019-01-01", end_date=None, force_download=False, fallback_csv=DEFAULT_CSV_PATH) -> pd.DataFrame:
    """
    Télécharge ou charge les données historiques du Bitcoin et convertit en MAD.
    Tente d'abord de récupérer le taux de change dynamique (USDMAD=X).
    En cas d'échec ou hors-ligne, utilise le fallback local.
    """
    df = None
    if not force_download and os.path.exists(fallback_csv):
        try:
            df = pd.read_csv(fallback_csv)
            logger.info("Données chargées depuis le cache local: %s", fallback_csv)
        except Exception as e:
            logger.warning("Erreur lors de la lecture du cache: %s", e)

    if df is None or force_download:
        try:
            logger.info("Téléchargement des données récentes depuis Yahoo Finance...")
            # Téléchargement BTC en USD
            btc = yf.download("BTC-USD", start=start_date, end=end_date, interval="1d", progress=False)
            if isinstance(btc.columns, pd.MultiIndex):
                btc.columns = btc.columns.droplevel(1)
            btc.reset_index(inplace=True)

            # Téléchargement du taux USD/MAD
            usd_mad = yf.download("USDMAD=X", start=start_date, end=end_date, interval="1d", progress=False)
            if isinstance(usd_mad.columns, pd.MultiIndex):
                usd_mad.columns = usd_mad.columns.droplevel(1)
            usd_mad.reset_index(inplace=True)

            # Merge sur la date
            btc['Date'] = pd.to_datetime(btc['Date']).dt.tz_localize(None)
            usd_mad['Date'] = pd.to_datetime(usd_mad['Date']).dt.tz_localize(None)

            merged = pd.merge(btc, usd_mad[['Date', 'Close']], on='Date', how='left', suffixes=('', '_fx'))
            merged['Close_fx'] = merged['Close_fx'].ffill().bfill().fillna(10.0)

            # Conversion en MAD
            df = pd.DataFrame()
            df['Date'] = merged['Date']
            df['Open'] = merged['Open'] * merged['Close_fx']
            df['High'] = merged['High'] * merged['Close_fx']
            df['Low'] = merged['Low'] * merged['Close_fx']
            df['Close'] = merged['Close'] * merged['Close_fx']
            df['Volume'] = merged['Volume']
            df['FX_Rate'] = merged['Close_fx']

            # Sauvegarde dans le CSV
            df.to_csv(fallback_csv, index=False)
            logger.info("Données téléchargées et sauvegardées avec succès.")
        except Exception as e:
            logger.error("Échec du téléchargement en ligne: %s. Utilisation du CSV local.", e)
            if os.path.exists(fallback_csv):
                df = pd.read_csv(fallback_csv)
            else:
                raise RuntimeError(f"Impossible de charger les données: {e}")

    # Nettoyage et standardisation
    df.columns = [c.lower() for c in df.columns]
    
    # Renommage des colonnes si format initial yfinance / TP
    column_mapping = {
        'fermeture_ajustee': 'close',
        'fermeture': 'close',
        'fermeture_mad': 'close_mad',
        'maximum': 'high',
        'minimum': 'low',
        'ouverture': 'open',
        'volume': 'volume'
    }
    df = df.rename(columns=column_mapping)
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

    # Assurer la présence des colonnes MAD
    if 'close_mad' not in df.columns:
        if 'close' in df.columns:
            # Si pas de colonne FX, appliquer taux moyen 10.2
            rate = df.get('fx_rate', 10.2)
            df['close_mad'] = df['close'] if 'fx_rate' in df.columns else df['close'] * rate
        else:
            raise ValueError("Colonne de prix de clôture introuvable.")

    if 'open_mad' not in df.columns and 'open' in df.columns:
        df['open_mad'] = df['open'] * df.get('fx_rate', 10.2)
    if 'high_mad' not in df.columns and 'high' in df.columns:
        df['high_mad'] = df['high'] * df.get('fx_rate', 10.2)
    if 'low_mad' not in df.columns and 'low' in df.columns:
        df['low_mad'] = df['low'] * df.get('fx_rate', 10.2)

    return df
