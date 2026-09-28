import re

class RouterEngine:
    # Security guardrail: Common prompt injection and jailbreak patterns
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"jailbreak",
        r"reveal secret",
        r"bypass rules",
    ]

    # Heuristic keywords indicating multi-step reasoning requirement
    REASONING_KEYWORDS = [
        "explain why", "step by step", "architect", "compare and contrast",
        "derive", "optimize", "refactor", "evaluate"
    ]

    @classmethod
    def check_security(cls, prompt: str) -> dict:
        """Scans prompt for common injection or jailbreak patterns."""
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return {
                    "is_threat": True,
                    "reason": f"Potential prompt injection detected (pattern: '{pattern}')"
                }
        return {"is_threat": False, "reason": None}

    @classmethod
    def calculate_complexity(cls, prompt: str) -> float:
        """Calculates complexity score between 0.0 (simple) and 1.0 (complex)."""
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())
        
        # Check for actual code syntax OR code-related terms
        has_code = bool(re.search(r"(def |class |import |function|\{|\}|var |let |const )", prompt))
        mentions_programming = any(term in prompt_lower for term in ["python", "code", "application", "script", "database", "api"])

        # Count how many reasoning keywords match
        reasoning_matches = sum(1 for kw in cls.REASONING_KEYWORDS if kw in prompt_lower)

        score = 0.1  # Base score

        # Length heuristic
        if word_count > 80:
            score += 0.4
        elif word_count > 35:
            score += 0.2

        # Code heuristic
        if has_code:
            score += 0.3
        elif mentions_programming:
            score += 0.2

        # Reasoning intent heuristic (adds 0.2 per matched keyword, up to 0.4)
        if reasoning_matches > 0:
            score += min(0.2 * reasoning_matches, 0.4)

        return min(round(score, 2), 1.0)

    @classmethod
    def analyze(cls, prompt: str) -> dict:
        """Main entry point for evaluating incoming requests."""
        # Step 1: Security Scan
        security_res = cls.check_security(prompt)
        if security_res["is_threat"]:
            return {
                "action": "BLOCK",
                "complexity_score": 1.0,
                "reason": security_res["reason"]
            }

        # Step 2: Complexity Evaluation
        complexity = cls.calculate_complexity(prompt)
        action = "CLOUD_MODEL" if complexity >= 0.5 else "LOCAL_MODEL"

        return {
            "action": action,
            "complexity_score": complexity,
            "reason": "Evaluated via word length, code syntax, and reasoning heuristics."
        }