from forsch.adk_bridge.gateway.message import CanonicalMessage
from forsch.adk_bridge.gateway.router import resolve_agent

AGENTS = {"build", "ops", "assistant", "shelby"}
CONFIG = {"mention_routing": True, "source_defaults": {"discord": "assistant"}}


def test_explicit_target_wins():
    m = CanonicalMessage(source="discord", sender="u", text="hi", target="build")
    assert resolve_agent(m, AGENTS, CONFIG) == "build"


def test_unknown_explicit_target_is_ignored():
    m = CanonicalMessage(source="discord", sender="u", text="hi", target="nope")
    assert resolve_agent(m, AGENTS, CONFIG) == "assistant"


def test_mention_routing():
    m = CanonicalMessage(source="sms", sender="u", text="hey @shelby look at this")
    assert resolve_agent(m, AGENTS, CONFIG) == "shelby"


def test_mention_is_case_insensitive_and_word_bounded():
    assert resolve_agent(CanonicalMessage(source="sms", sender="u", text="@OPS ping"), AGENTS, CONFIG) == "ops"
    assert resolve_agent(CanonicalMessage(source="sms", sender="u", text="@opsworld"), AGENTS, CONFIG) is None


def test_source_default_when_no_target_no_mention():
    m = CanonicalMessage(source="discord", sender="u", text="just chatting")
    assert resolve_agent(m, AGENTS, CONFIG) == "assistant"


def test_no_match_returns_none():
    m = CanonicalMessage(source="sms", sender="u", text="just chatting")
    assert resolve_agent(m, AGENTS, CONFIG) is None


def test_mention_routing_disabled():
    cfg = {"mention_routing": False, "source_defaults": {}}
    m = CanonicalMessage(source="sms", sender="u", text="@shelby hi")
    assert resolve_agent(m, AGENTS, cfg) is None
