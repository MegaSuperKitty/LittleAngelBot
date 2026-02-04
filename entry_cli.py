# -*- coding: utf-8 -*-
"""CLI entry for LittleAngelBot (debug)."""
import asyncio
import os

import yaml

from little_angel_bot import LittleAngelBot

BASE_DIR = os.path.dirname(__file__)
HISTORY_DIR = os.path.join(BASE_DIR, "chat_history")
AGENT_ROOT = os.getenv("LITTLE_ANGEL_AGENT_WORKSPACE", os.path.join(BASE_DIR, "agent_workspace"))
os.makedirs(AGENT_ROOT, exist_ok=True)
LOCAL_SECRETS_PATH = os.path.join(BASE_DIR, "local_secrets.yaml")


def _load_local_secrets(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


_LOCAL_SECRETS = _load_local_secrets(LOCAL_SECRETS_PATH)


def _get_secret(name: str, fallback: str = "") -> str:
    if fallback:
        return fallback
    value = os.getenv(name, "")
    if value:
        return value
    local = _LOCAL_SECRETS.get(name, "")
    return "" if local is None else str(local)

# === Optional local config (set and keep here for convenience) ===
# Example: BRAVE_API_KEY = "your_brave_api_key"
BRAVE_API_KEY = _get_secret("BRAVE_API_KEY", "")
# Example: ZHIPU_API_KEY = "your_zhipu_api_key"
ZHIPU_API_KEY = _get_secret("ZHIPU_API_KEY", "")
# Example: DASHSCOPE_API_KEY = "your_dashscope_api_key"
DASHSCOPE_API_KEY = _get_secret("DASHSCOPE_API_KEY", "")
# Example: BOTPY_APPID = "your_bot_appid" (not used in debug)
BOTPY_APPID = _get_secret("BOTPY_APPID", "")
# Example: BOTPY_SECRET = "your_bot_secret" (not used in debug)
BOTPY_SECRET = _get_secret("BOTPY_SECRET", "")

# Push into env so tools can pick them up.
if BRAVE_API_KEY and not os.getenv("BRAVE_API_KEY"):
    os.environ["BRAVE_API_KEY"] = BRAVE_API_KEY
if ZHIPU_API_KEY and not os.getenv("ZHIPU_API_KEY"):
    os.environ["ZHIPU_API_KEY"] = ZHIPU_API_KEY
if DASHSCOPE_API_KEY and not os.getenv("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY
if BOTPY_APPID and not os.getenv("BOTPY_APPID"):
    os.environ["BOTPY_APPID"] = BOTPY_APPID
if BOTPY_SECRET and not os.getenv("BOTPY_SECRET"):
    os.environ["BOTPY_SECRET"] = BOTPY_SECRET


class _DebugState:
    def __init__(self):
        self.running_task: asyncio.Task | None = None
        self.cancel_requested = False
        self.pending_input = False
        self.reply_seq = 1

    def next_seq(self) -> int:
        current = self.reply_seq
        self.reply_seq += 1
        return current


async def _run_task(bot: LittleAngelBot, user_id: str, content: str, state: _DebugState) -> None:
    def is_cancelled() -> bool:
        return state.cancel_requested

    try:
        reply_text = await asyncio.to_thread(bot.run_task, user_id, content, is_cancelled)
    finally:
        state.running_task = None
        bot.clear_ask_handler(user_id)

    if reply_text:
        print(f"Bot> {reply_text}")
        if state.pending_input:
            print("Bot> 我现在任务完成了，我注意到你之前给我发了消息，但我都没有听见，你可以重新和我说一遍")
            state.pending_input = False


async def main_async() -> None:
    bot = LittleAngelBot(HISTORY_DIR, max_rounds=20, max_steps=20, agent_root=AGENT_ROOT)
    user_id = "debug_user"
    state = _DebugState()

    print("LittleAngelBot CLI (type /quit to exit)")
    print(f"Agent root: {AGENT_ROOT}")
    while True:
        try:
            content = (await asyncio.to_thread(input, "You> ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not content:
            continue
        if content.lower() in {"/quit", "/exit"}:
            print("Bye.")
            break

        if not os.getenv("DASHSCOPE_API_KEY", "").strip():
            print("需要先配置百炼 API Key，否则无法继续对话。")
            continue
        if not os.getenv("ZHIPU_API_KEY", "").strip():
            print("当前未配置智谱 Key，暂时无法使用搜索引擎功能。")

        if state.running_task is not None and not state.running_task.done():
            if bot.has_pending_human(user_id):
                if content == "停止任务":
                    state.cancel_requested = True
                    bot.cancel_pending_human(user_id)
                    print("Bot> 已停止任务。")
                else:
                    bot.provide_human_input(user_id, content)
                continue
            if content == "停止任务":
                state.cancel_requested = True
                bot.cancel_pending_human(user_id)
                print("Bot> 已停止任务。")
            else:
                state.pending_input = True
                print(
                    "Bot> 正在完成您给的任务，在任务完成或者失败前我都会捂住我的耳朵不听任何别的话，除非你显式的输入【停止任务】这4个字"
                )
            continue

        state.cancel_requested = False
        state.pending_input = False
        state.reply_seq = 1

        def ask_handler(uid: str, question: str) -> None:
            print(f"Bot> {question}")

        bot.set_ask_handler(user_id, ask_handler)
        state.running_task = asyncio.create_task(_run_task(bot, user_id, content, state))


if __name__ == "__main__":
    asyncio.run(main_async())
