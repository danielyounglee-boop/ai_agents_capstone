"""Unit tests for memory and persistence engine."""

import os
import shutil
import pytest
from src.ai_agents_capstone.memory.session_memory import SessionMemory
from src.ai_agents_capstone.memory.profile_store import StudentProfileStore
from src.ai_agents_capstone.models.profile import StudentProfile, IEPAccommodation


def test_session_memory_rolling_buffer():
    memory = SessionMemory(session_id="test_sess", max_messages=4)
    for i in range(8):
        memory.add_message(role="user", content=f"Message {i}")

    # Should have compacted older messages into summarized_context
    assert len(memory.messages) <= 4
    assert len(memory.summarized_context) > 0


@pytest.mark.asyncio
async def test_session_memory_background_compaction():
    """Verify asynchronous background compaction worker execution."""
    memory = SessionMemory(session_id="test_async_sess", max_messages=4)
    for i in range(6):
        memory.add_message(role="user", content=f"Async message {i}")
    
    memory.schedule_background_compaction()
    # Allow background worker to complete
    import asyncio
    await asyncio.sleep(0.05)
    assert len(memory.messages) <= 4
    assert len(memory.summarized_context) > 0


def test_student_profile_store(tmp_path):
    store_dir = tmp_path / "profiles"
    store = StudentProfileStore(storage_dir=str(store_dir))

    profile = StudentProfile(
        student_id="test_student_01",
        name="Test Student",
        grade_level=4,
        reading_grade_level=3.5,
        interests=["Robots"],
        accommodations=[
            IEPAccommodation(category="visual_scaffolding", description="Use visual diagrams")
        ],
    )
    store.save_profile(profile)

    loaded = store.get_profile("test_student_01")
    assert loaded is not None
    assert loaded.name == "Test Student"
    assert loaded.reading_grade_level == 3.5

    # Test mastery vector update
    store.update_mastery("test_student_01", "fractions", "Fractions Addition", 0.9)
    updated = store.get_profile("test_student_01")
    assert "fractions" in updated.mastery_vectors
    assert updated.mastery_vectors["fractions"].mastery_score >= 0.8
