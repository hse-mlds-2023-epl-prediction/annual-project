import pytest
from pytest_mock import mocker
import asyncio
from aiogram.filters import Command
from aiogram.methods import AnswerCallbackQuery
from aiogram.methods import SendMessage
from main import games_today, games_tomorrow, games_ten
from pytest_mock import MockerFixture
from aiogram_tests import MockedBot
import api_client
from aiogram_tests.handler import CallbackQueryHandler
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import CALLBACK_QUERY
from aiogram_tests.types.dataset import MESSAGE
from aiogram_tests.bot import MockedBot  # Add this line

@pytest.mark.asyncio
async def test_games_today(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(games_today, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_today"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games today'

    assert answer_message == expectedResult

    mocker.patch('main.make_request', return_value=[{'Home': '1', 'Away': '2', 'Ground': '3'}])
    requester = MockedBot(request_handler=MessageHandler(games_today, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_today"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = '''<pre>+------+------+--------+
| Home | Away | Ground |
+------+------+--------+
| 1    | 2    |      3 |
+------+------+--------+</pre>'''

    assert answer_message == expectedResult


@pytest.mark.asyncio
async def test_games_tomorrow(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(games_tomorrow, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_tomorrow"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games tomorrow'

    assert answer_message == expectedResult

    mocker.patch('main.make_request', return_value=[{'Home': '1', 'Away': '2', 'Ground': '3'}])
    requester = MockedBot(request_handler=MessageHandler(games_tomorrow, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_tomorrow"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = '''<pre>+------+------+--------+
| Home | Away | Ground |
+------+------+--------+
| 1    | 2    |      3 |
+------+------+--------+</pre>'''

    assert answer_message == expectedResult


@pytest.mark.asyncio
async def test_games_ten(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(games_ten, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_ten"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games tomorrow'

    assert answer_message == expectedResult

    mocker.patch('main.make_request', return_value=[{'Home': '1', 'Away': '2', 'Ground': '3'}])
    requester = MockedBot(request_handler=MessageHandler(games_ten, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_ten"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = '''<pre>+------+------+--------+
| Home | Away | Ground |
+------+------+--------+
| 1    | 2    |      3 |
+------+------+--------+</pre>'''

    assert answer_message == expectedResult