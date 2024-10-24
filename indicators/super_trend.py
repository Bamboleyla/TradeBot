import pandas as pd

from indicators.atr import ATR


def super_trend(period: int, multiplier: int, quotes: pd.DataFrame, existing_data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the Super Trend indicator for the given quotes.

    :param period: The period for the ATR calculation.
    :param multiplier: The multiplier to use for the Super Trend calculation.
    :param quotes: The quotes DataFrame to process.
    :param existing_data: The existing DataFrame to add the Super Trend column to.
    :param column: The column name to use for the Super Trend data.
    :return: The existing_data DataFrame with the Super Trend column added.
    """
    atr_data = ATR(period, quotes)

    upper_band = quotes['high'] + (multiplier * atr_data)
    lower_band = quotes['low'] - (multiplier * atr_data)

    trend = pd.DataFrame(index=quotes.index)
    trend['close'] = quotes['close']
    trend['open'] = quotes['open']
    trend['upper'] = upper_band
    trend['lower'] = lower_band
    trend['trend'] = 0.00

    for index, row in trend.iterrows():
        if index == trend.index[0]:
            trend.loc[index, 'trend'] = row['lower'].round(2)
        else:
            prev_trend = trend.loc[index - 1, 'trend']

            upper = min(prev_trend, row['upper'])
            lower = max(prev_trend, row['lower'])

            close = row['close']
            open = row['open']

            if prev_trend < open:
                if close < prev_trend:
                    trend.loc[index, 'trend'] = row['upper'].round(2)
                else:
                    trend.loc[index, 'trend'] = lower.round(2)
            else:
                if close > prev_trend:
                    trend.loc[index, 'trend'] = row['lower'].round(2)
                else:
                    trend.loc[index, 'trend'] = upper.round(2)

    existing_data[column] = trend['trend']

    return existing_data
