from dataclasses import dataclass
import aiohttp


@dataclass
class Media:
    data: bytes

    filename: str | None = None
    mime_type: str | None = None


class LunaAPI:
    def __init__(self, luna_host: str):
        self.luna_host = luna_host.rstrip("/")
        self.session = aiohttp.ClientSession()

    async def reply(self, chat_id: int, *values: object, sep: str | None = " "):
        await self._reply(
            chat_id=chat_id,
            message=(sep or "").join(map(str, values)),
        )

    async def _reply(self, chat_id: int, message: str):
        url = f"{self.luna_host}/reply"
        payload = {"chat_id": chat_id, "message": message}
        async with self.session.post(url, json=payload) as resp:
            if not resp.ok:
                print(await resp.json())

    async def reply_media(self, chat_id: int, media_list: list[Media | bytes]):
        converted: list[Media] = []
        for m in media_list:
            if isinstance(m, Media):
                converted.append(m)
            elif isinstance(m, bytes):
                converted.append(Media(data=m))
            else:
                raise TypeError(f"Invalid media type: {type(m)}")
        await self._reply_media(chat_id, converted)

    async def _reply_media(self, chat_id: int, media_list: list[Media]):
        data = aiohttp.FormData()

        for i, media in enumerate(media_list):
            data.add_field(
                name="media",
                value=media.data,
                filename=media.filename or f"file_{i}",
                content_type=media.mime_type,
            )

        url = f"{self.luna_host}/reply_media?chat_id={chat_id}"
        async with self.session.post(url, data=data) as resp:
            if not resp.ok:
                print(await resp.json())

    async def query(self, query: str, binds: list[str | int | bool | float] = []):
        async with self.session.post(
            f"{self.luna_host}/query", json={"query": query, "binds": binds}
        ) as resp:
            if not resp.ok:
                raise Exception(await resp.json())

            return await resp.json()


@dataclass
class LunaRawChatLog:
    db_id: int
    log_id: int
    message: str
    attachment: str

    user_id: int

    chat_id: int
    room_private_meta: dict
    room_type: str

    openlink_id: int
    openlink_host_id: int
    openlink_room_cover_url: str
    openlink_room_name: str
    openlink_room_url: str

    crypto_user_nickname: str
    crypto_user_profile_url: str

    friends_nickname: str
    friends_profile_url: str

    open_nickname: str
    open_profile_url: str

    open_profile_link_id: int
    open_profile_type: int
    open_link_member_type: int

    send_at: int
    type: int

    v_meta: dict
