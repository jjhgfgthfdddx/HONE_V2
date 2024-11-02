from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_poster, temp
import re
from database.users_chats_db import db
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, LOG_CHANNEL
from database.ia_filterdb import save_file2, save_file3, save_file4, save_file5, check_file, unpack_new_file_id

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_info = await bot.get_me()  # Fetch bot information asynchronously
    bot_id = bot_info.id
    """Media Handler"""
    for file_type in ("document", "video"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    
    if message.id % 4 == 0:
        tru = await check_file(media)
        if tru == "okda":
            success, status_nb = await save_file2(media)
            if success and status_nb == 1 and await db.get_send_movie_update_status(bot_id):
                file_id, file_ref = unpack_new_file_id(media.file_id)
                await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)
            else:
                print("skipped duplicate file from saving to db 😌")
                
    if message.id % 4 == 1:
        tru = await check_file(media)
        if tru == "okda":
            success, status_nb = await save_file3(media)
            if success and status_nb == 1 and await db.get_send_movie_update_status(bot_id):
                file_id, file_ref = unpack_new_file_id(media.file_id)
                await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)
            else:
                print("skipped duplicate file from saving to db 😌")
    
    if message.id % 4 == 2:
        tru = await check_file(media)
        if tru == "okda":
            success, status_nb = await save_file4(media)
            if success and status_nb == 1 and await db.get_send_movie_update_status(bot_id):
                file_id, file_ref = unpack_new_file_id(media.file_id)
                await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)
            else:
                print("skipped duplicate file from saving to db 😌")
            
        else:
            if tru == "okda":
                success, status_nb = await save_file5(media)
                if success and status_nb == 1 and await db.get_send_movie_update_status(bot_id):
                    file_id, file_ref = unpack_new_file_id(media.file_id)
                    await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)
                else:
                    print("skipped duplicate file from saving to db 😌")

async def get_imdb(file_name):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb:
        return imdb.get('poster')
    return None
    
async def movie_name_format(file_name):
  filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
  return filename

async def check_qualities(text, qualities: list):
    quality = []
    for q in qualities:
        if q in text:
            quality.append(q)
    quality = ", ".join(quality)
    return quality[:-2] if quality.endswith(", ") else quality

async def send_movie_updates(bot, file_name, caption, file_id):
    try:
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None      
        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption)
        if not season:
            season = re.search(pattern, file_name) 
        if year:
            file_name = file_name[:file_name.find(year) + 4]      
        if not year:
            if season:
                season = season.group(1) if season else None       
                file_name = file_name[:file_name.find(season) + 1]
        qualities = ["ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", 
                     "camrip", "WEB-DL" "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", 
                     "dvdrip", "dvdscr", "HDTC", "dvdscreen", "HDTS", "hdts"]
        quality = await check_qualities(caption, qualities) or "HDRip"
        language = ""
        nb_languages = ["Hindi", "Bengali", "English", "Marathi", "Tamil", "Telugu", "Malayalam", "Kannada", "Punjabi", "Gujrati", "Korean", "Japanese", "Bhojpuri", "Dual", "Multi"]    
        for lang in nb_languages:
            if lang.lower() in caption.lower():
                language += f"{lang}, "
        language = language.strip(", ") or "𝖮𝗋𝗂𝗀𝗂𝗇𝖺𝗅 𝖠𝗎𝖽𝗂𝗈"
        movie_name = await movie_name_format(file_name)    
        if movie_name in processed_movies:
            return 
        processed_movies.add(movie_name)    
        poster_url = await get_imdb(movie_name)
        caption_message = f"<b>✅ {movie_name}</b>\n\n🔊 {language}\n\n<u>🆙 𝖥𝗂𝗅𝖾𝗌 𝖠𝗋𝖾 𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾</b>" 
        search_movie = movie_name.replace(" ", '-')
        movie_update_channel = await db.movies_update_channel_id()    
        btn = [[
            InlineKeyboardButton('Click Here To Search', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        if poster_url:
            await bot.send_message(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
                                   text=caption_message, reply_markup=reply_markup)
        else:
            await bot.send_message(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
                                   text=caption_message, reply_markup=reply_markup)  
    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')
