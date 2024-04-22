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

    id = Column(Integer, primary_key=True)

    user_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    note = Column(String, nullable=True, default=None)

    remind_at = Column(DateTime, nullable=False)

    remind_to = Column(String, nullable=True, default=None)

    is_reminded = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
