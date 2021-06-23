# Project files
import constants
import manual_utterances

# Python libraries
import logging
import numpy as np
import nltk
# import spacy
import wikipedia
import wikipediaapi

# telegram-python-bot api
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ConversationHandler, CallbackQueryHandler

API_TOKEN = constants.telegram_api_key

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

wiki = wikipediaapi.Wikipedia('en')
# nlp = spacy.load('en_core_web_sm')

CMD_TEXT_IDX = 0
CMD_FUNC_IDX = 1


def start_cmd(update, context):
    rand_idx = np.random.randint(len(manual_utterances.directed_greeting))
    msg_text = "{} {}. I'm a Smart bot, please talk to me!".format(
        manual_utterances.directed_greeting[rand_idx], update.message.from_user.first_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg_text)


def help_cmd(update, context):
    msg_text = """I am a Smart bot (very). You can use the following commands: \n\n""" \
                """/start - Restarts our converstation (I will lose all my memory).\n""" \
                """/caps -  I will shout your message back at you!\n""" \
                """/help - Returns list of commands and some helpful information.\n\n""" \
                """/wiki topic - Replace topic with something you want me to tell you about.\n\n""" \
                """Or you can ask me something you want to know more about."""

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg_text)


def caps_cmd(update, context: str) -> None:
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def wiki_cmd(update, context):
    query = ' '.join(context.args)
    topics = wikipedia.search(query)
    page = None
    for topic in topics:
        print(nltk.edit_distance(topic, query) / len(query))
        if nltk.edit_distance(topic, query) / len(query) < 0.2:
            try:
                page = wiki.page(topic)
                page = str(page.summary).split('\n')[0]
                break
            except Exception as ex:
                print(ex)
    if page is None:
        page = "I dont understand, and since I'm a genius you probably misspelled it."
    print(topics)
    context.bot.send_message(chat_id=update.effective_chat.id, text=page)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    logging.info(update.message.text)


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    known_commands = [('start', start_cmd),
                      ('help', help_cmd),
                      ('caps', caps_cmd),
                      ('wiki', wiki_cmd)]

    for cmd in known_commands:
        handler = CommandHandler(cmd[CMD_TEXT_IDX], cmd[CMD_FUNC_IDX])
        dispatcher.add_handler(handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # description_conv = ConversationHandler(
    #     entry_points=[
    #         CallbackQueryHandler(
    #             select_feature, pattern='^' + str(MALE) + '$|^' + str(FEMALE) + '$'
    #         )
    #     ],
    #     states={
    #         SELECTING_FEATURE: [
    #             CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$')
    #         ],
    #         TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input)],
    #     },
    #     fallbacks=[
    #         CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
    #         CommandHandler('stop', stop_nested),
    #     ],
    #     map_to_parent={
    #         # Return to second level menu
    #         END: SELECTING_LEVEL,
    #         # End conversation altogether
    #         STOPPING: STOPPING,
    #     },
    # )
    #
    # # Set up second level ConversationHandler (adding a person)
    # add_member_conv = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(select_level, pattern='^' + str(ADDING_MEMBER) + '$')],
    #     states={
    #         SELECTING_LEVEL: [
    #             CallbackQueryHandler(select_gender, pattern=f'^{PARENTS}$|^{CHILDREN}$')
    #         ],
    #         SELECTING_GENDER: [description_conv],
    #     },
    #     fallbacks=[
    #         CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
    #         CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
    #         CommandHandler('stop', stop_nested),
    #     ],
    #     map_to_parent={
    #         # After showing data return to top level menu
    #         SHOWING: SHOWING,
    #         # Return to top level menu
    #         END: SELECTING_ACTION,
    #         # End conversation altogether
    #         STOPPING: END,
    #     },
    # )
    #
    # # Set up top level ConversationHandler (selecting action)
    # # Because the states of the third level conversation map to the ones of the second level
    # # conversation, we need to make sure the top level conversation can also handle them
    # selection_handlers = [
    #     add_member_conv,
    #     CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
    #     CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
    #     CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
    # ]
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #     states={
    #         SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
    #         SELECTING_ACTION: selection_handlers,
    #         SELECTING_LEVEL: selection_handlers,
    #         DESCRIBING_SELF: [description_conv],
    #         STOPPING: [CommandHandler('start', start)],
    #     },
    #     fallbacks=[CommandHandler('stop', stop)],
    # )

    # dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()

    # Wait for stop signal
    updater.idle()


if __name__ == '__main__':
    main()
