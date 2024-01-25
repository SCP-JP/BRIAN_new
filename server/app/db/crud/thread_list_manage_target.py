from sqlalchemy.orm import Session

from .. import models


# ------
# ThreadListManageTarget
# ------

class ThreadListManageTargetCrud:
    @staticmethod
    def find(db: Session, guild_id: int, channel_id: int) -> models.ThreadListManageTarget | None:
        return db.query(models.ThreadListManageTarget).filter(
            models.ThreadListManageTarget.guild_id == guild_id,
            models.ThreadListManageTarget.channel_id == channel_id
        ).first()

    @staticmethod
    def find_or_create(db: Session, guild_id: int, channel_id: int) -> models.ThreadListManageTarget:
        # 重複チェック
        db_thread_list_manage_target = ThreadListManageTargetCrud.find(db, guild_id, channel_id)
        if db_thread_list_manage_target is not None:
            return db_thread_list_manage_target

        # 重複がない場合は作成
        db_thread_list_manage_target = models.ThreadListManageTarget(
            guild_id=guild_id,
            channel_id=channel_id
        )
        db.add(db_thread_list_manage_target)
        db.commit()
        db.refresh(db_thread_list_manage_target)
        return db_thread_list_manage_target

    @staticmethod
    def destroy(db: Session, guild_id: int, channel_id: int) -> models.ThreadListManageTarget | None:
        db_thread_list_manage_target = ThreadListManageTargetCrud.find(db, guild_id, channel_id)
        if db_thread_list_manage_target is None:
            return None
        db.delete(db_thread_list_manage_target)
        db.commit()
        return db_thread_list_manage_target
