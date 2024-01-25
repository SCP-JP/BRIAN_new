from sqlalchemy.orm import Session

from .. import models


# ------
# GuildConfig
# ------

class GuildConfigCrud:
    @staticmethod
    def find(db: Session, guild_id: int) -> models.GuildConfig | None:
        return db.query(models.GuildConfig).filter(models.GuildConfig.guild_id == guild_id).first()

    @staticmethod
    def find_or_create(db: Session, guild_id: int) -> models.GuildConfig:
        # 重複チェック
        db_guild_config = GuildConfigCrud.find(db, guild_id)
        if db_guild_config is not None:
            return db_guild_config

        # 重複がない場合は作成
        db_guild_config = models.GuildConfig(
            guild_id=guild_id
        )
        db.add(db_guild_config)
        db.commit()
        db.refresh(db_guild_config)
        return db_guild_config

    @staticmethod
    def destroy(db: Session, guild_id: int) -> models.GuildConfig | None:
        db_guild_config = GuildConfigCrud.find(db, guild_id)
        if db_guild_config is None:
            return None
        db.delete(db_guild_config)
        db.commit()
        return db_guild_config

    @staticmethod
    def update(db: Session, guild_id: int, data: dict) -> models.GuildConfig | None:
        db_guild_config = GuildConfigCrud.find(db, guild_id)
        if db_guild_config is None:
            return None
        for key, value in data.items():
            setattr(db_guild_config, key, value)
        db.commit()
        db.refresh(db_guild_config)
        return db_guild_config
