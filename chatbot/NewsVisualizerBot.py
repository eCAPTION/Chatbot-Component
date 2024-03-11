import telebot
from flask import Flask, request
from pyngrok import ngrok

from dotenv import load_dotenv
import os

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")

import sys
sys.path.append('../')
from chatbot import CommonDbOperations, ResponseHandler
from kafka_io_logic import KafkaEventHandler

# Initialize Flask app
app = Flask(__name__)

# Initialise Telegram bot
bot = telebot.TeleBot(bot_token, parse_mode=None)

database = None

# To keep track of the infographic links that the users have entered
latest_infographic_links = {}

# Define a route to handle incoming updates
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return ''

@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    visualize_news_button = telebot.types.InlineKeyboardButton(text="Visualize News Article", callback_data="receive_article")
    keyboard.add(visualize_news_button)
    modify_infographic_button = telebot.types.InlineKeyboardButton(text="Modify Infographic", callback_data="modify_infographic")
    keyboard.add(modify_infographic_button)
    view_infographic_stats_button = telebot.types.InlineKeyboardButton(text="View Infographic Stats", callback_data="view_infographic_stats")
    keyboard.add(view_infographic_stats_button)
    greeting_message = 'Greetings! What will you like to do today?'
    bot.send_message(message.chat.id, greeting_message, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'receive_article':
            reply_message = 'What is the article?'
            sent = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=reply_message)
            bot.register_next_step_handler(sent, receive_news_article)
        elif call.data == 'modify_infographic':
            reply_message = 'Please send me the link to the infographic that you wish to modify.'
            sent = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=reply_message)
            bot.register_next_step_handler(sent, receive_infographic)
        elif call.data == 'view_infographic_stats':
            reply_message = 'Please send me the link to the infographic that you wish to view the stats for.'
            sent = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=reply_message)
            bot.register_next_step_handler(sent, view_infographic_stats)
        elif call.data == 'vote_for_reliability':
            keyboard = telebot.types.InlineKeyboardMarkup()
            vote_reliable_button = telebot.types.InlineKeyboardButton(text="Reliable",
                                                                      callback_data="vote_reliable")
            keyboard.add(vote_reliable_button)
            vote_unreliable_button = telebot.types.InlineKeyboardButton(text="Unreliable",
                                                                        callback_data="vote_unreliable")
            keyboard.add(vote_unreliable_button)
            reply_message = "Do you view this news article as reliable or unreliable?"
            bot.send_message(call.message.chat.id, reply_message, reply_markup=keyboard)
        elif call.data == 'custom_modification':
            reply_message = "What change do you wish to make to this infographic?"
            sent = bot.send_message(call.message.chat.id, reply_message)
            bot.register_next_step_handler(sent, receive_infographic_changes)
        elif call.data == 'vote_reliable':
            link_to_infographic = latest_infographic_links.get(call.message.chat.id)
            if link_to_infographic is None:
                print('User has not entered an infographic link.')
            CommonDbOperations.increase_reliable_vote_count(database, link_to_infographic)
            reply_message = "You have voted this article as reliable!"
            bot.send_message(call.message.chat.id, reply_message)
        elif call.data == 'vote_unreliable':
            link_to_infographic = latest_infographic_links.get(call.message.chat.id)
            if link_to_infographic is None:
                print('User has not entered an infographic link.')
            CommonDbOperations.increase_unreliable_vote_count(database, link_to_infographic)
            reply_message = "You have voted this article as unreliable!"
            bot.send_message(call.message.chat.id, reply_message)
        elif call.data == 'add_comment':
            reply_message = "What comment do you wish to add?"
            sent = bot.send_message(call.message.chat.id, reply_message)
            bot.register_next_step_handler(sent, receive_comment)

def receive_news_article(message):
    if CommonDbOperations.check_if_news_article_infographic_exist(database, message.chat.id, message.text):
        link_to_infographic = CommonDbOperations.send_existing_news_article_infographic(database, message.chat.id, message.text)
        if link_to_infographic == '':
            reply_message = f"I am still generating the infographic that you have previously requested for {message.text}"
        else:
            reply_message = "You have already generated an infographic for this news article, where you can view it here: {}".format(link_to_infographic)
        bot.send_message(message.chat.id, reply_message)
    else:
        CommonDbOperations.create_news_article_document(database, message.chat.id, message.text)
        request_id = CommonDbOperations.assign_request_news_article(database, message.chat.id, message.text)
        KafkaEventHandler.emit_article_url(message.text, request_id)
        reply_message = '\U000023F3' + ' Please wait patiently while I generate your infographic ' + '\U000023F3'
        bot.send_message(message.chat.id, reply_message)

def receive_infographic(message):
    link_to_infographic = message.text
    is_valid_link = CommonDbOperations.check_if_infographic_link_exists(database, link_to_infographic)
    if is_valid_link:
        latest_infographic_links[message.chat.id] = link_to_infographic

        CommonDbOperations.increase_share_count(database, link_to_infographic)

        keyboard = telebot.types.InlineKeyboardMarkup()
        reliability_vote_button = telebot.types.InlineKeyboardButton(text="Vote For Reliability Of News Article",
                                                                     callback_data="vote_for_reliability")
        keyboard.add(reliability_vote_button)
        add_comment_button = telebot.types.InlineKeyboardButton(text="Add Comment",
                                                                callback_data="add_comment")
        keyboard.add(add_comment_button)
        custom_modification_button = telebot.types.InlineKeyboardButton(text="Type Out Modification",
                                                                        callback_data="custom_modification")
        keyboard.add(custom_modification_button)

        reply_message = "How will you like to modify the infographic?"
        bot.send_message(message.chat.id, reply_message, reply_markup=keyboard)
    else:
        reply_message = "You have sent an invalid link."
        bot.send_message(message.chat.id, reply_message)

def receive_infographic_changes(message):
    user_infographic = latest_infographic_links.get(message.chat.id)
    if user_infographic is None:
        print('User has not entered an infographic link.')
    proposed_user_changes = message.text
    request_id = CommonDbOperations.assign_request_infographic_changes(database, message.chat.id, user_infographic, proposed_user_changes)
    processing_message = '\U000023F3' + ' Please wait patiently while I modify your infographic ' + '\U000023F3'
    bot.send_message(message.chat.id, processing_message)
    intermediate_representation = ResponseHandler.generate_intermediate_representation(proposed_user_changes)
    KafkaEventHandler.emit_intermediate_representation(intermediate_representation, user_infographic, request_id)

def view_infographic_stats(message):
    link_to_infographic = message.text
    is_valid_link = CommonDbOperations.check_if_infographic_link_exists(database, link_to_infographic)
    if is_valid_link:
        CommonDbOperations.increase_share_count(database, link_to_infographic)
        infographic_document = CommonDbOperations.get_infographic_document(database, link_to_infographic)
        infographic_stats = format_infographic_stats(infographic_document)
        bot.send_message(message.chat.id, infographic_stats)
    else:
        reply_message = "You have sent an invalid link."
        bot.send_message(message.chat.id, reply_message)

def format_infographic_stats(infographic_document):
    overview = f"Share Count: {infographic_document['share_count']}\n"
    overview += f"Vote Counts for Reliable: {infographic_document['reliable_vote_count']}\n"
    overview += f"Vote Counts for Unreliable: {infographic_document['unreliable_vote_count']}\n"
    overview += "Comments:\n"
    comments = infographic_document['comments']
    comment_index = 1
    for comment in comments:
        overview += f'{comment_index}) {comment}\n'
        comment_index += 1
    return overview

def receive_comment(message):
    comment = message.text
    user_infographic = latest_infographic_links.get(message.chat.id)
    if user_infographic is None:
        print('User has not entered an infographic link.')
    CommonDbOperations.add_comment(database, user_infographic, comment)
    reply_message = f"You have commented: {comment}"
    bot.send_message(message.chat.id, reply_message)

def send_error_message_article_link(request_id, error_message):
    startup_database()
    request_document = CommonDbOperations.get_request(database, request_id)
    chat_id = request_document["chat_id"]
    reply_message = f'You have sent an invalid article link. The error is as follows:\n{error_message}'
    bot.send_message(chat_id, reply_message)

def send_new_infographic(request_id, infographic_link):
    startup_database()
    request_document = CommonDbOperations.get_request(database, request_id)
    chat_id = request_document["chat_id"]
    article_link = request_document["article_link"]
    CommonDbOperations.add_infographic_to_article(database, chat_id, article_link, infographic_link)
    reply_message = f"Great news! I've finished generating the infographic based on the news article ({article_link}) you linked.\nYou can check it out here: {infographic_link}"
    bot.send_message(chat_id, reply_message)

def send_modified_infographic(request_id, infographic_link):
    startup_database()
    request_document = CommonDbOperations.get_request(database, request_id)
    chat_id = request_document["chat_id"]
    old_infographic_link = request_document["infographic_link"]
    instruction = request_document["user_instruction"]
    CommonDbOperations.update_infographic_of_article(database, chat_id, old_infographic_link, infographic_link)
    reply_message = f"All done! I've modified your infographic based on your instructions for the infographic you provided:\nInfographic Link: {old_infographic_link}\nInstruction: {instruction}\n-------------------------------\nCheck out the updated infographic here: {infographic_link}"
    bot.send_message(chat_id, reply_message)

def startup_database():
    global database
    database = CommonDbOperations.startup_database()

if __name__ == '__main__':
    startup_database()

    ngrok.set_auth_token(ngrok_auth_token)

    # Set up ngrok tunnel
    public_url = str(ngrok.connect("8000", bind_tls=True)).split('"')[1]
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:8000\"".format(public_url))

    # Set the webhook for Telegram to send updates to the ngrok tunnel
    bot.remove_webhook()
    bot.set_webhook(url=f"{public_url}/webhook")

    # Run the Flask app
    app.run(port=8000)
