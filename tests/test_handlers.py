from bot_organizer import bot_organizer as bo

class TestEventHandlers:

    def test_event(self, bot, update, event_chat_data, get_logger):
        assert bo.event(bot, update, event_chat_data) == bo.EVENT_NAME
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_name(self, bot, update, event_chat_data, get_logger):
        assert bo.event_name(bot, update, event_chat_data) == bo.EVENT_DATE
        get_logger.info.assert_called_once()
        assert bo.NAME in event_chat_data[bo.LEE].keys()
        update.message.reply_text.assert_called_once()

    def test_good_event_date(self, bot, good_date_update, event_chat_data, get_logger):
        assert bo.event_date(bot, good_date_update, event_chat_data) == bo.EVENT_LOC
        get_logger.info.assert_called_once()
        assert bo.DATE in event_chat_data[bo.LEE].keys()
        good_date_update.message.reply_text.assert_called_once()

    def test_bad_event_date(self, bot, bad_date_update, event_chat_data, get_logger):
        assert bo.event_date(bot, bad_date_update, event_chat_data) == bo.EVENT_DATE
        get_logger.error.assert_called_once()
        assert bo.DATE not in event_chat_data[bo.LEE].keys()
        assert bad_date_update.message.reply_text.call_count == 2

    def test_bad_format_event_date(self, bot, bad_format_date_update, event_chat_data, get_logger):
        assert bo.event_date(bot, bad_format_date_update, event_chat_data) == bo.EVENT_DATE
        get_logger.error.assert_called_once()
        assert bo.DATE not in event_chat_data[bo.LEE].keys()
        bad_format_date_update.message.reply_text.assert_called_once()

    def test_skip_event_loc(self, bot, update, event_chat_data, get_logger):
        assert bo.skip_event_loc(bot, update) == bo.EVENT_MSG
        get_logger.info.assert_called_once()
        update.message.reply_text.assert_called_once()

    def test_event_loc(self, bot, update, event_chat_data, get_logger):
        assert bo.event_loc(bot, update, event_chat_data) == bo.EVENT_MSG
        get_logger.info.assert_called_once()