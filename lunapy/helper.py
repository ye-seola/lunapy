from lunapy.api import LunaAPI
from lunapy.type import ChatLog


class ChatHelper:
    def __init__(self, luna_api: LunaAPI):
        self.luna_api = luna_api

    async def get_chatlogs_by_log_id(self, log_id: int):
        res = await self.luna_api.query(
            """
            SELECT
                cl._id as db_id,
                cl.id as log_id,
                cl.chat_id as chat_id,
                cl.user_id as user_id,
                cl.type as type,
                kakao_decrypt(cl.message, json_extract(cl.v, "$.enc"), cl.user_id) as message,
                kakao_decrypt(cl.attachment, json_extract(cl.v, "$.enc"), cl.user_id) as attachment,
                cl.created_at as sent_at,
                                  
                COALESCE(
                    kakao_decrypt(friends.name, friends.enc),
                    kakao_decrypt(open.nickname, open.enc),
                    crypto_user.nickname
                ) AS nickname
            FROM db1.chat_logs cl
            LEFT JOIN db2.friends friends ON cl.user_id = friends.id
            LEFT JOIN db2.open_chat_member open ON cl.user_id = open.user_id
            LEFT JOIN user.user crypto_user ON cl.user_id = crypto_user.id
            WHERE cl.id = ?;
        """,
            [log_id],
        )

        if not res:
            return None

        return ChatLog(**res[0])
