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


# Cookie Name Constants -- these are the visible names of the cookies in browser storage
COOKIE_NBR_PLAYS = "boggle_plays"
COOKIE_HIGH_SCORE = "boggle_high"
COOKIE_EXPIRY = 5184000  # 5,184,000 seconds (60 days) = cookie expiration date

# Dictionary Key Name Constants - constants created for frequently used keys
G_CK = "cookie_data"
G_CK_PLAYS = "nbr_of_plays"
G_CK_SCORE_HIGH = "score_high"
G_CK_HIGH_IS_NEW = "score_high_is_new"

G_GO = "game_over_data"
G_GO_SCORE = "score"
G_GO_WDS_VALID = "words_valid"
G_GO_WDS_NOT_ON_BOARD = "words_not_on_board"
G_GO_WDS_NOT_WORD = "words_not_a_word"


def get_cookie_data():
    """ function reads the cookies COOKIE_NBR_PLAYS and COOKIE_HIGH_SCORE and returns 
        the following object with the data from the cookies:
        {
            G_CK_PLAYS: <int, nbr plays from cookie COOKIE_NBR_PLAYS>,
            G_CK_SCORE_HIGH: <int, high score from cookie COOKIE_HIGH_SCORE>
        }
        where G_CK_PLAYS = "nbr_of_plays" and G_CK_SCORE_HIGH = "score_high"
    """

    cookie_data = {}
    plays = request.cookies.get(COOKIE_NBR_PLAYS, "0")
    high = request.cookies.get(COOKIE_HIGH_SCORE, "0")

    cookie_data[G_CK_PLAYS] = int(plays) if (plays.isnumeric()) else 0
    cookie_data[G_CK_SCORE_HIGH] = int(high) if (high.isnumeric()) else 0

    return cookie_data


def update_cookie_data(score_last_game):
    """ update_cookie_data gets the cookie data and:
        - updates the number of plays by one 
        - checks whether a new high score was achieved. 

        Score information for the game that just ended is passed into the 
        function as an integer.

        update_cookie data returns the following dictionary:
        {
            G_CK_PLAYS: <int, updated nbr plays from cookie COOKIE_NBR_PLAYS>,
            G_CK_SCORE_HIGH: <int, updated high score from cookie COOKIE_HIGH_SCORE>
            G_CK_HIGH_IS_NEW: <True / False>
        }

    """
    cookie_data = get_cookie_data()

    cookie_data[G_CK_PLAYS] = cookie_data[G_CK_PLAYS] + 1

    # check for and update high score as necessary
    if (score_last_game > cookie_data[G_CK_SCORE_HIGH]):
        # We have a new high score
        cookie_data[G_CK_HIGH_IS_NEW] = True
        cookie_data[G_CK_SCORE_HIGH] = score_last_game
    else:
        cookie_data[G_CK_HIGH_IS_NEW] = False

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


def assemble_game_data(for_game_end):
    """ function assembles the data needed for the game board in one dictionary. The 
        dictionary may be composed of sub-dictionairies, but the goal is to have it 
        all in one place.

        for_game_end, True / False, is True when the data is for the end of the 
        game because values from the game_over_info session are required and cookie
        logic is an update when end of game.
    """

    # create an empty game dictionary called game. board, cookie_data, and button_attr
    #  sub dictionaries are created in the game dictionary since they are needed for
    #  game start and game end pages.
    game = {
        "board": {},
        G_CK: {},
        "button_attr": {}
    }

    if (for_game_end):
        # get the raw game board from the session, convert the raw game board to html
        #  and save both values in the board sub-dictionary.
        board_raw = session[GAME_SESSION]
        game["board"] = {
            "raw": board_raw,
            "html": create_game_board_html(board_raw)
        }

        game_over_data = session[GAME_OVER_INFO]
        game[G_GO] = game_over_data["params"]

        # note that cookie values are integers, not string. They are converted to integer
        #  in get_cookie_data
        game[G_CK] = update_cookie_data(game[G_GO][G_GO_SCORE])
        # cookie_scores has the following dictionary:
        #   {
        #     COOKIE_NBR_PLAYS: <updated nbr plays>,
        #     COOKIE_HIGH_SCORE: <high score>
        #     "new_high_score": <True / False>
        #   }

        if (game[G_CK][G_CK_HIGH_IS_NEW]):
            # add a message for flash messages to the dictionary. Note that since this is the
            #  first occurrence of a flash message, the flash list and sub-dictionaries are
            #  also created at this point.
            game["flash"] = []
            game["flash"].append({
                "msg_text": "&#x1F601; CONGRATULATIONS -- A new high score &#x1F601;",
                "msg_class": "high-score"
            })

        game["button_attr"] = {
            "id": "new-game",
            "text": "Start New Game"
        }
    else:
        # get the raw game board from the session, convert the raw game board to html
        #  and save both values in the board sub-dictionary.
        board_raw = boggle_game.make_board()
        game["board"] = {
            "raw": board_raw,
            "html": create_game_board_html(board_raw)
        }
        # save the game_board (raw version) to session storage
        session[GAME_SESSION] = board_raw

        # create an empty structure. This structure is accessed when populating the
        #  lists of words. The key values are not needed because get() is used in
        #  the template.
        game[G_GO] = {}

        game[G_CK] = get_cookie_data()
        # cookie_scores has the following dictionary:
        #   {
        #     COOKIE_NBR_PLAYS: <updated nbr plays>,
        #     COOKIE_HIGH_SCORE: <high score>
        #   }

        game["button_attr"] = {
            "id": "submit-guess",
            "text": "Guess"
        }

    return game


@ app.route("/")
def game_welcome():
    """ Renders a welcome page with the boggle game board.

        ?debug adds cookie and session data to the bottom of the page and sets
        the debug flag to True for the duration of the game / session.
    """

    show_debug_info = request.args.get("debug", False)
    show_debug_info = True if (show_debug_info == "") else False

    game = assemble_game_data(False)

    html = render_template("game.html", game_board=game["board"]["html"],
                           button_attr=game["button_attr"],
                           scoring=game[G_CK],
                           score=0,
                           words_played=game[G_GO],
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
        COOKIE_HIGH_SCORE, str(game[G_CK][G_CK_SCORE_HIGH]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")
    resp_obj.set_cookie(
        COOKIE_NBR_PLAYS, str(game[G_CK][G_CK_PLAYS]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")
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

    game_board = session[GAME_SESSION]

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

    game_values = request.get_json()
    # game_values should have dictionary that resembles
    # {params:
    #    {
    #       "score": score from the game that just ended,
    #       "words_valid": the list of valid words,
    #       "words_not_on_board": the list of words that were not on
    #                           the game board,
    #       "words_not_a_word": list of words that are not words
    #    }
    # The game_values dictionary is saved to the session and it recalled when
    #  the game_over page is rendered. The dictionary key names should align
    #  to the id's of list elements in page.html using a _ instead of a -.

    session[GAME_OVER_INFO] = game_values

    # make_response() can get called without arguments
    resp = make_response()

    return resp


@ app.route("/game_over")
def handle_game_over():
    """ handles the game_over. The 'welcome' template is used, but with different 
        button text. 

        The game_over session has the score and words played for the game that just
        completed. We need to check the score to see whether it is a new high score,
        increase the number of plays counter, and restore the word lists.

    """

    # assemble information needed for the game over. The goal is to have one
    #  dictionary with the data needed returned to handle_game_over instead of
    #  having a bunch of mini-dictionaries with keys that are really getting
    #  hard to keep track of and remember.
    # create_game_object
    # get the game board from the last game and convert it to html
    game = assemble_game_data(True)
    if (game[G_CK][G_CK_HIGH_IS_NEW]):
        for msg_data in game["flash"]:
            flash(msg_data["msg_text"], msg_data["msg_class"])

    html = render_template("game.html", game_board=game["board"]["html"],
                           button_attr=game["button_attr"],
                           score=game[G_GO][G_GO_SCORE],
                           scoring=game[G_CK],
                           words_played=game[G_GO],
                           debug=False,
                           session_name="",
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
        COOKIE_NBR_PLAYS, str(game[G_CK][G_CK_PLAYS]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")

    if (game[G_CK][G_CK_HIGH_IS_NEW]):
        # we have a new high score. Set a cookie with the update high score.
        resp_obj.set_cookie(
            COOKIE_HIGH_SCORE, str(game[G_CK][G_CK_SCORE_HIGH]), COOKIE_EXPIRY, None, "/", None, False, False, "Lax")

    return resp_obj
