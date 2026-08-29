from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from app.models.log import LoggedSet

class VolumeCalculator:
    """Computes workout volume metrics and progression ratios."""

    @staticmethod
    def get_weekly_volume(db: Session, user_id: int, days_back: int = 7) -> Dict[str, float]:
        """Calculates volume load (kg) grouped by muscle group over a recent window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        sets = db.query(LoggedSet).filter(
            LoggedSet.user_id == user_id,
            LoggedSet.logged_at >= cutoff
        ).all()

        volume_by_muscle = {}
        for s in sets:
            vol = s.volume_load
            volume_by_muscle[s.muscle_group] = round(volume_by_muscle.get(s.muscle_group, 0.0) + vol, 2)

        return volume_by_muscle

    @staticmethod
    def calculate_plateau_metrics(db: Session, user_id: int) -> Tuple[float, float, float, bool]:
        """Compares past 7 days volume vs prior 7-14 days volume. Returns (current_vol, prev_vol, pct_change, is_plateau)."""
        now = datetime.now(timezone.utc)
        week1_cutoff = now - timedelta(days=7)
        week2_cutoff = now - timedelta(days=14)

        current_sets = db.query(LoggedSet).filter(
            LoggedSet.user_id == user_id,
            LoggedSet.logged_at >= week1_cutoff
        ).all()

        prev_sets = db.query(LoggedSet).filter(
            LoggedSet.user_id == user_id,
            LoggedSet.logged_at >= week2_cutoff,
            LoggedSet.logged_at < week1_cutoff
        ).all()

        current_vol = sum(s.volume_load for s in current_sets)
        prev_vol = sum(s.volume_load for s in prev_sets)

        if prev_vol == 0.0:
            return (round(current_vol, 2), 0.0, 0.0, False)

        change_pct = round(((current_vol - prev_vol) / prev_vol) * 100.0, 1)

        # Plateau detected if volume has not grown or dropped > 5% despite consistent frequency
        is_plateau = len(current_sets) >= 10 and -10.0 <= change_pct <= 1.0

        return (round(current_vol, 2), round(prev_vol, 2), change_pct, is_plateau)
