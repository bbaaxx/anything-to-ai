"""LLM adapter for text summarization."""

import json
from typing import Any

from .exceptions import LLMError


class LLMAdapter:
    """Adapter for LLM client operations."""

    def __init__(self, llm_client: Any, model: str = "llama3.2:latest"):
        """Initialize adapter with LLM client.

        Args:
            llm_client: LLM client instance
            model: Model name to use (default: "llama3.2:latest")
        """
        self.llm_client = llm_client
        self.model = model

    def call(self, prompt: str) -> str:
        """Call LLM client with prompt."""
        try:
            from anyfile_to_ai.llm_client import LLMRequest, Message, MessageRole

            # Create request with user message
            request = LLMRequest(
                model=self.model,
                messages=[Message(role=MessageRole.USER, content=prompt)],
                temperature=0.7,
                max_tokens=2000,
            )

            # Generate response
            response = self.llm_client.generate(request)
            return response.content
        except Exception as e:
            msg = f"LLM call failed: {e}"
            raise LLMError(msg)

    @staticmethod
    def parse_response(response: str) -> dict[str, Any]:
        """Parse LLM response to extract summary, tags, and language."""
        # Try to parse as JSON (whole response)
        try:
            data = json.loads(response.strip())
            if "summary" in data and "tags" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass

        # Try to find JSON embedded in the response
        try:
            # Look for JSON object in the response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                if "summary" in data and "tags" in data:
                    return data
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: intelligent text parsing
        lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
        summary = ""
        tags = []
        in_summary = False
        in_tags = False

        for _i, line in enumerate(lines):
            line_lower = line.lower()

            # Detect summary section
            if '"summary"' in line_lower or "'summary'" in line_lower:
                # Try to extract from same line if format is: "summary": "text"
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        summary_candidate = parts[1].strip().strip(",").strip('"').strip("'")
                        if summary_candidate and not summary_candidate.startswith("["):
                            summary = summary_candidate
                            in_summary = False
                            continue
                in_summary = True
                in_tags = False
                continue

            # Detect tags section
            if '"tags"' in line_lower or "'tags'" in line_lower or line_lower.startswith("tags:"):
                in_tags = True
                in_summary = False
                # Try to extract from same line if format is: "tags": ["tag1", "tag2"]
                if "[" in line and "]" in line:
                    try:
                        start = line.index("[")
                        end = line.rindex("]") + 1
                        tags_str = line[start:end]
                        tags_list = json.loads(tags_str)
                        if isinstance(tags_list, list):
                            tags = [str(t).strip('"').strip("'") for t in tags_list if t]
                    except (json.JSONDecodeError, ValueError, IndexError):
                        pass
                continue

            # Collect summary lines
            if in_summary and not line.startswith(("{", "[", '"tags"', "'tags'")):
                if line and not line.startswith((",", "}", "]")):
                    clean_line = line.strip(",").strip('"').strip("'")
                    if clean_line:
                        if summary:
                            summary += " " + clean_line
                        else:
                            summary = clean_line

            # Collect tag lines
            elif in_tags:
                # Handle list format: - tag or * tag
                if line.startswith(("-", "*")):
                    tag = line[1:].strip().strip('"').strip("'").strip(",")
                    if tag and not tag.startswith(("[", "{")):
                        tags.append(tag)
                # Handle JSON array elements: "tag",
                elif line.startswith(('"', "'")):
                    tag = line.strip(",").strip('"').strip("'")
                    if tag and not tag.startswith(("[", "{")):
                        tags.append(tag)

        # If no summary found, use first substantial paragraph
        if not summary:
            for line in lines:
                if len(line) > 20 and not any(x in line.lower() for x in ['"summary"', '"tags"', "'summary'", "'tags'", ":", "{"]):
                    summary = line.strip('"').strip("'")
                    break

        # If still no summary, use whole response
        if not summary:
            summary = response.strip()

        # Ensure we have at least 3 tags
        if len(tags) < 3:
            # Extract meaningful words from summary as tags
            words = [w.strip(".,!?;:") for w in summary.split() if len(w) > 4]
            unique_words = list(dict.fromkeys(words))  # Remove duplicates while preserving order
            tags.extend(unique_words[: 3 - len(tags)])
            # Pad with generic tags if still not enough
            if len(tags) < 3:
                generic = ["content", "analysis", "text", "summary", "document"]
                tags.extend(generic[: 3 - len(tags)])

        return {
            "summary": summary,
            "tags": tags[:10],  # Limit to 10 tags
            "language": None,
        }


def get_default_llm_client(model: str = "llama3.2:latest", provider: str = "ollama") -> Any:
    """Get default LLM client configured for specified provider.

    Args:
        model: Model name to use (default: "llama3.2:latest")
        provider: Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

    Returns:
        Configured LLM client instance
    """
    try:
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig

        # Map provider to base URL
        provider_urls = {
            "ollama": "http://localhost:11434",
            "lmstudio": "http://localhost:1234",
            "mlx": "mlx",  # MLX uses local models
        }

        provider_lower = provider.lower()
        if provider_lower not in provider_urls:
            msg = f"Unknown provider: {provider}. Must be one of: ollama, lmstudio, mlx"
            raise LLMError(msg)

        # Create config for specified provider
        config = LLMConfig(
            provider=provider_lower,
            base_url=provider_urls[provider_lower],
        )
        return LLMClient(config)
    except ImportError:
        msg = "llm_client module not available"
        raise LLMError(msg)
    except Exception as e:
        msg = f"Failed to create default LLM client: {e}"
        raise LLMError(msg)
