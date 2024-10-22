import pandas as pd


def EMA(period: int, quotes: pd.DataFrame, existing_data: pd.DataFrame) -> pd.DataFrame:

    if existing_data['EMA'].isnull().all():
        existing_data['EMA'] = quotes['close'].ewm(span=period, adjust=False).mean().round(2)
        return existing_data

    if len(quotes) == len(existing_data):
        return existing_data

    last_index = existing_data.index[-1]
    next_index = quotes.index[quotes.index.get_loc(last_index) + 1]
    new_data = quotes.loc[next_index:, ['ticker', 'date']].copy()
    new_data['EMA'] = quotes.loc[next_index:, 'close'].ewm(span=period, adjust=False).mean().round(2)
    return pd.concat([existing_data, new_data], ignore_index=True)
