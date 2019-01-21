import pytest
from bot_organizer import bot_organizer as bo
from datetime import datetime, timedelta

@pytest.fixture(name='logger', scope='function')
def _logger(mocker):
    bo.logger = mocker.Mock()
    return bo.logger

@pytest.fixture(name='bot', scope='module')
def _bot():
    return object()

@pytest.fixture(name='event_chat_data', scope='function')
def event_chat_data():
    data = dict()
    data[bo.LEE] = dict()
    data[bo.LEE][bo.NAME] = 'TEST LEE'
    return data

@pytest.fixture(name='update', scope='function')
def _update(mocker):
    update = mocker.Mock()
    update.message.text = 'Test text'
    return update

@pytest.fixture(name='good_date_update', scope='function')
def _good_date_update(mocker):
    update = mocker.Mock()
    now = datetime.now()
    now_plus_10 = now + timedelta(minutes = 10)
    update.message.text = now_plus_10.strftime(bo.DATE_FORMAT)
    return update

@pytest.fixture(name='bad_date_update', scope='function')
def _bad_date_update(mocker):
    update = mocker.Mock()
    now = datetime.now()
    now_minus_10 = now - timedelta(minutes = 10)
    update.message.text = now_minus_10.strftime(bo.DATE_FORMAT)
    return update

@pytest.fixture(name='bad_format_date_update', scope='function')
def _bad_format_date_update(mocker):
    update = mocker.Mock()
    update.message.text = datetime.now().strftime('%f')
    return update