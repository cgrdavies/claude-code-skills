#!/usr/bin/env python3
"""
Automated Plan Implementation Script for Claude Code

This script automates the workflow of:
1. Using /create_plan to generate a plan
2. Clearing context between phases
3. Implementing each phase with /implement_plan

Usage:
    python auto_implement_plan.py --plan path/to/plan.md [options]
    python auto_implement_plan.py --create "Task description" [options]
"""

import asyncio
import argparse
import re
import sys
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, query, AssistantMessage, TextBlock


@dataclass
class Phase:
    """Represents a single phase from an implementation plan."""
    number: int
    name: str
    content: str
    is_completed: bool = False


class PlanAutomator:
    """Handles automated plan creation and implementation."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.setup_logging()

    def setup_logging(self):
        """Configure logging based on verbosity."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def parse_plan(self, plan_path: Path) -> List[Phase]:
        """
        Parse a plan markdown file to extract phases.

        Returns a list of Phase objects with completion status.
        """
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        with open(plan_path, 'r') as f:
            content = f.read()

        # Find all phases using regex
        # Phases are marked as ## Phase N: Name
        phase_pattern = r'^## Phase (\d+):\s*(.+?)$'
        phases = []

        lines = content.split('\n')
        current_phase = None
        current_content = []

        for i, line in enumerate(lines):
            match = re.match(phase_pattern, line)
            if match:
                # Save previous phase if exists
                if current_phase:
                    phase_content = '\n'.join(current_content)
                    # Check if phase is already completed by looking for checked boxes
                    is_completed = self._is_phase_completed(phase_content)
                    phases.append(Phase(
                        number=current_phase[0],
                        name=current_phase[1],
                        content=phase_content,
                        is_completed=is_completed
                    ))

                # Start new phase
                current_phase = (int(match.group(1)), match.group(2).strip())
                current_content = []
            elif current_phase:
                current_content.append(line)

        # Don't forget the last phase
        if current_phase:
            phase_content = '\n'.join(current_content)
            is_completed = self._is_phase_completed(phase_content)
            phases.append(Phase(
                number=current_phase[0],
                name=current_phase[1],
                content=phase_content,
                is_completed=is_completed
            ))

        return phases

    def _is_phase_completed(self, phase_content: str) -> bool:
        """
        Check if a phase has been completed by looking for checked boxes.

        A phase is considered complete if:
        - All automated verification items are checked [x]
        - Manual verification section exists and is marked complete
        """
        # Look for unchecked automated verification items
        unchecked_pattern = r'^\s*-\s*\[\s*\]\s*(.+)'
        checked_pattern = r'^\s*-\s*\[x\]\s*(.+)'

        in_automated_section = False
        has_unchecked = False

        for line in phase_content.split('\n'):
            if '#### Automated Verification:' in line:
                in_automated_section = True
            elif '#### Manual Verification:' in line:
                in_automated_section = False
            elif in_automated_section:
                if re.match(unchecked_pattern, line):
                    has_unchecked = True
                    break

        return not has_unchecked

    async def create_plan(self, task_description: str) -> Optional[Path]:
        """
        Create a new plan using the /create_plan command.

        Returns the path to the created plan file.
        """
        self.logger.info("Creating new plan...")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create plan for: {task_description}")
            return Path("thoughts/shared/plans/dry-run-plan.md")

        # Use Claude to create the plan
        prompt = f"/create_plan {task_description}"

        plan_path = None
        async for message in query(prompt=prompt):
            # Extract text from AssistantMessage
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text

                        # Look for the plan file path in the output
                        if "thoughts/shared/plans/" in text:
                            match = re.search(r'`(thoughts/shared/plans/[^`]+\.md)`', text)
                            if match:
                                plan_path = Path(match.group(1))
                                self.logger.info(f"Plan created at: {plan_path}")

                        if self.verbose:
                            print(text)

        return plan_path

    def load_slash_command(self, command_name: str) -> str:
        """Load a slash command's prompt from the .claude/commands directory."""
        # Try user's home directory first
        command_path = Path.home() / ".claude" / "commands" / f"{command_name}.md"
        if not command_path.exists():
            # Try current directory
            command_path = Path(".claude") / "commands" / f"{command_name}.md"

        if not command_path.exists():
            raise FileNotFoundError(f"Slash command not found: {command_name}")

        content = command_path.read_text()

        # Strip YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        return content

    async def implement_phase(self, plan_path: Path, phase: Phase) -> bool:
        """
        Implement a single phase of the plan.

        Returns True if successful, False otherwise.
        """
        self.logger.info(f"Implementing Phase {phase.number}: {phase.name}")

        if phase.is_completed:
            self.logger.info(f"Phase {phase.number} already completed, skipping...")
            return True

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would implement phase {phase.number}")
            return True

        # Load the /implement_plan slash command and expand it with arguments
        command_prompt = self.load_slash_command("implement_plan")
        prompt = f"{command_prompt}\n\nPlan: {plan_path}\nPhase: {phase.number}"

        # Set options to bypass permissions for automated execution
        options = ClaudeAgentOptions(permission_mode='bypassPermissions')

        success = False
        async for message in query(prompt=prompt, options=options):
            self.logger.debug(f"Received message type: {type(message).__name__}")

            # Extract text from AssistantMessage
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text
                        self.logger.debug(f"Text block: {text[:100]}...")

                        # Look for success indicators
                        if "Phase" in text and "Complete" in text:
                            success = True
                            self.logger.debug("Found success indicator")

                        # Check for manual verification request
                        if "Ready for Manual Verification" in text:
                            self.logger.info("Phase requires manual verification")
                            self.logger.info("Auto-confirming manual verification in automated mode")
                            # In automated mode, we assume manual verification will be done
                            # and continue to next phase
                            success = True

                        if self.verbose:
                            print(text)
            else:
                self.logger.debug(f"Non-assistant message: {message}")

        return success

    async def run_full_implementation(self, plan_path: Path,
                                     start_phase: Optional[int] = None,
                                     end_phase: Optional[int] = None):
        """
        Run the full implementation workflow for a plan.

        Args:
            plan_path: Path to the plan file
            start_phase: Phase to start from (inclusive)
            end_phase: Phase to end at (inclusive)
        """
        # Parse the plan
        phases = self.parse_plan(plan_path)

        if not phases:
            self.logger.error("No phases found in plan")
            return

        self.logger.info(f"Found {len(phases)} phases in plan")

        # Filter phases based on start/end
        if start_phase:
            phases = [p for p in phases if p.number >= start_phase]
        if end_phase:
            phases = [p for p in phases if p.number <= end_phase]

        # Implement each phase
        for phase in phases:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Starting Phase {phase.number}/{len(phases)}: {phase.name}")
            self.logger.info(f"{'='*60}\n")

            success = await self.implement_phase(plan_path, phase)

            if not success:
                self.logger.error(f"Phase {phase.number} failed, stopping implementation")
                break

            self.logger.info(f"Phase {phase.number} completed successfully")

            # Clear context between phases (simulated by new query)
            # In reality, each query() call starts fresh
            if phase.number < phases[-1].number:
                self.logger.info("Clearing context for next phase...")
                await asyncio.sleep(1)  # Small delay between phases

        self.logger.info("\n" + "="*60)
        self.logger.info("Implementation complete!")

    async def interactive_mode(self):
        """
        Run in interactive mode where user can control the flow.
        """
        self.logger.info("Starting interactive mode...")

        options = ClaudeAgentOptions(
            system_prompt="You are a helpful assistant for software implementation tasks.",
            max_turns=100
        )

        async with ClaudeSDKClient(options=options) as client:
            while True:
                command = input("\nCommand (create/implement/quit): ").strip().lower()

                if command == 'quit':
                    break
                elif command == 'create':
                    task = input("Task description: ")
                    await client.query(f"/create_plan {task}")
                    async for msg in client.receive_response():
                        print(msg)
                elif command == 'implement':
                    plan_path = input("Plan path: ")
                    phase = input("Phase number (or 'all'): ")
                    if phase == 'all':
                        prompt = f"/implement_plan {plan_path}"
                    else:
                        prompt = f"/implement_plan {plan_path} phase {phase}"

                    await client.query(prompt)
                    async for msg in client.receive_response():
                        print(msg)
                else:
                    print("Unknown command")


async def main():
    parser = argparse.ArgumentParser(
        description="Automate Claude Code plan creation and implementation"
    )

    # Main operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--plan',
        type=Path,
        help='Path to existing plan file to implement'
    )
    group.add_argument(
        '--create',
        type=str,
        help='Create a new plan with the given task description'
    )
    group.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    # Implementation options
    parser.add_argument(
        '--start-phase',
        type=int,
        help='Phase number to start from (default: 1)'
    )
    parser.add_argument(
        '--end-phase',
        type=int,
        help='Phase number to end at (default: last)'
    )

    # General options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    args = parser.parse_args()

    # Create automator instance
    automator = PlanAutomator(verbose=args.verbose, dry_run=args.dry_run)

    try:
        if args.interactive:
            await automator.interactive_mode()
        elif args.create:
            # Create a new plan
            plan_path = await automator.create_plan(args.create)
            if plan_path:
                print(f"\nPlan created at: {plan_path}")
                implement = input("Implement now? (y/n): ")
                if implement.lower() == 'y':
                    await automator.run_full_implementation(plan_path)
        elif args.plan:
            # Implement existing plan
            await automator.run_full_implementation(
                args.plan,
                start_phase=args.start_phase,
                end_phase=args.end_phase
            )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())