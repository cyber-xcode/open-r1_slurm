import json
import re
import zlib
from ftfy import fix_text
from ftfy.badness import sequence_weirdness

def compression_ratio(text: str) -> float:
    """Calculate the compression ratio using zlib (compressed size / original size)."""
    original = text.encode('utf-8')
    if not original:
        return 1.0
    compressed = zlib.compress(original)
    return len(compressed) / len(original)

def is_mojibake(text: str,
                repetition_length: int = 20,
                compression_ratio_threshold: float = 0.3) -> bool:
    """
    Determines if the provided text is likely mojibake based on several heuristics.
    
    Heuristics used:
      1. Repeated sequence: Checks for any character repeated 'repetition_length' or more times.
      2. Compression ratio: Highly repetitive text compresses extremely well.
    
    Returns:
      True if the text is likely mojibake, False otherwise.
    """
    if not text:
        return False

    # Heuristic 1: Long repeated sequences.
    if re.search(r'(.)\1{' + str(repetition_length - 1) + r',}', text):
        return True

    # Heuristic 2: Compression ratio.
    comp_ratio = compression_ratio(text)
    if comp_ratio < compression_ratio_threshold:
        return True

    return False

def _contains_mojibake(value: str) -> bool:
    """Check if the text contains mojibake by comparing weirdness before and after fixing."""
    weirdness_before = sequence_weirdness(value)
    fixed_value = fix_text(value)
    weirdness_after = sequence_weirdness(fixed_value)
    return weirdness_after < weirdness_before

def string_len_sensitive(value: str, digit_threshold: int = 15) -> bool:
    """Check if the text contains a sequence of digits longer than the threshold."""
    digit_pattern = re.compile(r'\d{' + str(digit_threshold) + r',}')
    return bool(digit_pattern.search(value))

def is_wired_text(value: str) -> dict:
    value = value if type( value) else str( value )

    """Determine if the text contains mojibake using multiple heuristics."""
    info = {
        "flg_moj": _contains_mojibake(value),
        "flg_len": string_len_sensitive(value),
        "flg_heu": is_mojibake(value),
    }
    info["flg"] = any(info.values())
    return info["flg"]# int( info["flg"] )


