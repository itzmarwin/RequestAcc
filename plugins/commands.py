import asyncio 
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c,m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    await m.reply_photo(f"https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Request.\n\nFor All Pending Join Request Use - /accept</b>",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
            ],[
                InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/Kingvj01'),
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/VJ_Botz')
            ]]
        )
    )

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accept Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except Exception as e:
        return await show.edit(f"**Your Login Session Expired Or Invalid.\n\nError: {str(e)}\n\nPlease /logout First Then Login Again By - /login**")
    
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        chat_username = vj.forward_from_chat.username
        chat_title = vj.forward_from_chat.title
        
        try:
            # First try to get chat info to resolve peer
            if chat_username:
                # If channel has username, use it to resolve
                info = await acc.get_chat(chat_username)
            else:
                # If no username, try with chat_id
                info = await acc.get_chat(chat_id)
            
            # Verify user is admin
            member = await acc.get_chat_member(info.id, "me")
            if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                await show.edit("**Error - Your Logged In Account Is Not Admin In This Channel/Group.**")
                await acc.disconnect()
                return
                
        except Exception as e:
            await show.edit(f"**Error - {str(e)}\n\nMake Sure:\n1. Your Logged In Account Is Admin In This Channel/Group\n2. Channel/Group Is Not Private Or You Have Access To It**")
            await acc.disconnect()
            return
    else:
        await acc.disconnect()
        return await show.edit("**Message Not Forwarded From Channel Or Group.**")
    
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    
    try:
        total_approved = 0
        while True:
            # Get pending join requests
            join_requests = []
            async for request in acc.get_chat_join_requests(info.id):
                join_requests.append(request)
            
            if not join_requests:
                break
            
            # Approve all pending requests
            await acc.approve_all_chat_join_requests(info.id)
            total_approved += len(join_requests)
            await asyncio.sleep(2)  # Small delay to avoid flood
            
        await acc.disconnect()
        await msg.edit(f"**✅ Successfully Accepted All Join Requests!\n\nTotal Approved: {total_approved}**")
        
    except Exception as e:
        await acc.disconnect()
        await msg.edit(f"**An error occurred:** {str(e)}")
        
@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if NEW_REQ_MODE == False:
        return 
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(m.from_user.id, "**Hello {}!\nWelcome To {}\n\n__Powered By : @VJ_Botz __**".format(m.from_user.mention, m.chat.title))
        except:
            pass
    except Exception as e:
        print(str(e))
        pass
