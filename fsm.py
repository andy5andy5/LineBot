import os
import bs4
import requests
import time

from transitions.extensions import GraphMachine
from bs4 import BeautifulSoup
from utils import send_text_message, send_button_message, send_confirm_message
from linebot import LineBotApi
from linebot.models import ButtonsTemplate, ConfirmTemplate, TemplateSendMessage, MessageTemplateAction
from selenium import webdriver

#global variable
departure = ''
destination = ''
date1 = 0
date2 = 0
people = 0   #number of people
planeclass = ''

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    #1
    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text.lower() == "開始"

    def on_enter_main_menu(self, event):
        print("I'm entering main menu")
        reply_token = event.reply_token
        url = 'https://i.imgur.com/3NcvvYn.jpg'
        title = '機票價格查詢助手'
        text = '請點選下列選項'
        button = [
            MessageTemplateAction(
                label='查詢機票價格',
                text='查詢機票價格'
            ),
            MessageTemplateAction(
                label='使用說明',
                text='使用說明'
            )
        ]
        send_button_message(reply_token, url, title, text, button)

    #2
    def is_going_to_introduction(self, event):
        text = event.message.text
        return text.lower() == "使用說明"

    def on_enter_introduction(self, event):
        print("I'm entering introduction")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "歡迎使用機票查詢助手！\n我的功用是幫助您\n快速搜尋機票！\n\n使用方法：\n1.點選\"查詢機票價格\"\n"
            + "2.輸入出發地與目的地\n3.輸入出發（及返回）日期\n4.輸入人數\n5.選擇艙等\n6.顯示搜尋結果")
        self.go_back()

    def on_exit_introduction(self):
        print("Leaving introduction")

    #3
    def is_going_to_departure_menu(self, event):
        text = event.message.text
        return text.lower() == "查詢機票價格"

    def on_enter_departure_menu(self, event):
        print("I'm entering departure menu")
        reply_token = event.reply_token
        url = 'https://i.imgur.com/cRwknYY.jpg'
        title = '出發機場'
        text = '請點選下列選項'
        button = [
            MessageTemplateAction(
                label='輸入出發機場代碼',
                text='輸入出發機場代碼'
            ),
            MessageTemplateAction(
                label='查詢機場代碼',
                text='查詢機場代碼'
            ),
            MessageTemplateAction(
                label='結束查詢',
                text='結束查詢'
            )
        ]
        send_button_message(reply_token, url, title, text, button)

    #4
    def is_going_to_departure(self, event):
        text = event.message.text
        return text.lower() == "輸入出發機場代碼"

    def on_enter_departure(self, event):
        print("I'm entering departure")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "請輸入出發機場代碼\n範例：\n桃園機場請輸入\"TPE\"\n松山機場請輸入\"TSA\"\n\n或輸入\"結束查詢\"回到目錄")
    
    #5
    def is_going_to_codesearch(self, event):
        text = event.message.text
        return text.lower() == "查詢機場代碼"

    def on_enter_codesearch(self, event):
        global departure
        print("I'm entering codesearch")
        reply_token = event.reply_token
        if departure == '':
            send_text_message(
                reply_token,
                "機場代碼查詢網頁：\nhttp://www.exbtr.com/TW/Page.aspx?tn=ca12_1_1_6&Tid=4 "
                + "\n\n請輸入或點選\n\"輸入出發機場代碼\"\n以繼續查詢")
        else:
            send_text_message(
                reply_token,
                "機場代碼查詢網頁：\nhttp://www.exbtr.com/TW/Page.aspx?tn=ca12_1_1_6&Tid=4 "
                + "\n\n請輸入或點選\n\"輸入到達機場代碼\"\n以繼續查詢")

    #6
    def is_going_to_destination_menu(self, event):
        global departure
        text = event.message.text
        departure = text.lower()
        return True

    def on_enter_destination_menu(self, event):
        print("I'm entering destination menu")
        reply_token = event.reply_token
        url = 'https://i.imgur.com/7M4Ecmh.jpg'
        title = '到達機場'
        text = '請點選下列選項'
        button = [
            MessageTemplateAction(
                label='輸入到達機場代碼',
                text='輸入到達機場代碼'
            ),
            MessageTemplateAction(
                label='查詢機場代碼',
                text='查詢機場代碼'
            ),
            MessageTemplateAction(
                label='結束查詢',
                text='結束查詢'
            )
        ]
        send_button_message(reply_token, url, title, text, button)

    #7
    def is_going_to_destination(self, event):
        text = event.message.text
        return text.lower() == "輸入到達機場代碼"

    def on_enter_destination(self, event):
        print("I'm entering destination")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "請輸入到達機場代碼\n範例：\n成田機場請輸入\"NRT\"\n羽田機場請輸入\"HND\"\n\n或輸入\"結束查詢\"回到目錄")

    #8
    def is_going_to_date1(self, event):
        global destination
        text = event.message.text
        destination = text.lower()
        return True

    def on_enter_date1(self, event):
        print("I'm entering date1")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "請輸入去程日期\n範圍為即日起算一年內\n格式：\n20220102請輸入220102\n\n或輸入\"結束查詢\"回到目錄")

    #9
    def is_going_to_date2_check(self, event):
        global date1
        text = event.message.text
        if text.isnumeric() == True:
            date1 = int(text)
            return True
        else:
            return False

    def on_enter_date2_check(self, event):
        print("I'm entering date2_check")
        reply_token = event.reply_token
        text = '需要訂購回程機票嗎？'
        button = [
            MessageTemplateAction(
                label='需要',
                text='需要訂購回程'
            ),
            MessageTemplateAction(
                label='不需要',
                text='不需要訂購回程'
            )
        ]
        send_confirm_message(reply_token, text, button)

    #10
    def is_going_to_date2(self, event):
        text = event.message.text
        return text.lower() == "需要訂購回程"

    def on_enter_date2(self, event):
        print("I'm entering date2")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "請輸入回程日期\n範圍為即日起算一年內\n格式：\n20220102請輸入220102\n\n或輸入\"結束查詢\"回到目錄")    

    #11
    def is_going_to_people(self, event):
        global date2
        text = event.message.text
        if text.lower() == "不需要訂購回程":
            return text.lower() == "不需要訂購回程"
        else:
            if text.isnumeric() == True:
                date2 = int(text)
                return True
            else:
                return False

    def on_enter_people(self, event):
        print("I'm entering people")
        reply_token = event.reply_token
        send_text_message(
            reply_token,
            "請輸入人數(最多4人)\n範例：2人請輸入\"2\"\n或輸入\"結束查詢\"回到目錄")

    #12
    def is_going_to_planeclass(self, event):
        global people
        text = event.message.text
        if int(text) > 0 and int(text) <= 4:
            people = int(text)
            return True
        else:
            return False

    def on_enter_planeclass(self, event):
        print("I'm entering planeclass")
        reply_token = event.reply_token
        url = 'https://i.imgur.com/WnhcPAG.jpg'
        title = '艙等選擇'
        text = '請點選下列選項(查詢時間約15秒)'
        button = [
            MessageTemplateAction(
                label='經濟艙',
                text='economy'
            ),
            MessageTemplateAction(
                label='商務艙',
                text='business'
            )
        ]
        send_button_message(reply_token, url, title, text, button)

    #13
    def is_going_to_result(self, event):
        global planeclass
        text = event.message.text
        if text == "economy" or text == "business":
            planeclass = text.lower()
            return True
        else:
            return False

    def on_enter_result(self, event):
        print("I'm entering result")
        global departure, destination, date1, date2, people, planeclass
        if date2 == 0:
            ticketurl = ('https://www.skyscanner.com.tw/transport/flights/' + departure + '/' + destination + '/' + str(date1) + '/?adults='
            + str(people) + '&adultsv2=' + str(people) + '&cabinclass=' + planeclass
            + '&children=0&childrenv2=&inboundaltsenabled=false&infants=0&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0')
        else:
            ticketurl = ('https://www.skyscanner.com.tw/transport/flights/' + departure + '/' + destination + '/' + str(date1) + '/' + str(date2) + '/?adults='
            + str(people) + '&adultsv2=' + str(people) + '&cabinclass=' + planeclass
            + '&children=0&childrenv2=&inboundaltsenabled=false&infants=0&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0')

        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("browser.privatebrowsing.autostart", True)

        driver = webdriver.Firefox(firefox_profile=firefox_profile)
        time.sleep(0.5)
        driver.get(ticketurl)
        for i in range(10):
            content = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, "html.parser")
            if people == 1:
                found = soup.find("span", class_="BpkText_bpk-text__ZWIzZ BpkText_bpk-text--lg__Nzk0N")
                if found != None:
                    price = found
            else:
                found1 = soup.find("span", class_="BpkText_bpk-text__ZWIzZ BpkText_bpk-text--lg__Nzk0N")
                found2 = soup.find("span", class_="BpkText_bpk-text__ZWIzZ BpkText_bpk-text--caption__NDJhY Price_totalPrice__MTJhN")
                if found1 != None:
                    price = found1
                if found2 != None:
                    total_price = found2
            time.sleep(1)
        print(ticketurl)
        if people == 1:
            print(price)
        else:
            print(total_price)

        reply_token = event.reply_token
        if price != "":
            if people == 1:
                send_text_message(
                    reply_token,
                    "依照您的搜尋條件：\n所查詢到最佳機票的價格：\n" + "總價 " + price.text + "\n(價格可能並非最低價\n推薦點入下面網址查看)"
                    + "\n\n訂票網址：\n" + ticketurl + "\n\n輸入\"結束查詢\"回到目錄")
            else:
                send_text_message(
                    reply_token,
                    "依照您的搜尋條件：\n所查詢到最佳機票的價格：\n" + "單價 " + price.text + "\n" + total_price.text + "\n(價格可能並非最低價\n推薦點入下面網址查看)"
                    + "\n\n訂票網址：\n" + ticketurl + "\n\n輸入\"結束查詢\"回到目錄")
        else:
            send_text_message(
                reply_token,
                "助手來不及抓到價格\n不好意思TAT\n\n以下為訂票網址\n請直接點入查看：\n"
                + ticketurl + "\n\n輸入\"結束查詢\"回到目錄")

        time.sleep(2)
        driver.close()
        driver.quit()

    #14
    def is_going_to_cancel(self, event):
        text = event.message.text
        return text.lower() == "結束查詢"

    def on_enter_cancel(self, event):
        print("I'm entering cancel")
        global departure, destination, date1, date2, people, planeclass
        departure = ''
        destination = ''
        date1 = 0
        date2 = 0
        people = 0
        planeclass = 0

        reply_token = event.reply_token
        url = 'https://i.imgur.com/3NcvvYn.jpg'
        title = '機票價格查詢助手'
        text = '請點選下列選項'
        button = [
            MessageTemplateAction(
                label='查詢機票價格',
                text='查詢機票價格'
            ),
            MessageTemplateAction(
                label='使用說明',
                text='使用說明'
            )
        ]
        send_button_message(reply_token, url, title, text, button)
        self.go_back()

    def on_exit_cancel(self):
        print("Leaving cancel")
