import asyncio 
from pyrogram import Client, filters, enums
from pyrogram.errors import PeerIdInvalid, ChannelPrivate, UserNotParticipant, ListenerTimeout
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start') & filters.private)
async def start_message(c, m):
    # Check if message is from a user (not channel/anonymous)
    if not m.from_user:
        return await m.reply("⚠️ Please send this command from your personal account, not from a channel.")
    
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            try:
                await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
            except Exception as e:
                logger.error(f"Could not send log to channel: {e}")
        
        await m.reply_photo(
            photo="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
            caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Request.\n\nFor All Pending Join Request Use - /accept\n\nFor Login Your Account Use - /login</b>",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
                ],[
                    InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/Kingvj01'),
                    InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/VJ_Botz')
                ]]
            )
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await m.reply("⚠️ An error occurred. Please try again.")

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    if not message.from_user:
        return await message.reply("⚠️ Please send this command from your personal account.")
    
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    
    if user_data is None:
        return await show.edit("**For Accept Pending Request You Have To /login First.**")
    
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except Exception as e:
        return await show.edit(f"**Your Login Session Expired Or Invalid.\n\nError: {str(e)}\n\nPlease /logout First Then Login Again By - /login**")
    
    await show.edit("**Now Send Channel/Group Username OR Forward A Message From Your Channel/Group**\n\n**Example:**\n- @YourChannelUsername\n- OR Forward any message\n\n**Make Sure Your Logged In Account Is Admin With Full Rights.**")
    
    try:
        # Use listen with timeout
        vj = await client.listen(message.chat.id, timeout=300)
    except ListenerTimeout:
        await acc.disconnect()
        return await show.edit("**⏰ Timeout! You took too long to respond. Please try /accept again.**")
    except Exception as e:
        await acc.disconnect()
        return await show.edit(f"**Error: {str(e)}\n\nPlease try /accept again.**")
    
    chat_id = None
    chat_title = None
    
    # Check if username is sent
    if vj.text and vj.text.startswith('@'):
        chat_username = vj.text
        try:
            info = await acc.get_chat(chat_username)
            chat_id = info.id
            chat_title = info.title
        except Exception as e:
            await acc.disconnect()
            return await show.edit(f"**Error - Cannot find channel/group with username {chat_username}\n\nMake Sure:\n1. Username is correct\n2. Your account has access to it**")
    
    # Check if message is forwarded
    elif vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        chat_title = vj.forward_from_chat.title
        chat_username = vj.forward_from_chat.username
        
        # Try to resolve peer using username first, if available
        try:
            if chat_username:
                info = await acc.get_chat(chat_username)
                chat_id = info.id
            else:
                # Try to join/access the channel to resolve peer
                try:
                    info = await acc.get_chat(chat_id)
                except PeerIdInvalid:
                    # If peer invalid, ask for username
                    await acc.disconnect()
                    return await show.edit(f"**Error - Cannot access this channel/group directly.\n\nPlease send the channel/group username instead (e.g., @channelname)\n\nOR\n\nMake sure your logged account is a member/admin of this channel first.**")
        except Exception as e:
            await acc.disconnect()
            return await show.edit(f"**Error - {str(e)}**")
    else:
        await acc.disconnect()
        return await show.edit("**Please send channel username (e.g., @channelname) OR forward a message from channel/group.**")
    
    try:
        await vj.delete()
    except:
        pass
    
    # Verify admin rights
    try:
        member = await acc.get_chat_member(chat_id, "me")
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await acc.disconnect()
            return await show.edit(f"**Error - Your logged account is not admin in {chat_title}**")
    except UserNotParticipant:
        await acc.disconnect()
        return await show.edit(f"**Error - Your logged account is not a member of {chat_title}**")
    except Exception as e:
        await acc.disconnect()
        return await show.edit(f"**Error - {str(e)}**")
    
    msg = await show.edit(f"**Accepting all join requests from {chat_title}... Please wait.**")
    
    try:
        total_approved = 0
        while True:
            # Get pending join requests
            join_requests = []
            async for request in acc.get_chat_join_requests(chat_id):
                join_requests.append(request)
            
            if not join_requests:
                break
            
            # Approve all pending requests
            await acc.approve_all_chat_join_requests(chat_id)
            total_approved += len(join_requests)
            await asyncio.sleep(2)
            
        await acc.disconnect()
        if total_approved > 0:
            await msg.edit(f"**✅ Successfully Accepted All Join Requests!\n\nChannel/Group: {chat_title}\nTotal Approved: {total_approved}**")
        else:
            await msg.edit(f"**No pending join requests found in {chat_title}**")
        
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
            try:
                await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
            except:
                pass
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(m.from_user.id, "**Hello {}!\nWelcome To {}\n\n__Powered By : @VJ_Botz __**".format(m.from_user.mention, m.chat.title))
        except:
            pass
    except Exception as e:
        logger.error(f"Error in auto-approve: {e}")
        pass
