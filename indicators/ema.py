import pandas as pd


class EMA_Indicator:
    """
    Calculates the Exponential Moving Average of a given time period.

    Attributes:
        None

    Methods:
        run: Calculates the Exponential Moving Average of a given time period and appends it to the existing data

    """

    def run(self, period: int, quotes: pd.DataFrame, existing_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the Exponential Moving Average of a given time period and appends it to the existing data

        Args:
            period (int): The time period for the Exponential Moving Average
            quotes (pd.DataFrame): The quotes for which the Exponential Moving Average should be calculated
            existing_data (pd.DataFrame): The existing data to which the calculated Exponential Moving Average should be appended

        Returns:
            pd.DataFrame: The existing data with the calculated Exponential Moving Average appended
        """
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
