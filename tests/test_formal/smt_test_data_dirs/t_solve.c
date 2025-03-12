int main() {
    int lo, mid, hi;
    __VERIFIER_assume( mid > 0 && lo == 0 && hi == 2 * mid);
    while(mid > 0) {
        lo = lo + 1;
        hi = hi - 1;
        mid = mid - 1;
    }
    assert(lo == hi);
}
