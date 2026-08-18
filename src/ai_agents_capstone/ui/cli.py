"""Rich Interactive CLI Interface for EduPathway AI."""

import time
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.markdown import Markdown

from ..orchestration.supervisor import EduPathwaySupervisor
from ..models.assessment import QuizSubmission, QuestionResponse
from ..memory.session_memory import SessionMemory
from ..tools.assessment_tool import generate_diagnostic_quiz


class EduPathwayCLI:
    """Terminal UI for student learning and educator IEP workflow."""

    def __init__(self):
        self.console = Console()
        self.supervisor = EduPathwaySupervisor()

    def print_banner(self) -> None:
        """Render the welcome banner."""
        banner_text = Text()
        banner_text.append("🌱 EduPathway AI\n", style="bold green")
        banner_text.append("Adaptive Learning & IEP Assistant (Agents for Good Track)\n", style="bold white")
        banner_text.append("Powered by Google Agent Development Kit (ADK)", style="italic cyan")
        self.console.print(Panel(banner_text, border_style="green", expand=False))

    def run_interactive_menu(self) -> None:
        """Main application loop."""
        while True:
            self.console.clear()
            self.print_banner()

            table = Table(title="Select Workflow Mode", border_style="blue", show_header=True)
            table.add_column("Option", style="bold cyan", width=8)
            table.add_column("Workflow Description", style="white")

            table.add_row("1", "🚀 Full Diagnostic & Adaptive Lesson Synthesis (Demo Scenario: Leo Martinez)")
            table.add_row("2", "💬 Interactive Socratic Tutoring Session")
            table.add_row("3", "👤 Inspect & Manage Student IEP Profiles & Mastery Vectors")
            table.add_row("4", "📊 View Latest Observability & Telemetry Trace")
            table.add_row("5", "Exit")

            self.console.print(table)
            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"], default="1")

            if choice == "1":
                self.run_demo_scenario()
            elif choice == "2":
                self.run_tutoring_interactive()
            elif choice == "3":
                self.inspect_profiles()
            elif choice == "4":
                self.view_latest_trace()
            elif choice == "5":
                self.console.print("[green]Thank you for using EduPathway AI. Empowering accessible learning![/green]")
                break

            Prompt.ask("\n[dim]Press Enter to return to main menu...[/dim]")

    def run_demo_scenario(self) -> None:
        """Run the comprehensive end-to-end multi-agent scenario for Leo Martinez."""
        self.console.print("\n[bold yellow]═══ STEP 1: LOADING STUDENT PROFILE & DIAGNOSTIC SUBMISSION ═══[/bold yellow]")
        student_id = "leo_m"
        profile = self.supervisor.profile_store.get_profile(student_id)

        if profile:
            self.console.print(f"[bold]Student:[/bold] {profile.name} | [bold]Grade:[/bold] {profile.grade_level} | [bold]Reading Level:[/bold] Grade {profile.reading_grade_level}")
            self.console.print(f"[bold]IEP Focus:[/bold] {profile.primary_disability_or_focus}")
            self.console.print(f"[bold]Accommodations:[/bold] {', '.join([a.category for a in profile.accommodations])}")

        # Simulated quiz submission where student struggled with unlike denominator addition
        submission = QuizSubmission(
            student_id=student_id,
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
                    student_work_steps="I added 1+1 on top and 2+4 on bottom.",
                ),
                QuestionResponse(
                    question_id="diag_frac_02",
                    question_text="Calculate: 2/3 + 1/6",
                    target_concept="equivalent fractions scaling",
                    student_answer="3/9",
                    correct_answer="5/6",
                    student_work_steps="2+1=3 and 3+6=9",
                ),
            ],
        )

        with self.console.status("[bold green]Executing Multi-Agent Coordination Pipeline...[/bold green]", spinner="dots"):
            result = self.supervisor.run_full_diagnostic_and_curriculum_flow(submission)

        report = result["assessment_report"]
        lesson = result["lesson_plan"]
        hitl_proposals = result["hitl_proposals"]

        # Render Assessment Report
        self.console.print("\n[bold cyan]═══ STEP 2: INTAKE & DIAGNOSTIC AGENT REPORT ═══[/bold cyan]")
        rep_panel = (
            f"[bold]Diagnostic Score:[/bold] {report.overall_accuracy_percentage}%\n"
            f"[bold]Reading Level Assessed:[/bold] Grade {report.assessed_reading_level}\n"
            f"[bold]Learning Gaps:[/bold] {', '.join([g.skill_name for g in report.learning_gaps])}\n"
            f"[bold]Misconception Identified:[/bold] {report.misconceptions[0].description if report.misconceptions else 'None'}\n"
            f"[bold]Correction Strategy:[/bold] {report.misconceptions[0].correction_strategy if report.misconceptions else 'None'}"
        )
        self.console.print(Panel(rep_panel, title="Assessment Report", border_style="cyan"))

        # Render HITL if triggered
        if hitl_proposals:
            self.console.print("\n[bold red]═══ ⚠️ HUMAN-IN-THE-LOOP (HITL) POLICY TRIGGERED ═══[/bold red]")
            for prop in hitl_proposals:
                self.console.print(
                    Panel(
                        f"[bold]Trigger Reason:[/bold] {prop.trigger_reason}\n"
                        f"[bold]Proposed Change:[/bold] {prop.proposed_change}\n"
                        f"[bold]Risk Level:[/bold] {prop.risk_level.upper()}",
                        title="Educator Action Required",
                        border_style="red",
                    )
                )
                approved = Confirm.ask("As the Special Ed Educator, do you APPROVE this proposal?", default=True)
                prop.decision = "APPROVED" if approved else "REJECTED"
                self.console.print(f"[green]Decision recorded: {prop.decision}[/green]")

        # Render Lesson Plan
        self.console.print("\n[bold green]═══ STEP 3: SYNTHESIZED IEP LESSON PLAN ═══[/bold green]")
        self.console.print(f"[bold]Title:[/bold] {lesson.title}")
        self.console.print(f"[bold]Target Skill:[/bold] {lesson.target_skill}")
        self.console.print(f"[bold]Exported Artifact:[/bold] `{result['exported_lesson_path']}`")

        for sec in lesson.sections:
            self.console.print(Panel(f"{sec.content}\n\n[bold]Check for Understanding:[/bold] {sec.check_for_understanding_question}", title=sec.title, border_style="green"))

        # Observability Summary
        self.console.print("\n[bold magenta]═══ STEP 4: OBSERVABILITY & TELEMETRY SUMMARY ═══[/bold magenta]")
        self.console.print(result["trace_summary"])
        self.console.print(f"Trace saved to: `{result['trace_filepath']}`")

    def run_tutoring_interactive(self) -> None:
        """Run real-time Socratic tutoring session."""
        self.console.print("\n[bold cyan]═══ INTERACTIVE SOCRATIC TUTOR ═══[/bold cyan]")
        student_id = "leo_m"
        profile = self.supervisor.profile_store.get_profile(student_id)

        if not profile:
            self.console.print("[red]Student profile not found. Please create or load a profile first.[/red]")
            return

        memory = SessionMemory(session_id="tutor_interactive_sess")
        exercise = PracticeExercise(
            exercise_id="prac_frac_01",
            prompt="Find the sum: 1/2 + 1/4 using visual fraction bars.",
            difficulty_level="scaffolded",
            hint_tier_1_concept="Think about what 1/2 looks like when cut into fourths. How many fourths equal 1/2?",
            hint_tier_2_strategy="Multiply the top and bottom of 1/2 by 2 to convert it to fourths: 2/4.",
            hint_tier_3_substep="Now that both have denominator 4, add the numerators: 2/4 + 1/4 = ?",
            solution_key="3/4",
            visual_aid_description="Fraction bar diagram partitioned into fourths.",
        )

        self.console.print(Panel(
            f"[bold]Problem:[/bold] {exercise.prompt}\n"
            f"[italic]Hint Guardrails active. Type your answer, ask for help, or type 'exit' to quit.[/italic]",
            title=f"Socratic Tutoring Session for {profile.name}",
            border_style="yellow",
        ))

        attempt = 1
        while True:
            student_msg = Prompt.ask("\n[bold cyan]Student (You)[/bold cyan]")
            if student_msg.lower().strip() in ["exit", "quit"]:
                break

            with self.console.status("[dim]Tutor is thinking...[/dim]"):
                tutor_turn = self.supervisor.conduct_tutoring_turn(
                    student_id=student_id,
                    exercise=exercise,
                    student_message=student_msg,
                    memory=memory,
                    attempt_count=attempt,
                )

            self.console.print(f"\n[bold green]🦉 EduPathway Tutor:[/bold green] {tutor_turn.response_text}")

            if tutor_turn.is_answer_correct or tutor_turn.mastery_demonstrated:
                self.console.print("\n[bold green]🎉 Problem Solved! Mastery updated in profile store.[/bold green]")
                break

            attempt += 1

    def inspect_profiles(self) -> None:
        """Inspect student IEP profiles and mastery vectors."""
        profiles = self.supervisor.profile_store.list_students()
        if not profiles:
            self.console.print("[yellow]No profiles found in storage.[/yellow]")
            return

        for p in profiles:
            table = Table(title=f"Student Profile: {p.name} ({p.student_id})", border_style="cyan")
            table.add_column("Property", style="bold white")
            table.add_column("Value", style="cyan")

            table.add_row("Grade Level", str(p.grade_level))
            table.add_row("Reading Grade Level", str(p.reading_grade_level))
            table.add_row("Primary Focus", p.primary_disability_or_focus or "None")
            table.add_row("Interests", ", ".join(p.interests))
            table.add_row("IEP Accommodations", ", ".join([a.category for a in p.accommodations]))

            self.console.print(table)

            if p.mastery_vectors:
                mv_table = Table(title=f"Mastery Vectors for {p.name}", border_style="green")
                mv_table.add_column("Topic", style="bold")
                mv_table.add_column("Mastery Score", style="green")
                mv_table.add_column("Attempts", style="white")

                for topic_id, mv in p.mastery_vectors.items():
                    bar = "█" * int(mv.mastery_score * 10) + "░" * (10 - int(mv.mastery_score * 10))
                    mv_table.add_row(mv.topic_name, f"{bar} ({mv.mastery_score * 100:.0f}%)", str(mv.attempts_count))

                self.console.print(mv_table)

    def view_latest_trace(self) -> None:
        """View the latest generated trace file."""
        import os
        traces_dir = "traces"
        if not os.path.exists(traces_dir):
            self.console.print("[yellow]No traces recorded yet.[/yellow]")
            return

        files = sorted([f for f in os.listdir(traces_dir) if f.endswith(".json")])
        if not files:
            self.console.print("[yellow]No trace files found in traces/ directory.[/yellow]")
            return

        latest_file = os.path.join(traces_dir, files[-1])
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.console.print(Panel(content[:1500] + ("\n... [truncated]" if len(content) > 1500 else ""), title=f"Latest Trace: {files[-1]}", border_style="magenta"))
