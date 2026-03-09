# -*- coding: utf-8 -*-
"""CLI entry point for LittleAngelBot local debugging."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from channels.common import AGENT_ROOT, HISTORY_DIR, LOCAL_SECRETS_PATH, load_local_secrets

from little_angel_bot import LittleAngelBot
from llm_provider import validate_llm_config


STOP_TASK_COMMANDS = {"stop_task", "停止任务"}
_LOCAL_SECRETS = load_local_secrets(LOCAL_SECRETS_PATH)


def _get_secret(name: str, fallback: str = "") -> str:
    """Return secret value from fallback, env, or local YAML.
    
    Args:
        name (str): Input value for name.
        fallback (str): Input value for fallback.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if fallback:
        return fallback
    value = os.getenv(name, "")
    if value:
        return value
    local = _LOCAL_SECRETS.get(name, "")
    return "" if local is None else str(local)


# Optional local config values for convenience.
LLM_API_KEY = _get_secret("LLM_API_KEY", "")
LLM_BASE_URL = _get_secret("LLM_BASE_URL", "")
LLM_MODEL = _get_secret("LLM_MODEL", "")
LLM_PROVIDER = _get_secret("LLM_PROVIDER", "")
BOTPY_APPID = _get_secret("BOTPY_APPID", "")
BOTPY_SECRET = _get_secret("BOTPY_SECRET", "")


# Export local config to environment if missing there.
for env_name, env_value in [
    ("LLM_API_KEY", LLM_API_KEY),
    ("LLM_BASE_URL", LLM_BASE_URL),
    ("LLM_MODEL", LLM_MODEL),
    ("LLM_PROVIDER", LLM_PROVIDER),
    ("BOTPY_APPID", BOTPY_APPID),
    ("BOTPY_SECRET", BOTPY_SECRET),
]:
    if env_value and not os.getenv(env_name):
        os.environ[env_name] = env_value


class _DebugState:
    """Track in-flight task status for the interactive CLI loop.
    
    Attributes:
        running_task (asyncio.Task | None): Instance field for running task.
        cancel_requested (bool): Instance field for cancel requested.
        pending_input (bool): Instance field for pending input.
        reply_seq (int): Instance field for reply seq.
    """

    def __init__(self):
        """Initialize task state fields.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        self.running_task: asyncio.Task | None = None
        self.cancel_requested = False
        self.pending_input = False
        self.reply_seq = 1

    def next_seq(self) -> int:
        """Return next reply sequence id.
        
        Args:
            None.
        
        Returns:
            int: Result produced by this function.
        """
        current = self.reply_seq
        self.reply_seq += 1
        return current


async def _run_task(bot: LittleAngelBot, user_id: str, content: str, state: _DebugState) -> None:
    """Execute one bot task and print final output to CLI.
    
    Args:
        bot (LittleAngelBot): Input value for bot.
        user_id (str): Identifier for the user.
        content (str): Text content to process.
        state (_DebugState): Input value for state.
    
    Returns:
        None: This method does not return a value.
    
    Note:
        This is a private helper used internally by the module/class.
    """

    def is_cancelled() -> bool:
        """Provide cancellation state to agent runtime.
        
        Args:
            None.
        
        Returns:
            bool: True when the condition is satisfied; otherwise False.
        """
        return state.cancel_requested

    try:
        reply_text = await asyncio.to_thread(bot.run_task, user_id, content, is_cancelled)
    finally:
        state.running_task = None
        bot.clear_ask_handler(user_id)

    if reply_text:
        print(f"Bot> {reply_text}")
        if state.pending_input:
            print("Bot> Task finished. I saw your earlier message; please send it again.")
            state.pending_input = False


async def main_async() -> None:
    """Run the interactive CLI chat loop.
    
    Args:
        None.
    
    Returns:
        None: This method does not return a value.
    """
    bot = LittleAngelBot(str(HISTORY_DIR), max_rounds=20, max_steps=20, agent_root=str(AGENT_ROOT))
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

        llm_error = validate_llm_config()
        if llm_error:
            print(f"LLM config is incomplete: {llm_error}")
            print("Please set LLM_API_KEY (required).")
            continue

        normalized = content.strip().lower()

        if state.running_task is not None and not state.running_task.done():
            if bot.has_pending_human(user_id):
                if normalized in STOP_TASK_COMMANDS:
                    state.cancel_requested = True
                    bot.cancel_pending_human(user_id)
                    print("Bot> Task stopped.")
                else:
                    bot.provide_human_input(user_id, content)
                continue

            if normalized in STOP_TASK_COMMANDS:
                state.cancel_requested = True
                bot.cancel_pending_human(user_id)
                print("Bot> Task stopped.")
            else:
                state.pending_input = True
                print("Bot> A task is running. Send 'stop_task' to interrupt.")
            continue

        state.cancel_requested = False
        state.pending_input = False
        state.reply_seq = 1

        def ask_handler(uid: str, question: str) -> None:
            """Render ask-human questions in CLI output.
            
            Args:
                uid (str): Input value for uid.
                question (str): Input value for question.
            
            Returns:
                None: This method does not return a value.
            """
            print(f"Bot> {question}")

        bot.set_ask_handler(user_id, ask_handler)
        state.running_task = asyncio.create_task(_run_task(bot, user_id, content, state))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
