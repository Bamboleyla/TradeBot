import pandas as pd


class WithDoubleTrend():
    def __init__(self):
        pass

    def long_open(self, previous: pd.DataFrame, current: pd.DataFrame) -> dict:
        if pd.notna(previous['ST_FAST_UP']) and pd.notna(previous['ST_SLOW_LOW']) and pd.notna(current['ST_FAST_LOW']) and pd.notna(current['ST_SLOW_LOW']):
            if previous['close'] <= previous['ST_FAST_UP'] and previous['close'] > previous['ST_SLOW_LOW']:
                if current['open'] > current['ST_FAST_LOW'] and current['open'] > current['ST_SLOW_LOW']:
                    return {'signal': 'LONG_BUY', 'order': 'BUY_LIMIT', 'price': previous['ST_FAST_UP']}

    def long_close(self, row: pd.DataFrame) -> dict:
        if pd.notna(row['ST_FAST_LOW']):
            if row['close'] < row['ST_FAST_LOW'] or row['open'] < row['ST_FAST_LOW']:
                return {'signal': 'LONG_SELL', 'order': 'SELL_LIMIT', 'price': row['close']}

    def __short_open(self):
        pass

    def __short_close(self):
        pass
