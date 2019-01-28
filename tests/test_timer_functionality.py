from bot_organizer import bot_organizer as bo


class TestTimerHandlers:

    def test_timer(self, bot, update, timer_chat_data, get_logger):
        return_val = bo.timer(bot, update, timer_chat_data)
        assert return_val == bo.TIMER_NAME
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_name(self, bot, update, timer_chat_data, get_logger):
        return_val = bo.timer_name(bot, update, timer_chat_data)
        assert return_val == bo.TIMER_DUE
        get_logger.info.assert_called_once()
        assert bo.NAME in timer_chat_data[bo.LTE].keys()
        update.message.reply_text.assert_called_once()

    def test_good_timer_due(self, bot, good_due_update,
                            timer_chat_data, get_logger):

        return_val = bo.timer_due(bot, good_due_update, timer_chat_data)
        assert return_val == bo.TIMER_MSG
        get_logger.info.assert_called_once()
        assert bo.DUE in timer_chat_data[bo.LTE].keys()
        good_due_update.message.reply_text.assert_called_once()

    def test_bad_format_timer_due(self, bot, bad_due_update,
                                  timer_chat_data, get_logger):

        return_val = bo.timer_due(bot, bad_due_update, timer_chat_data)
        assert return_val == bo.TIMER_DUE
        assert bo.DUE not in timer_chat_data[bo.LTE].keys()
        get_logger.error.assert_called_once()
        assert bad_due_update.message.reply_text.call_count == 1

    def test_skip_timer_msg(self, bot, update, job_queue, timer_chat_data,
                            get_logger, set_timer):

        return_val = bo.skip_timer_msg(bot, update, job_queue, timer_chat_data)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        set_timer.assert_called_once_with(update, job_queue, timer_chat_data)

    def test_timer_msg(self, bot, update, job_queue, timer_chat_data,
                       get_logger, set_timer):
        return_val = bo.timer_msg(bot, update, job_queue, timer_chat_data)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        set_timer.assert_called_once_with(update, job_queue, timer_chat_data)

    def test_cancel_timer(self, bot, update, get_logger):
        return_val = bo.cancel_timer(bot, update)
        assert return_val == bo.ConversationHandler.END
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_notif_str(self, good_timer_chat_data):
        return_val = bo.timer_notif_str(good_timer_chat_data[bo.LTE])
        assert isinstance(return_val, str)


class TestOneMessageTimerHandler:

    def test_good_new_timer(self, bot, update, good_timer_args,
                            job_queue, set_timer):
        chat_data = dict()
        bo.new_timer(bot, update, good_timer_args, job_queue, chat_data)
        assert bo.LTE in chat_data
        for field in bo.FIELDS[bo.LTE]:
            assert field in chat_data[bo.LTE]
        set_timer.assert_called_once_with(update, job_queue, chat_data)

    def test_bad_new_timer(self, bot, update, bad_timer_args,
                           job_queue, get_logger):
        chat_data = dict()
        bo.new_timer(bot, update, bad_timer_args, job_queue, chat_data)
        assert bo.LTE not in chat_data
        get_logger.error.assert_called_once()


class TestTimerSet:

    def test_good_set_timer(self, update, job_queue, good_timer_chat_data,
                            get_logger):

        bo.set_timer(update, job_queue, good_timer_chat_data)
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()
        job_queue.run_once.assert_called_once()
        assert bo.LTE not in good_timer_chat_data