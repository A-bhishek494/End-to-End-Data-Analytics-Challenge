def rate(numerator, denominator):
    return numerator / denominator if denominator else None

def assert_unique(df, key):
    dup=df[df.duplicated(key, keep=False)]
    if not dup.empty:
        raise ValueError(f'Expected unique key {key}; found {len(dup)} duplicate rows')
    return True
