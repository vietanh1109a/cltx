import telebot
from telebot.types import ChatPermissions
import requests
import random
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import time
import atexit
from telebot import TeleBot, types
import pytz
import threading
import json
import re
import traceback
from telebot.apihelper import ApiException

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
API_BOT = '7165323948:AAGe59mWIO0IhabXkeXPUyBikXmYcMeaQj4'
bot = telebot.TeleBot(API_BOT, parse_mode=None)

user_balance = {}
gitcode_amounts = {}
used_gitcodes = []
user_state = {}
user_bet_history = {}
user_bets = {}

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
group_chat_id = -4623617387

def save_balance_to_file():
    with open("sodu.txt", "w") as f:
        for user_id, balance in user_balance.items():
            balance_int = int(balance)
            f.write(f"{user_id} {balance_int}\n")


def load_balance_from_file():
    if os.path.exists("sodu.txt"):
        with open("sodu.txt", "r") as f:
            for line in f:
                if line.strip():
                    user_id, balance_str = line.strip().split()
                    balance = float(balance_str)
                    if balance.is_integer():
                        balance = int(balance)
                    user_balance[int(user_id)] = balance


def initialize_user_balance():
    if not user_balance:
        load_balance_from_file()


initialize_user_balance()


def on_exit():
    save_balance_to_file()


atexit.register(on_exit)

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#

def send_dice(chat_id):
    response = requests.get(
        f'https://api.telegram.org/bot{API_BOT}/sendDice?chat_id={chat_id}')
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'dice' in data['result']:
            return data['result']['dice']['value']
    return None


def calculate_tai_xiu(total_score):
    return "Tài" if 11 <= total_score <= 18 else "Xỉu"


def chan_le_result(total_score):
    return "Chẵn" if total_score % 2 == 0 else "Lẻ"


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
GITCODE_FILE = "gitcode.txt"

def create_gitcode(amount):
    gitcode = ''.join(
        random.choices('abcdefghiklmNOPQRSTUVWXYZ0321654987', k=8))
    gitcode_amounts[gitcode] = amount
    save_gitcodes_to_file()
    return gitcode


def remove_gitcode(gitcode):
    if gitcode in gitcode_amounts:
        del gitcode_amounts[gitcode]
        save_gitcodes_to_file()


def save_gitcodes_to_file():
    with open(GITCODE_FILE, "w") as f:
        for code, value in gitcode_amounts.items():
            f.write(f"{code}:{value}\n")


def read_gitcodes():
    if not os.path.exists(GITCODE_FILE):
        return
    with open(GITCODE_FILE, "r") as f:
        for line in f:
            gitcode, amount = line.strip().split(":")
            gitcode_amounts[gitcode] = int(amount)

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
admin_ids = [123456789]  # ID ADMIN

def is_admin(message):
    user_id = message.from_user.id
    return user_id in admin_ids

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Reg Code
@bot.message_handler(commands=['regcode'])
def create_gitcode_handler(message):
    if is_admin(message):
        command_parts = message.text.split(' ')
        if len(command_parts) == 2:
            try:
                amount = int(command_parts[1])
                process_gitcode_amount(message, amount)
            except ValueError:
                bot.reply_to(message, "Số tiền không hợp lệ.")
        else:
            bot.reply_to(message, "Vui lòng nhập đúng định dạng /regcode [số tiền].")
    else:
        bot.reply_to(message, "Chỉ admin mới có thể sử dụng lệnh này.")

def process_gitcode_amount(message, amount):
    try:
        formatted_amount = "{:,.0f}".format(amount).replace(".", ",")
        gitcode = create_gitcode(amount)
        bot.reply_to(
            message,
            f"Bạn đã tạo thành công gifcode, Gitcode của bạn là: [ <code>{gitcode}</code> ] có số tiền {formatted_amount} đồng.",
            parse_mode='HTML')
    except ValueError:
        bot.reply_to(message, "Số tiền không hợp lệ.")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#Code
@bot.message_handler(commands=['code'])
def naptien_gitcode(message):
    command_parts = message.text.split(' ')
    if len(command_parts) == 2:
        gitcode = command_parts[1].strip()
        process_naptien_gitcode(message, gitcode)
    else:
        bot.reply_to(message, "Vui lòng nhập đúng định dạng /code [mã code].")

def process_naptien_gitcode(message, gitcode):
    user_id = message.from_user.id
    if gitcode in gitcode_amounts:
        amount = gitcode_amounts[gitcode]

        if gitcode not in used_gitcodes:
            used_gitcodes.append(gitcode)

            if user_id not in user_balance:
                user_balance[user_id] = 0
            user_balance[user_id] += amount

            bot.reply_to(
                message,
                f"🎉 Gitcode thành công, số dư của code bạn vừa nhập: {user_balance[user_id]:,}đ."
            )

            bot.send_message(
                group_chat_id, f"""
Người chơi {message.from_user.first_name} 
User: {user_id}
Đã nạp: {amount:,}đ bằng Gitcode.""")

            save_balance_to_file()
            remove_gitcode(gitcode)
        else:
            bot.reply_to(message,
                         "Gitcode đã sử dụng. Vui lòng nhập Gitcode khác.")
    else:
        bot.reply_to(message, "Gitcode không hợp lệ hoặc đã được sử dụng.")


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#Start
@bot.message_handler(commands=["start"])
def show_main_menu(msg):
    user_id = msg.from_user.id

    if user_id not in user_balance:
        user_balance[user_id] = 0
        save_balance_to_file()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
    rows = [
        ["👤 Tài khoản", "🎲 Danh sách game"],
        ["🧑🏼‍💻 Hỗ trợ", "👥 Giới thiệu bạn bè"],
    ]

    for row in rows:
        markup.row(*[types.KeyboardButton(button_text) for button_text in row])

    # thay link ảnh bằng png
    photo_url = ""
    caption = """
<b>Chào Mừng Bạn Đã Đến Với Sân Chơi Giải Trí</b>
     <code>AnhTuan Game Bài Game Bài Uy Tín</code>
<b>Game Xanh Chính Nói Không Với Chỉnh Cầu</b>

👉 <strong>Cách chơi đơn giản, tiện lợi</strong> 🎁

👉 <b>Nạp rút nhanh chóng, đa dạng hình thức</b> 💸

👉 <b>Có Nhiều Phần Quà Dành Cho Người Chơi Mới</b> 🤝

👉 <b>Đua top thật hăng, nhận quà cực căng</b> 💍

👉 <b>An toàn, bảo mật tuyệt đối</b> 🏆

⚠️ <b>Chú ý đề phòng lừa đảo, Chúng Tôi Không ibonx Trước</b> ⚠️

🎗 Tham gia nhóm: https://t.me/sharesrctool để nhận Giftcode hàng ngày nhé! 

Nào, bây giờ bạn hãy chọn món theo Menu ở bên dưới nhé 👇👇👇
"""
    bot.send_photo(msg.chat.id,
                   photo_url,
                   caption=caption,
                   reply_markup=markup,
                   parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.message_handler(func=lambda message: message.text == "👤 Tài khoản")
def handle_check_balance_button(msg):
    check_balance(msg)


@bot.message_handler(func=lambda message: message.text == "🎲 Danh sách game")
def handle_game_list_button(msg):
    show_game_options(msg)


@bot.message_handler(func=lambda message: message.text == "🧑🏼‍💻 Hỗ trợ")
def handle_1_list_button(msg):
    show_admin_hotro(msg)


@bot.message_handler(
    func=lambda message: message.text == "👥 Giới thiệu bạn bè")
def handle_frien_list_button(msg):
    show_friend_options(msg)


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def check_balance(msg):
    user_id = msg.from_user.id
    balance = user_balance.get(user_id, 0)
    rounded_balance = round(balance)
    photo_link = "https://i.imgur.com/EubTrXo.jpeg"
    bot.send_photo(msg.chat.id,
                   photo_link,
                   caption=f"""
👤 <b>Tên Tài Khoản</b>: [ <code>{msg.from_user.first_name}</code> ]
💳 <b>ID Tài Khoản</b>: [ <code>{msg.from_user.id}</code> ]
💰 <b>Số Dư</b>: [ <code>{rounded_balance:,}</code> ] đ
          """,
                   parse_mode='HTML',
                   reply_markup=user_menu())


def user_menu():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        telebot.types.InlineKeyboardButton("💸 Nạp tiền",
                                           callback_data="nap_tien"),
        telebot.types.InlineKeyboardButton("💸 Rút tiền",
                                           callback_data="rut_tien"))

    markup.add(
        telebot.types.InlineKeyboardButton("📉 Lịch sử nạp",
                                           callback_data="show_history_1"),
        telebot.types.InlineKeyboardButton("📈 Lịch sử rút",
                                           callback_data="show_history"))

    markup.add(
        telebot.types.InlineKeyboardButton("📦 Nhập gitcode",
                                           callback_data="nhan_gitcode"),
        telebot.types.InlineKeyboardButton("📖 Tóm tắt lịch sử",
                                           callback_data="view_history"))
    markup.add(
        telebot.types.InlineKeyboardButton("🤝 Chuyển tiền",
                                           callback_data="chuyen_tien"))

    return markup


@bot.callback_query_handler(func=lambda call: call.data == 'rut_tien')
def show_menu_rut_tien(call):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("Momo",
                                           callback_data="rut_tien_momo"),
        telebot.types.InlineKeyboardButton("Bank",
                                           callback_data="rut_tien_bank"))
    bot.send_message(call.message.chat.id,
                     "Vui lòng chọn phương thức rút tiền",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'nap_tien')
def show_menu_nap_tien(call):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("Momo",
                                           callback_data="nap_tien_momo"),
        telebot.types.InlineKeyboardButton("Bank",
                                           callback_data="nap_tien_bank"))
    bot.send_message(call.message.chat.id,
                     "Lựa chọn phương thức nạp tiền",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'nap_tien_momo')
def show_nap_tien_momo(call):
    user_id = call.from_user.id

    message_content = f'''
📖 Thông tin chuyển khoản [momo] 

🏧 Số Tài Khoản: <code>1039910788</code>

🏧Chủ Tài Khoản: <code>TRAN ANH TUAN</code>

🏧 Nội Dung: [ <code>{user_id}</code> ] 

🆘 Vui lòng nhập đúng nội dung để tiền vào nhanh nhất.
'''
    bot.send_message(call.message.chat.id, message_content, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'nap_tien_bank')
def show_nap_tien_bank(call):
    user_id = call.from_user.id

    message_content = f'''
📖 Thông tin chuyển khoản [Bank] 

🏧 Ngân Hàng: VIETCOMBANK

🏧 Số Tài Khoản: <code>1039910788</code>

🏧 Chủ Tài Khoản: <code>TRAN ANH TUAN</code>

🏧 Nội Dung: [ <code>{user_id}</code> ] 

🆘 Vui lòng nhập đúng nội dung để tiền vào nhanh nhất.
'''

    bot.send_message(call.message.chat.id, message_content, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'nhan_gitcode')
def show_nhan_gitcode(call):

    bot.send_message(
        call.message.chat.id, f'''
🗂 Để nhập Giftcode, vui lòng thực hiện theo cú pháp sau:

/code [dấu cách] mã giftcode

➡️ Vd:   /code giftcode
''')


@bot.callback_query_handler(func=lambda call: call.data == 'chuyen_tien')
def show_chuyen_tien(call):

    bot.send_message(
        call.message.chat.id, f'''
💸 Vui lòng thực hiện theo hướng dẫn sau:

/chuyentien [dấu cách] ID nhận tiền [dấu cách] Số tiền muốn chuyển

➡️ Vd:   /chuyentien 123456789 200000

⚡️ Phí chuyển tiền là 20% được trừ vào tài khoản người chuyển.
''')


@bot.callback_query_handler(func=lambda call: call.data == 'rut_tien_bank')
def show_rut_tien_bank(call):

    bot.send_message(
        call.message.chat.id, f'''
🏧 Vui lòng thực hiện theo hướng dẫn sau:

👉 /rutbank [dấu cách] Mã ngân hàng [dấu cách]  Số tài khoản [dấu cách] Tên chủ tài khoản [dấu cách] Số tiền muốn rút.

👉 VD:  Muốn rút 100k đến TK số 01234567890 tại Ngân hàng Vietcombank. Thực hiện theo cú pháp sau:

/rutbank MBB 0987654321 NguyenVanA 10000

⚠️ Lưu ý: Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin Tài khoản. 

TÊN NGÂN HÀNG - MÃ NGÂN HÀNG
📌 Vietcombank => VCB
📌 BIDV => BIDV
📌 Vietinbank => VTB
📌 Techcombank => TCB
📌 MB Bank => MBB
📌 Agribank => AGR
📌 TienPhong Bank => TPB
📌 SHB bank => SHB
📌 ACB => ACB
📌 Maritime Bank => MSB
📌 VIB => VIB
📌 Sacombank => STB
📌 VP Bank => VPB
📌 SeaBank => SAB
📌 Shinhan bank Việt Nam => SHBVN
📌 Eximbank => EIB
📌 KienLong Bank => KLB
📌 Dong A Bank => DAB
📌 HD Bank => HDB
📌 LienVietPostBank => LVPB
📌 VietBank => VBB
📌 ABBANK => ABB
📌 PG Bank => PGB
📌 PVComBank => PVC
📌 Bac A Bank => BAB
📌 Sai Gon Commercial Bank => SCB
📌 BanVietBank => VCCB
📌 Saigonbank => SGB
📌 Bao Viet Bank => BVB
📌 Orient Commercial Bank => OCB
''')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.callback_query_handler(func=lambda call: call.data == 'rut_tien_momo')
def show_rut_tien_momo(call):

    bot.send_message(
        call.message.chat.id, f'''
💸 Vui lòng thực hiện theo hướng dẫn sau:

/rutmomo [dấu cách] SĐT [dấu cách] Số tiền muốn rút

➡️ VD  /rutmomo 0987112233 200000

⚠️ Lưu ý: ❌ Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin SĐT. 

❗️ Phí rút tiền: 1.900đ cho các giao dịch dưới 50.000đ. ( RÚT TỪ 50.000đ TRỞ LÊN KHÔNG MẤT PHÍ RÚT)
''')
    

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Xử lý lệnh /history
@bot.callback_query_handler(func=lambda call: call.data == 'show_history')
def show_history(call):
    try:
        user_id = call.from_user.id

        with open("historyrut.txt", "r") as history_file:
            user_history = ""
            for line in history_file:
                if str(user_id) in line:
                    user_history += line

        if user_history:
            bot.send_message(
                call.message.chat.id,
                f"Loại | UID | Số Tiền | Ngân Hàng | STK | Tên Chủ TK |\n{user_history}"
            )
        else:
            bot.send_message(call.message.chat.id, "Lịch sử của bạn là trống.")
    except Exception as e:
        print(str(e))
        bot.send_message(call.message.chat.id, "Đã xảy ra lỗi khi lấy lịch")
         
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Xử lý lệnh /history
@bot.callback_query_handler(func=lambda call: call.data == 'show_history_1')
def show_history_1(call):
    try:
        with open("historynap.txt", "r") as history_file:
            history = history_file.read()

        if history.strip():
            bot.send_message(
                call.message.chat.id,
                f"Loại | Tên | Số Tiền | Ngân Hàng | STK | Tên Chủ TK |\n{history}"
            )
        else:
            bot.send_message(call.message.chat.id, "Không có lịch sử nạp.")
    except Exception as e:
        print(str(e))
        bot.send_message(call.message.chat.id, "Đã xảy ra lỗi khi lấy lịch")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.callback_query_handler(func=lambda call: call.data == "view_history")
def view_history_callback(call):
    user_id = call.from_user.id
    user_has_history = False
    user_history = []
    bet_type_total = {"XX1":0, "XX2":0, "Tài": 0, "Xỉu": 0, "Chẵn": 0, "Lẻ": 0, "chan2":0, "le2":0, "Dice Value": 0, "D1":0, "D2":0, "D3":0, "D4":0, "D5":0, "D6":0}

    with open("lichsucuoc.txt", "r") as history_file:
        for line in history_file:
            entry = json.loads(line.strip())
            if entry["user_id"] == user_id:
                user_has_history = True
                user_history.append(entry)
                bet_type_total[entry["bet_type"]] += entry["amount"]

    if not user_has_history:
        bot.send_message(call.message.chat.id, "Bạn chưa có lịch sử cược.")
        return

    user_history.sort(key=lambda x: x["timestamp"], reverse=True)

    recent_transactions = user_history[:3]

    history_summary = ""
    total_bet_amount = 0
    for transaction in recent_transactions:
        total_bet_amount += transaction["amount"]

    for bet_type, total_amount in bet_type_total.items():
        history_summary += f"[<code>{bet_type}</code>]  |  [<code>{total_amount:,}</code>]đ\n"
    bot.send_message(call.message.chat.id, history_summary, parse_mode='HTML')


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.message_handler(commands=['chuyentien'])
def chuyentien(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(
                message,
                "Vui lòng nhập đúng định dạng: /chuyentien [ID người nhận] [số tiền]"
            )
            return

        recipient_id = int(parts[1])
        amount = float(parts[2])

        sender_id = message.from_user.id
        if sender_id not in user_balance:
            bot.reply_to(message,
                         "Số dư của bạn không đủ để thực hiện giao dịch.")
            return

        sender_balance = user_balance[sender_id]
        if amount > sender_balance:
            bot.reply_to(message,
                         "Số dư của bạn không đủ để thực hiện giao dịch.")
            return

        transfer_fee = amount * 0.2
        net_transfer_amount = amount - transfer_fee

        user_balance[sender_id] -= amount

        if recipient_id not in user_balance:
            user_balance[recipient_id] = 0
        user_balance[recipient_id] += net_transfer_amount

        save_balance_to_file()

        sender_formatted_balance = '{:,.0f} VNĐ'.format(
            user_balance[sender_id])
        recipient_formatted_balance = '{:,.0f} VNĐ'.format(
            user_balance[recipient_id])
        bot.send_message(
            sender_id,
            f"Chuyển thành công số tiền: {net_transfer_amount:,.0f} VNĐ cho người dùng có ID: {recipient_id} thành công.\nSố dư mới của bạn: {sender_formatted_balance}"
        )
        bot.send_message(
            recipient_id,
            f"Bạn đã nhận được {net_transfer_amount:,.0f} VNĐ từ người dùng có ID {sender_id}.\nSố dư mới của bạn: {recipient_formatted_balance}"
        )

        group_message = f"Người dùng có ID {sender_id} đã chuyển {net_transfer_amount:,.0f} VNĐ cho người dùng có ID {recipient_id}."
        bot.send_message(chat_id=group_chat_id, text=group_message)
       
    except ValueError:
        bot.reply_to(message, "Vui lòng nhập số tiền là một số hợp lệ.")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.message_handler(commands=["ctien"])
def set_balance(msg):
  if msg.from_user.id == 6929210318:
    bot.reply_to(msg, """
🔭Nhập user ID của thành viên🔨
        """)
    user_state[msg.from_user.id] = "set_user_id"
  else:
    bot.reply_to(msg, "Bạn không có quyền sử dụng lệnh này.")


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id] == "set_user_id")
def set_user_balance(msg):
  try:
    user_id = int(msg.text)
    bot.reply_to(
        msg, """
⏲Nhập số tiền muốn cộng hoặc trừ🪤 
🚬(ví dụ: +1000 hoặc -1000)🎚
🫡 Kèm Nội Dung 👊🏽
        """)
    user_state[msg.from_user.id] = (user_id, "setbalance")
  except ValueError:
    bot.reply_to(msg, "Vui lòng nhập một user ID hợp lệ.")


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id][1] == "setbalance")
def update_balance(msg):
  try:
    user_input = msg.text.split()
    if len(user_input) < 2:
      bot.reply_to(msg, "Vui lòng nhập số tiền và nội dung cần kèm")
      return

    balance_change = int(user_input[0])
    user_id, _ = user_state[msg.from_user.id]
    current_balance = user_balance.get(user_id, 0)
    new_balance = current_balance + balance_change
    user_balance[user_id] = new_balance
    del user_state[msg.from_user.id]
    save_balance_to_file()

    user_message = " ".join(user_input[1:])
    notification_message = f"""
🫥Bạn Đã Nạp Tiền Thành Công🤖
🫂SD Hiện Tại: {new_balance:,}đ🐥
👾Nội Dung: {user_message} 🫶🏽
🐝Chúc Bạn Chơi Game Vui Vẻ🐳
"""
    bot.send_message(user_id, notification_message)

    group_chat_id =  -4623617387
    bot.send_message(chat_id=group_chat_id, text=notification_message
                     ) 
  except ValueError:
        bot.reply_to(message, "Vui lòng nhập số tiền là một số hợp lệ.")


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_game_options(msg):
    photo_link = 'https://i.imgur.com/j8feXot.png'

    bot.send_photo(msg.chat.id,
                   photo_link,
                   caption="""
<b>SAOWIN Game Bài Sân Chơi Giải Trí</b>\n
<b>👇Hãy chọn các game phía dưới nhé👇</b>
        """,
                   reply_markup=create_game_options(),
                   parse_mode='HTML')


def create_game_options():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        telebot.types.InlineKeyboardButton("🎲 TX 3 Xúc Xắc",
                                           callback_data="game_tai"),
        telebot.types.InlineKeyboardButton("🎲 TX 1 Xúc Xắc",
                                           callback_data="game_tai2"))
    markup.add(
        telebot.types.InlineKeyboardButton("🎰 Nổ Hũ",
                                           callback_data="game_slot"))

    markup.add(
        telebot.types.InlineKeyboardButton("⚪️ Chẳn lẻ",
                                           callback_data="game_chan"),
        telebot.types.InlineKeyboardButton("🔴 Quân vị",
                                           callback_data="game_chan2"))
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎲 Tài Xỉu Room", callback_data="game_txrom"))

    return markup

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_admin_hotro(msg):
    photo_link = "https://i.imgur.com/LnwfKzU.png"
    bot.send_photo(msg.chat.id,
                   photo_link,
                   caption=f"""
THÔNG TIN HỖ TRỢ GAME PHÍA DƯỚI 
🚨 HỖ TRỢ 24/24 🚨
          """,
                   parse_mode='HTML',
                   reply_markup=user_hotro())

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def user_hotro():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)

    markup.add(
        telebot.types.InlineKeyboardButton("Quản Lý",
                                           url="https://t.me/giangalus"),
        telebot.types.InlineKeyboardButton("Quản Trị Viên",
                                           url="https://t.me/giangalus"),
        telebot.types.InlineKeyboardButton("Home",
                                           url="https://t.me/giangalus"))

    return markup


def show_friend_options(msg):
    bot.send_message(msg.chat.id,
                     text=f"""
Tạm thời bảo trì.
            """,
                     parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def game_callback(call):
    if call.data == "game_tai":
        show_tai_bet_amount_options(call.from_user.id)
    elif call.data == "game_tai2":
        show_tai2_bet_amount_options(call.from_user.id)
    elif call.data == "game_chan":
        show_game_chan_bet_amount_options(call.from_user.id)
    elif call.data == "game_chan2":
        show_game_chan2_bet_amount_options(call.from_user.id)
    elif call.data == "game_slot":
        show_slot_bet_amount_options(call.from_user.id)
    elif call.data == "game_txrom":
        show_txroom_options(call.from_user.id)
        pass

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_tai_bet_amount_options(user_id):

    bot.send_message(user_id,
                     """
🎲 TÀI - XỈU TELEGRAM 🎲

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. 

👉 Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

👉 Kết Quả Xanh Chính Nói Không Với Chỉnh Cầu.

🔖 Thể lệ như sau

[Lệnh] ➤ [Tỷ lệ] ➤ [Kết quả]

T   |  1.95  | 11 - 18
X   |  1.95  | 3 - 10 
XX1   |  1.95  | 3-5-7-9-11-13-15-17
XX2   |  1.95  | 4-6-8-10-12-14-16-18

🎮 CÁCH CHƠI: Chat tại đây nội dung sau

👉 Đặt: [Lệnh] [dấu cách] [Số tiền cược]

[ Ví dụ: X 1000 hoặc T 1000 & XX1 1000 hoặc XX2 1000 ]

""",
                     parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_tai2_bet_amount_options(user_id):

    bot.send_message(user_id,
                     """
🎲 XÚC XẮC TELEGRAM 🎲

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. 

👉 Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

👉 Kết Quả Xanh Chính Nói Không Với Chỉnh Cầu.

🔖 Thể lệ như sau:

[Lệnh] ➤ [Tỷ lệ] ➤ [Kết quả]
D1   ➤   x5  ➤ Xúc Xắc: ➊ 
D2   ➤   x5  ➤ Xúc Xắc: ➋ 
D3   ➤   x5  ➤ Xúc Xắc: ➌
D4   ➤   x5  ➤ Xúc Xắc: ➍
D5   ➤   x5  ➤ Xúc Xắc: ➎
D6   ➤   x5  ➤ Xúc Xắc: ➏

🎮 CÁCH CHƠI: Chat tại đây nội dung sau

👉 Đặt: [Lệnh] [dấu cách] [Số tiền]

[ Ví dụ: D1 1000 hoặc D2 1000 ]

  """,
                     parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_game_chan_bet_amount_options(user_id):

    bot.send_message(user_id,
                     """
🎲 CHẴN - LẺ TELEGRAM 🎲

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. 

👉 Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

👉 Kết Quả Xanh Chính Nói Không Với Chỉnh Cầu.

🔖 Thể lệ như sau

[Lệnh] ➤ [Tỷ lệ] ➤ [Kết quả]

C  |  1.95  |  ➋ ▪️ ➍ ▪️ ➏

L  |  1.95  |  ➊ ▪️ ➌ ▪️ ➎

🎮 CÁCH CHƠI: Chat tại đây nội dung sau

👉 Đặt: [Lệnh] [dấu cách] [Số tiền cược]

[ Ví dụ: C 1000 hoặc L 1000 ]

""",
                     parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_game_chan2_bet_amount_options(user_id):

    bot.send_message(user_id,
                     """
⚪️ CHẴN LẺ QUÂN VỊ 🔴

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. 

👉 Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

👉 Kết Quả Xanh Chính Nói Không Với Chỉnh Cầu.

🔖 Thể lệ như sau

⚠️ Kết quả Chẵn: ⚪️-⚪️-⚪️-⚪️ ▪️ 🔴-🔴-🔴-🔴 ▪️ 🔴-🔴-⚪️-⚪️

⚠️ Kết quả Lẻ: ⚪️-⚪️-⚪️-🔴 ▪️ 🔴-🔴-🔴-⚪️

🎁 Tỷ lệ trả thưởng: x1.7

🎮 CÁCH CHƠI: Chat tại đây nội dung sau

👉 Đặt Chẵn: C2 [dấu cách] Số tiền cược

👉 Đặt Lẻ: L2 [dấu cách] Số tiền cược

[ Ví dụ: C2 1000 hoặc L2 1000 ]


""",
                     parse_mode='HTML')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_slot_bet_amount_options(user_id):

    bot.send_message(user_id,
                     """
🎰 SLOT TELEGRAM

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

❗️ Lưu ý: Các biểu tượng Emoji của Telegram click vào có thể tương tác được tránh bị nhầm lẫn các đối tượng giả mạo bằng ảnh gif.

🌟🌟🌟 Thể lệ 🌟🌟🌟

[lệnh] | [kết quả] | [trả thưởng]
  S    |   3 Nho   | x10
  S    |   3 Chanh | x10
  S    |   3 Bar   | x15
  S    |   3 777   | x25

🎰 Cách chơi
[lệnh] - [dấu cách] - [số tiền cược]
Ví dụ: S 1000 - S 15000     
""",
                     parse_mode='HTML')
def txroom():

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        telebot.types.InlineKeyboardButton("Game Tài Xỉu",
                                           url="https://t.me/sharesrctool")),

    return markup

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def show_txroom_options(user_id):

    bot.send_message(user_id,
                     """
🎲 TÀI - XỈU ROOM 🎲

👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. 

👉 Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.

👉 Kết Quả Xanh Chính Nói Không Với Chỉnh Cầu.

🔖 Thể lệ như sau

[Lệnh] ➤ [Tỷ lệ] ➤ [Kết quả]

TAI   |  1.9  | 11 - 18
XIU   |  1.9  | 3 - 10 
TAI ALL   |  1.9  | 11 - 18
XIU ALL   |  1.9  | 3 - 10 

🎮 CÁCH CHƠI: Chat tại đây nội dung sau

👉 Đặt: [Lệnh] [dấu cách] [Số tiền cược]

[ Ví dụ: XIU 1000 hoặc TAI 1000 & XIU ALL hoặc TAI ALL ]

""",
                     parse_mode='HTML', reply_markup=txroom())



#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def calculate_tai_xiu1(total_score):
    return "Tài" if total_score in [3, 5, 7, 9, 11, 13, 15, 17] else "Xỉu"

@bot.message_handler(
    func=lambda message: message.text.startswith(("XX1 ", "XX2 ")))
def bet_amount1(msg):
    try:
        parts = msg.text.split()
        if len(parts) != 2:
            bot.reply_to(
                msg,
                "Vui lòng nhập cược theo đúng định dạng: XX1/XX2 [dấu cách] Số tiền cược"
            )
            return

        bet_type, amount_str = parts
        bet_type = bet_type.upper()
        amount = int(amount_str)
        if amount <= 1000:
            bot.reply_to(msg, "Số tiền cược phải lớn hơn 1,000.")
            return
        elif amount > 10000000:
            bot.reply_to(msg, "Số tiền cược không được vượt quá 10,000,000.")
            return

        user_id = msg.from_user.id
        balance = user_balance.get(user_id, 0)
        if amount > balance:
            bot.reply_to(msg, "Số dư không đủ để đặt cược.")
            return

        user_balance[user_id] = balance - amount
        dice_results = [send_dice(msg.chat.id) for _ in range(3)]
        total_score = sum(dice_results)
        time.sleep(3)
        result_text = f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║ 🧭 <code>Thống Kê Tài Xỉu</code> 🧭
║ <code>{' + '.join(str(x) for x in dice_results)} = ({total_score})</code>
║ <b>Kết quả</b>: [ <code>{calculate_tai_xiu1(total_score)}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Bạn cược</b>: <code>{"XX1" if bet_type == "XX1" else "XX2"}</code>
║ <b>Message ID</b>: <code>{msg.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>"""
        vietnam_time = datetime.utcnow() + timedelta(hours=7)
        timestamp_vietnam = vietnam_time.strftime('%H:%M:%S')
        result_text += f"\n║ <b>Thời gian</b>: <code>{timestamp_vietnam}</code>"

        if (bet_type == "XX1" and calculate_tai_xiu1(total_score)
                == "Tài") or (bet_type == "XX2"
                              and calculate_tai_xiu1(total_score) == "Xỉu"):
            win_amount = int(amount * 1.95)
            result_text += f"\n║ <b>THẮNG</b> [ +<code>{win_amount:,}</code> ]"
            user_balance[user_id] += win_amount
        else:
            result_text += f"\n║ <b>THUA</b> [ -<code>{amount:,}</code> ]"

        formatted_balance = "{:,.0f}".format(user_balance[user_id])
        result_text += f"\n║ <b>Số Dư Mới</b>: <code>{formatted_balance}</code>"

        result_text += "\n╚══ ══ ══ ══ ══ ══ ══ ══╝"

        save_balance_to_file()

        with open("lichsucuoc.txt", "a") as history_file:
            history_entry = {
                "user_id": user_id,
                "bet_type": "XX1" if bet_type == "XX1" else "XX2",
                "amount": amount,
                "outcome": calculate_tai_xiu1(total_score),
                "timestamp": timestamp_vietnam
            }
            history_file.write(json.dumps(history_entry) + "\n")

        bot.send_message(chat_id=group_chat_id,
                         text=result_text,
                         parse_mode='HTML')

        bot.send_message(chat_id=msg.chat.id,
                         text=result_text,
                         parse_mode='HTML')
    except ValueError:
        pass

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.message_handler(
    func=lambda message: message.text.startswith(("T ", "X ")))
def bet_amount(msg):
    try:
        parts = msg.text.split()
        if len(parts) != 2:
            bot.reply_to(
                msg,
                "Vui lòng nhập cược theo đúng định dạng: T/X [dấu cách] Số tiền cược"
            )
            return

        bet_type, amount_str = parts
        amount = int(amount_str)
        if amount <= 1000:
            bot.reply_to(msg, "Số tiền cược phải lớn hơn 1,000.")
            return
        elif amount > 10000000:
            bot.reply_to(msg, "Số tiền cược không được vượt quá 10,000,000.")
            return

        user_id = msg.from_user.id
        balance = user_balance.get(user_id, 0)
        if amount > balance:
            bot.reply_to(msg, "Số dư không đủ để đặt cược.")
            return

        current_state = "tai" if bet_type == "T" else "xiu"
        user_balance[user_id] = balance - amount
        dice_results = [send_dice(msg.chat.id) for _ in range(3)]
        total_score = sum(dice_results)
        time.sleep(3)
        result_text = f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║ 🧭 <code>Thống Kê Tài Xỉu</code> 🧭
║ <code>{' + '.join(str(x) for x in dice_results)} = ({total_score})</code>
║ <b>Kết quả</b>: [ <code>{calculate_tai_xiu(total_score)}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Bạn cược</b>: <code>{"Tài" if current_state == "tai" else "Xỉu"}</code>
║ <b>Message ID</b>: <code>{msg.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>"""
        vietnam_time = datetime.utcnow() + timedelta(hours=7)
        timestamp_vietnam = vietnam_time.strftime('%H:%M:%S')
        result_text += f"\n║ <b>Thời gian</b>: <code>{timestamp_vietnam}</code>"

        if (current_state == "tai" and calculate_tai_xiu(total_score)
                == "Tài") or (current_state == "xiu"
                              and calculate_tai_xiu(total_score) == "Xỉu"):
            win_amount = int(amount * 1.95)
            result_text += f"\n║ <b>THẮNG</b> [ +<code>{win_amount:,}</code> ]"
            user_balance[user_id] += win_amount
        else:
            result_text += f"\n║ <b>THUA</b> [ -<code>{amount:,}</code> ]"

        formatted_balance = "{:,.0f}".format(user_balance[user_id])
        result_text += f"\n║ <b>Số Dư Mới</b>: <code>{formatted_balance}</code>"

        result_text += "\n╚══ ══ ══ ══ ══ ══ ══ ══╝"

        save_balance_to_file()

        with open("lichsucuoc.txt", "a") as history_file:
            history_entry = {
                "user_id": user_id,
                "bet_type": "Tài" if current_state == "tai" else "Xỉu",
                "amount": amount,
                "outcome": calculate_tai_xiu(total_score),
                "timestamp": timestamp_vietnam
            }
            history_file.write(json.dumps(history_entry) + "\n")

        bot.send_message(chat_id=group_chat_id,
                         text=result_text,
                         parse_mode='HTML')

        bot.send_message(chat_id=msg.chat.id,
                         text=result_text,
                         parse_mode='HTML')
    except ValueError:
        pass

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#


@bot.message_handler(func=lambda message: message.text.startswith(
    ("D1 ", "D2 ", "D3 ", "D4 ", "D5 ", "D6 ")))
def bet1_amount(msg):
    try:
        command, amount_str = msg.text.split(maxsplit=1)
        amount = int(amount_str)

        if amount <= 1999:
            bot.reply_to(msg, "Số tiền cược phải lớn hơn 2,000.")
            return
        elif amount > 1999999:
            bot.reply_to(msg, "Số tiền cược không được vượt quá 2,000,000.")
            return

        user_id = msg.from_user.id
        balance = user_balance.get(user_id, 0)
        if amount > balance:
            bot.reply_to(msg, "Số dư không đủ để đặt cược.")
            return

        current_state = command.strip()
        user_balance[user_id] = balance - amount

        dice_results = [send_dice(msg.chat.id) for _ in range(1)]
        total_score = sum(dice_results)
        time.sleep(4)
        result_text = f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║ 🧭 <code>Thống Kê Tài Xỉu</code> 🧭
║ <b>Kết quả</b>: [ <code>{' + '.join(str(x) for x in dice_results)}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{msg.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Bạn cược</b>: <code>{current_state}</code>"""
        vietnam_time = datetime.utcnow() + timedelta(hours=7)
        timestamp_vietnam = vietnam_time.strftime('%H:%M:%S')
        result_text += f"\n║ <b>Thời gian</b>: <code>{timestamp_vietnam}</code>"

        if current_state == "D1":
            if total_score == 1:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"
        elif current_state == "D2":
            if total_score == 2:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"
        elif current_state == "D3":
            if total_score == 3:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"
        elif current_state == "D4":
            if total_score == 4:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"
        elif current_state == "D5":
            if total_score == 5:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"
        elif current_state == "D6":
            if total_score == 6:
                win_amount = int(amount * 5)  # Payout for D1
                result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code>] đ"
                user_balance[user_id] += win_amount
            else:
                result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code>] đ"

        formatted_balance = "{:,.0f} đ".format(user_balance[user_id])
        result_text += f"\n║ <b>Số dư mới</b>: <code>{formatted_balance}</code>"

        result_text += f"\n╚══ ══ ══ ══ ══ ══ ══ ══╝"

        bet_info = (amount, calculate_tai_xiu(total_score), result_text)
        user_bet_history.setdefault(user_id, []).append(bet_info)

        save_balance_to_file()

        with open("lichsucuoc.txt", "a") as history_file:
            history_entry = {
                "user_id": user_id,
                "bet_type": current_state,
                "amount": amount,
                "outcome":
                "Thắng" if total_score == int(current_state[1]) else "Thua",
                "timestamp": timestamp_vietnam
            }
            history_file.write(json.dumps(history_entry) + "\n")

        bot.send_message(chat_id=group_chat_id,
                         text=result_text,
                         parse_mode='HTML')

        bot.send_message(chat_id=msg.chat.id,
                         text=result_text,
                         parse_mode='HTML',
                         reply_to_message_id=msg.message_id)

    except ValueError:
        pass

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot.message_handler(
    func=lambda message: message.text.startswith(("C ", "L ")))
def bet_amount_chan_le(msg):
    try:
        bet_info = msg.text.split()
        if len(bet_info) != 2:
            bot.reply_to(
                msg,
                "Vui lòng nhập cược theo đúng định dạng: C/L [dấu cách] Số tiền cược"
            )
            return

        choice, amount_str = bet_info
        amount = int(amount_str)

        if choice not in ["C", "L"]:
            bot.reply_to(msg, "Vui lòng chọn 'C' (Chẵn) hoặc 'L' (Lẻ).")
            return
        elif amount <= 1999:
            bot.reply_to(msg, "Số tiền cược phải lớn hơn 2,000.")
            return
        elif amount > 1999999:
            bot.reply_to(msg, "Số tiền cược không được vượt quá 2,000,000.")
            return

        user_id = msg.from_user.id
        balance = user_balance.get(user_id, 0)
        if amount > balance:
            bot.reply_to(msg, "Số dư không đủ để đặt cược.")
            return

        user_balance[user_id] -= amount
        current_state = "chan" if choice == "C" else "le"

        dice_results = [send_dice(msg.chat.id) for _ in range(1)]
        time.sleep(3)
        check_winner_chan_le(user_id, choice, amount, current_state,
                             dice_results, msg)  # Pass 'msg' here

    except ValueError:
        bot.reply_to(
            msg, "Vui lòng nhập một số tiền hợp lệ. Ví dụ: C 1000 hoặc L 1000")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def check_winner_chan_le(user_id, choice, amount, current_state, dice_results,
                         msg):
    total_score = sum(dice_results)
    result_text = f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║🧭 <code>Thống Kê Chẵn Lẻ</code> 🧭
║ <b>Xúc xắc</b>: [ <code>{' - '.join(str(x) for x in dice_results)}</code> ]
║ <b>Kết quả</b>: [ <code>{chan_le_result(total_score)}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Bạn Cược</b>: <code>{current_state}</code>
║ <b>Message ID</b>: <code>{msg.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
"""
    vietnam_time = datetime.utcnow() + timedelta(hours=7)
    timestamp_vietnam = vietnam_time.strftime('%H:%M:%S')
    result_text += f"║ <b>Thời gian</b>: <code>{timestamp_vietnam}</code>\n"

    if (current_state == "chan"
            and total_score % 2 == 0) or (current_state == "le"
                                          and total_score % 2 != 0):
        win_amount = int(amount * 1.95)
        result_text += f"║ <b>THẮNG</b> [<code>{win_amount:,}</code>] đ"
        user_balance[user_id] += win_amount
    else:
        result_text += f"║ <b>THUA</b> [<code>{amount:,}</code>] đ"

    formatted_balance = "{:,.0f}".format(user_balance[user_id])
    result_text += f"\n║ <b>Số dư mới</b>: <code>{formatted_balance}</code>"

    bet_info = (amount, chan_le_result(total_score), result_text)
    user_bet_history.setdefault(user_id, []).append(bet_info)
    result_text += "\n╚══ ══ ══ ══ ══ ══ ══ ══╝"

    save_balance_to_file()

    with open("lichsucuoc.txt", "a") as history_file:
        history_entry = {
            "user_id":
            user_id,
            "bet_type":
            "Chẵn" if choice == "C" else "Lẻ",
            "amount":
            amount,
            "outcome":
            "Thắng" if (current_state == "chan" and total_score % 2 == 0) or
            (current_state == "le" and total_score % 2 != 0) else "Thua",
            "timestamp":
            timestamp_vietnam
        }
        history_file.write(json.dumps(history_entry) + "\n")

    bot.send_message(chat_id=group_chat_id,
                     text=result_text,
                     parse_mode='HTML')

    bot.send_message(chat_id=user_id, text=result_text, parse_mode='HTML')


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def calculate_result(score):
    probabilities = {"⚪️": 0.5, "🔴": 0.5}

    result = ""
    for _ in range(4):
        result += random.choices(list(probabilities.keys()),
                                 weights=probabilities.values())[0]

    return result


@bot.message_handler(
    func=lambda message: message.text.startswith(("C2 ", "L2 ")))
def bet_amount_chan2_le2(msg):
    try:
        command, amount_str = msg.text.split(maxsplit=1)
        bet_type = command.strip()
        amount = int(amount_str)

        if amount <= 1999:
            bot.reply_to(msg, "Số tiền cược phải lớn hơn 2,000.")
            return
        elif amount > 1999999:
            bot.reply_to(msg, "Số tiền cược không được vượt quá 2,000,000.")
            return

        if bet_type == "C2":
            current_state = "chan2"
        elif bet_type == "L2":
            current_state = "le2"
        else:
            bot.reply_to(msg, "Cách chơi không hợp lệ. Vui lòng thử lại.")
            return

        user_id = msg.from_user.id
        balance = user_balance.get(user_id, 0)
        if amount > balance:
            bot.reply_to(msg, "Số dư không đủ để đặt cược.")
            return

        user_balance[user_id] = balance - amount

        countdown_message = bot.reply_to(msg, "⌛️")
        time.sleep(4)
        bot.edit_message_text(chat_id=countdown_message.chat.id,
                              message_id=countdown_message.message_id,
                              text="Đang xóc quân vị. Vui lòng chờ kết quả...")
        time.sleep(1)
        dice_result = calculate_result(5)

        check_winner_chan2_le2(user_id, current_state, amount, dice_result,
                               msg.message_id)

    except ValueError:
        bot.reply_to(
            msg,
            "Vui lòng nhập một số tiền hợp lệ.\nVí dụ: C2 1000 hoặc L2 1000.")


def check_winner_chan2_le2(user_id, current_state, amount, dice_result,
                           message_id):
    result_text = f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║ 🧭 <code>Thống Kê Chẵn Lẻ</code> 🧭
║ <b>Kết quả</b>: [ <code>{dice_result}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Bạn Cược</b>: <code>{current_state}</code>"""
    vietnam_time = datetime.utcnow() + timedelta(hours=7)
    timestamp_vietnam = vietnam_time.strftime('%H:%M:%S')
    result_text += f"\n║ <b>Thời gian</b>: <code>{timestamp_vietnam}</code>"

    if current_state == "le2":
        if dice_result.count("🔴") == 1 or dice_result.count("🔴") == 3:
            win_amount = amount * 1.7
            result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code> ]đ "
            user_balance[user_id] += win_amount
        else:
            result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code> ]đ"

    elif current_state == "chan2":
        if (dice_result.count("🔴") == 2 and dice_result.count("⚪️") == 2) or \
                (dice_result.count("🔴") == 4 or dice_result.count("⚪️") == 4):
            win_amount = amount * 1.7
            result_text += f"\n║ <b>THẮNG</b> [ <code>{win_amount:,}</code> ] đ"
            user_balance[user_id] += win_amount
        else:
            result_text += f"\n║ <b>THUA</b> [ <code>{amount:,}</code> ] đ"

    formatted_balance = "{:,.0f} đ".format(user_balance[user_id])
    result_text += f"\n║ <b>Số dư mới</b>: <code>{formatted_balance}</code>"

    bet_info = (amount, result_text)
    user_bet_history.setdefault(user_id, []).append(bet_info)
    result_text += "\n╚══ ══ ══ ══ ══ ══ ══ ══╝"
    save_balance_to_file()

    with open("lichsucuoc.txt", "a") as history_file:
        history_entry = {
            "user_id": user_id,
            "bet_type": current_state,
            "amount": amount,
            "outcome": "Thắng" if "THẮNG" in result_text else "Thua",
            "timestamp": timestamp_vietnam
        }
        history_file.write(json.dumps(history_entry) + "\n")

    bot.send_message(chat_id=group_chat_id,
                     text=result_text,
                     parse_mode='HTML')

    bot.send_message(chat_id=user_id, text=result_text, parse_mode='HTML')


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#

MIN_BET_AMOUNT = 1000
MAX_BET_AMOUNT = 15000

@bot.message_handler(func=lambda message: message.text.startswith('S '))
def dice(message):
    bet_match = re.match(r'S\s+(\d+)', message.text)
    if not bet_match:
        bot.send_message(message.chat.id, "Sử dụng lệnh theo cú pháp: S <số tiền cược>")
        return
    
    bet_amount = int(bet_match.group(1))

    if bet_amount < MIN_BET_AMOUNT or bet_amount > MAX_BET_AMOUNT:
        bot.send_message(message.chat.id, f"Số tiền cược phải min {MIN_BET_AMOUNT} max {MAX_BET_AMOUNT}.")
        return
    
    user_id = message.from_user.id
    if user_id not in user_balance:
        user_balance[user_id] = 0

    if user_balance[user_id] < bet_amount:
        bot.send_message(message.chat.id, "Số dư của bạn không đủ để đặt cược.")
        return

    user_balance[user_id] -= bet_amount  

    response = send_dice_V1(message.chat.id)
    if response == 64:
        user_balance[user_id] += 25 * bet_amount  
        reward = 25 * bet_amount
        formatted_balance = '{:,.0f} VNĐ'.format(user_balance[user_id])
        result_text = "Thắng"
        time.sleep(4)
        bot.send_message(message.chat.id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
        bot.send_message(group_chat_id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
    elif response == 43 or response == 22:
        user_balance[user_id] += 10 * bet_amount  
        reward = 10 * bet_amount 
        formatted_balance = '{:,.0f} VNĐ'.format(user_balance[user_id])
        result_text = "Thắng"
        time.sleep(4)
        bot.send_message(message.chat.id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
        bot.send_message(group_chat_id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
    elif response == 1:
        user_balance[user_id] += 15 * bet_amount  
        reward = 15 * bet_amount 
        formatted_balance = '{:,.0f} VNĐ'.format(user_balance[user_id])
        result_text = "Thắng"
        time.sleep(4)
        bot.send_message(message.chat.id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
        bot.send_message(group_chat_id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  🏆 <code>Chiến Thắng</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số tiền bạn nhận được</b>: [ <code>{int(reward):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
    else:
        formatted_balance = '{:,.0f} VNĐ'.format(user_balance[user_id])
        result_text = "Thua"
        time.sleep(4)
        bot.send_message(message.chat.id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  😮‍💨 <code>Thất Bại</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')
        bot.send_message(group_chat_id, f"""
╔══ ══ ══ ══ ══ ══ ══ ══╗
║  🧭 <code>Thống Kê Quay Hũ</code> 🧭
║  😮‍💨 <code>Thất Bại</code>
║ <b>Kết quả từ hũ</b>: [ <code>{response}</code> ]
║══ ══ ══ ══ ══ ══ ══ ══
║ <b>Message ID</b>: <code>{message.message_id}</code>
║ <b>ID</b>: <code>{user_id}</code>
║ <b>Số tiền đã cược</b>: [ <code>{int(bet_amount):,}</code> ]
║ <b>Số dư mới</b>: [ <code>{formatted_balance}</code> ]
╚══ ══ ══ ══ ══ ══ ══ ══╝
""", parse_mode='HTML')

    save_balance_to_file()

    timestamp_vietnam = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
    current_state = "Dice Value" 
    with open("lichsucuoc.txt", "a") as history_file:
        history_entry = {
            "user_id": user_id,
            "bet_type": current_state,
            "amount": bet_amount,
            "outcome": "Thắng" if "THẮNG" in result_text else "Thua",
            "timestamp": timestamp_vietnam
        }
        history_file.write(json.dumps(history_entry) + "\n")

def send_dice_V1(chat_id):
    response = requests.get(
        f'https://api.telegram.org/bot{API_BOT}/sendDice?chat_id={chat_id}&emoji=🎰'
    )
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'dice' in data['result']:
            return data['result']['dice']['value']
    return None


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Xử lý lệnh /ruttien
@bot.message_handler(commands=['rutbank'])
def handle_ruttien(message):
    try:
        command_parts = message.text.split()[1:]
        if len(command_parts) != 4:
            bot.reply_to(
                message,
                "Sai cú pháp. Vui lòng sử dụng /rutbank [tên ngân hàng] [số tài khoản] [chủ tài khoản] [số tiền]"
            )
            return

        bank_name = command_parts[0]
        account_number = command_parts[1]
        account_holder = command_parts[2]
        amount = float(command_parts[3])

        if amount < 100000:
            bot.reply_to(message,
                         "Số tiền rút từ Bank phải ít nhất là 100,000 VNĐ.")
            return

        user_id = message.from_user.id
        if user_id not in user_balance:
            bot.reply_to(message,
                         "Bạn chưa có số dư trong tài khoản của mình.")
            return

        if user_balance[user_id] < amount:
            bot.reply_to(message, "Số dư không đủ để rút tiền.")
            return

        user_balance[user_id] -= amount
        save_balance_to_file()

        amount_str = '{:,.0f}'.format(amount).replace(',', '.')

        with open("historyrut.txt", "a") as history_file:
            history_file.write(
                f"Bank {user_id} {amount_str} {bank_name} {account_number} {account_holder}\n"
            )

        bot.reply_to(
            message,
            f"Rút tiền thành công từ tài khoản của bạn.\nSố tiền: {amount_str}\nNgân hàng: {bank_name}\nSố tài khoản: {account_number}\nChủ tài khoản: {account_holder}"
        )

        bot.send_message(
            group_chat_id,
            f"Người dùng {user_id}\nĐã rút tiền từ Bank.\nSố tiền: {amount_str}\nNgân hàng: {bank_name}\nSố tài khoản: {account_number}\nChủ tài khoản: {account_holder}"
        )

    except Exception as e:
        pass
        bot.reply_to(message,
                     "Đã xảy ra lỗi trong quá trình xử lý yêu cầu của bạn.")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Xử lý lệnh /rutmomo
@bot.message_handler(commands=['rutmomo'])
def handle_rutmomo(message):
    try:
        command_parts = message.text.split()[1:]
        if len(command_parts) != 2:
            bot.reply_to(
                message,
                "Sai cú pháp. Vui lòng sử dụng /rutmomo [SĐT] [số tiền]")
            return

        phone_number = command_parts[0]
        amount = float(command_parts[1])

        if amount < 50000:
            bot.reply_to(message,
                         "Số tiền rút từ Momo phải ít nhất là 50,000 VNĐ.")
            return

        user_id = message.from_user.id
        if user_id not in user_balance:
            bot.reply_to(message,
                         "Bạn chưa có số dư trong tài khoản của mình.")
            return

        if user_balance[user_id] < amount:
            bot.reply_to(message, "Số dư không đủ để rút tiền.")
            return

        user_balance[user_id] -= amount
        save_balance_to_file()
        amount = '{:,.0f}'.format(amount).replace(',', '.')

        with open("historyrut.txt", "a") as history_file:
            history_file.write(f"Momo {user_id} {amount} {phone_number}\n")

        bot.reply_to(
            message,
            f"Rút tiền thành công qua Momo.\nSố tiền: {amount}\nSố điện thoại: {phone_number}"
        )

        bot.send_message(
            group_chat_id,
            f"Người dùng {user_id}\nĐã rút tiền qua Momo.\nSố tiền: {amount}\nSố điện thoại: {phone_number}"
        )

    except Exception as e:
        pass
        bot.reply_to(message,
                     "Đã xảy ra lỗi trong quá trình xử lý yêu cầu của bạn.")

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#----------------------------------------------------------------------------------------
#Code phần Game Tài Xỉu Room => doneta ủng hộ t li cafe vcb: 1039910788
#----------------------------------------------------------------------------------------
bot2 = telebot.TeleBot('6320448321:AAFfghGaDCPUjA6kJz_fQ5cbME-PvS9J8x8')


def send_dice_room(group_chat_id2):
    response = requests.get(
        f'https://api.telegram.org/bot#/sendDice?chat_id=#'
    )
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'dice' in data['result']:
            return data['result']['dice']['value']
    return None

@bot2.message_handler(commands=['on'])
def turn_off(message):
    if message.chat.type != 'private':
        chat_id = message.chat.id
        permissions = ChatPermissions(can_send_messages=False)
        bot2.set_chat_permissions(chat_id, permissions)
        bot2.reply_to(message, 'on.')
    else:
        bot2.reply_to(message, 'This command can only be used in groups.')

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
@bot2.message_handler(commands=['on'])
def turn_on(message):
    if message.chat.type != 'private':
        chat_id = message.chat.id
        permissions = ChatPermissions(can_send_messages=True)
        bot2.set_chat_permissions(chat_id, permissions)
        bot2.reply_to(message, 'on.')
    else:
        bot2.reply_to(message, 'This command can only be used in groups.')


def save_session_to_file():
    with open("phien.txt", "w") as file:
        file.write(str(current_session))


def load_session_from_file():
    global current_session
    try:
        with open("phien.txt", "r") as file:
            contents = file.read()
            if contents.strip() == "":  # Check if file is empty
                current_session = 1  # Default value if file is empty
            else:
                current_session = int(contents)
    except FileNotFoundError:
        current_session = 1  # Default value if file does not exist
    except ValueError:
        print("Error: Invalid data in phien.txt file")
        current_session = 1  # Default value if data is invalid

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Hàm lưu lịch sử phiên vào file
def save_session_history_to_file():
    if not threading.main_thread().is_alive():
        last_10_sessions = session_results[-10:]  # Ví dụ, bạn có thể gán giá trị này
        try:
            bot2.set_chat_permissions(group_chat_id2, permissions)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Telegram API error: {e}")
        display_last_10 = " ".join(
            ["⚫️" if session == 'TAI' else "⚪️" for session in last_10_sessions])
        with open("matphien.txt", "w") as file:
            file.write(display_last_10)
    else:
        last_10_sessions = session_results[-10:]  # Ví dụ, bạn có thể gán giá trị này
        display_last_10 = " ".join(
            ["⚫️" if session == 'TAI' else "⚪️" for session in last_10_sessions])
        with open("matphien.txt", "w") as file:
            file.write(display_last_10)

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
# Hàm load lịch sử phiên từ file
def load_session_history_from_file():
    global session_results
    try:
        with open("matphien.txt", "r") as file:
            session_history = file.read().split()
            session_results = [
                'TAI' if session == '⚫️' else 'XIU'
                for session in session_history
            ]
    except FileNotFoundError:
        session_results = []
group_chat_id2 = -1002611467986

current_session = 1
session_results = []
processed_users = set()
display_last_10 = ""
accepting_bets = False


def check_result(dice_sum):
    if 11 <= dice_sum <= 18:
        return 'TAI'
    elif 3 <= dice_sum <= 10:
        return 'XIU'
    else:
        return 'None'

def notify_bet_success(user_id, bet_type, bet_amount):
    bet_message = f"Game TX Room\nUser: [{user_id}] đã cược [{bet_type}] số tiền [{bet_amount:,} đ] thành công!"
    bot.send_message(-123456789, bet_message)

def confirm_bet(user_id, bet_type, bet_amount, original_message_id):
    global user_balance

    if user_balance.get(user_id, 0) >= bet_amount:
        if user_id not in user_bets:
            user_bets[user_id] = {'TAI': 0, 'XIU': 0}

        user_bets[user_id][bet_type.upper()] += bet_amount
        user_balance[user_id] -= bet_amount
        save_balance_to_file()

        encoded_user_id = f"***{str(user_id)[-4:]}"
        confirmation_message = f"✅ [<code>{encoded_user_id}</code>] vừa cược thành công [<code>{int(bet_amount):,}</code>] đ lệnh {bet_type}"
        bot2.send_message(group_chat_id2, confirmation_message, parse_mode='HTML')
        confirmation_message1 = f"✅ Bạn vừa cược TX Room [<code>{int(bet_amount):,}</code>] đ lệnh {bet_type}"
        bot.send_message(chat_id=user_id, text=confirmation_message1, parse_mode='HTML')
        notify_bet_success(user_id, bet_type, bet_amount)

        return True
    else:
        encoded_user_id = f"***{str(user_id)[-4:]}"
        bot2.send_message(group_chat_id2, "❌{} Không đủ số dư để đặt cược.".format(encoded_user_id), reply_to_message_id=original_message_id)
        return False

def calculate_user_winnings(user_id, game_result):
    if (game_result == 'TAI' and user_bets[user_id]['TAI']
            > 0) or (game_result == 'XIU' and user_bets[user_id]['XIU'] > 0):
        winnings = 1.9 * (user_bets[user_id]['TAI'] +
                          user_bets[user_id]['XIU'])
        user_balance[user_id] += winnings
        save_balance_to_file()
        return winnings
    return 0


def calculate_user_losses(user_id, game_result):
    if (game_result != 'TAI' and user_bets[user_id]['TAI']
            > 0) or (game_result != 'XIU' and user_bets[user_id]['XIU'] > 0):
        return user_bets[user_id]['TAI'] + user_bets[user_id]['XIU']
    return 0


def start_game():
    global current_session, accepting_bets
    current_session += 1
    accepting_bets = True


    turn_on_group_chat()
    bot2.send_message(
        group_chat_id2,
        f"<b>⌛️ Mời Bạn Đặt Cược Phiên #<code>{current_session}</code>⌛️</b>\n\n"
        f"▪️ <b>Cách Chơi</b>: <code>TAI</code> [ số tiền ] <code>XIU</code> [ số tiền ]\n"
        f"▪️ <b>Cách Chơi</b>: <code>TAI ALL</code> [ TẤT TAY ] <code>XIU ALL</code> [ TẤT TAY ]\n"
        f"▪️ Ví Dụ: <b>TAI</b> 10000 & <b>XIU</b> 10000\n\n"
        f"<b><i>▪️ KQ: ⚫️ 11 - 18 | ⚪️ 3 -10 </i></b>\n"
        f"▪️ Trả thưởng cho người thắng *1.95\n"
        f"▪️<b> Min cược: 1.000 - Max cược: 100.000.000</b>\n\n"
        f"▪️ <b>Chỉ được cược 1 mặt trong phiên</b>\n"
        f"▪️ <b>Bắt đầu cược thời gian [ 130s ]</b>\n\n"
        f"<pre>🎊 Xin mời các đại gia ra tay</pre>\n",
        parse_mode='HTML')
    time.sleep(40)

    total_bet_T = sum([user_bets[user_id]['TAI'] for user_id in user_bets])
    total_bet_X = sum([user_bets[user_id]['XIU'] for user_id in user_bets])
    total_bet_TAI = sum(
        [1 for user_id in user_bets if user_bets[user_id]['TAI'] > 0])
    total_bet_XIU = sum(
        [1 for user_id in user_bets if user_bets[user_id]['XIU'] > 0])

    last_10_sessions = session_results[-10:]
    display_last_10 = " ".join(
        ["⚫️" if session == 'TAI' else "⚪️" for session in last_10_sessions])

    bot2.send_message(
        group_chat_id2,
        f"<b>⏰ Thời Gian Cược Phiên #[<code>{current_session}</code>] Còn [ <code>60</code> ] Giây</b>\n\n"
        f"<b>Tổng Cược ⚫️ | Tổng Cược ⚪️</b>\n\n"
        f"<b>⚫️ TÀI: [<code>{int(total_bet_T):,}</code>] đ      ⚪️ XỈU: [<code>{int(total_bet_X):,}</code>] đ</b>\n\n"
        f"<i>Số người cược TÀI -- XỈU</i>\n\n"
        f"<b>👁‍🗨 TÀI: [<code>{int(total_bet_TAI):,}</code>]      👁‍🗨 XỈU: [<code>{int(total_bet_XIU):,}</code>]</b>\n\n"
        f"🗒 10 Kết quả phiên gần nhất\n\n<code>{display_last_10}</code>",
        parse_mode='HTML')

    time.sleep(60)

    total_bet_T = sum([user_bets[user_id]['TAI'] for user_id in user_bets])
    total_bet_X = sum([user_bets[user_id]['XIU'] for user_id in user_bets])
    total_bet_TAI = sum(
        [1 for user_id in user_bets if user_bets[user_id]['TAI'] > 0])
    total_bet_XIU = sum(
        [1 for user_id in user_bets if user_bets[user_id]['XIU'] > 0])

    bot2.send_message(
        group_chat_id2,
        f"<b>⏰ Thời Gian Cược Phiên #[<code>{current_session}</code>] Còn [ <code>30</code> ] Giây</b>\n\n"
        f"<b>Tổng Cược ⚫️ | Tổng Cược ⚪️</b>\n\n"
        f"<b>⚫️ TÀI: [<code>{int(total_bet_T):,}</code>] đ      ⚪️ XỈU: [<code>{int(total_bet_X):,}</code>] đ</b>\n\n"
        f"<i>Số người cược TÀI -- XỈU</i>\n\n"
        f"<b>👁‍🗨 TÀI: [<code>{int(total_bet_TAI):,}</code>]      👁‍🗨 XỈU: [<code>{int(total_bet_XIU):,}</code>]</b>\n\n"
        f"🗒 10 Kết quả phiên gần nhất\n\n<code>{display_last_10}</code>",
        parse_mode='HTML')
    time.sleep(30)

    total_bet_T = sum([user_bets[user_id]['TAI'] for user_id in user_bets])
    total_bet_X = sum([user_bets[user_id]['XIU'] for user_id in user_bets])
    total_bet_TAI = sum(
        [1 for user_id in user_bets if user_bets[user_id]['TAI'] > 0])
    total_bet_XIU = sum(
        [1 for user_id in user_bets if user_bets[user_id]['XIU'] > 0])

    turn_off_group_chat()

    time.sleep(5)

    accepting_bets = False

    bot2.send_message(
        group_chat_id2, f"<b>⏰ Hết Thời Gian Vui Lòng Chờ Kết Quả</b>\n\n"
        f"<i>Tổng cược ⚫️ TÀI -- ⚪️ XỈU</i>\n\n"
        f"<b>⚫️ TÀI: [<code>{int(total_bet_T):,}</code>] đ      ⚪️ XỈU: [<code>{int(total_bet_X):,}</code>] đ</b>\n\n"
        f"<i>Số người cược TÀI -- XỈU</i>\n\n"
        f"<b>👁‍🗨 TÀI: [<code>{int(total_bet_TAI):,}</code>]      👁‍🗨 XỈU: [<code>{int(total_bet_XIU):,}</code>]</b>\n\n"
        f"<b>🎲 Chuẩn bị tung xúc xắc.... 🎲</b>",
        parse_mode='HTML')


    time.sleep(3)

    result = [send_dice_room(group_chat_id2) for _ in range(3)]
    dice_sum = sum(result)
    game_result = check_result(dice_sum)
    session_results.append(game_result)

    send_game_result_and_process_winnings(result, dice_sum, game_result)

    save_session_to_file()

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def send_game_result_and_process_winnings(result, dice_sum, game_result):
    global current_session
    last_10_sessions = session_results[-10:]
    display_last_10 = " ".join(
        ["⚫️" if session == 'TAI' else "⚪️" for session in last_10_sessions])
    last_1_sessions = session_results[-1:]
    display_last_1 = " ".join(
        ["⚫️" if session == 'TAI' else "⚪️" for session in last_1_sessions])

    total_winnings = 0
    total_losses = 0
    user_winnings_dict = {}

    for user_id in user_bets:
        if user_id not in processed_users:
            try:
                user_winnings = calculate_user_winnings(user_id, game_result)
                user_losses = calculate_user_losses(user_id, game_result)
                total_winnings += user_winnings
                total_losses += user_losses
                processed_users.add(user_id)
                user_winnings_dict[user_id] = user_winnings

                if user_winnings > 0:
                    message_text = f"✅ Thắng Rồi  [ <code>{int(user_winnings):,}</code> ] đ trong phiên cược Room.\n\n<pre>Kết Quả: {result} -- {check_result(dice_sum)} -- {display_last_1}</pre>"
                else:
                    message_text = f"❌ Thua Rồi [ <code>{int(user_losses):,}</code> ] đ trong phiên cược Room.\n\n<pre>Kết Quả: {result} -- {check_result(dice_sum)} -- {display_last_1}</pre>"

                bot.send_message(chat_id=user_id,
                                 text=message_text,
                                 parse_mode='HTML')
            except Exception as e:
                print(f"{user_id}: {str(e)}")

    sorted_user_winnings = sorted(user_winnings_dict.items(),
                                  key=lambda x: x[1],
                                  reverse=True)

    leaderboard_message = "\n┃".join([
        f"{i+1} - <code>{'*' * 3 + str(uid)[-4:]}</code> - [<code>{int(winnings):,}</code>] đ"
        for i, (uid, winnings) in enumerate(sorted_user_winnings[:10])
    ])

    time.sleep(4)
    result_message = f"<pre>Phiên #{current_session}\n{result} - {game_result} - {display_last_1}</pre>"
    bot2.send_message(-1002068755755, result_message, parse_mode='HTML')
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Kết Quả TX [ Room ]",
                                            url="https://t.me/sharesrctool")
    keyboard.add(url_button)
    bot2.send_message(
        group_chat_id2,
        f"<b>Kết Quả Cược Của Phiên #[<code>{current_session}</code>]</b>\n"
        f"┏ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
        f"┃ <b>( <code>{result}</code> -- {check_result(dice_sum)} -- {display_last_1} )</b>\n"
        f"┃\n"
        f"┃ <b>🔎 Tổng thắng</b>: [ <code>{int(total_winnings):,}</code> ]đ\n"
        f"┃ <b>🔎 Tổng thua</b>: [ <code>{int(total_losses):,}</code> ] đ\n"
        f"┃━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ \n"
        f"┃ <b>📑 Lịch Sử Phiên Gần Nhất</b>\n"
        f"┃ {display_last_10}\n"
        f"┃━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ \n"
        f"┃ <b>🏆 Top Bảng Xếp Hạng</b>\n"
        f"┃ TOP - ID - Tiền Thắng\n"
        f"┃{leaderboard_message}\n"
        f"┗ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━",
        parse_mode='HTML',
        reply_markup=keyboard)

    user_bets.clear()
    processed_users.clear()
    save_balance_to_file()



def game_timer():
    while True:

        start_game()


#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#

@bot2.message_handler(func=lambda message: True)
def handle_message(message):
    global accepting_bets

    if accepting_bets:
        chat_id = message.chat.id

        if message.text.lower() == '/menu':
            send_betting_menu(message)
        elif message.text and len(message.text.split()) == 2:
            bet_type, bet_amount_str = message.text.split()

            if bet_type.upper() in ['TAI', 'XIU'] or (bet_type.upper() == 'TAI' and bet_amount_str.upper() in ['ALL', '1000', '50000']):
                user_id = message.from_user.id

                try:
                    if bet_amount_str.upper() == 'ALL':
                        bet_amount = user_balance.get(user_id, 0)
                    else:
                        bet_amount = int(bet_amount_str)

                    if 1000 <= bet_amount <= 100000000:
                        opposite_bet_type = 'TAI' if bet_type.upper() == 'XIU' else 'XIU'
                        if user_bets.get(user_id) and user_bets[user_id][opposite_bet_type] > 0:
                            bot2.send_message(group_chat_id2, "❌ Không được cược cả hai bên trong một phiên.")
                        else:
                            if confirm_bet(user_id, bet_type, bet_amount, message.message_id):
                                  bot2.delete_message(group_chat_id2, message.message_id)
                    else:
                        bot2.send_message(group_chat_id2, "❌ Số tiền cược phải từ 1.000 đến 100.000.000")
                except ValueError:
                    return True
                except telebot.apihelper.ApiException as e:
                    pass
                    return True
                except Exception as e:
                    bot2.send_message(user_id, f"❌ Đã xảy ra lỗi: {str(e)}")
        else:
            return True
    else:
        bot2.send_message(message.chat.id,
                          "❌ Cược không được chấp nhận vào lúc này. Vui lòng chờ tập tiếp theo.")



def send_betting_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tai_buttons = [
        types.KeyboardButton("tai 5000"),
        types.KeyboardButton("tai 20000"),
        types.KeyboardButton("tai 50000"),
        types.KeyboardButton("tai ALL")
    ]
    xiu_buttons = [
        types.KeyboardButton("xiu 5000"),
        types.KeyboardButton("xiu 20000"),
        types.KeyboardButton("xiu 50000"),
        types.KeyboardButton("xiu ALL")
    ]
    keyboard.row(*tai_buttons)
    keyboard.row(*xiu_buttons)
    bot2.send_message(message.chat.id, "Vui lòng chọn cược.", reply_markup=keyboard)

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def turn_on_group_chat():
    permissions = ChatPermissions(can_send_messages=True)
    bot2.set_chat_permissions(group_chat_id2, permissions)


def turn_off_group_chat():
    permissions = ChatPermissions(can_send_messages=False)
    bot2.set_chat_permissions(group_chat_id2, permissions)

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
load_balance_from_file()
load_session_from_file()
load_session_history_from_file()

timer_thread = threading.Thread(target=game_timer)
timer_thread.start()


def poll_bot():
    bot.polling()

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
def poll_bot2():
    bot2.polling()

#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
thread_bot = threading.Thread(target=poll_bot)
thread_bot2 = threading.Thread(target=poll_bot2)

thread_bot.start()
thread_bot2.start()


















#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
#<-----Tác Giả: Tran Anh Tuan--Box Tele: @sharesrctool--Vui Lòng Không Xoá Phần Này--->#
