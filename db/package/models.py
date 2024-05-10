from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, DateTime, UniqueConstraint, Boolean, String

from .connection import Base


class ThreadListManageTarget(Base):
    __tablename__ = 'thread_list_manage_target'

    id = Column(Integer, primary_key=True)

    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # guild_idとchannel_idでユニーク
    __table_args__ = (
        UniqueConstraint('guild_id', 'channel_id'),
    )


class GuildConfig(Base):
    __tablename__ = 'guild_config'

    id = Column(Integer, primary_key=True)

    guild_id = Column(BigInteger, nullable=False, unique=True)

    # BOT: ThreadListManager
    thread_list_threshold = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class RemindTarget(Base):
    __tablename__ = 'remind_target'

    # PK
    id = Column(Integer, primary_key=True)

    # リマインド作成者
    user_id = Column(BigInteger, nullable=False)
    # リマインド対象Ch
    channel_id = Column(BigInteger, nullable=False)

    # 備考
    note = Column(String, nullable=True, default=None)

    # リマインド日時
    remind_at = Column(DateTime, nullable=False)

    # リマインドを受け取るユーザー（文字列）
    remind_to = Column(String, nullable=True, default=None)

    # リマインド済であるか
    is_reminded = Column(Boolean, default=False)

    # スヌーズを行うか
    is_snooze = Column(Boolean, default=False)
    # 前のリマインドのDiscordメッセージID
    previous_remind_message_id = Column(BigInteger, nullable=True, default=None)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
