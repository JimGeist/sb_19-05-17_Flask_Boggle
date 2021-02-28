from unittest import TestCase
from app import app, set_session_cookie, get_cookie_data, get_raw_game_board, update_cookie_data, create_game_board_html
from app import assemble_game_data
from flask import session, request, jsonify
from boggle import Boggle


class FlaskTests(TestCase):

    def test_welcome(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            hdrs = str(resp.headers)

            self.assertEqual(resp.status_code, 200)
            # score / statistics
            self.assertIn('id="score"', html)
            self.assertIn('id="high-score"', html)
            self.assertIn('id="nbr-plays"', html)
            # board / table-o-letters
            self.assertIn('id="boggle-board"', html)
            # form guess input and submit-guess button
            self.assertIn('id="guess"', html)
            self.assertIn('id="submit-guess"', html)
            # word lists
            self.assertIn('id="words-valid"', html)
            self.assertIn('id="words-not-on-board"', html)
            self.assertIn('id="words-not-a-word"', html)
            # messaging
            self.assertIn('id="messages"', html)

            # set boggle_plays and boggle_high cookies
            self.assertIn('boggle_plays=0', hdrs)
            self.assertIn('boggle_high', hdrs)

    def test_check_word(self):
        with app.test_client() as client:
            #
            game_board = [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]
            #
            with client.session_transaction() as change_session:
                change_session['boggle_session'] = game_board

            resp = client.get('/api/check_word?word=FETCH')
            # /api/check_word responds with json
            json_data = resp.get_json()
            self.assertEqual(json_data, {'result': {'result': 'ok'}})

            resp = client.get('/api/check_word?word=CAMERA')
            json_data = resp.get_json()
            self.assertEqual(
                json_data, {'result': {'result': 'not-on-board'}})

            resp = client.get('/api/check_word?word=MADEUPWORD')
            json_data = resp.get_json()
            self.assertEqual(
                json_data, {'result': {'result': 'not-word'}})

    def test_handle_save_game(self):
        with app.test_client() as client:
            # with client.session_transaction() as change_session:
            #     change_session['boggle_gameover'] = "test"
            # const res = await axios.put(`${ROOT_API}save_game`, {
            #     params: {
            #         "score": inScore,
            #         "words_valid": wordsValid,
            #         "words_not_on_board": wordsNotOnBoard,
            #         "words_not_a_word": wordsNotWords
            #   }

            resp = client.put(
                '/api/save_game?score=80&words_valid=val1')
            # /api/save_game responds with json response code only, no json data
            self.assertEqual(resp.status, '200 OK')

            json_data = resp.get_json()

            # import pdb
            # pdb.set_trace()
            self.assertEqual(json_data, None)

    def test_game_over_redirect(self):
        with app.test_client() as client:
            game_board = [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]
            resp = client.get('/game_over')
            html = resp.get_data(as_text=True)
            hdrs = str(resp.headers)

            # without cookies or session cookie, the game_over will
            #  redirect to root (/)
            self.assertEqual(resp.status_code, 302)

            # test for successful redirect to root (/)
            resp = client.get('/game_over', follow_redirects=True)
            html = resp.get_data(as_text=True)
            hdrs = str(resp.headers)

            # without cookies or session cookie, the game_over will
            #  redirect to root (/)
            self.assertEqual(resp.status_code, 200)
            # score / statistics
            self.assertIn('id="score"', html)
            self.assertIn('id="high-score"', html)
            self.assertIn('id="nbr-plays"', html)
            # board / table-o-letters
            self.assertIn('id="boggle-board"', html)
            # form guess input and submit-guess button
            self.assertIn('id="guess"', html)
            self.assertIn('id="submit-guess"', html)
            # word lists
            self.assertIn('id="words-valid"', html)
            self.assertIn('id="words-not-on-board"', html)
            self.assertIn('id="words-not-a-word"', html)
            # messaging
            self.assertIn('id="messages"', html)

            # set boggle_plays and boggle_high cookies
            self.assertIn('boggle_plays=0', hdrs)
            self.assertIn('boggle_high', hdrs)

    def test_game_over(self):
        with app.test_client() as client:
            game_board = [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]
            #
            game_over_data = {"params": {
                "score": 900,
                "words_valid": "list valid words",
                "words_not_on_board": "list of words not on game board",
                "words_not_a_word": "list of words that are not words"
            }}

            with client.session_transaction() as change_session:
                change_session['boggle_session'] = game_board
            with client.session_transaction() as change_session:
                change_session['boggle_gameover'] = game_over_data
            # with client.session_transaction() as change_session:
            #     change_session['boggle_gameover'] = {"params": {"score": 900}}
            resp = client.get('/game_over')
            html = resp.get_data(as_text=True)
            hdrs = str(resp.headers)

            # session cookie with partial last game info
            self.assertEqual(resp.status_code, 200)
            # score / statistics
            self.assertIn('id="score"', html)
            self.assertIn('id="high-score"', html)
            self.assertIn('id="nbr-plays"', html)
            # board / table-o-letters
            self.assertIn('id="boggle-board"', html)
            # form guess input and new-game button
            self.assertIn('id="guess"', html)
            self.assertIn('id="new-game"', html)
            # word lists
            self.assertIn('id="words-valid"', html)
            self.assertIn('>list valid words<', html)
            self.assertIn('id="words-not-on-board"', html)
            self.assertIn('>list of words not on game board<', html)
            self.assertIn('id="words-not-a-word"', html)
            self.assertIn('>list of words that are not words<', html)
            # messaging
            self.assertIn('id="messages"', html)

            # set boggle_plays cookie to 1
            self.assertIn('boggle_plays=1', hdrs)
            # set boggle_high cookie to 900
            self.assertIn('boggle_high=900', hdrs)

    def test_create_game_board_html(self):
        with app.test_request_context('/'):

            # create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
            #     'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']])

            self.assertIn("<tr><td>R</td><td>W</td><td>C</td><td>E</td><td>D</td></tr>", create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]))
            self.assertIn("<tr><td>N</td><td>W</td><td>I</td><td>X</td><td>W</td></tr>", create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]))
            self.assertIn("<tr><td>H</td><td>F</td><td>H</td><td>M</td><td>G</td></tr>", create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]))
            self.assertIn("<tr><td>E</td><td>T</td><td>C</td><td>A</td><td>M</td></tr>", create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]))
            self.assertIn("<tr><td>F</td><td>B</td><td>D</td><td>S</td><td>H</td></tr>", create_game_board_html([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]))

    def test_get_cookie_data(self):
        with app.test_request_context('/'):

            # cookies for high score and number of plays do not exist, but
            #  we can at least check that the dictionary returned has 0 for
            #  number of plays and high score.
            self.assertEqual(0, get_cookie_data()["nbr_of_plays"])
            self.assertEqual(0, get_cookie_data()["score_high"])

    def test_update_cookie_data(self):
        with app.test_request_context('/game_over'):

            # cookie for high score and number of plays do not exist and the
            #  values for high score and number of plays default to 0
            # when last game score is 0: nbr_plays is 1, high score is 0,
            #  new high is false
            self.assertEqual(1, update_cookie_data(0)["nbr_of_plays"])
            self.assertEqual(0, update_cookie_data(0)["score_high"])
            self.assertEqual(False, update_cookie_data(0)["score_high_is_new"])

            # cookie for high score and number of plays do not exist and the
            #  values for high score and number of plays default to 0
            # when score is 10: nbr_plays is 1, high score is 10, new high is True
            self.assertEqual(1, update_cookie_data(10)["nbr_of_plays"])
            self.assertEqual(10, update_cookie_data(10)["score_high"])
            self.assertEqual(True, update_cookie_data(10)["score_high_is_new"])

    def test_assemble_game_data_startgame(self):
        with app.test_request_context('/'):

            set_session_cookie("boggle_session", [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']])
            game = assemble_game_data(False)
            # check for raw board
            self.assertEqual([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], ['H', 'F', 'H', 'M', 'G'], [
                'E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']], game["board"]["raw"])
            # check for html board
            self.assertIn(
                '<table class="tbl-game" id="boggle-board">', game["board"]["html"])
            self.assertIn(
                "<tr><td>R</td><td>W</td><td>C</td><td>E</td><td>D</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>N</td><td>W</td><td>I</td><td>X</td><td>W</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>H</td><td>F</td><td>H</td><td>M</td><td>G</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>E</td><td>T</td><td>C</td><td>A</td><td>M</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>F</td><td>B</td><td>D</td><td>S</td><td>H</td></tr>", game["board"]["html"])

            # check for cookie data -- nbr_of_plays and high_score should be 0 because
            #  cookies did not exist
            self.assertEqual(0, game["cookie_data"]["nbr_of_plays"])
            self.assertEqual(0, game["cookie_data"]["score_high"])

            # check for correct button data -- id should be 'submit-guess' and
            #  text should be 'Guess'
            self.assertEqual("submit-guess", game["button_attr"]["id"])
            self.assertEqual("Guess", game["button_attr"]["text"])

    def test_assemble_game_data_endgame_nogameoverdata(self):
        with app.test_request_context('/game_over'):

            set_session_cookie("boggle_session", [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']])
            # game_over_data = {"params": {
            #     "score": 900,
            #     "words_valid": "list valid words",
            #     "words_not_on_board": "list of words not on game board",
            #     "words_not_a_word": "list of words that are not words"
            # }}
            # with client.session_transaction() as change_session:
            #     change_session['boggle_gameover'] = game_over_data

            game = assemble_game_data(True)
            # check for raw board
            self.assertEqual([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], ['H', 'F', 'H', 'M', 'G'], [
                'E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']], game["board"]["raw"])
            # check for html board
            self.assertIn(
                '<table class="tbl-game" id="boggle-board">', game["board"]["html"])
            self.assertIn(
                "<tr><td>R</td><td>W</td><td>C</td><td>E</td><td>D</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>N</td><td>W</td><td>I</td><td>X</td><td>W</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>H</td><td>F</td><td>H</td><td>M</td><td>G</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>E</td><td>T</td><td>C</td><td>A</td><td>M</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>F</td><td>B</td><td>D</td><td>S</td><td>H</td></tr>", game["board"]["html"])

            # game over data is needed but it did not exist. game_over route
            #  may have been entered on url instead of by JavaScript.
            # data_is_good is False
            self.assertEqual(False, game["data_is_good"])

    def test_assemble_game_data_endgame_gameoverdata(self):
        with app.test_request_context('/game_over'):

            set_session_cookie("boggle_session", [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']])
            game_over_data = {"params": {
                "score": 900,
                "words_valid": "list valid words",
                "words_not_on_board": "list of words not on game board",
                "words_not_a_word": "list of words that are not words"
            }}
            set_session_cookie("boggle_gameover", game_over_data)

            game = assemble_game_data(True)
            # check for raw board
            self.assertEqual([['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], ['H', 'F', 'H', 'M', 'G'], [
                'E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']], game["board"]["raw"])
            # check for html board
            self.assertIn(
                '<table class="tbl-game" id="boggle-board">', game["board"]["html"])
            self.assertIn(
                "<tr><td>R</td><td>W</td><td>C</td><td>E</td><td>D</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>N</td><td>W</td><td>I</td><td>X</td><td>W</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>H</td><td>F</td><td>H</td><td>M</td><td>G</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>E</td><td>T</td><td>C</td><td>A</td><td>M</td></tr>", game["board"]["html"])
            self.assertIn(
                "<tr><td>F</td><td>B</td><td>D</td><td>S</td><td>H</td></tr>", game["board"]["html"])

            self.assertEqual(900, game["game_over_data"]["score"])
            self.assertEqual("list valid words",
                             game["game_over_data"]["words_valid"])
            self.assertEqual("list of words not on game board",
                             game["game_over_data"]["words_not_on_board"])
            self.assertEqual("list of words that are not words",
                             game["game_over_data"]["words_not_a_word"])

            # cookies were not found so "nbr_of_plays" and "score_high" from the
            #  cookie default to 0
            # The game completed and we verified the game data above. Since the
            #  game completed, "nbr_of_plays" is now 1, 900 is the "score_high"
            #  and score_high_is_new is True
            self.assertEqual(1, game["cookie_data"]["nbr_of_plays"])
            self.assertEqual(900, game["cookie_data"]["score_high"])
            self.assertEqual(True, game["cookie_data"]["score_high_is_new"])

            # we have a new high score. Verify the message
            self.assertEqual("high-score", game["flash"][0]["msg_class"])
            self.assertEqual(
                "&#x1F601; CONGRATULATIONS -- A new high score &#x1F601;", game["flash"][0]["msg_text"])

            # check for correct button data -- id should be 'new-game' and
            #  text should be 'Guess'
            self.assertEqual("new-game", game["button_attr"]["id"])
            self.assertEqual("Start New Game", game["button_attr"]["text"])
            # game over data is needed but it did not exist. game_over route
            #  may have been entered on url instead of by JavaScript.
            # data_is_good is False
            self.assertEqual(True, game["data_is_good"])
