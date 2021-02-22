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
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# Establish the session name for the game. session[GAME_SESSION] holds the game board,
#  words, and score.
GAME_SESSION = "boggle_session"

# game_session_data = {
#     GAME_SESSION_BOARD_RAW: [<< raw board list returned from make_board() >>],
#     GAME_SESSION_BOARD_HTML: "<< html table version of the raw board >>"
# }
# Where GAME_SESSION_BOARD_RAW = "game_board_raw" and GAME_SESSION_BOARD_HTML = "game_board_html"
GAME_SESSION_BOARD_RAW = "game_board_raw"
GAME_SESSION_BOARD_HTML = "game_board_html"


def create_game_board():
    """ function creates the Boggle game board and returns 
        {
            game_board_raw: [multidimensional list returned by boggle_game.make_board()],
            game_board_html: "text html equivalent of raw board data"
        }
    """
    game_board_out = {
        GAME_SESSION_BOARD_RAW: boggle_game.make_board(),
        GAME_SESSION_BOARD_HTML: ""
    }
    if(len(game_board_out["game_board_raw"]) > 0):
        delim = "</td><td>"
        board = ""
        for row in game_board_out[GAME_SESSION_BOARD_RAW]:
            board = board + f"    <tr><td>{(delim).join(row)}</td></tr>\n"
        # we have the rows and data with the proper element tags.
        board = f'  <table id="boggle-board">\n{board}\n  </table>'
        game_board_out[GAME_SESSION_BOARD_HTML] = board

    return game_board_out


@ app.route("/")
def game_welcome():
    """ Renders a welcome page with the boggle game board.

        ?debug adds cookie and session data to the bottom of the page and sets
        the debug flag to True for the duration of the game / session.
    """

    show_debug_info = request.args.get("debug", False)
    show_debug_info = True if (show_debug_info == "") else False

    game_board = create_game_board()

    # save the game_board (raw and html versions) to session storage
    session[GAME_SESSION] = game_board

    return render_template("welcome.html", game_board=game_board["game_board_html"],
                           button_text="Guess",
                           debug=show_debug_info,
                           session_name=GAME_SESSION,
                           cookie="")


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
        game_board[GAME_SESSION_BOARD_RAW], word_guess)

    # print(f"\n\ncheck_word(): guessed word = {word_guess}", flush=True)
    # print(
    #     f"check_word(): game board = {game_board[GAME_SESSION_BOARD_RAW]}", flush=True)
    # print(
    #     f"check_word(): word_guess_valid = {word_guess_valid}", flush=True)
    # print(
    #     f"check_word(): jsonify(word_guess_valid) = {jsonify(word_guess_valid)}\n\n", flush=True)

    return jsonify({"result": word_guess_valid})
