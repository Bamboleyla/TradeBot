import pandas as pd
import talib


def super_trend(config: pd.DataFrame, data: pd.DataFrame, last_data: pd.DataFrame = None) -> pd.DataFrame:

    def create_supet_trend_lines(period: int, multiplier: int) -> None:
        """Create SuperTrend lines for the given period and multiplier.

        This function calculates the Average True Range (ATR) for a specified period
        and uses it to determine the upper and lower SuperTrend lines by applying
        the specified multiplier.

        Args:
            period (int): The period over which to calculate the ATR.
            multiplier (int): The multiplier to apply to the ATR for the SuperTrend lines.
        """
        # Define column names for ATR and SuperTrend lines
        name_ATR = f'ATR {period}'
        name_upper_line = f'UP {multiplier}'
        name_lower_line = f'LOW {multiplier}'

        # Calculate ATR for the given period
        data[name_ATR] = talib.ATR(data['high'].values, data['low'].values, data['close'].values,
                                   timeperiod=period)

        # Calculate upper and lower SuperTrend lines using the multiplier
        data[name_upper_line] = data['high'] + (multiplier * data[name_ATR])
        data[name_lower_line] = data['low'] - (multiplier * data[name_ATR])

        # Initialize columns for the SuperTrend values
        data[f'ST {period} {multiplier} UP'] = pd.Series(dtype=float)
        data[f'ST {period} {multiplier} LOW'] = pd.Series(dtype=float)

    for params in config:
        create_supet_trend_lines(params['period'], params['multiplier'])

    # calculate SuperTrends
    prev_trend = ['lower'] * len(config)

    if last_data is not None:
        prev_trend.clear()
        for params in config:
            upper = f'ST {params["period"]} {params["multiplier"]} UP'
            lower = f'ST {params["period"]} {params["multiplier"]} LOW'
            if (not pd.isnull(last_data.iloc[-1][upper])):
                prev_trend.append('upper')
            elif (not pd.isnull(last_data.iloc[-1][lower])):
                prev_trend.append('lower')
            else:
                raise ValueError("error:006 Something went wrong")

    def calculate_trend(prefix: str, name: str, trend: str) -> None:
        """Calculate the SuperTrend value for a given period and multiplier based on the previous value and the current close/open price.

        The function takes into account the previous trend (lower or upper) and the current close/open price to determine the current SuperTrend value.

        Args:
            prefix (str): The prefix for the column names of the upper and lower SuperTrend lines.
            name (str): The name of the column in the data DataFrame to store the SuperTrend value.
            trend (str): The previous trend (lower or upper).
        """
        # Check if the upper and lower SuperTrend lines are None
        if pd.isnull(row[f'UP {prefix}']) or pd.isnull(row[f'LOW {prefix}']):
            # If there last data, copy the values from it
            if last_data is not None:
                data.loc[index, name + ' UP'] = last_data.loc[index, name + ' UP']
                data.loc[index, name + ' LOW'] = last_data.loc[index, name + ' LOW']
            # If last data is None, stop the calculation
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
        columns_to_drop = [
            f'ATR {params["period"]}',
            f'UP {params["multiplier"]}',
            f'LOW {params["multiplier"]}',
        ]
        data.drop(columns=columns_to_drop, inplace=True)

    return data
