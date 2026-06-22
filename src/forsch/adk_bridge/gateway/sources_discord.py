"""Discord source adapter: discord.Message -> CanonicalMessage (pure; no network)."""
from __future__ import annotations

from forsch.adk_bridge.gateway.message import CanonicalMessage


def discord_to_canonical(message, channel_map: dict[str, str]) -> CanonicalMessage:
    """Normalize a discord.Message. Resolves the channel->agent target (None for DMs,
    so the router's source default applies). Mirrors the keying the bridge already uses:
    sender=discord:<author id>, session_id=<agent>:<channel id>."""
    is_dm = getattr(message, "guild", None) is None
    target = None if is_dm else channel_map.get(message.channel.name.lower())
    prefix = target or "dm"
    return CanonicalMessage(
        source="discord",
        sender=f"discord:{message.author.id}",
        text=message.content,
        target=target,
        session_id=f"{prefix}:{message.channel.id}",
        raw=message,
    )
