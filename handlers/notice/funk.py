from telethon import TelegramClient, events
from utils import env
from services.services import getNotice
from asgiref.sync import sync_to_async
from main.models import Notice


client = TelegramClient(env.PHONE_NUMBER, env.API_ID, env.API_HASH)
last_notice_data = {}


    
chat_ids = [
    -1001950144985, -1001661240991, -1001696066827, -1001368447491,
    -1002469632510, -1001698975338, -1001698342886, -1002083400408,
    -1002068631562, -1002089458891, -1002230508278, -1001889067613,
    -1002341287738, -1002225373901, -1002206635995, -1002169615850,
    -1002202717276, -1002232013574, -1002406606261, -1002387686287,
    -1002211977483, -1002232778089, -1002067577089, -1002161701360,
    -1001927709760, -1001934813270, -1002318451740, -1001561634319,
    -1002237859063, -1001869944953, -1001768202236, -1001830606441,
    -1002219596565, -1001932433103, -1002298605058, -1002114024623,
    -1002483533745, -1001276254263, -1002178966866, -1002215121340,
    -1002355702294, -1002297602082, -1002228677318, -1002247652778,
    -1002291327774, -1002285384904, -1002225184030, -1002385819649,
    -1002220553035, -1001570432014, -1002379133637, -1002474360096,
    -1001790205450, -1002372123702, -1002001875045, -1002143591933,
    -1002376541471, -1002357488084, -1002299313513, -1002247652778,
    -1002360266775, -1002301648032, -1002220623140, -1001950144985,
    -1001503290336, -1001689353727, -1002091350845, -1002308491767,
    -1001561994254, -1002459403501, -1002248065061, -1001945152898,
    -1001801467376, -1002141143999, -1002159005012, -1002164491449,
    -1002357301670, -1002176213545, -1002345459660, -1001661001936,
    -1002085064659, -1002192007005, -1002247208452, -1002433091888,
    -1001995597670, -1002375234737, -1001502734345, -1001830606441,
    -1001502734345, -1002133733161, -1002367286161
]


message_counters = {chat_id: 0 for chat_id in chat_ids}
last_sents = {chat_id: False for chat_id in chat_ids}

async def is_chat_accessible(chat_id):
    try:
        await client.get_entity(chat_id)
        return True
    except Exception as e:
        print(f"Chat {chat_id} is not accessible: {e}")
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Chat {chat_id} is not accessible. Error: {e}\n")
        return False



async def send_notice(notice, chat_id):
    try:
        formatted_description = f"**{notice.descriptions}**"
        await client.send_message(chat_id, formatted_description, parse_mode='Markdown')
        last_sents[chat_id] = True
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        last_sents[chat_id] = False
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Chat ID: {chat_id} - Error sending message: {e}\n")



@client.on(events.NewMessage())
async def handler(event):
    global message_counters, last_sents
    if event.chat_id in chat_ids:
        if not event.out:
            notices = await sync_to_async(getNotice)()
            if notices:
                message_counters[event.chat_id] += 1
                print(f"New message received in chat {event.chat_id}. Current count: {message_counters[event.chat_id]}")

                notice_list = await sync_to_async(list)(Notice.objects.all())
                if notice_list:
                    notice = notice_list[0]
                    if message_counters[event.chat_id] >= notice.interval and not last_sents[event.chat_id]:
                        if await is_chat_accessible(event.chat_id):
                            await send_notice(notice, event.chat_id)
                            message_counters[event.chat_id] = 0
                        else:
                            print(f"Cannot send message to chat {event.chat_id}, not accessible.")
                    elif message_counters[event.chat_id] < notice.interval:
                        last_sents[event.chat_id] = False

