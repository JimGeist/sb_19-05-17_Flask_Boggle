from unittest import TestCase
from app import app, create_game_board
from flask import session, request, jsonify
from boggle import Boggle


class FlaskTests(TestCase):

    # @ classmethod
    # def setUpClass(cls):
    #     """ Set up session storage with a game board. """
    #     with app.test_client() as client:
    #         #
    #         game_board = {"game_board_raw": [['T', 'L', 'B', 'H', 'Q'], ['C', 'D', 'L', 'D', 'D'], [
    #             'S', 'Q', 'Y', 'Z', 'N'], ['B', 'U', 'M', 'T', 'L'], ['U', 'W', 'M', 'P', 'V']]}
    #         #     # #session["boggle_session"] = game_board
    #         with client.session_transaction() as change_session:
    #             change_session['boggle_session'] = game_board

    def test_create_game_board(self):
        self.assertDictEqual(create_game_board(), {
            "game_board_raw": [], "game_board_html": ""})

    def test_welcome(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # the table with the board has id = boggle-board
            self.assertIn('<table id="boggle-board">', html)

    def test_check_word(self):
        with app.test_client() as client:
            #
            game_board = {"game_board_raw": [['R', 'W', 'C', 'E', 'D'], ['N', 'W', 'I', 'X', 'W'], [
                'H', 'F', 'H', 'M', 'G'], ['E', 'T', 'C', 'A', 'M'], ['F', 'B', 'D', 'S', 'H']]}
            #
            with client.session_transaction() as change_session:
                change_session['boggle_session'] = game_board

            resp = client.get('/api/check_word?word=FETCH')
            # /api/check_word responds with json
            json_data = resp.get_json()
            # import pdb
            # pdb.set_trace()
            self.assertEqual(json_data, {'result': {'result': 'ok'}})

            resp = client.get('/api/check_word?word=CAMERA')
            json_data = resp.get_json()
            self.assertEqual(
                json_data, {'result': {'result': 'not-on-board'}})

            resp = client.get('/api/check_word?word=HOOBAJOOB')
            json_data = resp.get_json()
            self.assertEqual(
                json_data, {'result': {'result': 'not-word'}})
