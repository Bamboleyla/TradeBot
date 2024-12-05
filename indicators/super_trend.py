import pandas as pd
import talib


def super_trend(config: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:

    def create_supet_trend_lines(period: int, multiplier: int):
        name_ATR = f'ATR {period}'
        name_upper_line = f'UP {multiplier}'
        name_lower_line = f'LOW {multiplier}'

        data[name_ATR] = talib.ATR(data['high'].values, data['low'].values, data['close'].values,
                                   timeperiod=period)  # calculate ATR for first period

        data[name_upper_line] = data['high'] + (multiplier * data[name_ATR])
        data[name_lower_line] = data['low'] - (multiplier * data[name_ATR])

        data[f'ST {period} {multiplier} UP'] = pd.Series(dtype=float)
        data[f'ST {period} {multiplier} LOW'] = pd.Series(dtype=float)

    for params in config:
        create_supet_trend_lines(params['period'], params['multiplier'])

    # calculate SuperTrends
    prev_trend = ['lower', 'lower']

    def calculate_trend(prefix: str, name: str, trend: str) -> None:
        if pd.isnull(row[f'UP {prefix}']) or pd.isnull(row[f'LOW {prefix}']):
            return

        upper = round(row[f'UP {prefix}'], 2) if pd.isnull(data.loc[index - 1, name+' UP']
                                                           ) else round(min(data.loc[index - 1, name+' UP'], row[f'UP {prefix}']), 2)
        lower = round(row[f'LOW {prefix}'], 2) if pd.isnull(data.loc[index - 1, name+' LOW']
                                                            ) else round(max(data.loc[index - 1, name+' LOW'], row[f'LOW {prefix}']), 2)

        close = row['close']
        open = row['open']

        if trend == 'lower':
            if open >= lower:
                if close >= lower:
                    data.loc[index, name+' LOW'] = lower
                elif close < lower:
                    data.loc[index, name + ' UP'] = round(row[f'UP {prefix}'], 2)
                    trend = 'upper'
                else:
                    raise ValueError("error:001 Something went wrong")
            elif open < lower:
                data.loc[index, name + ' UP'] = round(row[f'UP {prefix}'], 2)
                trend = 'upper'
            else:
                raise ValueError("error:002 Something went wrong")
        elif trend == 'upper':
            if open <= upper:
                if close <= upper:
                    data.loc[index, name + ' UP'] = upper
                elif close > upper:
                    data.loc[index, name + ' LOW'] = round(row[f'LOW {prefix}'], 2)
                    trend = 'lower'
                else:
                    raise ValueError("error:003 Something went wrong")
            elif open > upper:
                data.loc[index, name + ' LOW'] = round(row[f'LOW {prefix}'], 2)
                trend = 'lower'
            else:
                raise ValueError("error:004 Something went wrong")
        else:
            raise ValueError("error:005 Unexpected value")

        prev_trend[i] = trend

    for index, row in data.iterrows():
        for i, params in enumerate(config):
            calculate_trend(params['multiplier'], f'ST {params['period']} {params['multiplier']}', prev_trend[i])

    for params in config:
        data.drop(columns=[f'ATR {params['period']}', f'UP {params['multiplier']}', f'LOW {params['multiplier']}'], inplace=True)

    return data
