import datetime
import json
import os

import requests
#from discord import Webhook, RequestsWebhookAdapter
from discord import SyncWebhook


#################### GENERATE MESSAGES #########################
def trim_datetime(dt):
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    date_only = datetime.datetime.strptime(dt, TIME_FORMAT)
    date_only = date_only.strftime(DATE_FORMAT)
    return date_only


def generate_new_cve_message(cve_data: dict) -> str:
    ''' Generate new CVE message for sending to slack '''
    friendly_time = "%Y-%m-%d"
    # Emoji's for copy and pasting here: https://www.freecodecamp.org/news/all-emojis-emoji-list-for-copy-and-paste/
    message = f"🚨  *{cve_data['CVE_ID']}*  🚨\n"
    message += f"💥  *CVSSv3.1*: {cve_data['CVSSv3_Score']}\n"
    #message += f"📅  *Published*: {datetime.datetime.strptime(cve_data['Published'], friendly_time)}"
    message += f"📅  *Published*: {cve_data['Published']}"
    #message += f" - *Modified*: {datetime.datetime.strptime(cve_data['Last_Modified'], friendly_time)}\n"
    #message += f" - *Modified*: {cve_data['Last_Modified']}\n"
    message += "\n📓  *Description*: " 
    message += cve_data["Description"] if len(cve_data["Description"]) < 500 else cve_data["Description"][:500] + "..."
    
    # if cve_data["Vuln_Status"]:
    #     message += f"\n🔓  *Vulnerable* (_limit to 10_): " + ", ".join(cve_data["Vuln_Status"][:10])
    if cve_data.get('ExploitDB_ID') is not None:
        #message = "😈  *Public Exploits* (_limit 10_):\n" + "\n".join(public_expls[:20])
        message += f"\n\n😈  *Exploit-DB*: https://www.exploit-db.com/exploits/{cve_data['ExploitDB_ID']}"
    if cve_data.get("\nExploit_References"):
        message += f"\n🔓  *Exploit References* (_limit 5_):\n" + "\n".join(cve_data["Exploit_References"][:5])
    
    message += f"\n🔗  *GitHub Dork:* https://github.com/search?q={cve_data['CVE_ID']}"
    message += "\nℹ️   *More information* (_limit to 5_):\n" + "\n".join(cve_data["Normal_References"][:5])
    message += "\n"
    return message


# def generate_modified_cve_message(cve_data: dict) -> str:
#     ''' Generate modified CVE message for sending to slack '''

#     message = f"📣 *{cve_data['CVE_ID']}*(_{cve_data['CVSSv3_Score']}_) was modified the {cve_data['Last_Modified'].split('T')[0]} (_originally published the {cve_data['Published'].split('T')[0]}_)\n"
#     return message


# def generate_exploits_message(cve_data: dict) -> str:
#     ''' Given the list of public exploits, generate the message '''

#     message = ""
#     if cve_data.get('ExploitDB_ID') is not None:
#         #message = "😈  *Public Exploits* (_limit 10_):\n" + "\n".join(public_expls[:20])
#         message = f"😈  *Exploit-DB IDs*: {cve_data['ExploitDB_ID']}\n"
#     return message


#################### SEND MESSAGES - SLACK #########################

def send_slack_mesage(message: str):
    ''' Send a message to the slack group '''

    slack_url = os.getenv('SLACK_WEBHOOK')

    if not slack_url:
        #print("SLACK_WEBHOOK wasn't configured in the secrets!")
        return
    
    json_params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": message
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    # if public_expls_msg:
    #     json_params["blocks"].append({
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn", 
    #                 "text": public_expls_msg
    #             }
    #     })
    requests.post(slack_url, json=json_params)
    return


#################### SEND MESSAGES - TELEGRAM #########################

def send_telegram_message(message: str):
    ''' Send a message to the telegram group '''

    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')    

    if not telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN wasn't configured in the secrets!")
        return
    
    if not telegram_chat_id:
        print("TELEGRAM_CHAT_ID wasn't configured in the secrets!")
        return
    
    #if public_expls_msg:
        #message = message + "\n" + public_expls_msg

    message = message.replace(".", "\.").replace("-", "\-").replace("(", "\(").replace(")", "\)").replace("_", "").replace("[","\[").replace("]","\]").replace("{","\{").replace("}","\}").replace("=","\=")
    r = requests.get(f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage?parse_mode=MarkdownV2&text={message}&chat_id={telegram_chat_id}')

    resp = r.json()
    if not resp['ok']:
        r = requests.get(f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage?parse_mode=MarkdownV2&text=Error with' + message.split("\n")[0] + f'{resp["description"]}&chat_id={telegram_chat_id}')
        resp = r.json()
        if not resp['ok']:
            print("ERROR SENDING TO TELEGRAM: " + message.split("\n")[0] + resp["description"])
    return


#################### SEND MESSAGES - DISCORD #########################

def send_discord_message(message: str, public_expls_msg: str):
    ''' Send a message to the discord channel webhook '''

    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    if not discord_webhook_url:
        print("DISCORD_WEBHOOK_URL wasn't configured in the secrets!")
        return
    
    if public_expls_msg:
        message = message + "\n" + public_expls_msg

    message = message.replace("(", "\(").replace(")", "\)").replace("_", "").replace("[","\[").replace("]","\]").replace("{","\{").replace("}","\}").replace("=","\=")
    #webhook = Webhook.from_url(discord_webhook_url, adapter=RequestsWebhookAdapter())
    webhook = SyncWebhook.from_url(discord_webhook_url)
    if public_expls_msg:
        message = message + "\n" + public_expls_msg
    
    #webhook.send(message)
    webhook.send(content=message)
    return
