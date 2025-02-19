def time_to_minutes(time_str):
    """Convert time string to minutes"""
    if pd.isna(time_str):
        return None
    try:
        h, m, s = map(float, time_str.split(':'))
        return h * 60 + m + s / 60
    except:
        return None
        
def time_to_hours(time_str):
    """Convert time string to hours"""
    if pd.isna(time_str):
        return None
    try:
        h, m, s = map(float, time_str.split(':'))
        return h + m / 60 + s / 3600
    except:
        return None