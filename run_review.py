# Trigger run: 2026-02-12 11:35:00
"""
🛡️ Security Guardian - GitHub Action Runner
══════════════════════════════════════════════

This script is the entry point for the GitHub Actions workflow.
It:
1. Reads the PR number from arguments/environment
2. Initializes the Security Guardian agent
3. Triggers the "Mode 3: GitHub PR Review" workflow
4. Ensures the analysis and enforcement pipeline runs to completion

Usage:
  python run_review.py --pr 123
"""

import os
import sys
import argparse
import asyncio
import logging
from google.adk.agents import Agent

# Import our configured root agent
# Note: In a real package structure, this might be 'from my_agent.agent import root_agent'
# Adjusting path to ensure local import works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SecurityGuardianRunner")


async def run_review(pr_number: int):
    """Run the security review for a specific PR."""
    logger.info(f"🚀 Starting Security Guardian Review for PR #{pr_number}")

    # Construct the user request for Mode 3
    user_prompt = (
        f"Please perform a comprehensive security review for Pull Request #{pr_number}. "
        f"This is an automated run from GitHub Actions. "
        f"Execute the full pipeline including finding vulnerabilities, context analysis, "
        f"risk scoring, fix generation, verification, and strictly ENFORCE the findings "
        f"using the enforcement_agent to label codes, request changes, or auto-patch."
    )

    try:
        # Run the agent using run_async
        context = await root_agent.run_async(user_prompt)

        # The result in ADK 1.24+ is typically in context.final_result
        # We'll print a confirmation and log the final output.
        logger.info("✅ Security Review Processing Completed")

        if hasattr(context, 'final_result'):
            print(context.final_result)
        else:
            print(str(context))

    except Exception as e:
        logger.error(f"❌ Error running security review: {str(e)}", exc_info=True)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run Security Guardian for a PR")
    parser.add_argument("--pr", type=int, help="Pull Request number to review")

    args = parser.parse_args()

    # Fallback to environment variable if argument not provided
    pr_number = args.pr or int(os.environ.get("PR_NUMBER", 0))

    if not pr_number:
        logger.error("❌ No PR number provided. Usage: python run_review.py --pr <number>")
        sys.exit(1)

    # Check for GITHUB_TOKEN
    if not os.environ.get("GITHUB_TOKEN"):
        logger.warning("⚠️ GITHUB_TOKEN not set. GitHub API calls (comments/labels) will likely fail.")

    # Run the async loop
    asyncio.run(run_review(pr_number))


if __name__ == "__main__":
    main()
