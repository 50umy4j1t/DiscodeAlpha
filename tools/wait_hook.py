import asyncio
import os
from typing import Any

import httpx

from agno.run.agent import RunInput
from agno.session import AgentSession
from agno.utils.log import log_warning

WAIT_MESSAGE = "Please wait, building apps take time ⏳"

# Tracks running typing tasks so the post_hook can cancel them
_typing_tasks: dict[str, asyncio.Task] = {}


async def _telegram_typing_loop(chat_id: str, token: str) -> None:
    """Send Telegram 'typing' chat action every 4 seconds until cancelled."""
    url = f"https://api.telegram.org/bot{token}/sendChatAction"
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.post(url, json={"chat_id": chat_id, "action": "typing"}, timeout=5)
            except httpx.HTTPError:
                pass
            await asyncio.sleep(4)



async def send_wait_message(
    run_input: RunInput,
    session: AgentSession,
    **kwargs: Any,
) -> None:
    """Pre-hook: sends a wait message and starts a background typing indicator."""
    session_id = session.session_id or ""
    user_id = session.user_id or ""

    # --- Telegram ---
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if tg_token and session_id:
        chat_id = session_id.split(":")[0] if ":" in session_id else session_id
        try:
            int(chat_id)
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    json={"chat_id": chat_id, "text": WAIT_MESSAGE},
                    timeout=5,
                )
            task = asyncio.create_task(_telegram_typing_loop(chat_id, tg_token))
            _typing_tasks[session_id] = task
            return
        except (ValueError, httpx.HTTPError) as e:
            log_warning(f"Failed to send Telegram wait message: {e}")

    # --- WhatsApp ---
    wa_token = os.environ.get("WHATSAPP_ACCESS_TOKEN") or os.environ.get("WA_ACCESS_TOKEN")
    wa_phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID") or os.environ.get("WA_PHONE_NUMBER_ID")
    if wa_token and wa_phone_id and user_id:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://graph.facebook.com/v21.0/{wa_phone_id}/messages",
                    headers={"Authorization": f"Bearer {wa_token}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": user_id,
                        "type": "text",
                        "text": {"body": WAIT_MESSAGE},
                    },
                    timeout=5,
                )
            return
        except httpx.HTTPError as e:
            log_warning(f"Failed to send WhatsApp wait message: {e}")

    # --- Slack ---
    # Slack's agno router already sets a typing status via assistant_threads_setStatus,
    # and the session_id format (entity_id:thread_id) doesn't contain the channel_id,
    # so we skip Slack here.


async def stop_typing(
    session: AgentSession,
    **kwargs: Any,
) -> None:
    """Post-hook: cancels the background typing indicator."""
    session_id = session.session_id or ""
    task = _typing_tasks.pop(session_id, None)
    if task and not task.done():
        task.cancel()
