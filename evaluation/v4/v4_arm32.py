"""v4_arm32 - the 3.2 arm of the 4.0 comparison: the full 3.2 head (w556) with the SAME instrument as 4.0 (ledger entries,
k, L, word, rho; law "3.2") and none of the law. Never admitted; used only to run the V4 panels on both arms identically."""
import time

from oracle_release_runtime_w556 import OracleReleaseRuntimeW556
from oracle_release_runtime_w557 import ledger_append, ledger_entry


class OracleV32Instrumented(OracleReleaseRuntimeW556):
    def chat(self, text, session_id="default"):
        t0 = time.perf_counter()
        r = super().chat(text, session_id)
        try:
            ledger_append(ledger_entry(text, session_id, r, round(1000.0 * (time.perf_counter() - t0), 1), "3.2"))
        except Exception:  # noqa: BLE001
            pass
        return r
