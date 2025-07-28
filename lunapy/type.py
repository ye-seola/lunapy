from dataclasses import dataclass
from enum import Enum
import typing

from lunapy.api import Media, LunaAPI

from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ChatContext(Generic[T]):
    sender: "User"
    channel: "Channel"
    message: "Message"
    is_mine: bool
    origin: str
    api: LunaAPI
    state: T

    async def reply(self, *values: object, sep: str | None = " "):
        await self.api.reply(self.channel.id, *values, sep=sep)

    async def reply_media(self, media_list: list[Media | bytes]):
        await self.api.reply_media(self.channel.id, media_list=media_list)


@dataclass
class FeedEventUser:
    id: int
    nickname: str


@dataclass
class User:
    id: int
    nickname: str
    profile_url: str

    open_extra: "OpenUserExtra | None"


@dataclass
class Message:
    db_id: int
    log_id: int
    send_at: int

    type: "MessageType"

    content: str
    attachment: str

    mention_info: "MentionInfo"


@dataclass
class Channel:
    id: int
    type: str
    private_meta: dict

    open_extra: "OpenChannelExtra | None"


@dataclass
class OpenUserExtra:
    member_type: int
    profile_link_id: int
    profile_type: int


@dataclass
class OpenChannelExtra:
    link_id: int
    link_url: str
    host_user_id: int
    name: str
    cover_url: str


@dataclass
class MentionInfo:
    all_mention: "AllMention | None"
    mentions: list["Mention"]


@dataclass
class AllMention:
    at: int


@dataclass
class Mention:
    user_id: int
    at: list[int]
    len: int


LunaEventName = typing.Literal[
    "chat",
    "message",
    "user_joined",
    "user_left",
    "user_kicked",
    "message_deleted",
    "message_hidden",
]


class MessageType(Enum):
    UNKNOWN = -999
    FEED = 0
    TEXT = 1
    PHOTO = 2
    VIDEO = 3
    CONTACT = 4
    AUDIO = 5
    ANIMATED_EMOTICON = 6
    DIGITAL_ITEM_GIFT = 7
    LINK = 9
    OLD_LOCATION = 10
    AVATAR = 11
    STICKER = 12
    SCHEDULE = 13
    VOTE = 14
    LOCATION = 16
    PROFILE = 17
    FILE = 18
    ANIMATED_STICKER = 20
    NUDGE = 21
    SPRITECON = 22
    SHARP_SEARCH = 23
    POST = 24
    ANIMATED_STICKER_EX = 25
    REPLY = 26
    MULTI_PHOTO = 27
    MVOIP = 51
    VOX_ROOM = 52
    LEVERAGE = 71
    ALIMTALK = 72
    PLUS_LEVERAGE = 73
    PLUS = 81
    PLUS_EVENT = 82
    PLUS_VIRAL = 83
    SCHEDULE_FOR_OPEN_LINK = 96
    VOTE_FOR_OPEN_LINK = 97
    POST_FOR_OPEN_LINK = 98

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class FeedType(Enum):
    UNKNOWN = -9999
    USER_LEFT = 2
    USER_JOINED = 4
    USER_KICKED = 6
    MESSAGE_DELETED = 14
    MESSAGE_HIDDEN = 26

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@dataclass
class ChatLog:
    db_id: int
    log_id: int
    chat_id: int
    user_id: int
    nickname: str
    type: int
    message: str
    attachment: str
    sent_at: int
