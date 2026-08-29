import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.services.volume_calculator import VolumeCalculator

logger = logging.getLogger("fitmorph.worker")

scheduler = BackgroundScheduler()

def audit_user_plateau(db: Session, user: User) -> bool:
    """Checks an individual user for training plateau and schedules a deload if detected."""
    curr_vol, prev_vol, change_pct, is_plateau = VolumeCalculator.calculate_plateau_metrics(db, user.id)

    if is_plateau:
        active_plan = db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user.id,
            WorkoutPlan.is_active == True
        ).first()

        if active_plan and not active_plan.deload_scheduled:
            active_plan.deload_scheduled = True
            db.commit()
            logger.info(f"PlateauWorker: Scheduled Deload Week for user {user.id} (Volume change: {change_pct}%)")
            return True
    return False

def run_weekly_plateau_audit():
    """Background cron job iterating over all users to detect volume plateaus."""
    logger.info("Starting scheduled weekly plateau audit...")
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        plateaued_count = 0
        for u in users:
            if audit_user_plateau(db, u):
                plateaued_count += 1
        logger.info(f"Weekly plateau audit finished: checked {len(users)} users, scheduled {plateaued_count} deloads.")
    except Exception as e:
        logger.error(f"Error running plateau audit worker: {e}")
    finally:
        db.close()

def start_scheduler():
    """Starts the background scheduler for plateau and volume checks."""
    if not scheduler.running:
        scheduler.add_job(run_weekly_plateau_audit, "interval", hours=24, id="plateau_audit_job")
        scheduler.start()
        logger.info("BackgroundScheduler started successfully.")

def shutdown_scheduler():
    """Gracefully stops the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("BackgroundScheduler stopped.")
