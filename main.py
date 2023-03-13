import requests
import json
import os
import threading
import time

# Insert your penAI API key here:
API_KEY = 'API_KEY'
# Models: 'gpt-3.5-turbo' for ChatGPT.
# Alternatively you can use text-davinci-003,text-curie-001,text-babbage-001,text-ada-001 or your pre-trained model.
# However this, will require some changes in code. I will probably make another repo explaining this.
MODEL = 'gpt-3.5-turbo'
# Telegram Bot token (From Father bot)
BOT_TOKEN = 'BOT_TOKEN'
# Stop sequence (Not really required for ChatGPT, however very important for pre-trained models)
# The stop symbol depends on your dataset. If you don't use pre-trained model, skip this part
STOP_SYMBOLS = "END"

users = {}

# Function that gets the response from OpenAI's chatbot
def openAI(promptArr):
    # Make the request to the OpenAI API
    # Here you can set completion parameters as you wish. Read more about them on OpenAI website.
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers = {'Authorization': f'Bearer {API_KEY}'},
        json = {'model': MODEL, 'stop': STOP_SYMBOLS, 'temperature': 0.4, 'max_tokens': 500,
             'frequency_penalty': 1, "presence_penalty": 1, "messages": promptArr}
    )
    print(response)

    result = response.json()
    print(result)
    final_result = ''.join(result['choices'][0]['message']['content'])
    return final_result


users = {}


# Function that gets an Image from OpenAI
# Here you also can change generation parameters for the images
def openAImage(prompt):
    # Make the request to the OpenAI API
    resp = requests.post(
        'https://api.openai.com/v1/images/generations',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'prompt': prompt, 'n': 1, 'size': '1024x1024'}
    )
    response_text = json.loads(resp.text)

    return response_text['data'][0]['url']


# Function that sends a message to a specific telegram group
def telegram_bot_sendtext(bot_message, chat_id, msg_id, usr_id):
    data = {
        'chat_id': chat_id,
        'text': bot_message,
        'reply_to_message_id': msg_id
    }
    response = requests.post(
        'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
        json=data
    )
    return response.json()


# Function that sends an image to a specific telegram group
def telegram_bot_sendimage(image_url, chat_id, msg_id, usr_id):
    data = {
        'chat_id': chat_id,
        'photo': image_url,
        'reply_to_message_id': msg_id
    }
    url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendPhoto'

    response = requests.post(url, data=data)
    return response.json()


def _get_user(id):
    user = users.get(id, {'id': id, 'last_text': '', 'last_prompt_time': 0})
    users[id] = user
    return user


# Function that retrieves the latest requests from users in a Telegram group,
# generates a response using OpenAI, and sends the response back to the group.
def Chatbot():
    # Retrieve last ID message from text file for ChatGPT update
    cwd = os.getcwd()
    chat = []
    filename = cwd + '/chatgpt.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")
    else:
        print("File Exists")

    with open(filename) as f:
        last_update = f.read()

    # Check for new messages in Telegram group
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}'
    response = requests.get(url)
    data = json.loads(response.content)

    for result in data['result']:
        try:
            # Checking for new message
            if float(result['update_id']) > float(last_update):
                # Checking for new messages that did not come from chatGPT
                if not result['message']['from']['is_bot']:
                    last_update = str(int(result['update_id']))

                    # Retrieving message ID of the sender of the request
                    msg_id = str(int(result['message']['message_id']))

                    # Retrieving user ID of the sender of the request
                    usr_id = str(int(result['message']['from']['id']))
                    print(usr_id)

                    # Retrieving the chat ID
                    chat_id = str(result['message']['chat']['id'])

                    # Checking if user wants an image
                    if '/img' in result['message']['text']:
                        prompt = result['message']['text'].replace("/img", "")
                        bot_response = openAImage(prompt)
                        print(telegram_bot_sendimage(bot_response, chat_id, msg_id, usr_id))
                    # Checking that user mentionned chatbot's username in message
                    if '@RektGPT_BOT' in result['message']['text']:

                        # user = _get_user(usr_id)
                        # last_text = user['last_text']
                        # if time.time() - user['last_prompt_time'] > 600:
                        #     last_text = ''
                        #     user['last_prompt_time'] = 0
                        #     user['last_text'] = ''

                        print ('Here is the result!!!!')
                        print(result)
                        content = f"{result['message']['text'].replace('@RektGPT_BOT', '')}"
                        # prompt = f"{last_text + result['message']['text']} ->"[-1000:].replace("@RektGPT_BOT", " Q:")
                        prompt = {'role': 'user', 'content': content}
                        chat.append(prompt)
                        print(prompt)
                        # Calling OpenAI API
                        bot_response = openAI(chat)
                        chat.append(bot_response)

                        # user['last_text'] = prompt + " " + bot_response
                        # test = user['last_text'] = prompt + " " + bot_response
                        # user['last_prompt_time'] = time.time()
                        # print(test)

                        # Sending back response to telegram group
                        print(telegram_bot_sendtext(bot_response, chat_id, msg_id, usr_id))
                    # Verifying that the user is responding to the ChatGPT bot
                    if 'reply_to_message' in result['message']:
                        if result['message']['reply_to_message']['from']['is_bot']:

                            # user = _get_user(usr_id)
                            # last_text = user['last_text']
                            # if time.time() - user['last_prompt_time'] > 600:
                            #     last_text = ''
                            #     user['last_prompt_time'] = 0
                            #     user['last_text'] = ''

                            print('Here is the result!!!!')
                            print(result)
                            content = f"{result['message']['text'].replace('@RektGPT_BOT', '')}"
                            # prompt = f"{last_text + result['message']['text']} ->"[-1000:].replace("@RektGPT_BOT", " Q:")
                            prompt = {'role': 'user', 'content': content}
                            chat.append(prompt)
                            print(prompt)
                            # Calling OpenAI API
                            bot_response = openAI(chat)
                            chat.append(bot_response)

                            # user['last_text'] = prompt + " " + bot_response
                            # test = user['last_text'] = prompt + " " + bot_response
                            # user['last_prompt_time'] = time.time()
                            # print(test)

                            print(telegram_bot_sendtext(bot_response, chat_id, msg_id, usr_id))
        except Exception as e:
            print(e)

    # Updating file with last update ID
    with open(filename, 'w') as f:
        f.write(last_update)

    return "done"


# Running a check every 5 seconds to check for new messages
def main():
    timertime = 5
    Chatbot()
    # 5 sec timer
    threading.Timer(timertime, main).start()


# Run the main function
if __name__ == "__main__":
    main()
