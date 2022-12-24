import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, ConfirmTemplate, TemplateSendMessage, MessageTemplateAction


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"

def send_button_message(reply_token, url, title, text, button):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url = url,
            title = title,
            text = text,
            actions = button
        )
    )
    line_bot_api.reply_message(reply_token, message)
    
    return "OK"

def send_confirm_message(reply_token, text, button):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='Comfirm template',
        template=ButtonsTemplate(
            text = text,
            actions = button
        )
    )
    line_bot_api.reply_message(reply_token, message)
    
    return "OK"

"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""