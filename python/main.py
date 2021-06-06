#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import cv2
import logging
import telegram
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update, InlineQueryResultCachedVideo
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown
from PIL import Image
import glob

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('שלום, אנא צלם סרטון עבור כל חדר')


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


# def inlinequery(update: Update, _: CallbackContext) -> None:
#     """Handle the inline query."""
#     query = update.inline_query.query
#
#     if query == "":
#         return
#
#     results = [
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Caps",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Bold",
#             input_message_content=InputTextMessageContent(
#                 "*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
#             ),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Italic",
#             input_message_content=InputTextMessageContent(
#                 f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
#             ),
#         ),
#     ]
#
#     update.message.reply_text(results)


def message_video_handler(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    message = update.effective_message
    if message is None:
        return

    chat = update.effective_chat

    if chat is None:
        return

    chat_type = chat.type
    bot = context.bot

    if chat_type != telegram.Chat.PRIVATE:
        return

    message_id = message.message_id
    chat_id = message.chat.id
    attachment = message.video

    if attachment is None:
        return

    user = update.effective_user

    input_file_id = attachment.file_id

    input_file = bot.get_file(input_file_id)
    input_file_url = input_file.file_path

    root_path = os.getcwd()

    video_path = root_path + "/files/video.mp4"
    detect_path = "runs\\detect"
    detect_subdirs = get_subdirs(detect_path)
    detect_subdirs = [0 if (dir == "exp") else int(dir.replace("exp", "")) for dir in detect_subdirs]
    detect_subdirs.sort()

    current_exp_num = detect_subdirs[-1] + 1

    input_file.download(custom_path=video_path)
    update.message.reply_text("הוידאו עבר בהצלחה")
    os.system(
        "py \""+root_path+"/yolo/detect.py\" --source \"" + video_path + "\"" + " --save-txt --save-crop")

    labels_path = detect_path + "\\exp" + str(current_exp_num)

    crops_path = labels_path + "\\crops"
    crops_subdirs = get_subdirs(crops_path)
    crops_subdirs = [dir for dir in crops_subdirs]
    print(crops_subdirs)

    labels_list = []
    for label in crops_subdirs:
        print(label)
        image_size_list = []
        image_name_list = []
        for filename in glob.glob(crops_path + "\\" + label + "\\*.jpg"):  # assuming gif
            im = Image.open(filename)
            img_size = im.size
            image_size_list.append(img_size)
            image_name_list.append(filename)
        best_img = image_name_list[image_size_list.index(max(image_size_list))]  # largest image
        labels_list.append({"Name": label, "Img": best_img})

    print(labels_list)

    # detect.detect("--source " + video_path)
    # vid_file = cv2.VideoCapture(video_path)
    # vid_file.set(cv2.CAP_PROP_FPS, 15)


def get_subdirs(d):
    return [os.path.join(d, o).replace(d + "\\", "") for o in os.listdir(d)
            if os.path.isdir(os.path.join(d, o))]


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(InlineQueryHandler(inlinequery))

    dispatcher.add_handler(MessageHandler(Filters.video, message_video_handler))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # detect_path = "runs\\detect"
    # detect_subdirs = get_subdirs(detect_path)
    # detect_subdirs = [0 if (dir == "exp") else int(dir.replace("exp", "")) for dir in detect_subdirs]
    # detect_subdirs.sort()
    #
    # current_exp_num = detect_subdirs[-1]
    #
    # labels_path = detect_path + "\\exp8"
    #
    # crops_path = labels_path + "\\crops"
    # crops_subdirs = get_subdirs(crops_path)
    # crops_subdirs = [dir for dir in crops_subdirs]
    # print(crops_subdirs)
    #
    # labels_list = []
    # for label in crops_subdirs:
    #     print(label)
    #     image_size_list = []
    #     image_name_list = []
    #     for filename in glob.glob(crops_path+"\\" + label + "\\*.jpg"):  # assuming gif
    #         im = Image.open(filename)
    #         img_size = im.size
    #         image_size_list.append(img_size)
    #         image_name_list.append(filename)
    #     best_img = image_name_list[image_size_list.index(max(image_size_list))] # largest image
    #     labels_list.append({"Name":label, "Img": best_img})
    #
    # print(labels_list)
    main()
