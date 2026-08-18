"""Short-term conversation buffer and rolling memory engine with asynchronous background consolidation."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class ConversationMessage:
    """A single message in the conversation history."""

    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionMemory:
    """Short-term sliding window conversation buffer with asynchronous background compaction."""

    def __init__(self, session_id: str, max_messages: int = 12):
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: List[ConversationMessage] = []
        self.summarized_context: str = ""
        self.total_turns_recorded: int = 0
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="mem_consolidator")
        self.background_tasks: List[Any] = []

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Append a message and dispatch asynchronous background compaction if threshold is reached."""
        msg = ConversationMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.total_turns_recorded += 1

        if len(self.messages) > self.max_messages:
            self.schedule_background_compaction()

    def schedule_background_compaction(self) -> None:
        """Dispatch background memory consolidation task without blocking user interactions."""
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._async_compact_history())
            self.background_tasks.append(task)
        except RuntimeError:
            # Fallback to background thread execution if outside an active event loop
            self._executor.submit(self._compact_history_sync)

    async def _async_compact_history(self) -> None:
        """Asynchronous background memory condensation worker."""
        await asyncio.to_thread(self._compact_history_sync)

    def _compact_history_sync(self) -> None:
        """Condense older messages into a rolling semantic summary in the background."""
        if len(self.messages) <= self.max_messages // 2:
            return

        # Evict oldest 4 messages into summary
        evicted = self.messages[:4]
        self.messages = self.messages[4:]

        evicted_text = "; ".join([f"{m.role}: {m.content[:100]}" for m in evicted])
        if self.summarized_context:
            self.summarized_context = f"{self.summarized_context} | Prior turns: {evicted_text}"
        else:
            self.summarized_context = f"Prior dialogue summary: {evicted_text}"

    def get_formatted_history(self) -> List[Dict[str, str]]:
        """Return history suitable for LLM context injection."""
        formatted = []
        if self.summarized_context:
            formatted.append({
                "role": "system",
                "content": f"[Previous Conversation Summary]: {self.summarized_context}",
            })

        for msg in self.messages:
            formatted.append({"role": msg.role, "content": msg.content})

        return formatted

    def get_raw_transcript(self) -> str:
        """Get plain text transcript of the current session."""
        lines = []
        for msg in self.messages:
            time_str = msg.timestamp.strftime("%H:%M:%S")
            lines.append(f"[{time_str}] {msg.role.upper()}: {msg.content}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Reset the conversation memory."""
        self.messages.clear()
        self.summarized_context = ""
        self.total_turns_recorded = 0
