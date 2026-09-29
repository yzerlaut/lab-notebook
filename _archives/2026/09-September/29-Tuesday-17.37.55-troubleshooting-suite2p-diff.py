# %%
import numpy as np, pprint
old = np.load('/Users/yann/Desktop/good/ops.npy', allow_pickle=True).item()
new = np.load('/Users/yann/Desktop/bad/settings.npy', allow_pickle=True).item()
# same for db.npy
def diff(a, b, p=''):
    for k in sorted(set(a)|set(b)):
        if isinstance(a.get(k), dict) and isinstance(b.get(k), dict): diff(a[k], b[k], p+k+'.')
        elif repr(a.get(k)) != repr(b.get(k)): print(p+k, ':', a.get(k), '->', b.get(k))
diff(old, new)
# %%
