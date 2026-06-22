from types import SimpleNamespace
from forsch.adk_bridge.gateway.router import resolve_agent, build_source_defaults
from forsch.adk_bridge.gateway.sources_discord import discord_to_canonical

CONFIG = {
    "agents": {"build": {}, "assistant": {}, "dm_fallback": "assistant"},
    "mention_routing": True,
}
CHANNEL_MAP = {"team-build": "build"}
AGENTS = {"build", "assistant"}


def _msg(channel_name, author_id=1, guild=object(), content="hi"):
    chan = SimpleNamespace(name=channel_name, id=999)
    return SimpleNamespace(author=SimpleNamespace(id=author_id), guild=guild, channel=chan, content=content)


def test_channel_message_routes_like_old_logic():
    cfg = {**CONFIG, "source_defaults": build_source_defaults(CONFIG)}
    msg = _msg("team-build")
    canonical = discord_to_canonical(msg, CHANNEL_MAP)
    old = CHANNEL_MAP.get(msg.channel.name.lower())
    assert resolve_agent(canonical, AGENTS, cfg) == old == "build"


def test_dm_routes_to_fallback_like_old_logic():
    cfg = {**CONFIG, "source_defaults": build_source_defaults(CONFIG)}
    msg = _msg("irrelevant", guild=None)
    canonical = discord_to_canonical(msg, CHANNEL_MAP)
    assert canonical.target is None
    assert resolve_agent(canonical, AGENTS, cfg) == "assistant"


def test_unmapped_channel_returns_none_like_old_logic():
    cfg = {**CONFIG, "source_defaults": {}}
    msg = _msg("random-channel")
    canonical = discord_to_canonical(msg, CHANNEL_MAP)
    assert resolve_agent(canonical, AGENTS, cfg) is None


def test_session_id_and_sender_match_existing_keying():
    msg = _msg("team-build", author_id=42)
    canonical = discord_to_canonical(msg, CHANNEL_MAP)
    assert canonical.sender == "discord:42"
    assert canonical.session_id == "build:999"
