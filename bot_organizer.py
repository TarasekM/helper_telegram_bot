from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from datetime import datetime

import logging

TOKEN_FILENAME = 'TOKEN.txt'

def read_token(filename):
    with open(filename,'r') as file:
        token = file.readline()
        return token

def start(bot, update):
    update.message.reply_text('Hi! I\'m orginizer helper bot!')
    
def help(bot, update):
    update.message.reply_text('Currently you can use only this commands:\n'
                             '/set <seconds> <timer_name>(optional) - to set timer.\n'
                             '/new_event <hour "HH:MI:SS"> <date "YYYY-MM-DD">'
                             '<event_name> - to create an new event')

    #update.message.reply_text('Currently you can use only this commands:\
    #                         \n/set <seconds> <timer_name>(optional) - to set timer.')
    
def alarm(bot, job):
    """Send the alarm message."""
    chat_id = job.context[0]
    try:
        timer_name = job.context[1]
        bot.send_message(chat_id, text=f'Beep: {timer_name}!')
    except IndexError:
        bot.send_message(chat_id, text='Beep!')

def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        
        try:
            # args[1] should contain the name of the timer
            timer_name = args[1]
        except IndexError:
            timer_name = 'timer'
        if timer_name in chat_data:
            update.message.reply_text(f'Updating \'{timer_name}\' timer')
            timer = chat_data[timer_name]
            timer.schedule_removal()
        timer = job_queue.run_once(alarm, due, context=[chat_id, timer_name])
        chat_data[timer_name] = timer
        update.message.reply_text(f'Timer \'{timer_name}\' successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds> <timer_name>(optional)')
        
def new_event(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        time = args[0]
        date = args[1]
        event_name = ' '.join(args[2:])
        time_now = str(datetime.now().time().replace(microsecond=0))
        date_now = str(datetime.now().date())
        
        if time_now > time or date_now > date:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        
        if name in chat_data:
            update.message.reply_text(f'Updating \'{event_name}\' event')
            event = chat_data[event_name]
            event.schedule_removal()
        event = job_queue.run_once(event_alarm, time_difference, context=[chat_id, timer_name])
        chat_data[event_name] = event
        update.message.reply_text(f'Event {event_name} successfully set!')

    except IndexError:
        update.message.reply_text('Usage: /new_event <hour "HH:MI:SS"> <date "YYYY-MM-DD">'
                        '<event_name>')

def event_alarm(bot, job):
    """Send the alarm message."""
    #TODO
    chat_id = job.context[0]
    try:
        event_name = job.context[1]
        bot.send_message(chat_id, text=f'Beep: {event_name}!')
    except IndexError:
        bot.send_message(chat_id, text='Beep!')

def time_difference(time_now, time_future):
    #TODO
    return 0


def unset(bot, update, args, chat_data):
    """Remove the job if the user changed their mind."""
    try:
        timer_name = args[0]
    except IndexError:
        timer_name = 'timer'
        
    if timer_name not in chat_data:
        update.message.reply_text(f'You have no active {timer_name}.')
        return
    
    timer = chat_data[timer_name]
    timer.schedule_removal()
    del chat_data[timer_name]

    update.message.reply_text(f'{timer_name.capitalize()} successfully unset!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
def main():
    updater = Updater(read_token(TOKEN_FILENAME))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    
    dispatcher.add_handler(CommandHandler("new_event", new_event,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    
    dispatcher.add_handler(CommandHandler("unset", unset,
                                          pass_args=True,
                                          pass_chat_data=True))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__=='__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)
    main()
