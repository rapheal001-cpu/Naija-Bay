"""Failure-tolerant helpers for the Channels layer (SkillStream pattern)."""

import asyncio
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

CHANNEL_LAYER_TIMEOUT = 3.0


async def _send(layer, group, message, timeout):
    await asyncio.wait_for(layer.group_send(group, message), timeout=timeout)


def safe_group_send(group, message, *, timeout=CHANNEL_LAYER_TIMEOUT):
    layer = get_channel_layer()
    if layer is None:
        return False
    try:
        async_to_sync(_send)(layer, group, message, timeout)
    except Exception:
        logger.warning(
            "Channel layer group_send failed (group=%s, type=%s); real-time delivery skipped",
            group,
            message.get("type") if isinstance(message, dict) else None,
            exc_info=True,
        )
        return False
    return True


async def async_safe_group_send(layer, group, message, *, timeout=CHANNEL_LAYER_TIMEOUT):
    try:
        await asyncio.wait_for(layer.group_send(group, message), timeout=timeout)
    except Exception:
        logger.warning(
            "Channel layer group_send failed (group=%s, type=%s); real-time delivery skipped",
            group,
            message.get("type") if isinstance(message, dict) else None,
            exc_info=True,
        )
        return False
    return True


async def safe_group_add(layer, group, channel_name, *, timeout=CHANNEL_LAYER_TIMEOUT):
    try:
        await asyncio.wait_for(layer.group_add(group, channel_name), timeout=timeout)
    except Exception:
        logger.warning("Channel layer group_add failed (group=%s)", group, exc_info=True)
        return False
    return True


async def safe_group_discard(layer, group, channel_name, *, timeout=CHANNEL_LAYER_TIMEOUT):
    try:
        await asyncio.wait_for(
            layer.group_discard(group, channel_name), timeout=timeout
        )
    except Exception:
        logger.warning("Channel layer group_discard failed (group=%s)", group, exc_info=True)
        return False
    return True


CHANNEL_LAYER_UNAVAILABLE_CLOSE_CODE = 1013
