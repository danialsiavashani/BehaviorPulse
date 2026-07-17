from app.services.llm.base import LLMClient


class FallbackClient(LLMClient):
    """Used when no LLM_API_KEY is configured. Returns a deterministic
    summary built directly from the evidence packet, instead of an
    LLM-written one.
    """

    def summarize_observation_analysis(self, evidence_packet: dict) -> dict:
        top_subjects = evidence_packet.get("top_subjects", [])
        top_day = evidence_packet.get("top_day")
        top_time_window = evidence_packet.get("top_time_window")
        recurring_pattern = evidence_packet.get("recurring_pattern")

        if top_subjects:
            subject_summary = ", ".join(
                f"{s['subject_label']} ({s['percentage']}%)" for s in top_subjects[:3]
            )
            summary = f"Observed subjects: {subject_summary}."
            if top_day and top_time_window:
                summary += f" Activity is concentrated around {top_time_window}, especially on {top_day}."
        else:
            summary = "Not enough data yet to identify a clear pattern."

        if top_day and top_time_window:
            prediction = f"Based on the strongest recurring window, the next likely activity window is {top_day} around {top_time_window}."
        else:
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