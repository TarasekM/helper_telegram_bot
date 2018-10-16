from orginizer_bot import OrginizerBot

def main():
    with open('TOKEN.txt', 'r') as token:
        TOKEN = token.read()
    bot = OrginizerBot(TOKEN)
    bot.run()

if __name__ == '__main__':
    main()