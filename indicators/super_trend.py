import pandas as pd

from indicators.atr import ATR


def super_trend(period: int, multiplier: int, quotes: pd.DataFrame, existing_data: pd.DataFrame, column: str) -> pd.DataFrame:
    if not existing_data[column].isna().any():  # if all values are not null, return existing_data. No need to update
        return existing_data

    first_nan_index = existing_data[column][existing_data[column].isnull()].index[0]  # get the index of the first nan

    if first_nan_index - period > 0:  # if there is enough data, because the first nan is not in too early (we need data for the period, for calculation ATR)
        quotes = quotes.loc[(first_nan_index - period):]  # get the data for the period, which needs to be updated

    atr_data = ATR(period, quotes)  # calculate ATR

    trend = pd.DataFrame(index=quotes.index)
    trend[['date', 'open', 'close']] = quotes[['date', 'open', 'close']]
    trend['upper'] = quotes['high'] + (multiplier * atr_data)
    trend['lower'] = quotes['low'] - (multiplier * atr_data)
    trend['trend'] = pd.Series(dtype='float64')

    # calculate SuperTrend
    prev_trend = 'lower'
    for index, row in trend.iterrows():
        if not pd.isna(existing_data.loc[index, column]):  # if not all values are null, use existing data
            trend.loc[index, 'trend'] = existing_data.loc[index, column]
        else:
            # prev_trend = row['lower'] if index == 0 else trend.loc[index - 1, 'trend']

            upper = round(row['upper'], 2)if index == 0 else round(min(trend.loc[index - 1, 'trend'], row['upper']), 2)
            lower = round(row['lower'], 2)if index == 0 else round(max(trend.loc[index - 1, 'trend'], row['lower']), 2)

            close = row['close']
            open = row['open']

            if prev_trend == 'lower':
                if open >= lower:
                    if close >= lower:
                        trend.loc[index, 'trend'] = lower
                    elif close < lower:
                        trend.loc[index, 'trend'] = round(row['upper'], 2)
                        prev_trend = 'upper'
                    else:
                        raise ValueError("error:001 Something went wrong")
                elif open < lower:
                    trend.loc[index, 'trend'] = round(row['upper'], 2)
                    prev_trend = 'upper'
                else:
                    raise ValueError("error:002 Something went wrong")
            elif prev_trend == 'upper':
                if open <= upper:
                    if close <= upper:
                        trend.loc[index, 'trend'] = upper
                    elif close > upper:
                        trend.loc[index, 'trend'] = round(row['lower'], 2)
                        prev_trend = 'lower'
                    else:
                        raise ValueError("error:003 Something went wrong")
                elif open > upper:
                    trend.loc[index, 'trend'] = round(row['lower'], 2)
                    prev_trend = 'lower'
                else:
                    raise ValueError("error:004 Something went wrong")
            else:
                raise ValueError("error:005 Unexpected value")

    if first_nan_index - period > 0:  # if there is enough data, because the first nan is not in too early
        # add SuperTrend to existing_data
        existing_data[column] = pd.concat([existing_data[column][:first_nan_index], trend['trend'][period:]], ignore_index=True)

    else:  # if there is not enough data, because the first nan is in too early
        existing_data[column] = trend['trend']

    return existing_data
