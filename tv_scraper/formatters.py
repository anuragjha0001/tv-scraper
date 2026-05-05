"""Output Formatters"""

def to_pandas(tuples, **kwargs):
    import pandas as pd
    if not tuples:
        return pd.DataFrame()
    df = pd.DataFrame(tuples, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    return df.set_index('timestamp')

def to_numpy(tuples, **kwargs):
    import numpy as np
    if not tuples:
        return np.array([], dtype=[('timestamp','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('volume','f8')])
    dtype = np.dtype([('timestamp','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('volume','f8')])
    return np.array(tuples, dtype=dtype)

def to_arrays(tuples, **kwargs):
    import numpy as np
    if not tuples:
        return tuple(np.array([], dtype='f8') for _ in range(6))
    ts, o, h, l, c, v = zip(*tuples)
    return (np.array(ts,'i8'), np.array(o,'f8'), np.array(h,'f8'), np.array(l,'f8'), np.array(c,'f8'), np.array(v,'f8'))

def to_dict(tuples, keys=None, **kwargs):
    if not tuples:
        return []
    keys = keys or ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return [dict(zip(keys, bar)) for bar in tuples]

def to_json(tuples, **kwargs):
    import json
    data = to_dict(tuples)
    return json.dumps(data, **kwargs) if kwargs else json.dumps(data)

def to_csv(tuples, **kwargs):
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    writer.writerows(tuples)
    return output.getvalue()
