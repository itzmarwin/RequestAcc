# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from plugins.database import db
import logging

# Import ListenerTimeout from pyromod
try:
    from pyromod.exceptions import ListenerTimeout
except ImportError:
    # If not available, create a custom exception
    class ListenerTimeout(Exception):
        pass

logger = logging.getLogger(__name__)

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    if not message.from_user:
        return await message.reply("⚠️ Please send this command from your personal account.")
    
    # First check if user exists in database
    if not await db.is_user_exist(message.from_user.id):
        await message.reply("**You are not logged in.**")
        return
    
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        await message.reply("**You are not logged in.**")
        return 
    
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    if not message.from_user:
        return await message.reply("⚠️ Please send this command from your personal account.")
    
    # First add user to database if not exists
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Your Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return 
    
    user_id = int(message.from_user.id)
    
    try:
        phone_number_msg = await bot.ask(
            chat_id=user_id, 
            text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>",
            timeout=300
        )
    except ListenerTimeout:
        return await message.reply("**⏰ Timeout! Login process cancelled. Please try /login again.**")
    except Exception as e:
        logger.error(f"Error in ask: {e}")
        return await message.reply(f"**Error: {str(e)}\n\nPlease try /login again.**")
    
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    
    try:
        await client.connect()
    except Exception as e:
        return await phone_number_msg.reply(f"**Connection Error: {str(e)}**")
    
    await phone_number_msg.reply("Sending OTP...")
    
    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await client.disconnect()
        return await phone_number_msg.reply('**Phone number is invalid.**')
    except Exception as e:
        await client.disconnect()
        return await phone_number_msg.reply(f"**Error: {str(e)}**")
    
    try:
        phone_code_msg = await bot.ask(
            user_id, 
            "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel the process**", 
            filters=filters.text, 
            timeout=600
        )
    except ListenerTimeout:
        await client.disconnect()
        return await message.reply("**⏰ Timeout! Login process cancelled.**")
    except Exception as e:
        await client.disconnect()
        logger.error(f"Error in OTP ask: {e}")
        return await message.reply(f"**Error: {str(e)}**")
    
    if phone_code_msg.text == '/cancel':
        await client.disconnect()
        return await phone_code_msg.reply('<b>Process cancelled!</b>')
    
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await client.disconnect()
        return await phone_code_msg.reply('**OTP is invalid.**')
    except PhoneCodeExpired:
        await client.disconnect()
        return await phone_code_msg.reply('**OTP is expired.**')
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(
                user_id, 
                '**Your account has enabled two-step verification. Please provide the password.\n\nEnter /cancel to cancel the process**', 
                filters=filters.text, 
                timeout=300
            )
        except ListenerTimeout:
            await client.disconnect()
            return await message.reply("**⏰ Timeout! Login process cancelled.**")
        except Exception as e:
            await client.disconnect()
            return await message.reply(f"**Error: {str(e)}**")
        
        if two_step_msg.text == '/cancel':
            await client.disconnect()
            return await two_step_msg.reply('<b>Process cancelled!</b>')
        
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await client.disconnect()
            return await two_step_msg.reply('**Invalid Password Provided**')
        except Exception as e:
            await client.disconnect()
            return await two_step_msg.reply(f"**Error: {str(e)}**")
    except Exception as e:
        await client.disconnect()
        return await phone_code_msg.reply(f"**Error: {str(e)}**")
    
    try:
        string_session = await client.export_session_string()
        await client.disconnect()
    except Exception as e:
        await client.disconnect()
        return await message.reply(f"**Error exporting session: {str(e)}**")
    
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string</b>')
    
    try:
        # Save session to database
        await db.set_session(message.from_user.id, session=string_session)
        await bot.send_message(
            message.from_user.id, 
            "<b>✅ Account Login Successfully.\n\nNow you can use /accept command to accept all pending join requests.\n\nIf You Get Any Error Related To AUTH KEY Then /logout first and /login again</b>"
        )
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")


# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
