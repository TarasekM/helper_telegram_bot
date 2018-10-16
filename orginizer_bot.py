from telegram import InlineQueryResult, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
import logging


class OrginizerBot(object):
    
    def __init__(self, TOKEN):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.__TOKEN = TOKEN
        self.updater = Updater(token=self.__TOKEN)
        self.dispatcher = self.updater.dispatcher
        self.__add_handlers()

    def __add_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.start))
        self.dispatcher.add_handler(CommandHandler("set", self.set_timer,
                                    pass_args=True,
                                    pass_job_queue=True,
                                    pass_chat_data=True))
        self.dispatcher.add_handler(CommandHandler("unset", self.unset, pass_chat_data=True))

        # log all errors
        self.dispatcher.add_error_handler(self.error)

    def start(self, bot, update):
        update.message.reply_text(
        'Hi! I\'m orginizer bot!\n\
        Currently you can use:\n\
        /set <seconds> command to set a timer.'
        )

    def alarm(self, bot, job):
        """Send the alarm message."""
        bot.send_message(job.context, text='Beep!')

    def set_timer(self, bot, update, args, job_queue, chat_data):
        chat_id = update.message.chat_id
        try:
            # args[0] should contain the time for the timer in seconds
            due = int(args[0])
            if due < 0:
                update.message.reply_text('Sorry we can not go back to future!')
                return

            # Add job to queue
            job = job_queue.run_once(self.alarm, due, context=chat_id)
            chat_data['job'] = job

            update.message.reply_text('Timer successfully set!')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <seconds>')

    def unset(self, bot, update, chat_data):
        """Remove the job if the user changed their mind."""
        if 'job' not in chat_data:
            update.message.reply_text('You have no active timer')
            return

        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']

        update.message.reply_text('Timer successfully unset!')

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()