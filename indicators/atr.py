import pandas as pd


def ATR(period: int, quotes: pd.DataFrame) -> pd.Series:
    high_low = quotes['high'] - quotes['low']
    high_close = (quotes['high'] - quotes['close'].shift(1)).abs()
    low_close = (quotes['low'] - quotes['close'].shift(1)).abs()

    # true_range
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.ewm(span=period, adjust=False).mean()
