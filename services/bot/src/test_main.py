import pytest
from main import games_today, games_tomorrow, games_ten, tomorrow_predict, today_predict, ten_predict, stats
from pytest_mock import MockerFixture
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

@pytest.mark.asyncio
async def test_games_today(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(games_today, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="games_today"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games today'

    assert answer_message == expectedResult

    val = [{'Home': '1', 'Away': '2', 'Ground': '3'}]
    mocker.patch('main.make_request', return_value=val)
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

    val = [{'Home': '1', 'Away': '2', 'Ground': '3'}]
    mocker.patch('main.make_request', return_value=val)
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

    expectedResult = 'No games'

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


@pytest.mark.asyncio
async def test_tomorrow_predict(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(tomorrow_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="tomorrow_predict"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games tomorrow'

    assert answer_message == expectedResult

    val = [{'Home': '1', 'Away': '2', 'Predict': '3', 'Proba': 0.9999}]
    mocker.patch('main.make_request', return_value=val)
    requester = MockedBot(request_handler=MessageHandler(tomorrow_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="tomorrow_predict"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = '''<pre>+------+------+---------+-------+
| Home | Away | Predict | Proba |
+------+------+---------+-------+
| 1    | 2    |    3    |  1.00 |
+------+------+---------+-------+</pre>'''

    assert answer_message == expectedResult


@pytest.mark.asyncio
async def test_ten_predict(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(ten_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="ten_predict"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games'

    assert answer_message == expectedResult

    val = [{'Home': '1', 'Away': '2', 'Predict': '3', 'Proba': 0.9999}]
    mocker.patch('main.make_request', return_value=val)
    requester = MockedBot(request_handler=MessageHandler(ten_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="ten_predict"))
    answer_message = calls.send_message.fetchone().text

    print('>>>>>>>>>>>>', answer_message)

    expectedResult = '''<pre>+------+------+---------+-------+
| Home | Away | Predict | Proba |
+------+------+---------+-------+
| 1    | 2    |    3    |  1.00 |
+------+------+---------+-------+</pre>'''

    assert answer_message == expectedResult

@pytest.mark.asyncio
async def test_today_predict(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(today_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="today_predict"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No games today'

    assert answer_message == expectedResult

    val = [{'Home': '1', 'Away': '2', 'Predict': '3', 'Proba': 0.9999}]
    mocker.patch('main.make_request', return_value=val)
    requester = MockedBot(request_handler=MessageHandler(today_predict, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="today_predict"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = '''<pre>+------+------+---------+-------+
| Home | Away | Predict | Proba |
+------+------+---------+-------+
| 1    | 2    |    3    |  1.00 |
+------+------+---------+-------+</pre>'''

    assert answer_message == expectedResult

@pytest.mark.asyncio
async def test_stats(mocker: MockerFixture):
    mocker.patch('main.make_request', return_value=[])
    requester = MockedBot(request_handler=MessageHandler(stats, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="stats"))
    answer_message = calls.send_message.fetchone().text

    expectedResult = 'No stats'

    assert answer_message == expectedResult

    val = [{'team_name': '1', 'avg_score_home': 0.5, 'avg_score_away': 0.5}]
    mocker.patch('main.make_request', return_value=val)
    requester = MockedBot(request_handler=MessageHandler(stats, auto_mock_success=False))
    calls = await requester.query(MESSAGE.as_object(text="stats"))
    answer_message = calls.send_message.fetchone().text

    print(answer_message)

    expectedResult = '''<pre>+-----------+----------------+----------------+
| team_name | avg_score_home | avg_score_away |
+-----------+----------------+----------------+
|     1     |           0.50 |           0.50 |
+-----------+----------------+----------------+</pre>'''

    assert answer_message == expectedResult
