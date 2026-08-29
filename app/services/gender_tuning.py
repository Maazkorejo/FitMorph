class GenderTuner:
    """Adapts workout parameters based on gender-specific physiology and recovery mechanics."""

    @staticmethod
    def get_rep_and_rest_protocol(goal: str, gender: str, is_compound: bool) -> dict:
        """Calculates tailored rep targets, rest periods, and RPE based on goal and gender."""
        is_female = gender.lower() == "female"

        if goal == "strength":
            if is_female:
                # Women handle slightly higher relative intensity before form breakdown
                reps = "3-5" if is_compound else "6-8"
                rest = 120 if is_compound else 75
                rpe = 8.5
            else:
                reps = "2-5" if is_compound else "5-8"
                rest = 180 if is_compound else 90
                rpe = 9.0

        elif goal == "fat_loss":
            if is_female:
                # High density, capitalize on faster intra-set recovery
                reps = "12-15"
                rest = 45 if not is_compound else 60
                rpe = 7.5
            else:
                reps = "10-12"
                rest = 60 if not is_compound else 75
                rpe = 8.0

        else:  # hypertrophy (muscle building)
            if is_female:
                reps = "10-12" if is_compound else "12-15"
                rest = 60 if not is_compound else 75
                rpe = 8.0
            else:
                reps = "8-10" if is_compound else "10-12"
                rest = 90 if is_compound else 60
                rpe = 8.5

        return {
            "reps": reps,
            "rest_seconds": rest,
            "rpe_target": rpe
        }

    @staticmethod
    def get_muscle_priority_weights(gender: str) -> dict:
        """Returns relative volume multiplier biases per muscle group."""
        if gender.lower() == "female":
            return {
                "Glutes": 1.4,
                "Hamstrings": 1.2,
                "Quads": 1.1,
                "Upper Back": 1.2,  # posture support
                "Chest": 0.8,
                "Shoulders": 1.0,
                "Core": 1.1
            }
        else:
            return {
                "Chest": 1.3,
                "Shoulders": 1.3,  # V-taper delts
                "Lats": 1.3,
                "Upper Back": 1.2,
                "Quads": 1.1,
                "Hamstrings": 1.0,
                "Glutes": 0.9,
                "Core": 1.0
            }
