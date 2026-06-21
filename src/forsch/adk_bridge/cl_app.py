import os
import chainlit as cl
from forsch.adk_bridge.runtime import get_runtime
from forsch.adk_bridge.run import stream_agent

_TOKEN = os.environ.get("CHAT_TOKEN", "")


@cl.header_auth_callback
def header_auth(headers) -> cl.User | None:
    # The CRM embed (behind Frappe login) supplies the token; only then is a user issued.
    if _TOKEN and headers.get("x-chat-token") == _TOKEN:
        return cl.User(identifier="zach")
    return None if _TOKEN else cl.User(identifier="zach")  # open when no token set (dev)


@cl.set_chat_profiles
async def profiles(user):
    rt = get_runtime()
    return [cl.ChatProfile(name=name, markdown_description=f"Chat with the **{name}** agent.")
            for name in rt.agents]


@cl.on_chat_start
async def start():
    agent_name = cl.user_session.get("chat_profile") or next(iter(get_runtime().agents))
    cl.user_session.set("agent_name", agent_name)
    await cl.Message(content=f"Connected to **{agent_name}**.").send()


@cl.on_message
async def on_message(message: cl.Message):
    rt = get_runtime()
    agent_name = cl.user_session.get("agent_name")
    agent = rt.agents[agent_name]
    user = cl.user_session.get("user")
    sid = cl.user_session.get("id")            # Chainlit session id = the thread for now (Phase 2 maps to entity)
    msg = cl.Message(content="")
    async for tok in stream_agent(agent, agent_name, rt.session_service,
                                  user_id=f"chat:{user.identifier}", session_id=f"{agent_name}:{sid}", text=message.content):
        await msg.stream_token(tok)
    await msg.update()
