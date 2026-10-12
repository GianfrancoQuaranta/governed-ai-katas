import pytest

from eval_gate import Case, CapabilityResult, gate, run_eval


def fake_model(inp):
    if inp.get("explode"):
        raise RuntimeError("provider 500")
    return inp["answer"]


def case(id, capability, answer, expected, **extra):
    return Case(id, capability, {"answer": answer, **extra}, lambda out, e=expected: out == e)


CASES = [
    case("msg-1", "collection_msg", "ok", "ok"),
    case("msg-2", "collection_msg", "ok", "ok"),
    case("msg-3", "collection_msg", "wrong amount", "ok"),
    case("msg-4", "collection_msg", "ok", "ok"),
    case("cls-1", "complaint_class", "fraud", "fraud"),
    case("cls-2", "complaint_class", "billing", "billing"),
]


def test_groups_results_by_capability():
    results = run_eval(CASES, fake_model)
    assert set(results) == {"collection_msg", "complaint_class"}
    msg = results["collection_msg"]
    assert (msg.total, msg.passed) == (4, 3)
    assert msg.pass_rate == pytest.approx(0.75)
    assert msg.failed_ids == ["msg-3"]
    assert results["complaint_class"].pass_rate == pytest.approx(1.0)


def test_model_errors_count_as_failures():
    cases = [case("a", "cap", "x", "x"), case("b", "cap", "x", "x", explode=True)]
    result = run_eval(cases, fake_model)["cap"]
    assert (result.total, result.passed, result.failed_ids) == (2, 1, ["b"])


def test_check_errors_count_as_failures():
    def broken_check(out):
        raise KeyError("missing field")

    cases = [Case("a", "cap", {"answer": "x"}, broken_check)]
    assert run_eval(cases, fake_model)["cap"].failed_ids == ["a"]


def result(cap, passed, total):
    return CapabilityResult(cap, total, passed, passed / total, [])


def test_approves_when_everything_passes():
    results = {"a": result("a", 95, 100), "b": result("b", 99, 100)}
    decision = gate(results, {"a": 0.9, "b": 0.98})
    assert decision.approved and decision.reasons == []


def test_blocks_below_threshold():
    decision = gate({"a": result("a", 85, 100)}, {"a": 0.9})
    assert not decision.approved
    assert len(decision.reasons) == 1 and "a" in decision.reasons[0]


def test_blocks_capability_without_threshold():
    results = {"a": result("a", 100, 100), "summaries": result("summaries", 100, 100)}
    decision = gate(results, {"a": 0.9})
    assert not decision.approved
    assert any("summaries" in r for r in decision.reasons)


def test_blocks_threshold_without_results():
    decision = gate({"a": result("a", 100, 100)}, {"a": 0.9, "call_summary": 0.8})
    assert not decision.approved
    assert any("call_summary" in r for r in decision.reasons)


def test_blocks_regression_even_above_threshold():
    decision = gate({"a": result("a", 93, 100)}, {"a": 0.9}, baseline={"a": 0.97})
    assert not decision.approved
    assert any("a" in r for r in decision.reasons)


def test_small_drop_within_tolerance_is_ok():
    decision = gate({"a": result("a", 96, 100)}, {"a": 0.9}, baseline={"a": 0.97}, max_regression=0.02)
    assert decision.approved


def test_reports_every_problem():
    results = {"a": result("a", 80, 100), "b": result("b", 90, 100), "c": result("c", 50, 100)}
    decision = gate(results, {"a": 0.9, "b": 0.85}, baseline={"b": 0.99})
    assert not decision.approved
    for cap in ("a", "b", "c"):
        assert any(cap in r for r in decision.reasons)


@pytest.mark.stretch
def test_confidence_mode_blocks_small_lucky_samples():
    small = {"a": result("a", 20, 20)}
    assert gate(small, {"a": 0.9}).approved
    assert not gate(small, {"a": 0.9}, use_confidence=True).approved


@pytest.mark.stretch
def test_confidence_mode_passes_large_clean_samples():
    large = {"a": result("a", 998, 1000)}
    assert gate(large, {"a": 0.98}, use_confidence=True).approved
