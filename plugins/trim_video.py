#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


'''@pyrogram.Client.on_message(pyrogram.Filters.command(["trim1"]))
async def convert_to_audio(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return'''
      
@pyrogram.Client.on_message(pyrogram.Filters.command(["trim1"]))
async def trim_video(bot, update):
    text_=update.text
    
    TRChatBase(update.from_user.id, update.text, "c2a")
    if (update.reply_to_message is not None) and (update.reply_to_message.media is not None) :
        download_location = Config.DOWNLOAD_LOCATION + "/"
        ab=await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_FILE,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_FILE,
                ab,
                c_time
            )
        )
        if the_real_download_location is not None:
            a=await bot.edit_message_text(
                text=f"Video Download Successfully, now trying to trim it. \n\n⌛️Wait for some time.",
                chat_id=update.chat.id,
                message_id=ab.message_id
            )
            # don't care about the extension
            # convert video to audio format
            text = text_.split(" ", 1)[1]
            text2=text.split(':')
            print(text2[1], text2[0])
            start_time=int(text2[0])
            end_time=int(text2[1])
            f_name = the_real_download_location.rsplit('/',1)[-1]
            video_file_location = f_name+'trimmed.mp4'
            ffmpeg_extract_subclip(f"{the_real_download_location}",  text2[0],  text2[1],  targetname= f"{video_file_location}")
            #clip = VideoFileClip(the_real_download_location).subclip(start_time, end_time)
            #clip.write_videofile(video_file_location)
            logger.info(video_file_location)
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            metadata = extractMetadata(createParser(video_file_location))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            '''thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
            else:
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # get the correct width, height, and duration for videos greater than 10MB
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((90, height))
                img.save(thumb_image_path, "JPEG")'''
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            # try to upload file
            await a.delete()
            c_time = time.time()
            
            up=await bot.send_message(
            text=Translation.UPLOAD_START,
            chat_id=update.chat.id,
            )

            c_time = time.time()
            await bot.send_video(
                chat_id=update.chat.id,
                video=video_file_location,
                duration=duration,
                # performer="",
                # title="",
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    up, 
                    c_time
                )
            )
            try:
                os.remove(the_real_download_location)
                os.remove(video_file_location)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=up.message_id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"**Reply** with a telegram video file to convert.",
            reply_to_message_id=update.message_id
        )
