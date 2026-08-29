from typing import List

class CardioEngine:
    """Calculates personalized cardio protocols aligned with goal, body mass, and joint safety."""

    @staticmethod
    def get_prescribed_cardio(
        goal: str,
        weight_kg: float,
        bmi: float,
        equipment: str,
        injuries: List[str]
    ) -> str:
        has_knee_pain = "knees" in [i.lower() for i in injuries]
        is_heavy = bmi >= 27.5 or weight_kg >= 95.0

        if goal == "fat_loss":
            if has_knee_pain or is_heavy:
                if equipment == "full_gym":
                    return "Zone 2 Low-Impact Incline Walk: 35 min at 12% incline, 4.5 km/h (protects knees)"
                elif equipment == "dumbbells_only":
                    return "Zone 2 Outdoor Steady Walk / Stationary Bike: 35 min at comfortable conversational pace"
                else:
                    return "Zone 2 Low-Impact Living Room Walk & Arm Pulses: 30 min (zero knee impact)"
            else:
                if equipment == "full_gym":
                    return "Hybrid Cardio: 25 min Zone 2 Stairmaster + 10 min HIIT Rower (20s sprint / 40s easy)"
                else:
                    return "HIIT Metabolic Intervals: 15 min (30s high knees/shadow boxing + 30s walk) + 15 min brisk walk"

        elif goal == "hypertrophy":
            # Moderate recovery cardio that doesn't blunt muscle growth
            if equipment == "full_gym":
                return "Zone 2 Active Recovery: 20 min stationary bike or flat treadmill walk (aids nutrient delivery)"
            else:
                return "Zone 2 Post-Workout Outdoor Walk: 20 min at relaxed pace (maintains metabolic health)"

        else:  # strength
            # Minimal fatigue-inducing cardio
            return "Light Aerobic Flush: 15 min easy walk or stationary cycling (clears metabolic waste)"
