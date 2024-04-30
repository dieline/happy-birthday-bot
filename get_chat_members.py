from pyrogram import Client

api_id = 21777839
api_hash = '81c5a13cf6e4de1c982d47a9607afebe'
bot_token = '6801000433:AAFxb9rCFs8dtZukC_Peu9ZgIYlGuew4gG0'


async def get_chat_members(chat_id):
    app = Client("Имя | Бот", api_id=api_id, api_hash=api_hash, bot_token=bot_token, in_memory=True)
    chat_members = []
    await app.start()
    async for member in app.get_chat_members(chat_id):
        chat_members = chat_members + [member.user.id]
    await app.stop()
    return chat_members
