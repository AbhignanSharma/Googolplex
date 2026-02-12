# 🛡️ Security Guardian — Autonomous Enterprise Security Agent

An enterprise-grade, multi-agent security review system that automatically analyzes code, detects vulnerabilities, generates surgical fixes, and enforces security policies directly on GitHub Pull Requests.

## 🚀 Key Features

- **Multi-Agent Pipeline**: 8 specialized agents working in sequence (Vulnerability → Context → supply Chain → Secrets → Risk → Fix → Verify → Enforce)
- **Zero Trust Enforcement**: Automatically blocks PRs, requests changes, adds labels, and creates patch PRs based on risk score.
- **Attack Simulation**: Generates realistic 3-step attack chains and concrete exploit payloads for critical findings.
- **Surgical Fixes**: Produces minimal, diff-style fixes that are easy to review (under 30 seconds).
- **Security Maturity Scorecard**: Rates your project across 7 dimensions (Auth, Input Validation, Secrets, etc.).
- **Historical Risk Tracking**: Monitors security score trends over time.

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo>
   cd my_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR
   pip install google-adk requests bcrypt
   ```

3. **Set up environment variables**:
   Create a `.env` file or export:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="us-central1"
   export GITHUB_TOKEN="ghp_..."  # Required for PR reviews
   ```

## 🛠️ Integration with GitHub Actions

The system includes a pre-configured GitHub Actions workflow in `.github/workflows/security-guardian.yml`.

**To activate:**
1. Commit the workflow file to your repository.
2. Create a PR.
3. The "🛡️ Security Guardian Review" action will run automatically.

**What happens:**
- **Critical/High Issues**: PR is BLOCKED ⛔. Changes requested. A Patch PR is created with fixes. Label `security-critical` added.
- **Medium Issues**: PR receives a WARNING ⚠️. Review comments posted. Label `security-warning`.
- **Low/Clean**: PR is APPROVED ✅. Label `security-approved`.

## 🖥️ Local Usage

You can run the full security review locally on a PR without pushing:

```bash
# Review a specific PR
python run_review.py --pr 123
```

OR start the interactive web UI to chat with the agent:

```bash
adk web --port 8000
# Then open http://localhost:8000
```

## 🏗️ Architecture

The system uses Google ADK with a **Tool-Data / Model-Intelligence** philosophy:

1. **Tools** (Python) provide raw data: file content, git diffs, dependency manifests.
2. **LLM** (Gemini) provides intelligence: vulnerability detection, threat modeling, fix generation.
3. **Enforcement Agent** takes action: posts to GitHub, creates branches, manages labels.

## 🤝 Contributing

This agent is designed to be extensible.
- Add new tools in `tools.py`
- Refine agent prompts in `prompts.py`
- Customize enforcement rules in `Enforcement Agent` prompt.
