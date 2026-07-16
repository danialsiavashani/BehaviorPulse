from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract interface every LLM provider client must implement.

    The rest of the app only ever depends on this interface, never on a
    specific provider's SDK - swapping DeepSeek for Gemini or Claude later
    means writing one new class here, not touching any calling code.
    """

    @abstractmethod
    def summarize_observation_analysis(self, evidence_packet: dict) -> dict:
        """Takes the compact evidence packet computed by the analytics
        engine and returns a dict with exactly these keys:
            - summary: str
            - prediction: str
            - recommendations: list[str]

        Implementations must never invent numbers that aren't already
        present in evidence_packet - the LLM explains computed facts, it
        doesn't calculate anything itself.
        """
        raise NotImplementedError