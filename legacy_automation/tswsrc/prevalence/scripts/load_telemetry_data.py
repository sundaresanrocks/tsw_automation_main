

dates_str = '20140107,20140108,20140109,20140110,20140111,20140112,20140113,20140114'

def load_data_for_date(date_str):
    """Load data for one date from folder into telemetry database"""

def load_all_dates(date_cs_str):
    """Load for all dates from a comma separated string"""
    for date in dates_str.strip().split(','):
        print(date)


