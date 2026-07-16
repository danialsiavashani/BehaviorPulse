from app.services.llm.base import LLMClient


class FallbackClient(LLMClient):
    """Used when no LLM_API_KEY is configured. Returns the deterministic
    summary/prediction the analytics engine already computed, instead of
    an LLM-written one. The app should never be fully broken just because
    no LLM key is set - per spec, it must still return computed metrics
    and a simple fallback summary.
    """

    def summarize_observation_analysis(self, evidence_packet: dict) -> dict:
        subject = evidence_packet.get("subject_label", "the subject")
        top_day = evidence_packet.get("top_day")
        top_time_window = evidence_packet.get("top_time_window")
        recurring_pattern = evidence_packet.get("recurring_pattern")

        if top_day and top_time_window:
            summary = f"{subject} observations are concentrated around {top_time_window}, especially on {top_day}."
            prediction = f"Based on the strongest recurring window, the next likely observation window is {top_day} around {top_time_window}."
        else:
            summary = f"Not enough data yet to identify a clear pattern for {subject}."
            prediction = "Not enough data yet to make a reliable prediction."

        recommendations = []
        if recurring_pattern:
            recommendations.append(f"Pattern detected: {recurring_pattern}. Consider monitoring this window closely.")
        recommendations.append("Configure an LLM provider for richer, plain-language analysis summaries.")

        return {
            "summary": summary,
            "prediction": prediction,
            "recommendations": recommendations,
        }