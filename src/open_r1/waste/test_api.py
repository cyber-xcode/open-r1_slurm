# ===================== Dynamic SMT loader from JSONL =====================
# Put this near the top of open_r1/test_api.py, before the Z3 tests import/use.

import os, json, random
import pytest

def _cc(snippet: str):
    # newline after opening ``` so your extractor sees content
    return [[{"content": f"```\n{snippet}\n```"}]]

# Where to read JSONL
# default to the path you showed; can override via env JSONL_PATH
JSONL_PATH = os.getenv(
    "JSONL_PATH",
    os.path.join(os.path.dirname(__file__),
                 "../..", "data_dir",
                 "c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_5k.jsonl"),
)

assert os.path.isfile(JSONL_PATH) , JSONL_PATH
# Optional: force a specific record by idx (filename), e.g. SMT_IDX="b1f9cf51d3904edada8c4aa470f7c246_3.smt"
SMT_IDX = os.getenv("SMT_IDX")

# Fallback candidates if SMT_IDX is not set
_SMT_FALLBACK_CANDIDATES = [
    "823e1f29bc8aebba70ab53e04b376998_2.smt",
    "85b8f2f0659658825b21891e8fde6bf9_2.smt",
    "0f4df6045f11e1b924b6ea775a67987a_1.smt",
    "e3ac1326e742c5ea9bf20d4223fde4c4_2.smt",
    "b1f9cf51d3904edada8c4aa470f7c246_3.smt",
    "5c82145cbd6c840035f8bc62d4bc7c84_1.smt",
    "9b24fd2c3d117c10a6e11dcb67cd95e6_4.smt",
    "e5db2753465b4f35244147fb9fc2ac36_0.smt",
    "49a1fca8251c27e0ad68da6040e6b594_3.smt",
    "a13f92c5b7364bfab7916358fb8d4a39_0.smt",
]

def _iter_jsonl(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue

def _pick_smt_from_jsonl(path, target_idx=None):
    """
    Return (smt_code, chosen_idx) by:
      1) target_idx (SMT_IDX),
      2) fallback candidate list (first match),
      3) otherwise the first entry that has 'smt_code'
    """
    if not os.path.isfile(path):
        return None, None, f"JSONL not found: {path}"

    selected = None

    # First pass: collect all entries (avoid loading huge files if big; break early when found)
    entries = []
    for obj in _iter_jsonl(path):
        idx = obj.get("idx")
        smt = obj.get("smt_code")
        if not smt:
            continue
        entries.append((idx, smt))

    if not entries:
        return None, None, f"No entries with 'smt_code' in {path}"

    # 1) exact target_idx
    if target_idx:
        for idx, smt in entries:
            if idx == target_idx:
                return smt, idx, None
        return None, None, f"SMT_IDX={target_idx} not found in {path}"

    # 2) first match from fallback candidate list
    for cand in _SMT_FALLBACK_CANDIDATES:
        for idx, smt in entries:
            if idx == cand:
                return smt, idx, None

    # 3) Otherwise take the first valid record
    idx, smt = entries[0]
    return smt, idx, None

# Resolve once per session and share via fixture
_SMT_TEXT, _SMT_IDX, _SMT_ERR = _pick_smt_from_jsonl(JSONL_PATH, SMT_IDX)

@pytest.fixture(scope="session")
def smt_text():
    print ( "_SMT_TEXT" , _SMT_TEXT )
    assert _SMT_TEXT is not None 
    if _SMT_TEXT is None:
        pytest.skip(
            f"Could not load SMT from JSONL. Reason: {_SMT_ERR}. "
            f"Set JSONL_PATH to your dataset, or SMT_IDX to a specific record."
        )
    return _SMT_TEXT

# ===================== End dynamic SMT loader =====================


