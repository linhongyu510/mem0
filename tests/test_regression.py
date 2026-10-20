"""Regression test: batch inserts must retain the NEWEST 10 messages."""
import importlib.util, os
MEM0 = os.environ.get("MEM0_REPO", "/tmp/memscan/repos/mem0")
spec = importlib.util.spec_from_file_location("storage", f"{MEM0}/mem0/memory/storage.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

def test_batch_inserts_keep_newest():
    m = S.SQLiteManager(":memory:")
    m.save_messages([{"role":"user","content":f"msg-{i:02d}"} for i in range(15)], "s")
    kept = [x["content"] for x in m.get_last_messages("s", limit=100)]
    assert kept == [f"msg-{i:02d}" for i in range(5,15)], f"kept wrong window: {kept}"

if __name__ == "__main__":
    test_batch_inserts_keep_newest()
    print("PASS")
