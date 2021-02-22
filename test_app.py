from unittest import TestCase
from app import app, create_game_board
from flask import session
from boggle import Boggle


class FlaskTests(TestCase):

    # TODO -- write tests for every view function / feature!
    def test_create_game_board(self):
        self.assertIs(create_game_board(), {
                      "game_board_raw": [], "game_board_html": ""})

    def test_welcome(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # the table with the board has id = boggle-board
            self.assertIn('<table id="boggle-board">', html)
