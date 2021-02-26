import pdb
from flask import Flask, request, render_template, redirect, flash, session, make_response, jsonify
from flask import session
from boggle import Boggle

# # debug toolbar
# from flask_debugtoolbar import DebugToolbarExtension

boggle_game = Boggle()


app = Flask(__name__)
app.config['SECRET_KEY'] = "the password is 'P A S S W O R D'"

# # debug toolbar
# debug = DebugToolbarExtension(app)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Session Cookie Setup
# SESSION_COOKIE_SAMESITE='Lax' set due to warning in Firefox:
# Cookie “session” will be soon rejected because it has the “SameSite” attribute set to
# “None” or an invalid value, without the “secure” attribute. To know more about the
# “SameSite“ attribute,
# read https://developer.mozilla.org/docs/Web/HTTP/Headers/Set-Cookie/SameSite
# chrome did not like when SESSION_COOKIE_SECURE was set to True.
# app.config.update(
#     SESSION_COOKIE_SECURE=True,
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Lax'
# )
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)


# Establish the session name for the game. session[GAME_SESSION] holds the game board.
GAME_SESSION = "boggle_session"
# session[GAME_OVER_INFO] holds the score and word lists for the game that just ended.
GAME_OVER_INFO = "boggle_gameover"

# game_session_data = {
#     GAME_SESSION_BOARD_RAW: [<< raw board list returned from make_board() >>]
# }
# Where GAME_SESSION_BOARD_RAW = "game_board_raw"
GAME_SESSION_BOARD_RAW = "game_board_raw"


# Cookie Constants
COOKIE_NBR_PLAYS = "boggle_plays"
COOKIE_HIGH_SCORE = "boggle_high"
COOKIE_DELIM = "<!>"
# COOKIE_NBR_PLAYS = "nbr_plays"
# COOKIE_HIGH_SCORE = "high_score"
COOKIE_EXPIRY = 5184000  # 5,184,000 seconds (60 days) = cookie expiration date


def get_cookie_data():
    """ function reads the cookies COOKIE_NBR_PLAYS and COOKIE_HIGH_SCORE and returns 
        the following object with the data from the cookies:
        {
            COOKIE_NBR_PLAYS: <int, nbr plays from cookie COOKIE_NBR_PLAYS>,
            COOKIE_HIGH_SCORE: <int, high score from cookie COOKIE_HIGH_SCORE>
        }
        where COOKIE_NBR_PLAYS = "boggle_plays" and COOKIE_HIGH_SCORE = "boggle_high"
    """

    cookie_data = {}
    plays = request.cookies.get(COOKIE_NBR_PLAYS, "0")
    high = request.cookies.get(COOKIE_HIGH_SCORE, "0")

    cookie_data[COOKIE_NBR_PLAYS] = int(
        plays) if (plays.isnumeric()) else 0
    cookie_data[COOKIE_HIGH_SCORE] = int(high) if (high.isnumeric()) else 0

    return cookie_data


def update_cookie_data(score_last_game):
    """ update_cookie_data gets the cookie data and:
        - updates the number of plays by one 
        - checks whether a new high score was achieved. 

        Score information for the game that just ended is passed into the 
        function as an integer.

        update_cookie data returns the following dictionary:
        {
            COOKIE_NBR_PLAYS: <int, updated nbr plays from cookie COOKIE_NBR_PLAYS>,
            COOKIE_HIGH_SCORE: <int, updated high score from cookie COOKIE_HIGH_SCORE>
            "new_high_score": <True / False>
        }

    """
    cookie_data = get_cookie_data()

    cookie_data[COOKIE_NBR_PLAYS] = cookie_data[COOKIE_NBR_PLAYS] + 1

    # check for and update high score as necessary
    if (score_last_game > cookie_data[COOKIE_HIGH_SCORE]):
        # We have a new high score
        cookie_data["new_high_score"] = True
        cookie_data[COOKIE_HIGH_SCORE] = score_last_game
    else:
        cookie_data["new_high_score"] = False

    return cookie_data


def create_game_board_html(game_board_raw):
    """ function creates the Boggle game board html from the raw board data.

        function returns a string html table with the letters.

    """

    if(len(game_board_raw) > 0):
        delim = "</td><td>"
        board = ""
        for row in game_board_raw:
            board = board + f"    <tr><td>{(delim).join(row)}</td></tr>\n"
        # we have the rows and data with the proper element tags.
        board = f'  <table class="tbl-game" id="boggle-board">\n{board}\n  </table>'
        return board
    else:
        return ""


def get_game_board_raw():
    """ function calls the boggle_game.make_board for the random letters to use in the game
        board. The raw board is saved in the session since it is needed whenever a word 
        guess requires validation. 

        A separate function converts the random letters to an html table.

    """
    return boggle_game.make_board()


@ app.route("/")
def game_welcome():
    """ Renders a welcome page with the boggle game board.

        ?debug adds cookie and session data to the bottom of the page and sets
        the debug flag to True for the duration of the game / session.
    """

    show_debug_info = request.args.get("debug", False)
    show_debug_info = True if (show_debug_info == "") else False

    game_board_raw = get_game_board_raw()
    game_board_html = create_game_board_html(game_board_raw)

    # save the game_board (raw version) to session storage
    session[GAME_SESSION] = game_board_raw

    cookie_scores = get_cookie_data()
    button_attr = {
        "id": "submit-guess",
        "text": "Guess"
    }

    # game.html is used to deliver the game board at the start of the game
    #  and it is used again when the game is over.
    # At the start of the game, but button id is "submit-guess" and the
    #  words played is an empty dictionary. The dictionary structure is
    #  used instead of passing in 3 arguments to the template.
    # When game.html is used when the game is over, the words_played will
    #  have values.
    words_played = {
        "words_valid": "",
        "words_not_on_board": "",
        "words_not_a_word": ""
    }

    html = render_template("game.html", game_board=game_board_html,
                           button_attr=button_attr,
                           scoring=cookie_scores,
                           words_played=words_played,
                           debug=show_debug_info,
                           session_name=GAME_SESSION,
                           cookie="")

    resp_obj = make_response(html)
    # set_cookie(key (str) {COOKIE_HIGH_SCORE},
    #   value (str) {str(cookie_scores[COOKIE_HIGH_SCORE])},
    #   max_age (Union[datetime.timedelta, int, None] {COOKIE_EXPIRY},
    #   expires: Union[str, datetime.datetime, int, float, None] {None},
    #   path (str) {'/'}, domain (None) {None},
    #   secure (bool) {False},
    #   httponly (bool) = {False},
    #   samesite (Optional [str]) {"Lax"})
    resp_obj.set_cookie(
        COOKIE_HIGH_SCORE, str(cookie_scores[COOKIE_HIGH_SCORE]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")
    resp_obj.set_cookie(
        COOKIE_NBR_PLAYS, str(cookie_scores[COOKIE_NBR_PLAYS]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")
    return resp_obj


@ app.route("/api/check_word")
def check_word():
    """ Checks the word passed in to ensure it is a valid word and that
        the word exists on the current game board.

        The guessed word is passed in as a query string ?word=:guess

        check_word needs to respond with dictionary of {“result”: “ok”}, 
        {“result”: “not-on-board”}, or {“result”: “not-word”}.

    """

    word_guess = request.args.get("word", "")
    word_guess_valid = {}

    # import pdb
    # pdb.set_trace()

    game_board = session[GAME_SESSION]

    # word_guess_valid["result"] = boggle_game.check_valid_word(
    #     game_board[GAME_SESSION_BOARD_RAW], word_guess)
    word_guess_valid["result"] = boggle_game.check_valid_word(
        game_board, word_guess)

    return jsonify({"result": word_guess_valid})


@ app.route("/api/save_game", methods=["PUT"])
def handle_save_game():
    """ takes the score, valid words, not on board, and not a word lists and saves
        them in the session cookie.

        The values are needed when the game_over screen is rendered and sent. The 
        score is needed so we can incorporate the score into the cookie for storage 
        in the browser. 
        It seems klugey, but it is a game, and the scores and number of plays should 
        persist beyond the browser
        session.

    """

    score = request.args.get("score", "")

    game_values = request.get_json()
    # game_values should have dictionary that resembles
    # {params:
    #    {
    #       "score": score from the game that just ended,
    #       "wordsValid": the list of valid words,
    #       "wordsNotOnBoard": the list of words that were not on
    #                           the game board,
    #       "wordsNotWords": list of words that were not words
    #    }
    # The game_values dictionary is saved to the session and it recalled
    #  when the game_over page is rendered.

    print(f"\n\nsave_game: game_values: {game_values}", flush=True)

    session[GAME_OVER_INFO] = game_values

    resp = make_response()

    # import pdb
    # pdb.set_trace()

    return resp


@ app.route("/game_over")
def handle_game_over():
    """ handles the game_over. The 'welcome' template is used, but with different 
        button text. 

        The game_over session has the score and words played for the game that just
        completed. We need to check the score to see whether it is a new high score,
        increase the number of plays counter, and restore the word lists.

    """

    # get the game board from the last game and convert it to html
    game_board = session[GAME_SESSION]
    game_board_html = create_game_board_html(game_board)

    game_data = session[GAME_OVER_INFO]
    cookie_scores = update_cookie_data(game_data["params"]["score"])
    # cookie_scores has the following dictionary:
    #   {
    #     COOKIE_NBR_PLAYS: <updated nbr plays>,
    #     COOKIE_HIGH_SCORE: <high score>
    #     "new_high_score": <True / False>
    #   }
    if (cookie_scores["new_high_score"]):
        flash("CONGRATULATIONS -- A new high score &#x1F601;!", "high-score")

    words_played = game_data["params"]

    button_attr = {
        "id": "new-game",
        "text": "Start New Game"
    }

    # import pdb
    # pdb.set_trace()

    print(f"\ngame_over: game_data: {game_data}", flush=True)
    print(f"game_over: words_played: {words_played}", flush=True)

    html = render_template("game.html", game_board=game_board_html,
                           button_attr=button_attr,
                           scoring=cookie_scores,
                           words_played=words_played,
                           debug=False,
                           session_name=GAME_SESSION,
                           cookie="")

    resp_obj = make_response(html)
    # set_cookie(key (str) {COOKIE_HIGH_SCORE},
    #   value (str) {str(cookie_scores[COOKIE_HIGH_SCORE])},
    #   max_age (Union[datetime.timedelta, int, None] {COOKIE_EXPIRY},
    #   expires: Union[str, datetime.datetime, int, float, None] {None},
    #   path (str) {'/'}, domain (None) {None},
    #   secure (bool) {False},
    #   httponly (bool) = {False},
    #   samesite (Optional [str]) {"Lax"})
    resp_obj.set_cookie(
        COOKIE_HIGH_SCORE, str(cookie_scores[COOKIE_HIGH_SCORE]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")
    resp_obj.set_cookie(
        COOKIE_NBR_PLAYS, str(cookie_scores[COOKIE_NBR_PLAYS]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")

    # import pdb
    # pdb.set_trace()
    return resp_obj
