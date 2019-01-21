from bot_organizer import bot_organizer as bo


class TestEventHandlers:

    def test_event(self, bot, update, event_chat_data, get_logger):
        return_val = bo.event(bot, update, event_chat_data)
        assert return_val == bo.EVENT_NAME
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_name(self, bot, update, event_chat_data, get_logger):
        return_val = bo.event_name(bot, update, event_chat_data)
        assert return_val == bo.EVENT_DATE
        get_logger.info.assert_called_once()
        assert bo.NAME in event_chat_data[bo.LEE].keys()
        update.message.reply_text.assert_called_once()

    def test_good_event_date(self, bot, good_date_update,
                             event_chat_data, get_logger):
        return_val = bo.event_date(bot, good_date_update, event_chat_data)
        assert return_val == bo.EVENT_LOC
        get_logger.info.assert_called_once()
        assert bo.DATE in event_chat_data[bo.LEE].keys()
        good_date_update.message.reply_text.assert_called_once()

    def test_bad_event_date(self, bot, bad_date_update,
                            event_chat_data, get_logger):
        return_val = bo.event_date(bot, bad_date_update, event_chat_data)
        assert return_val == bo.EVENT_DATE
        get_logger.error.assert_called_once()
        assert bo.DATE not in event_chat_data[bo.LEE].keys()
        assert bad_date_update.message.reply_text.call_count == 2

    def test_bad_format_event_date(self, bot, bad_format_date_update,
                                   event_chat_data, get_logger):
        return_val = bo.event_date(bot, bad_format_date_update,
                                   event_chat_data)
        assert return_val == bo.EVENT_DATE
        get_logger.error.assert_called_once()
        assert bo.DATE not in event_chat_data[bo.LEE].keys()
        bad_format_date_update.message.reply_text.assert_called_once()

    def test_skip_event_loc(self, bot, update, event_chat_data, get_logger):
        return_val = bo.skip_event_loc(bot, update)
        assert return_val == bo.EVENT_MSG
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_loc(self, bot, update, event_chat_data, get_logger):
        return_val = bo.event_loc(bot, update, event_chat_data)
        assert return_val == bo.EVENT_MSG
        get_logger.info.assert_called_once()

    def test_skip_event_msg(self, bot, update, job_queue, event_chat_data,
                            get_logger, set_event):
        return_val = bo.skip_event_msg(bot, update, job_queue, event_chat_data)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        set_event.assert_called_once_with(update, job_queue, event_chat_data)

    def test_event_msg(self, bot, update, job_queue, event_chat_data,
                       get_logger, set_event):
        return_val = bo.event_msg(bot, update, job_queue, event_chat_data)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        set_event.assert_called_once_with(update, job_queue, event_chat_data)

    def test_cancel_event(self, bot, update, get_logger):
        return_val = bo.cancel_event(bot, update)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_notif_str(self, good_event_chat_data):
        return_val = bo.event_notif_str(good_event_chat_data[bo.LEE])
        assert isinstance(return_val, str)


class TestOneMessageEventHandler():

    def test_good_new_event(self, bot, update, good_event_args, 
                            job_queue, set_event):
        chat_data = dict()
        bo.new_event(bot, update, good_event_args,
                    job_queue, chat_data)
        assert bo.LEE in chat_data
        for field in bo.FIELDS[bo.LEE]:
            assert field in chat_data[bo.LEE]
        set_event.assert_called_once_with(update, job_queue, chat_data)

    def test_bag_new_event(self, bot, update, bad_event_args,
                           job_queue, get_logger, set_event):
        chat_data = dict()
        bo.new_event(bot, update, bad_event_args,
                     job_queue, chat_data)
        assert bo.LEE not in chat_data
        get_logger.error.assert_called_once()

class TestEventSet():

    def test_good_set_event(self, update, job_queue,
                            good_event_chat_data, get_logger):
        bo.set_event(update, job_queue, good_event_chat_data)
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        job_queue.run_once.assert_called_once()
        assert bo.LEE not in good_event_chat_data

    def test_bad_set_event(self, update, job_queue,
                           bad_event_chat_data, get_logger):
        bo.set_event(update, job_queue, bad_event_chat_data)
        get_logger.error.assert_called_once()
        update.message.reply_text.assert_called_once()