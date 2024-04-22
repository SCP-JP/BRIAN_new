from sqlalchemy.orm import Session

from .. import models


# ------
# RemindTarget
# ------

class RemindTargetCrud:
    @staticmethod
    def get_targets(db: Session):
        # is_remindedがFalseで、remind_atが現在時刻より前のものを取得
        return db.query(models.RemindTarget).filter(
            models.RemindTarget.is_reminded == False,
            models.RemindTarget.remind_at <= models.datetime.now()
        ).all()

    @staticmethod
    def get_user_targets(db: Session, user_id: int):
        return db.query(models.RemindTarget).filter(
            models.RemindTarget.user_id == user_id,
            models.RemindTarget.is_reminded == False
        ).order_by(models.RemindTarget.remind_at.asc()).all()

    @staticmethod
    def create(db: Session, user_id: int, channel_id: int, note: str | None,
               remind_at: models.datetime, remind_to: str | None):
        db_remind_target = models.RemindTarget(
            user_id=user_id,
            channel_id=channel_id,
            note=note,
            remind_at=remind_at,
            remind_to=remind_to
        )
        db.add(db_remind_target)
        db.commit()
        db.refresh(db_remind_target)
        return db_remind_target

    @staticmethod
    def get_last_created_reminder(db: Session, user_id: int, channel_id: int):
        return db.query(models.RemindTarget).filter(
            models.RemindTarget.user_id == user_id,
            models.RemindTarget.channel_id == channel_id
        ).order_by(models.RemindTarget.created_at.desc()).first()

    @staticmethod
    def update_remind_flag(db: Session, remind_target_id: int):
        db.query(models.RemindTarget).filter(models.RemindTarget.id == remind_target_id).update(
            {'is_reminded': True}
        )
        db.commit()
        return True

    @staticmethod
    def delete(db: Session, remind_target_id: int):
        db.query(models.RemindTarget).filter(
            models.RemindTarget.id == remind_target_id, models.RemindTarget.is_reminded == False).delete()
        db.commit()
        return True
