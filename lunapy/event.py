from dataclasses import dataclass

from lunapy.type import FeedEventUser, User


@dataclass
class UserJoined:
    joined_users: list[FeedEventUser]
    timestamp: int


@dataclass
class UserLeft:
    left_user: FeedEventUser
    timestamp: int


@dataclass
class UserKicked:
    kicked_user: FeedEventUser
    kicked_by: User
    timestamp: int


@dataclass
class MessageDeleted:
    log_id: int
    timestamp: int


@dataclass
class MessageHidden:
    log_ids: list[int]
    timestamp: int
