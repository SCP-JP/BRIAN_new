from datetime import datetime

from pydantic import BaseModel


class ThreadListManageTargetBase(BaseModel):
    guild_id: str
    channel_id: str


class ThreadListManageTargetCreate(ThreadListManageTargetBase):
    pass


class ThreadListManageTarget(ThreadListManageTargetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class GuildConfigBase(BaseModel):
    guild_id: str
    thread_list_threshold: int | None


class GuildConfigCreate(GuildConfigBase):
    pass


class GuildConfig(GuildConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
