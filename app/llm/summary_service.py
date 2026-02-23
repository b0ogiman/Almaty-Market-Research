"""Executive summary generation via LLM."""

from app.llm.openai_client import OpenAIClient
from app.llm.prompts import ExecutiveSummaryPrompt
from app.logging_config import get_logger

logger = get_logger("llm.summary")


class ExecutiveSummaryService:
    """Generate executive summaries from findings."""

    def __init__(self, client: OpenAIClient | None = None) -> None:
        self.client = client or OpenAIClient()

    async def generate(
        self,
        key_findings: list[str],
        top_opportunities: list[str],
    ) -> str:
        """Generate executive summary text."""
        if not key_findings and not top_opportunities:
            return "No data available for summary."
        messages = ExecutiveSummaryPrompt.build(key_findings, top_opportunities)
        try:
            return await self.client.complete(messages, temperature=0.3)
        except Exception as e:
            logger.exception("Summary generation failed: %s", str(e))
            return "Summary generation failed."
