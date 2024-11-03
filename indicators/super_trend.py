import pandas as pd
import talib


def super_trend(period: int, multiplier: int, data: pd.DataFrame) -> pd.DataFrame:

    data['ATR'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=period)  # calculate ATR

    data['upper'] = data['high'] + (multiplier * data['ATR'])
    data['lower'] = data['low'] - (multiplier * data['ATR'])

    name = f'ST{multiplier}'
    data[name] = pd.Series(dtype='float64')

    # calculate SuperTrend
    prev_trend = 'lower'
    for index, row in data.iterrows():
        if pd.isnull(row['upper']) or pd.isnull(row['lower']):
            continue

        upper = round(row['upper'], 2)if pd.isnull(data.loc[index - 1, 'upper']) else round(min(data.loc[index - 1, name], row['upper']), 2)
        lower = round(row['lower'], 2)if pd.isnull(data.loc[index - 1, 'lower']) else round(max(data.loc[index - 1, name], row['lower']), 2)

        close = row['close']
        open = row['open']

        if prev_trend == 'lower':
            if open >= lower:
                if close >= lower:
                    data.loc[index, name] = lower
                elif close < lower:
                    data.loc[index, name] = round(row['upper'], 2)
                    prev_trend = 'upper'
                else:
                    raise ValueError("error:001 Something went wrong")
            elif open < lower:
                data.loc[index, name] = round(row['upper'], 2)
                prev_trend = 'upper'
            else:
                raise ValueError("error:002 Something went wrong")
        elif prev_trend == 'upper':
            if open <= upper:
                if close <= upper:
                    data.loc[index, name] = upper
                elif close > upper:
                    data.loc[index, name] = round(row['lower'], 2)
                    prev_trend = 'lower'
                else:
                    raise ValueError("error:003 Something went wrong")
            elif open > upper:
                data.loc[index, name] = round(row['lower'], 2)
                prev_trend = 'lower'
            else:
                raise ValueError("error:004 Something went wrong")
        else:
            raise ValueError("error:005 Unexpected value")

    return data
