# -*- coding: utf-8 -*-
"""ReCAP: recursive planning with re-injection on top of ReAct."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import json

from ReAct import ReActAgent, get_response
from context import ContextWindowManager


class ReCAPAgent:
    """ReCAP planner + executor that wraps a base ReAct agent."""

    def __init__(
        self,
        base_agent: ReActAgent,
        max_depth: int = 3,
        max_subtasks: int = 5,
        max_steps: int = 20,
        store_internal_messages: bool = True,
        context_manager: Optional[ContextWindowManager] = None,
        summarizer=None,
    ):
        self.base_agent = base_agent
        self.max_depth = max_depth
        self.max_subtasks = max_subtasks
        self.max_steps = max_steps
        self.store_internal_messages = store_internal_messages
        self.context_manager = context_manager or base_agent.context_manager or ContextWindowManager()
        self.system_prompt = base_agent.system_prompt
        self.summarizer = summarizer

    def run(self, history: List[Dict[str, str]], tools=None, cancel_checker=None) -> Tuple[str, List[Dict[str, str]]]:
        context = history if hasattr(history, "get_messages") else None
        history_messages = context.get_history_messages() if context else (history or [])
        messages = list(history_messages or [])
        if context:
            context.set_runtime_messages(messages)
        new_messages: List[Dict[str, str]] = []
        task_text = self._latest_user_task(messages)
        if not task_text:
            return "", new_messages

        final_text, delta = self._solve(
            task_text, messages, tools, depth=0, cancel_checker=cancel_checker, context=context
        )
        return final_text, delta

    def _solve(
        self,
        task_text: str,
        messages: List[Dict[str, str]],
        tools,
        depth: int,
        cancel_checker=None,
        context=None,
    ) -> Tuple[str, List[Dict[str, str]]]:
        new_messages: List[Dict[str, str]] = []
        if cancel_checker and cancel_checker():
            return "", []
        plan = self._plan(task_text, messages)
        if not plan.get("subtasks"):
            plan = {
                "thought": "fallback",
                "subtasks": [{"task": task_text, "is_primitive": True}],
            }

        plan_msg = {"role": "assistant", "content": f"[ReCAP PLAN]\n{json.dumps(plan, ensure_ascii=False)}"}
        messages.append(plan_msg)
        new_messages.append(plan_msg)
        self._sync_context(context, messages)

        remaining = list(plan.get("subtasks", []))
        last_result = ""
        step_count = 0

        while remaining:
            if cancel_checker and cancel_checker():
                return "", []
            step_count += 1
            if step_count > self.max_steps:
                final_text = "Reached ReCAP step limit; returning partial result."
                assistant_msg = {"role": "assistant", "content": final_text}
                new_messages.append(assistant_msg)
                return last_result or final_text, new_messages
            current = remaining.pop(0)
            subtask = (current.get("task") or "").strip()
            is_primitive = bool(current.get("is_primitive"))
            if not subtask:
                continue

            subtask_msg = {"role": "user", "content": f"[Subtask] {subtask}"}
            messages.append(subtask_msg)
            new_messages.append(subtask_msg)
            self._sync_context(context, messages)

            if is_primitive or depth >= self.max_depth:
                result, sub_new = self.base_agent.run(messages, tools=tools, cancel_checker=cancel_checker)
            else:
                result, sub_new = self._solve(
                    subtask, messages, tools, depth + 1, cancel_checker=cancel_checker, context=context
                )
            messages.extend(sub_new)
            new_messages.extend(sub_new)
            self._sync_context(context, messages)
            last_result = result
            if self._needs_user_input(subtask, result):
                return last_result, new_messages

            reinject = {
                "role": "assistant",
                "content": self._format_reinject(task_text, subtask, result, remaining),
            }
            messages.append(reinject)
            new_messages.append(reinject)
            self._sync_context(context, messages)

            if remaining:
                refined = self._refine(task_text, remaining, subtask, result, messages)
                if refined.get("subtasks"):
                    remaining = list(refined["subtasks"])
                    refine_msg = {
                        "role": "assistant",
                        "content": f"[ReCAP UPDATE]\n{json.dumps(refined, ensure_ascii=False)}",
                    }
                    messages.append(refine_msg)
                    new_messages.append(refine_msg)
                    self._sync_context(context, messages)

        return last_result, new_messages

    @staticmethod
    def _sync_context(context, messages: List[Dict[str, str]]) -> None:
        if context is not None and hasattr(context, "set_runtime_messages"):
            context.set_runtime_messages(messages)

    def _plan(self, task_text: str, messages: List[Dict[str, str]]) -> Dict:
        prompt = (
            "你是任务规划器。请根据当前任务生成子任务列表，要求：\n"
            f"- 当前任务：{task_text}\n"
            f"- 子任务数量不超过 {self.max_subtasks}。\n"
            "- 显式标注 is_primitive（是否可直接执行的最小动作）。\n"
            "- 输出 JSON 且仅包含以下字段：thought, subtasks。\n"
            "- subtasks 中每一项只包含 task 与 is_primitive。\n"
        )
        triggered_by_non_assistant = messages and messages[-1].get("role") != "assistant"
        windowed = self.context_manager.compress_messages(
            messages,
            summarizer=self.summarizer,
            preserve_system=False,
            triggered_by_non_assistant=triggered_by_non_assistant,
        )
        planner_messages = [{"role": "system", "content": self.system_prompt}] + windowed + [
            {"role": "user", "content": prompt}
        ]
        response = get_response(planner_messages, tools=None, stream=False)
        return self._parse_plan(response.content, task_text)

    def _refine(
        self,
        task_text: str,
        remaining: List[Dict[str, object]],
        subtask: str,
        result: str,
        messages: List[Dict[str, str]],
    ) -> Dict:
        remain_json = json.dumps(remaining, ensure_ascii=False)
        prompt = (
            "你是任务规划器。请根据执行结果更新剩余子任务列表，要求：\n"
            f"- 当前任务：{task_text}\n"
            f"- 已完成子任务：{subtask}\n"
            f"- 执行结果：{result}\n"
            f"- 当前剩余子任务：{remain_json}\n"
            "- 输出 JSON 且仅包含以下字段：thought, subtasks。\n"
            "- subtasks 中每一项只包含 task 与 is_primitive。\n"
        )
        triggered_by_non_assistant = messages and messages[-1].get("role") != "assistant"
        windowed = self.context_manager.compress_messages(
            messages,
            summarizer=self.summarizer,
            preserve_system=False,
            triggered_by_non_assistant=triggered_by_non_assistant,
        )
        refiner_messages = [{"role": "system", "content": self.system_prompt}] + windowed + [
            {"role": "user", "content": prompt}
        ]
        response = get_response(refiner_messages, tools=None, stream=False)
        return self._parse_plan(response.content, task_text, fallback_remaining=remaining)

    def _parse_plan(
        self,
        content: Optional[str],
        task_text: str,
        fallback_remaining: Optional[List[Dict[str, object]]] = None,
    ) -> Dict:
        if not content:
            return {"thought": "empty", "subtasks": fallback_remaining or []}
        text = content.strip()
        data = _extract_json(text)
        if not isinstance(data, dict):
            return {"thought": "fallback", "subtasks": fallback_remaining or [{"task": task_text, "is_primitive": True}]}

        subtasks = []
        for item in data.get("subtasks", []) or []:
            task = (item.get("task") if isinstance(item, dict) else "") or ""
            task = str(task).strip()
            if not task:
                continue
            is_primitive = False
            if isinstance(item, dict):
                is_primitive = bool(item.get("is_primitive"))
            subtasks.append({"task": task, "is_primitive": is_primitive})
        if not subtasks and fallback_remaining is not None:
            subtasks = fallback_remaining
        return {"thought": str(data.get("thought", "")).strip(), "subtasks": subtasks}

    def _format_reinject(
        self,
        task_text: str,
        subtask: str,
        result: str,
        remaining: List[Dict[str, object]],
    ) -> str:
        remaining_text = json.dumps(remaining, ensure_ascii=False)
        return (
            "[ReCAP REINJECT]\n"
            f"Task: {task_text}\n"
            f"Done: {subtask}\n"
            f"Result: {result}\n"
            f"Remaining: {remaining_text}"
        )

    def _needs_user_input(self, subtask: str, result: str) -> bool:
        if not result:
            return False
        if any(k in subtask for k in ["ask user", "wait for user", "need user", "user input"]):
            return True
        text = result.strip()
        if text.endswith('?'):
            return True
        hints = ["please", "need", "tell me", "provide", "could you", "can you", "what is", "which"]
        return any(h in text for h in hints)

    def _latest_user_task(self, messages: List[Dict[str, str]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return (msg.get("content") or "").strip()
        return ""


def _extract_json(text: str):
    if not text:
        return None
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{") and part.endswith("}"):
                try:
                    return json.loads(part)
                except Exception:
                    pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None
