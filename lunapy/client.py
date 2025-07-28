import asyncio
import json
from websockets.asyncio.client import connect
from websockets import ConnectionClosed

from lunapy.api import LunaAPI, LunaRawChatLog
from lunapy.dispatcher import Dispatcher
from lunapy.event import (
    FeedEventUser,
    MessageDeleted,
    MessageHidden,
    UserJoined,
    UserKicked,
    UserLeft,
)
from lunapy.router import Router
from lunapy.services import ChatService
from lunapy.type import (
    AllMention,
    Channel,
    ChatContext,
    FeedType,
    LunaEventName,
    Mention,
    MentionInfo,
    Message,
    MessageType,
    OpenChannelExtra,
    User,
    OpenUserExtra,
)


class LunaClient:
    def __init__(self, luna_host: str, state: object):
        self.luna_host = luna_host
        self.luna_api = LunaAPI("http://" + self.luna_host)
        self.dispatcher = Dispatcher()
        self.chat_service = ChatService(self.luna_api)
        self.state = state

    def include_router(self, router: Router):
        for event_name, handler in router.get_handlers():
            self.dispatcher.register(event_name, handler)

    async def close(self):
        await self.luna_api.session.close()

    async def start(self):
        async def connect_ws(url: str, timeout: float = 5.0):
            return await asyncio.wait_for(connect(url), timeout)

        while True:
            try:
                ws = await connect_ws(f"ws://{self.luna_host}/ws")
                print("연결 성공")

                try:
                    async for msg in ws:
                        try:
                            self._process(msg)
                        except Exception as e:
                            print("Processing Error", e)
                finally:
                    await ws.close()
            except (ConnectionClosed, IOError, Exception) as e:
                print(f"3초 후 재연결 합니다 {e}")
                await asyncio.sleep(3)
                continue

    def _process(self, msg: str | bytes):
        event_name: LunaEventName = "message"
        chat = self._parse(msg)

        container = {
            ChatContext: chat,
            ChatService: self.chat_service,
        }

        if chat.message.type == MessageType.FEED:
            feed = json.loads(chat.message.content)
            feed_type = FeedType(feed["feedType"])
            timestamp = chat.message.send_at

            if feed_type == FeedType.USER_JOINED:
                event_name = "user_joined"

                container[UserJoined] = UserJoined(
                    joined_users=[
                        FeedEventUser(id=user["userId"], nickname=user["nickName"])
                        for user in feed["members"]
                    ],
                    timestamp=timestamp,
                )
            elif feed_type == FeedType.USER_LEFT:
                event_name = "user_left"

                member = feed["member"]
                container[UserLeft] = UserLeft(
                    left_user=FeedEventUser(
                        id=member["userId"], nickname=member["nickName"]
                    ),
                    timestamp=timestamp,
                )
            elif feed_type == FeedType.USER_KICKED:
                event_name = "user_kicked"

                member = feed["member"]
                container[UserKicked] = UserKicked(
                    kicked_user=FeedEventUser(
                        id=member["userId"], nickname=member["nickName"]
                    ),
                    kicked_by=chat.sender,
                    timestamp=timestamp,
                )
            elif feed_type == FeedType.MESSAGE_DELETED:
                event_name = "message_deleted"
                container[MessageDeleted] = MessageDeleted(
                    log_id=feed["logId"],
                    timestamp=timestamp,
                )
            elif feed_type == FeedType.MESSAGE_HIDDEN:
                # TODO: process old hidden type
                event_name = "message_hidden"

                container[MessageHidden] = MessageHidden(
                    log_ids=[info["logId"] for info in feed["chatLogInfos"]],
                    timestamp=timestamp,
                )
        else:
            event_name = "message"

        self.dispatcher.dispatch("chat", container)
        self.dispatcher.dispatch(event_name, container)

    def _parse(self, msg: str | bytes):
        chatlog = LunaRawChatLog(**json.loads(msg))

        sender = User(id=chatlog.user_id, nickname="", profile_url="", open_extra=None)
        channel = Channel(
            id=chatlog.chat_id,
            type=chatlog.room_type,
            private_meta=chatlog.room_private_meta,
            open_extra=None,
        )
        message = Message(
            db_id=chatlog.db_id,
            log_id=chatlog.log_id,
            send_at=chatlog.send_at,
            type=MessageType(chatlog.type),
            content=chatlog.message,
            attachment=chatlog.attachment,
            mention_info=self._parse_mention_info(chatlog.attachment),
        )

        if channel.type == "OM":
            sender.nickname = chatlog.open_nickname
            sender.profile_url = chatlog.open_profile_url

            sender.open_extra = OpenUserExtra(
                member_type=chatlog.open_link_member_type,
                profile_link_id=chatlog.open_profile_link_id,
                profile_type=chatlog.open_profile_type,
            )

            channel.open_extra = OpenChannelExtra(
                link_id=chatlog.openlink_id,
                link_url=chatlog.openlink_room_url,
                host_user_id=chatlog.openlink_host_id,
                name=chatlog.openlink_room_name,
                cover_url=chatlog.openlink_room_cover_url,
            )
        else:
            sender.nickname = chatlog.crypto_user_nickname or chatlog.friends_nickname
            sender.profile_url = (
                chatlog.crypto_user_profile_url or chatlog.friends_profile_url
            )

        return ChatContext(
            sender=sender,
            message=message,
            channel=channel,
            is_mine=chatlog.v_meta["isMine"],
            origin=chatlog.v_meta["origin"],
            api=self.luna_api,
            state=self.state,
        )

    def _parse_mention_info(self, attachment: str):
        try:
            attachm: dict = json.loads(attachment)
        except Exception:
            return MentionInfo(None, [])

        all_mention = None
        if "all_mention" in attachm:
            all_mention = AllMention(at=attachm.get("all_mention", {}).get("at", -1))

        mentions = list(
            map(
                lambda v: Mention(user_id=v["user_id"], at=v["at"], len=v["len"]),
                attachm.get("mentions", []),
            )
        )

        return MentionInfo(all_mention, mentions)
