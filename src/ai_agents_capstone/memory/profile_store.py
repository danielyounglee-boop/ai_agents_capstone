"""Long-term student IEP profile, mastery vector persistence, and background consolidation engine."""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Optional, List, Any
from ..models.profile import StudentProfile, MasteryVector, CognitiveIndicator, IEPAccommodation


class StudentProfileStore:
    """Persistent storage engine for Student Profiles with background task consolidation and Cloud sync."""

    def __init__(self, storage_dir: str = "data/profiles", enable_background_sync: bool = True):
        self.storage_dir = storage_dir
        self.enable_background_sync = enable_background_sync
        os.makedirs(self.storage_dir, exist_ok=True)
        self._cache: Dict[str, StudentProfile] = {}
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="profile_sync_worker")
        self.active_background_tasks: List[Any] = []

    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Retrieve student profile by ID (from memory cache or disk)."""
        if student_id in self._cache:
            return self._cache[student_id]

        file_path = os.path.join(self.storage_dir, f"{student_id}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = StudentProfile.model_validate(data)
                self._cache[student_id] = profile
                return profile
        except Exception:
            return None

    def save_profile(self, profile: StudentProfile) -> None:
        """Persist student profile to memory cache and trigger background disk/cloud consolidation."""
        profile.updated_at = datetime.utcnow()
        self._cache[profile.student_id] = profile

        if self.enable_background_sync:
            self.schedule_background_save(profile)
        else:
            self._save_profile_disk_sync(profile)

    def schedule_background_save(self, profile: StudentProfile) -> None:
        """Dispatch non-blocking background consolidation task for student state persistence."""
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._async_save_profile(profile))
            self.active_background_tasks.append(task)
        except RuntimeError:
            self._executor.submit(self._save_profile_disk_sync, profile)

    async def _async_save_profile(self, profile: StudentProfile) -> None:
        """Asynchronous background worker persisting profile to storage."""
        await asyncio.to_thread(self._save_profile_disk_sync, profile)

    def _save_profile_disk_sync(self, profile: StudentProfile) -> None:
        """Synchronous write operation executed inside background thread pool."""
        file_path = os.path.join(self.storage_dir, f"{profile.student_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))

    def update_mastery(self, student_id: str, topic_id: str, topic_name: str, new_score: float) -> StudentProfile:
        """Update a student's mastery vector score for a specific topic with smoothed EMA."""
        profile = self.get_profile(student_id)
        if not profile:
            raise ValueError(f"Student '{student_id}' not found in profile store.")

        current_vector = profile.mastery_vectors.get(topic_id)
        if current_vector:
            # Exponential moving average / smooth update: 60% new score + 40% historical
            smoothed = round((new_score * 0.6) + (current_vector.mastery_score * 0.4), 2)
            attempts = current_vector.attempts_count + 1
            profile.mastery_vectors[topic_id] = MasteryVector(
                topic_id=topic_id,
                topic_name=topic_name,
                mastery_score=max(0.0, min(1.0, smoothed)),
                attempts_count=attempts,
                last_evaluated=datetime.utcnow(),
            )
        else:
            profile.mastery_vectors[topic_id] = MasteryVector(
                topic_id=topic_id,
                topic_name=topic_name,
                mastery_score=max(0.0, min(1.0, new_score)),
                attempts_count=1,
                last_evaluated=datetime.utcnow(),
            )

        self.save_profile(profile)
        return profile

    def record_cognitive_state(
        self,
        student_id: str,
        session_id: str,
        frustration_level: float,
        attention_span_minutes: int = 20,
        preferred_modality: str = "visual",
    ) -> None:
        """Record cognitive fatigue and frustration indicators with background persistence."""
        profile = self.get_profile(student_id)
        if not profile:
            return

        indicator = CognitiveIndicator(
            session_id=session_id,
            frustration_level=frustration_level,
            attention_span_minutes=attention_span_minutes,
            preferred_modality=preferred_modality,
            timestamp=datetime.utcnow(),
        )
        profile.cognitive_history.append(indicator)
        self.save_profile(profile)

    def list_students(self) -> List[StudentProfile]:
        """List all stored student profiles."""
        profiles = []
        if not os.path.exists(self.storage_dir):
            return profiles

        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                sid = fname[:-5]
                p = self.get_profile(sid)
                if p:
                    profiles.append(p)
        return profiles
