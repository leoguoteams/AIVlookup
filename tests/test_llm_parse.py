import json
import sys
import os
import types

# Ensure the repo root (where main.py resides) is in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the LLM helper from main.py
try:
    from main import llm_find_best_from_top3
except Exception as e:
    raise SystemExit(f"Cannot import llm_find_best_from_top3: {e}")

class DummyResp:
    def __init__(self, data):
        self.status_code = 200
        self._data = data
    def json(self):
        return self._data

def test_llm_parse_top3_json(monkeypatch):
    # Prepare a dummy top3 data and A/B data
    a_text = "A材料"
    top3_data = [("C1","NameA","SpecA","SizeA"), ("C2","NameB","SpecB","SizeB"), ("C3","NameC","SpecC","SizeC")]
    # Simulate LL.M JSON response: top3 with one item at index 0 with score 85
    json_content = json.dumps({"top3": [{"index": 0, "score": 85}], "best_index": 0})
    resp = DummyResp({"output": {"choices": [{"message": {"content": json_content}}]}})

    import requests
    def fake_post(url, json=None, headers=None, verify=None, timeout=None):
        return resp
    monkeypatch.setattr(requests, "post", fake_post)

    result = llm_find_best_from_top3(a_text, top3_data, api_key="test", log_func=lambda x: None)
    # Expect best_idx=0 and the code/name/spec/size come from top3_data[0]
    assert isinstance(result, tuple) and len(result) >= 6
    best_idx, code, name, spec, size, score = result
    assert best_idx == 0
    assert code == top3_data[0][0]
    assert name == top3_data[0][1]
    assert spec == top3_data[0][2]
    assert size == top3_data[0][3]
    assert score == 85

def test_llm_parse_old_format(monkeypatch):
    # Old format: {"index":0, "score":85}
    a_text = "A材料"
    top3_data = [("C1","NameA","SpecA","SizeA")]
    json_content = json.dumps({"index": 0, "score": 85})
    resp = DummyResp({"output": {"choices": [{"message": {"content": json_content}}]}})
    import requests
    def fake_post(url, json=None, headers=None, verify=None, timeout=None):
        return resp
    monkeypatch.setattr(requests, "post", fake_post)
    result = llm_find_best_from_top3(a_text, top3_data, api_key="test", log_func=lambda x: None)
    assert isinstance(result, tuple) and len(result) >= 6
