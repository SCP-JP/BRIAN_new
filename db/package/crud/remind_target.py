from datetime import timedelta

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
               remind_at: models.datetime, remind_to: str | None,
               is_snooze: bool = False, previous_remind_message_id: int | None = None):
        db_remind_target = models.RemindTarget(
            user_id=user_id,
            channel_id=channel_id,
            note=note,
            remind_at=remind_at,
            remind_to=remind_to,
            is_snooze=is_snooze,
            previous_remind_message_id=previous_remind_message_id
        )
        db.add(db_remind_target)
        db.commit()
        db.refresh(db_remind_target)
        return db_remind_target

    @staticmethod
    def create_snooze(db: Session, existing_target: models.RemindTarget):
        interval_hours = (existing_target.remind_at - existing_target.created_at).seconds // 3600
        remind_at = existing_target.remind_at + timedelta(hours=interval_hours)
        return RemindTargetCrud.create(
            db, existing_target.user_id, existing_target.channel_id, existing_target.note,
            remind_at, existing_target.remind_to,
            is_snooze=True,
            previous_remind_message_id=existing_target.remind_message_id
        )

    @staticmethod
    def cancel_snooze(db: Session, previous_message_id: int):
        db.query(models.RemindTarget).filter(
            models.RemindTarget.previous_remind_message_id == previous_message_id
        ).delete()
        db.commit()
        return True

    @staticmethod
    def get_by_remind_message_id(db: Session, remind_message_id: int):
        return db.query(models.RemindTarget).filter(
            models.RemindTarget.remind_message_id == remind_message_id
        ).first()

    @staticmethod
    def get_last_created_reminder(db: Session, user_id: int, channel_id: int):
        return db.query(models.RemindTarget).filter(
            models.RemindTarget.user_id == user_id,
            models.RemindTarget.channel_id == channel_id
        ).order_by(models.RemindTarget.created_at.desc()).first()

    @staticmethod
    def update_remind_flag(db: Session, remind_target_id: int, remind_message_id: int):
        db.query(models.RemindTarget).filter(models.RemindTarget.id == remind_target_id).update(
            {'is_reminded': True, 'remind_message_id': remind_message_id}
        )
        db.commit()
        return True

    @staticmethod
    def delete(db: Session, remind_target_id: int):
        db.query(models.RemindTarget).filter(
            models.RemindTarget.id == remind_target_id, models.RemindTarget.is_reminded == False).delete()
        db.commit()
        return True
