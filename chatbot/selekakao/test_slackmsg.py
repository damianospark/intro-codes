import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta


slack_client = WebClient(token=SLACK_BOT_TOKEN)


def send_message_to_channel(channel_name, message):
    try:
        response = slack_client.conversations_list()
        channels = response['channels']
        channel_id = None

        for channel in channels:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break

        if channel_id is not None:
            slack_client.chat_postMessage(channel=channel_id, text=message)
            print(f'Message sent to {channel_name}')
        else:
            print(f'Channel {channel_name} not found.')

    except SlackApiError as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    channel_name = 'chatbot-today'
    message = '이기우(5248)-영등포\n명혜영(3998)-관악\n양민화(8703)-강남'

    now = datetime.now()
    answr_time = now.strftime('%Y-%m-%d %H:%M:%S')

    send_message_to_channel(channel_name, '> 응답현황 : {now}')
    send_message_to_channel(channel_name, message)
