from datetime import datetime, timedelta
import pandas as pd

# Load the holiday data
holidays = pd.read_csv('holidays.tsv', sep='\t', header=None, names=['date', 'holiday'], comment='#')
holidays['date'] = pd.to_datetime(holidays['date'], format='%Y%m%d')


def is_holiday(date: datetime.date):
    # Check if the provided date is a holiday or a weekend
    if date in holidays['date'].dt.date.values or date.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == date, 'holiday'].values[0] if date in holidays['date'].dt.date.values else "주말"
        date_str = date.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''


def is_today_holiday():
    # Check if today is a holiday or a weekend
    today = datetime.now().date()
    if today in holidays['date'].dt.date.values or today.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == today, 'holiday'].values[0] if today in holidays['date'].dt.date.values else "주말"
        date_str = today.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''


def is_tomorrow_holiday():
    # Check if tomorrow is a holiday or a weekend
    tomorrow = datetime.now().date() + timedelta(days=1)
    if tomorrow in holidays['date'].dt.date.values or tomorrow.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == tomorrow, 'holiday'].values[0] if tomorrow in holidays['date'].dt.date.values else "주말"
        date_str = tomorrow.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''


if __name__ == '__main__':
    b, s = is_holiday(datetime.strptime('20230527', '%Y%m%d'))
    print(b, s)
    b, s = is_tomorrow_holiday()
    print(b, s)
    b, s = is_today_holiday()
    print(b, s)
