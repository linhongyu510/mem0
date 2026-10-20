"""
Repro: mem0 SQLiteManager.save_messages rolling-window keeps the OLDEST batch
rows and drops the NEWEST when one save_messages() call inserts >10 rows,
because every row in the batch shares a single `created_at` and the eviction
ORDER BY created_at DESC LIMIT 10 has no tiebreaker.

Run from the cloned mem0 repo (no deps needed; storage.py is stdlib-only).
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
MEM0 = os.environ.get("MEM0_REPO", "/tmp/memscan/repos/mem0")

spec = importlib.util.spec_from_file_location("storage", f"{MEM0}/mem0/memory/storage.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

def snapshot(mgr, scope):
    return [m["content"] for m in mgr.get_last_messages(scope, limit=100)]

# Fresh scope, one batch of 15 messages (as a multi-turn conversation would arrive).
m = S.SQLiteManager(":memory:")
batch = [{"role": "user", "content": f"msg-{i:02d}"} for i in range(15)]
m.save_messages(batch, "scope-A")
kept = snapshot(m, "scope-A")
print("inserted batch size : 15")
print("rows kept after eviction:", len(kept))
print("kept (oldest->newest)   :", kept)
print()
print("EXPECTED (newest 10)    :", [f"msg-{i:02d}" for i in range(5, 15)])
print("ACTUAL   (oldest 10)   :", kept)
assert kept == [f"msg-{i:02d}" for i in range(0, 10)], "unexpected"
print()
print(">>> BUG CONFIRMED: the newest 5 messages (msg-10..msg-14) were evicted;")
print(">>> the rolling window retained the oldest 10 instead.")
