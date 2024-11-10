import pandas as pd
import talib


def super_trend(config: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:

    data['ATR_fast'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values,
                                 timeperiod=config.iloc[0]['period'])  # calculate ATR for first period

    data['upper_fast'] = data['high'] + (config.iloc[0]['multiplier'] * data['ATR_fast'])
    data['lower_fast'] = data['low'] - (config.iloc[0]['multiplier'] * data['ATR_fast'])

    data['ATR_slow'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values,
                                 timeperiod=config.iloc[1]['period'])  # calculate ATR for second period

    data['upper_slow'] = data['high'] + (config.iloc[1]['multiplier'] * data['ATR_slow'])
    data['lower_slow'] = data['low'] - (config.iloc[1]['multiplier'] * data['ATR_slow'])

    # calculate SuperTrends
    prev_trend_fast = 'lower'
    prev_trend_slow = 'lower'

    for index, row in data.iterrows():

        def calculate_trend(prefix: str, name: str, prev_trend: str) -> None:
            if pd.isnull(row['upper_'+prefix]) or pd.isnull(row['lower_'+prefix]):
                return

            upper = round(row['upper_'+prefix], 2)if pd.isnull(data.loc[index - 1, 'upper_'+prefix]
                                                               ) else round(min(data.loc[index - 1, name], row['upper_'+prefix]), 2)
            lower = round(row['lower_'+prefix], 2)if pd.isnull(data.loc[index - 1, 'lower_'+prefix]
                                                               ) else round(max(data.loc[index - 1, name], row['lower_'+prefix]), 2)

            close = row['close']
            open = row['open']

            if prev_trend == 'lower':
                if open >= lower:
                    if close >= lower:
                        data.loc[index, name] = lower
                    elif close < lower:
                        data.loc[index, name] = round(row['upper_'+prefix], 2)
                        prev_trend = 'upper'
                    else:
                        raise ValueError("error:001 Something went wrong")
                elif open < lower:
                    data.loc[index, name] = round(row['upper_'+prefix], 2)
                    prev_trend = 'upper'
                else:
                    raise ValueError("error:002 Something went wrong")
            elif prev_trend == 'upper':
                if open <= upper:
                    if close <= upper:
                        data.loc[index, name] = upper
                    elif close > upper:
                        data.loc[index, name] = round(row['lower_'+prefix], 2)
                        prev_trend = 'lower'
                    else:
                        raise ValueError("error:003 Something went wrong")
                elif open > upper:
                    data.loc[index, name] = round(row['lower_'+prefix], 2)
                    prev_trend = 'lower'
                else:
                    raise ValueError("error:004 Something went wrong")
            else:
                raise ValueError("error:005 Unexpected value")

            if prefix == 'fast':
                nonlocal prev_trend_fast
                prev_trend_fast = prev_trend
            elif prefix == 'slow':
                nonlocal prev_trend_slow
                prev_trend_slow = prev_trend

        calculate_trend('fast', 'ST_FAST', prev_trend_fast)
        calculate_trend('slow', 'ST_SLOW', prev_trend_slow)

    data.drop(columns=['ATR_fast', 'ATR_slow', 'upper_fast', 'lower_fast', 'upper_slow', 'lower_slow'], inplace=True)

    return data
