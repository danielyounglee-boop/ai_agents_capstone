import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ai_agents_capstone.ui.cli import EduPathwayCLI
from src.ai_agents_capstone.orchestration.supervisor import EduPathwaySupervisor
from src.ai_agents_capstone.models.assessment import QuizSubmission, QuestionResponse


def main():
    """Main CLI execution router."""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("Running EduPathway AI Automated Demo Pipeline...")
        supervisor = EduPathwaySupervisor()
        submission = QuizSubmission(
            student_id="leo_m",
            quiz_id="quiz_fractions_addition_gr5",
            subject="Mathematics",
            topic="fractions_addition_unlike_denominators",
            grade_target=5,
            responses=[
                QuestionResponse(
                    question_id="diag_frac_01",
                    question_text="What is 1/2 + 1/4?",
                    target_concept="finding common denominators",
                    student_answer="2/6",
                    correct_answer="3/4",
                    student_work_steps="I added across: 1+1=2 and 2+4=6",
                )
            ],
        )
        result = supervisor.run_full_diagnostic_and_curriculum_flow(submission)
        print(f"✅ Demo execution complete! Session: {result['session_id']}")
        print(f"📄 Exported Lesson Plan: {result['exported_lesson_path']}")
        print(f"📊 Trace File: {result['trace_filepath']}")
        print("\n" + result["trace_summary"])
    else:
        cli = EduPathwayCLI()
        cli.run_interactive_menu()


if __name__ == "__main__":
    main()
