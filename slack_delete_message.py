"""Delete old Slack messages at specific channel."""
from datetime import datetime
from time import sleep
import json
import re
import sys
import urllib.parse
import urllib.request

DELETE_URL = "https://slack.com/api/chat.delete"
HISTORY_URL = "https://slack.com/api/conversations.history"
API_TOKEN = 'xoxp-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TERM = 60 * 60 * 24 * 7  # 1 week


def clean_old_message(channel_id):
    print('Start cleaning message at channel "{}".'.format(channel_id))
    current_ts = int(datetime.now().strftime('%S'))
    messages = get_message_history(channel_id)
    print("**********************Message List START*****************************")
    print(messages)
    print("**********************Message List END*****************************")
    print("**********************Delete Message List START*****************************")
    for message in messages:
        if current_ts - int(re.sub(r'\.\d+$', '', message['ts'])) < TERM:
            delete_message(channel_id, message['ts'])
            print(message)
    print("**********************Delete Message List END*****************************")


def get_message_history(channel_id, count=800):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'token': API_TOKEN,
        'channel': channel_id,
        'count': str(count)
    }

    req_url = '{}?{}'.format(HISTORY_URL, urllib.parse.urlencode(params))
    req = urllib.request.Request(req_url, headers=headers)

    message_history = []
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        if 'messages' in data:
            message_history = data['messages']

    return message_history


def delete_message(channel_id, message_ts):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'token': API_TOKEN,
        'channel': channel_id,
        'ts': message_ts
    }

    req_url = '{}?{}'.format(DELETE_URL, urllib.parse.urlencode(params))
    req = urllib.request.Request(req_url, headers=headers)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        if 'ok' not in data or data['ok'] is not True:
            print('Failed to delete message. ts: {}'.format(message_ts))


def lambda_handler(event, context):
    if 'target_ch_ids' not in event:
        print('Target channel id is required.')
        return False

    for target_ch_id in event['target_ch_ids']:
        clean_old_message(target_ch_id)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("The first parameter for slack channel id is required.")
    else:
        clean_old_message(args[1])
