import re

class Pattern:
    def __init__(self, type, regex, severity):
        self.type = type
        self.regex = re.compile(regex)
        self.severity = severity

PATTERNS = [
    # ── Hardcoded Secrets ─────────────────────────────────────────────────
    Pattern(
        type="Hardcoded Secret",
        regex=r"(?i)(password|passwd|pwd|secret|token|api_key|access_key|auth_key|client_secret)\s*[:=]\s*['\"][\w\-]{8,}['\"]",
        severity="High"
    ),
    Pattern(
        type="Hardcoded Secret",
        regex=r"(?i)sk-live-[\w]{20,}",
        severity="Critical"
    ),
    Pattern(
        type="Hardcoded Secret",
        regex=r"(?i)AKIA[0-9A-Z]{16}",
        severity="Critical"
    ),

    # ── SQL Injection ─────────────────────────────────────────────────────
    Pattern(
        type="SQL Injection",
        regex=r"(?i)(SELECT|INSERT|UPDATE|DELETE).*WHERE.*(?:'|\")\s*\+\s*\w+",
        severity="Critical"
    ),
    Pattern(
        type="SQL Injection",
        regex=r"(?i)(SELECT|INSERT|UPDATE|DELETE).*WHERE.*\$\{\w+\}",
        severity="Critical"
    ),
]
