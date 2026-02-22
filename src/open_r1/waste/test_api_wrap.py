import importlib, os

import open_r1.test_api as t

def _reload():
    importlib.reload(t)
    return t

def _check(tmod):
    assert tmod._SMT_ERR is None
    print (tmod)
    assert isinstance(tmod._SMT_TEXT, str) and tmod._SMT_TEXT.strip()
    assert tmod._SMT_TEXT.lstrip().startswith("(")

def test_each_fallback_candidate():
    for cand in t._SMT_FALLBACK_CANDIDATES:
        os.environ["SMT_IDX"] = cand
        print ( cand )
        _check(_reload())


