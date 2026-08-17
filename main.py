"""Entry point for the AI Agent."""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from ai_agents_capstone.agent import get_client, run_agent_turn

# Load environment variables from .env
load_dotenv()

console = Console()


def main():
    console.print(Panel.fit("[bold green]5-Day AI Agents Intensive Capstone Agent[/bold green]\n[dim]Powered by Google Gemini 2.5[/dim]"))
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY is not configured.")
        console.print("Please add your Gemini API Key in [yellow].env[/yellow] file.")
        sys.exit(1)

    client = get_client()
    console.print("[cyan]Agent initialized and ready. Type 'exit' or 'quit' to quit.[/cyan]\n")

    while True:
        try:
            user_input = console.input("[bold blue]User > [/bold blue]")
            if not user_input.strip():
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[italic]Goodbye![/italic]")
                break

            console.print("[dim]Thinking...[/dim]")
            response = run_agent_turn(client, user_input)
            console.print(f"[bold green]Agent >[/bold green] {response}\n")
        except KeyboardInterrupt:
            console.print("\n[italic]Session terminated.[/italic]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}\n")


if __name__ == "__main__":
    main()
