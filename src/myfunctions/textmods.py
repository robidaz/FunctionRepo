import re

def cleanse_df(df):
    df.replace(
        to_replace='[^\x00-\x7f]',
        value='?',
        regex=True,
        inplace=True)
    
def normalize_spacing(string):
    try:
        string = re.sub(r'\s\s+', ' ', string)
        string = string.rstrip('\n')
        string = string.lstrip()
    except Exception:
        pass
    return string