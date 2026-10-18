from app.agents.orchestrator import Orchestrator


def test_dispatch_records_one_trace_entry():
    orch = Orchestrator()
    message = orch.dispatch(
        trace_id="trace-1",
        sender="orchestrator",
        recipient="narrator",
        payload={"note": "no-op"},
    )

    assert message.step == 0
    assert message.sender == "orchestrator"
    assert message.recipient == "narrator"

    trace = orch.get_trace("trace-1")
    assert len(trace) == 1
    assert trace[0].payload == {"note": "no-op"}


def test_dispatch_increments_step_per_trace():
    orch = Orchestrator()
    orch.dispatch(trace_id="trace-1", sender="orchestrator", recipient="scoring")
    second = orch.dispatch(trace_id="trace-1", sender="scoring", recipient="orchestrator")

    assert second.step == 1
    assert len(orch.get_trace("trace-1")) == 2


def test_traces_are_isolated_per_trace_id():
    orch = Orchestrator()
    orch.dispatch(trace_id="trace-a", sender="orchestrator", recipient="narrator")
    orch.dispatch(trace_id="trace-b", sender="orchestrator", recipient="verifier")

    assert len(orch.get_trace("trace-a")) == 1
    assert len(orch.get_trace("trace-b")) == 1
    assert orch.get_trace("trace-a")[0].recipient == "narrator"


def test_unknown_trace_id_returns_empty_list():
    orch = Orchestrator()
    assert orch.get_trace("does-not-exist") == []
