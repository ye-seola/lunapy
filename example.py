import asyncio
from dataclasses import dataclass
from lunapy import LunaClient, Router, ChatContext
from lunapy.event import MessageDeleted, MessageHidden, UserJoined, UserKicked, UserLeft
from lunapy.services import ChatService

router = Router()

# @router.on_event("chat")
# async def on_all_chat(chat: ChatContext):
#     pass


@router.on_event("message")
async def on_message(chat: ChatContext["AppState"]):
    if chat.message.content == "/asdf":
        chat.state.count += 1
        await chat.reply("HELLO", chat.state.count)


@router.on_event("user_joined")
async def on_user_joined(chat: ChatContext, ev: UserJoined):
    print("user_joined", ev)


@router.on_event("user_kicked")
async def on_user_kicked(chat: ChatContext, ev: UserKicked):
    print("user_kicked", ev)


@router.on_event("user_left")
async def on_user_left(chat: ChatContext, ev: UserLeft):
    print("user_left", ev)


@router.on_event("message_deleted")
async def on_message_deleted(
    chat: ChatContext, ev: MessageDeleted, chat_service: ChatService
):
    print("message_deleted", ev)
    print(await chat_service.get_chatlogs_by_log_id(ev.log_id))


@router.on_event("message_hidden")
async def on_message_hidden(chat: ChatContext, ev: MessageHidden):
    print("message_hidden", ev)


@dataclass
class AppState:
    count: int = 0


async def main():
    client = LunaClient("127.0.0.1:5612", AppState())
    client.include_router(router)

    try:
        await client.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        await client.close()
        print("\n프로그램을 종료합니다.")


if __name__ == "__main__":
    asyncio.run(main())
