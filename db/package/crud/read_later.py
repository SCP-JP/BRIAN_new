from sqlalchemy.orm import Session

from .. import models


# ------
# ReadLater
# ------

class ReadLaterCrud:
    @staticmethod
    def find_by_message(db: Session, user_id: int, guild_id: int, channel_id: int, message_id: int):
        return db.query(models.ReadLaterMessage).filter(
            models.ReadLaterMessage.user_id == user_id,
            models.ReadLaterMessage.guild_id == guild_id,
            models.ReadLaterMessage.channel_id == channel_id,
            models.ReadLaterMessage.message_id == message_id
        ).first()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(models.ReadLaterMessage).filter(
            models.ReadLaterMessage.id == id
        ).first()

    @staticmethod
    def find_all_by_user_id(db: Session, user_id: int):
        return db.query(models.ReadLaterMessage).filter(
            models.ReadLaterMessage.user_id == user_id
        ).all()

    @staticmethod
    def find_all_undone_by_user_id(db: Session, user_id: int):
        return db.query(models.ReadLaterMessage).filter(
            models.ReadLaterMessage.user_id == user_id,
            models.ReadLaterMessage.is_done == False
        ).all()

    @staticmethod
    def find_all_done_by_user_id(db: Session, user_id: int):
        return db.query(models.ReadLaterMessage).filter(
            models.ReadLaterMessage.user_id == user_id,
            models.ReadLaterMessage.is_done == True
        ).all()

    @staticmethod
    def create(db: Session, user_id: int, guild_id: int, channel_id: int, message_id: int):
        if ReadLaterCrud.find_by_message(db, user_id, guild_id, channel_id, message_id) is not None:
            return None

        db_message = models.ReadLaterMessage(
            user_id=user_id,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def mark_done(db: Session, record_id: int, is_done: bool):
        db_message = ReadLaterCrud.get_by_id(db, record_id)
        if db_message is None:
            return None
        db_message.is_done = is_done
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def delete(db: Session, record_id: int):
        db_message = ReadLaterCrud.get_by_id(db, record_id)
        if db_message is None:
            return None
        db.delete(db_message)
        db.commit()
        return db_message
