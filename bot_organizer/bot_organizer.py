import logging
from datetime import datetime
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                          RegexHandler, ConversationHandler)

TOKEN_FILENAME = 'TOKEN.txt' # replace with the path to the file with token to your _bot
EVENT_NAME, EVENT_DATE, EVENT_LOC, EVENT_MSG = range(4)

LEE = 'last_event_entry'
LTE = 'last_timer_entry'
NAME = 'name'
DUE = 'due'
DATE = 'date'
LOC = 'location'
MSG = 'message'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
JOB_STR_END = '_job'

start_reply_keyboard = [['/event','/timer'], ['/cancel','/help']]
start_markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=False)
logger = None

def get_logger():
    return logging.getLogger(__name__)

def read_token(filename):
    with open(filename,'r') as file:
        token = file.readline().strip()
        return token

#--------------------------------------------------------------------------------
# Code block for the event conversation handler.
#--------------------------------------------------------------------------------
def event(_bot, update, chat_data):
    """New event entry start function
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    chat_data[LEE] = {NAME: None, DATE: None,
                      LOC: None, MSG: None}
    user = update.message.from_user
    get_logger().info(f'{user.first_name} started new event entry.')
    update.message.reply_text('Ok.Let\'s create new event!\n'
                              'Send /cancel to cancel the command.\n'
                              'Enter the name of the event you want '
                              'me to write down:')
    return EVENT_NAME

def event_name(_bot, update, chat_data):
    """Function to save event name and ask for event date
    in the event conversation.
    
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    chat_data[LEE][NAME] = update.message.text
    get_logger().info(f'{user.first_name}\'s event name: {update.message.text}')
    update.message.reply_text(f'Ok. Now, please, enter the date and time of the:'
                              f'{update.message.text}\nPlease, enter date in the'
                              ' "YYYY-MM-DD HH:MI:SS" format!')
    return EVENT_DATE


def event_date(_bot, update, chat_data):
    """Function to save event date and ask for event location.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user

    try:
        event_date = datetime.strptime(update.message.text.strip(),
                                       DATE_FORMAT)
        if event_date < datetime.now():
            update.message.reply_text('Sorry we can not go back to future!')
            raise ValueError
    except ValueError:
        get_logger().error(f'{user.first_name}\'s {chat_data[LEE][NAME]} '
                     f'entered wrong date: {update.message.text}')
        update.message.reply_text('Please, enter date in the '
                                  '"YYYY-MM-DD HH:MI:SS" format!')
        return EVENT_DATE
    
    chat_data[LEE][DATE] = event_date
    get_logger().info(f'{user.first_name}\'s {chat_data[LEE][NAME]} date: {event_date}')
    update.message.reply_text('Done! Now send me the location of the event'
                              ' or /skip:\n')
    return EVENT_LOC


def skip_event_loc(_bot, update):
    """Function to handle event location skip
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    get_logger().info(f'{user.first_name} did not send a location of the event.')
    update.message.reply_text('Ok! Now send me the message you want me to send '
                              'to you as a reminder for the event or /skip:\n')
    return EVENT_MSG


def event_loc(_bot, update, chat_data):
    """Function to save event location and ask for event message.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    get_logger().info(f'{user.first_name}\'s location of the {chat_data[LEE][NAME]}:'
                f' {update.message.text}')
    chat_data[LEE][LOC] = update.message.text
    update.message.reply_text('Ok! I\'ve writen down location of the event!\n'
                              'Now send me the message you want me to send you'
                              'as a reminder for the event or /skip:\n')
    return EVENT_MSG

def skip_event_msg(_bot, update, job_queue, chat_data):
    """Function to handle event message skip and set up event.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    get_logger().info(f'{user.first_name} did not send a message for the event.')
    update.message.reply_text('Done! I wrote down all the info about the event!')
    
    set_event(update, job_queue, chat_data)
    return ConversationHandler.END

def event_msg(_bot, update, job_queue, chat_data):
    """Function to save event message and set up event.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    get_logger().info(f'{user.first_name}\'s message for the {chat_data[LEE][NAME]}:'
                '\n {update.message.text}')
    chat_data[LEE][MSG] = update.message.text
    update.message.reply_text('Done! I wrote down all the info about the event!')
    
    set_event(update, job_queue, chat_data)
    return ConversationHandler.END

   
def cancel_event(_bot, update):
    """Function to handle new event entry cancel
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user
    get_logger().info(f'User {user.first_name} canceled the new event.')
    update.message.reply_text('Ok, I canceled the new event entry!')
    return ConversationHandler.END
#--------------------------------------------------------------------------------
# End of the code block for the event conversation handler.
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Setters for event and timer code block
#--------------------------------------------------------------------------------
def set_event(update, job_queue, chat_data):
    """Function to set up event notification job."""
    event_name = chat_data[LEE][NAME]
    event_job_name = event_name+JOB_STR_END
    user = update.message.from_user
    
    if event_job_name in chat_data:
        update.message.reply_text(f'Updating \'{event_name}\' entry')
        event_job = chat_data[event_job_name]
        event_job.schedule_removal()

    if chat_data[LEE][DATE] > datetime.now():
        event_job = job_queue.run_once(alarm, when=chat_data[LEE][DATE],
                                       context=[
                                           update.message.chat_id,
                                           event_name, 
                                           event_notif_str(chat_data[LEE])
                                       ]
                                      )
        chat_data[event_job_name] = event_job
        get_logger().info(f'{user.first_name} set up new event {chat_data[LEE][NAME]}!')
        update.message.reply_text(f'Event {chat_data[LEE][NAME]} successfully set!')    
    else:
        update.message.reply_text('Sorry we can not go back to future!')

    del chat_data[LEE]
            
def event_notif_str(event_dict):
    """Function to build event notification string."""
    notif = ''.join(('Event: ', event_dict[NAME]))
    notif = ''.join((notif, '\nDate: ',
                     event_dict[DATE].strftime("%Y-%m-%d %H:%M:%S")))
    if event_dict[LOC] is not None:
        notif = ''.join((notif, '\nLocation: ', event_dict[LOC]))
    if event_dict[MSG] is not None:
        notif = ''.join((notif, '\nMessage: ', event_dict[MSG]))
    return notif

def set_timer(update, job_queue, chat_data):
    """Function to set up new timer notification job."""
    timer_name = chat_data[LTE][NAME]
    timer_job_name = timer_name+JOB_STR_END
    user = update.message.from_user
    
    if timer_job_name in chat_data:
        update.message.reply_text(f'Updating \'{timer_name}\' entry')
        timer_job = chat_data[timer_job_name]
        timer_job.schedule_removal()
    
    timer_job = job_queue.run_once(alarm, chat_data[LTE][DUE], 
                               context=[
                                   update.message.chat_id,
                                   timer_name,
                                   timer_notif_str(chat_data[LTE])
                               ]
                              )
    chat_data[timer_job_name] = timer_job
    get_logger().info(f'User {user.first_name} set up new timer {timer_name} '
                f'for {chat_data[LTE][DUE]} seconds.')
    update.message.reply_text(f'Timer {chat_data[LTE][NAME]} successfully set!')    
    del chat_data[LTE]

def timer_notif_str(timer_dict):
    """Function to build timer notification string."""
    notif = ''.join(('Timer: ', timer_dict[NAME]))
    if timer_dict[MSG] is not None:
        notif = ''.join((notif, '\nMessage: ', timer_dict[MSG]))
    return notif

#--------------------------------------------------------------------------------
# End of the setters for event and timer code block.
#--------------------------------------------------------------------------------


def start(_bot, update):
    """Function for start command handler.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    update.message.reply_text('Hi! I\'m organizer helper bot!\n'
                              'Write /help to see all available commands.',
                              reply_markup=start_markup)
def help(_bot, update):
    """Function for help command handler.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    update.message.reply_text('Currently you can use only:\n'
                              '/new_timer <seconds> [timer_name] [timer_message]'
                              ' - to set timer.\n'
                              '/new_event <date "YYYY-MM-DD"> <time "HH:MI:SS">'
                              '<event_name> [event_loc] [event_msg]'
                              ' - to create an new event.\n'
                              '/event to create new event using conversation'
                              ' handler.')
    
def alarm(_bot, job):
    """Function to send alarm notification message to the user 
    who set up the event or timer.
    """
    chat_id = job.context[0]
    # job_event_name = job.context[1]
    job_message = job.context[2]
    _bot.send_message(chat_id, text=job_message)

def new_timer(_bot, update, args, job_queue, chat_data):
    """Add a job with notification for the new timer to the queue.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    user = update.message.from_user

    try:
        # args[1] should contain the name of the timer
        timer_name = args[1]
    except IndexError:
        timer_name = 'timer'
        
    try:
        # args[0] should contain the time for the timer in seconds
        timer_due = int(args[0])
        if timer_due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            raise ValueError
    except (IndexError, ValueError):
        get_logger().error(f'{user.first_name}\'s {timer_name} '
                     f'entered wrong timer due: {update.message.text}')
        update.message.reply_text('Usage: /new_timer <seconds> [timer_name] [timer_message]') 
        return
   
    
    timer_msg = None
    if args[2:]:
        timer_msg = ' '.join(args[2:])
    # adding info aboud event to chat data dict as 'last_timer_entry'
    chat_data[LTE] = dict()
    chat_data[LTE][NAME] = timer_name
    chat_data[LTE][DUE] = timer_due
    chat_data[LTE][MSG] = timer_msg
    # set up the job_queue notification for the event
    set_timer(update, job_queue, chat_data)
    
def new_event(_bot, update, args, job_queue, chat_data):
    """Add a job with notification for the new event to the queue.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    # check mandatory arguments: event_date and event_name
    try:
        date = args[0]
        time = args[1]
        event_date = datetime.strptime(' '.join((date, time)), '%Y-%m-%d %H:%M:%S')
        print('event date set')
        if event_date < datetime.now():
            update.message.reply_text('Sorry we can not go back to future!')
            return
        event_name = args[2]
    # if mandatory arguments are absent or not valid
    except (IndexError, ValueError):
        update.message.reply_text('Usage:/new_event <date_time "YYYY-MM-DD HH:MI:SS">'
                                  '<event_name> [event_loc] [event_msg]\n'
                                  'All data must be in the correct order!')
        # not valid command - exit the function
        return
    # adding optional arguments
    event_loc = None
    if args[3:]:
        event_loc = args[3]
    event_msg = None
    if args[4:]:
        event_msg = ' '.join(args[4:])
    # adding info aboud event to chat data dict as 'last_event_entry'
    chat_data[LEE] = dict()
    chat_data[LEE][NAME] = event_name
    chat_data[LEE][DATE] = event_date
    chat_data[LEE][LOC] = event_loc
    chat_data[LEE][MSG] = event_msg
    # set up the job_queue notification for the event
    set_event(update, job_queue, chat_data)

def unset(_bot, update, args, chat_data):
    """Remove the job if the user changed their mind.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    try:
        job_name = ''.join((args[0], JOB_STR_END))
    except IndexError:
        job_name = ''.join(('timer', JOB_STR_END))
        
    if job_name not in chat_data:
        update.message.reply_text(f'You have no active {job_name}.')
        return
    
    job = chat_data[job_name]
    job.schedule_removal()
    del chat_data[job_name]
    update.message.reply_text(f'{job_name} successfully unset!')

def error(_bot, update, error):
    """Log Errors caused by Updates.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    get_logger().warning(f'Update "{update}" caused error "{error}"')

def unknown(_bot, update):
    """Function for unknown command handler.
    
    :param _bot: Not used, required only by telegram-bot api.
    """
    update.message.reply_text('Sorry, I didn\'t understand that command.')
    
def main():
    """Main function to initialize bot, add all handlers and start listening
    to the user's input.
    """
    updater = Updater(read_token(TOKEN_FILENAME))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('new_timer', new_timer,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    dispatcher.add_handler(CommandHandler('new_event', new_event,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    dispatcher.add_handler(CommandHandler('unset', unset,
                                          pass_args=True,
                                          pass_chat_data=True))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('event', event, pass_chat_data=True)],

        states={
            EVENT_NAME: [MessageHandler(Filters.text, event_name, pass_chat_data=True)],
            EVENT_DATE: [MessageHandler(Filters.text, event_date, pass_chat_data=True)],
            EVENT_LOC: [MessageHandler(Filters.text, event_loc, pass_chat_data=True),
                        CommandHandler('skip', skip_event_loc)],
            EVENT_MSG: [MessageHandler(Filters.text, event_msg,
                                       pass_job_queue=True, pass_chat_data=True),
                        CommandHandler('skip', skip_event_msg, 
                                       pass_job_queue=True, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel_event),
                   CommandHandler('event', event, pass_chat_data=True)]
    )
    
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    # log all errors
    dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the _bot gracefully.
    updater.idle()

if __name__=='__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()