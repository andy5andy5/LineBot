import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "main_menu", "introduction", "departure_menu", "departure", "destination_menu", "destination",
            "codesearch", "date1", "date2_check", "date2", "people", "planeclass", "result", "cancel"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",#1
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "introduction",
            "conditions": "is_going_to_introduction",#2
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "departure_menu",
            "conditions": "is_going_to_departure_menu",#3
        },
        {
            "trigger": "advance",
            "source": ["departure_menu", "codesearch"],
            "dest": "departure",
            "conditions": "is_going_to_departure",#4
        },
        {
            "trigger": "advance",
            "source": ["departure_menu", "destination_menu"],
            "dest": "codesearch",
            "conditions": "is_going_to_codesearch",#5
        },
        {
            "trigger": "advance",
            "source": "departure",
            "dest": "destination_menu",
            "conditions": "is_going_to_destination_menu",#6
        },
        {
            "trigger": "advance",
            "source": ["destination_menu", "codesearch"],
            "dest": "destination",
            "conditions": "is_going_to_destination",#7
        },
        {
            "trigger": "advance",
            "source": "destination",
            "dest": "date1",
            "conditions": "is_going_to_date1",#8
        },
        {
            "trigger": "advance",
            "source": "date1",
            "dest": "date2_check",
            "conditions": "is_going_to_date2_check",#9
        },
        {
            "trigger": "advance",
            "source": "date2_check",
            "dest": "date2",
            "conditions": "is_going_to_date2",#10
        },
        {
            "trigger": "advance",
            "source": ["date2", "date2_check"],
            "dest": "people",
            "conditions": "is_going_to_people",#11
        },
        {
            "trigger": "advance",
            "source": "people",
            "dest": "planeclass",
            "conditions": "is_going_to_planeclass",#12
        },
        {
            "trigger": "advance",
            "source": "planeclass",
            "dest": "result",
            "conditions": "is_going_to_result",#13
        },
        {
            "trigger": "advance",
            "source": ["departure_menu", "destination_menu", "date1", "date2", "result"],
            "dest": "cancel",
            "conditions": "is_going_to_cancel",#14
        },
        {"trigger": "go_back", "source": ["introduction", "cancel"], "dest": "main_menu"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            if machine.state == "user":
                send_text_message(event.reply_token, "請輸入\"開始\"進入主目錄")
            elif machine.state == "main_menu":
                send_text_message(event.reply_token, "請點選主目錄選項")
            elif machine.state == "departure_menu":
                send_text_message(event.reply_token, "請點選出發機場目錄選項")
            elif machine.state == "destination_menu":
                send_text_message(event.reply_token, "請點選到達機場目錄選項")
            elif machine.state == "codesearch":
                send_text_message(event.reply_token, "請點選或輸入\n\"輸入出發/到達機場代碼\"")
            elif machine.state == "date1" or machine.state == "date2":
                send_text_message(event.reply_token, "請輸入正確日期")
            elif machine.state == "date2_check":
                send_text_message(event.reply_token, "請確認是否需要訂購回程")
            elif machine.state == "people":
                send_text_message(event.reply_token, "請確認人數為1~4人")
            elif machine.state == "planeclass":
                send_text_message(event.reply_token, "請點選艙等選項")
            elif machine.state == "result":
                send_text_message(event.reply_token, "請輸入\"結束查詢\"回到主目錄")
            else:
                send_text_message(event.reply_token, "請確認輸入值")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
