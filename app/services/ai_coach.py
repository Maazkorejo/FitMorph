import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("fitmorph.ai_coach")

class AICoach:
    """Provides personalized coaching cues, recovery advice, and form guidance."""

    @classmethod
    def get_coaching_advice(
        cls,
        goal: str,
        gender: str,
        equipment: str,
        injuries: list[str],
        recent_volume_change: float
    ) -> Dict[str, Any]:
        """Generates contextual coaching recommendations based on training state."""
        # Attempt Gemini if key present
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)

                prompt = f"""You are an elite strength & conditioning coach.
User Profile:
- Goal: {goal}
- Gender: {gender}
- Equipment: {equipment}
- Flagged Joint Issues: {', '.join(injuries) if injuries else 'None'}
- Weekly Volume Change: {recent_volume_change}%

Give a concise, highly practical 3-bullet coaching brief covering:
1. Form/Joint safety tip for their flagged injuries.
2. Recovery/Nutrition focus for their specific goal.
3. Mindset/Progression cue for the upcoming week.
Keep it punchy, motivating, and strictly safe.
"""
                response = model.generate_content(prompt)
                return {
                    "source": "gemini-1.5-flash",
                    "coaching_advice": response.text.strip()
                }
            except Exception as e:
                logger.warning(f"AI Coach Gemini API call failed: {e}. Using deterministic fallback.")

        # Deterministic Biomechanical Advice
        tips = []
        if "lower_back" in injuries:
            tips.append("Spinal Safety: Prioritize chest-supported rows and maintain neutral pelvis during all hip hinges.")
        elif "knees" in injuries:
            tips.append("Knee Protection: Focus on hip-dominant hinge movements (RDLs/glute bridges) and keep knees tracking over 2nd toe.")
        elif "shoulders" in injuries:
            tips.append("Rotator Cuff Protection: Keep elbows tucked at 45 degrees on pressing; avoid extreme flared flaring.")
        else:
            tips.append("Progressive Overload: Aim to add 1 rep or 1-2kg on primary compound lifts each week.")

        if goal == "fat_loss":
            tips.append("Nutrition & Cardio: Keep protein high (2.0g/kg) and hit your 30-min Zone 2 LISS cardio to maximize lipid oxidation.")
        elif goal == "strength":
            tips.append("Recovery: Rest 2-3 full minutes between heavy compound sets to allow complete phosphocreatine replenishment.")
        else:
            tips.append("Hypertrophy: Focus on controlled 3-second negatives (eccentrics) to maximize mechanical tension.")

        return {
            "source": "deterministic_coach",
            "coaching_advice": "\n".join(f"• {t}" for t in tips)
        }
