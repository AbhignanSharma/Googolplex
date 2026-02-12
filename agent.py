"""
🛡️ SECURITY GUARDIAN — Enterprise Autonomous Security Review System
════════════════════════════════════════════════════════════════════

Multi-agent security analysis platform built on Google ADK.

Architecture:
  TOOLS: provide DATA (read files, git diffs, GitHub API, codebase search)
  LLM: provides INTELLIGENCE (security analysis, threat modeling, fix generation)
  AGENTS: specialize in DIMENSIONS (vulns, context, supply chain, secrets, risk, fixes)
  ENFORCEMENT: Zero Trust actions (label, block, patch PR, track history)

Capabilities:
  - ANY language, framework, technology stack
  - ANY scale — code snippets, files, PRs, entire repos
  - Attack Simulation with 3-step chains
  - Exploit Proof generation with concrete payloads
  - Security Maturity Scorecard (7 dimensions)
  - GitHub integration: auto-review PRs, create patch PRs, add labels
  - Historical risk tracking with trend analysis

Pipeline (8 agents):
  User Input → Orchestrator → Vulnerability Analysis → Context & Impact →
  Supply Chain → Secrets Detection → Risk Assessment + Threat Modeling →
  Fix Generation (surgical) → Fix Verification → Enforcement (GitHub Actions)
"""

from google.adk.agents import Agent, SequentialAgent
from prompts import (
    ORCHESTRATOR_INSTRUCTION,
    PATTERN_AGENT_INSTRUCTION,
    CONTEXT_AGENT_INSTRUCTION,
    DEPENDENCY_AGENT_INSTRUCTION,
    SECRETS_AGENT_INSTRUCTION,
    RISK_SCORING_INSTRUCTION,
    FIX_GENERATOR_INSTRUCTION,
    VERIFICATION_AGENT_INSTRUCTION,
    ENFORCEMENT_AGENT_INSTRUCTION,
)
from tools import (
    read_file,
    list_files,
    get_git_diff,
    search_in_code,
    get_dependency_file,
    get_recent_commits,
)
from github_tools import (
    get_pr_diff,
    get_pr_file_content,
    post_review_comment,
    add_security_label,
    create_patch_pr,
    record_risk_score,
)


# ═══════════════════════════════════════════════════════════════════
# SPECIALIZED ANALYSIS AGENTS (LLM = Intelligence)
# ═══════════════════════════════════════════════════════════════════

pattern_agent = Agent(
    model='gemini-1.5-flash',
    name='pattern_agent',
    description=(
        'Deep vulnerability analysis across ALL security dimensions — '
        'injection, auth, crypto, access control, data protection, business logic, '
        'configuration, and more. Language and framework agnostic.'
    ),
    instruction=PATTERN_AGENT_INSTRUCTION,
    output_key='pattern_analysis',
)

context_agent = Agent(
    model='gemini-1.5-flash',
    name='context_agent',
    description=(
        'Real-world impact and blast radius assessment. Determines data sensitivity, '
        'exposure level, compliance implications, and lateral movement potential.'
    ),
    instruction=CONTEXT_AGENT_INSTRUCTION,
    output_key='context_analysis',
)

dependency_agent = Agent(
    model='gemini-1.5-flash',
    name='dependency_agent',
    description=(
        'Supply chain security using LLM knowledge of package vulnerabilities. '
        'Evaluates dependencies, version pinning, typosquatting, and ecosystem risks.'
    ),
    instruction=DEPENDENCY_AGENT_INSTRUCTION,
    output_key='dependency_analysis',
)

secrets_agent = Agent(
    model='gemini-1.5-flash',
    name='secrets_agent',
    description=(
        'Semantic credential and secrets detection. Understands context to distinguish '
        'real secrets from placeholders, including encoded and obfuscated credentials.'
    ),
    instruction=SECRETS_AGENT_INSTRUCTION,
    output_key='secrets_analysis',
)

risk_scoring_agent = Agent(
    model='gemini-1.5-flash',
    name='risk_scoring_agent',
    description=(
        'Quantitative risk scoring with attack simulation, exploit proofs, and '
        'security maturity scorecard. Produces actionable threat models.'
    ),
    instruction=RISK_SCORING_INSTRUCTION,
    output_key='risk_assessment',
)

fix_generator_agent = Agent(
    model='gemini-1.5-flash',
    name='fix_generator_agent',
    description=(
        'Surgical, minimal security fix generation. Produces diff-style fixes '
        'that change only vulnerable lines — reviewable in under 30 seconds.'
    ),
    instruction=FIX_GENERATOR_INSTRUCTION,
    output_key='security_fixes',
)

verification_agent = Agent(
    model='gemini-1.5-flash',
    name='verification_agent',
    description=(
        'Independent fix verification and quality gate. Re-analyzes fixes for '
        'correctness, regression, best practices, and minimality.'
    ),
    instruction=VERIFICATION_AGENT_INSTRUCTION,
    output_key='verification_result',
)

enforcement_agent = Agent(
    model='gemini-1.5-flash',
    name='enforcement_agent',
    description=(
        'Zero Trust GitHub enforcement. Adds severity labels, requests changes, '
        'creates patch PRs, and tracks risk history based on the risk score.'
    ),
    instruction=ENFORCEMENT_AGENT_INSTRUCTION,
    tools=[
        get_pr_diff,
        get_pr_file_content,
        post_review_comment,
        add_security_label,
        create_patch_pr,
        record_risk_score,
    ],
    output_key='enforcement_result',
)

# ═══════════════════════════════════════════════════════════════════
# SEQUENTIAL ANALYSIS PIPELINE (8 agents)
# Each agent builds on findings from all previous agents
# ═══════════════════════════════════════════════════════════════════

security_pipeline = SequentialAgent(
    name='security_analysis_pipeline',
    description=(
        'Complete 8-agent security analysis pipeline: '
        'Vulnerability Analysis → Context & Impact → Supply Chain → '
        'Secrets Detection → Risk Scoring & Threat Modeling → '
        'Fix Generation (surgical) → Fix Verification → Enforcement.'
    ),
    sub_agents=[
        pattern_agent,       # 1. Find vulnerabilities
        context_agent,       # 2. Assess real-world impact
        dependency_agent,    # 3. Supply chain risks
        secrets_agent,       # 4. Credential exposure
        risk_scoring_agent,  # 5. Quantify risk + attack sim + exploit proof + maturity
        fix_generator_agent, # 6. Generate minimal fixes
        verification_agent,  # 7. Verify fixes independently
        enforcement_agent,   # 8. GitHub actions (label, block, patch PR)
    ],
)

# ═══════════════════════════════════════════════════════════════════
# ROOT ORCHESTRATOR AGENT
# Entry point — gathers data with tools, delegates to pipeline
# ═══════════════════════════════════════════════════════════════════

root_agent = Agent(
    model='gemini-1.5-flash',
    name='security_guardian',
    description=(
        'Security Guardian — enterprise autonomous security review system. '
        'Analyzes ANY code (any language, framework, scale) for vulnerabilities, '
        'generates surgical fixes, simulates attacks, and enforces results on GitHub.'
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[
        read_file,
        list_files,
        get_git_diff,
        search_in_code,
        get_dependency_file,
        get_recent_commits,
        get_pr_diff,
        get_pr_file_content,
    ],
    sub_agents=[security_pipeline],
)
