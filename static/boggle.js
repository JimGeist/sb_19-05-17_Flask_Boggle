const ROOT_GAME = "http://127.0.0.1:5000"
const ROOT_API = `${ROOT_GAME}/api/`

let score = 0;

const wordsPlayed = new Set();

const checkResults = {
    "ok": {
        "idSuffix": "valid",
        "scoreAdjustor": 1,
        "comma": ""
    },
    "not-on-board": {
        "idSuffix": "not-on-board",
        "scoreAdjustor": -1,
        "comma": ""
    },
    "not-word": {
        "idSuffix": "not-a-word",
        "scoreAdjustor": -1,
        "comma": ""
    }
}

async function gameOver() {

    // postMessage("< < <  GAME   OVER  > > >", "game-over");
    // $("#messages").removeClass("error").addClass("game-over").text("< < <  GAME   OVER  > > >");
    //$("#messages").text("< < <  GAME   OVER  > > >");

    $("#submit-guess").prop("disabled", true);

    // save the score is session storage
    // remember words that were played.
    const wordsValid = $("#words-valid").text();
    const wordsNotOnBoard = $("#words-not-on-board").text();
    const wordsNotWords = $("#words-not-a-word").text();
    await saveGame(score, wordsValid, wordsNotOnBoard, wordsNotWords);

    // game over sends the final game screen. Sending the screen also sends cookies with the 
    //  high score and number of plays. This game's score was sent to the server already via
    //  setScore.



    window.location = `${ROOT_GAME}/game_over`

    // score = score;

}


/**
 * startTimer is a timer function. The code was found at 
 *  https://stackoverflow.com/questions/20618355/the-simplest-possible-javascript-countdown-timer
 * The code was changed by adding logic to end the timer after one iteration. When the timer ends,
 *  instead of restarting, the interval is cleared and the gameOver function is called.  
 * 
 * @param {*} duration - the length of the timer in seconds 
 * @param {*} display  - the dom element that will receives the minutes and seconds for the timer
 */
function startTimer(duration, display) {

    // from https://stackoverflow.com/questions/20618355/the-simplest-possible-javascript-countdown-timer

    let start = Date.now();
    let diff;
    let minutes;
    let seconds;

    let throughOnce = false;

    function timer() {
        // get the number of seconds that have elapsed since 
        // startTimer() was called
        diff = duration - (((Date.now() - start) / 1000) | 0);

        // does the same job as parseInt truncates the float
        minutes = (diff / 60) | 0;
        seconds = (diff % 60) | 0;

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (diff <= 0) {
            clearInterval(intervalHandle);
            display.textContent = "00:00";
            gameOver();
        }

    };
    // we don't want to wait a full second before the timer starts
    timer();
    let intervalHandle = setInterval(timer, 1000);

}


async function saveGame(inScore, wordsValid, wordsNotOnBoard, wordsNotWords) {



    /** function synopsis:
     *   makes a put request to save the score in session storage. No data is expected back
     *   
     */

    // const res = await axios.put(`${ROOT_API}set_score`, {
    //     params: {
    //         "score": inScore,
    //         "wordsValid": JSON.stringify(wordsValid),
    //         "wordsNotOnBoard": JSON.stringify(wordsNotOnBoard),
    //         "wordsNotWords": JSON.stringify(wordsNotWords)
    //     }
    // });


    const res = await axios.put(`${ROOT_API}save_game`, {
        params: {
            "score": inScore,
            "words_valid": wordsValid,
            "words_not_on_board": wordsNotOnBoard,
            "words_not_a_word": wordsNotWords
        }
    });

}


async function checkWord(guess) {

    /** function synopsis:
     *   function calls the server to check the guessed word.
     * 
     *   Server will reply with a JSON response which contains either a 
     *   dictionary of {“result”: “ok”}, {“result”: “not-on-board”}, or {“result”: “not-word”}.
     *   
     *   ROOT_API = http://127.0.0.1/api/
     *    check word route: check_word?word=:guessed_word
     * 
     *   {
     *      statusIsOK: true when OK, false when status was not 200
     *      result: result from response or ERROR
     *      message: the error message
     *   }
     */

    results_out = {
        "statusIsOK": null,
        "result": null,
        "message": null
    }

    try {
        const res = await axios.get(`${ROOT_API}check_word?word=${guess}`);

        if (res.status === 200) {
            results_out["statusIsOK"] = true;
            results_out["result"] = res.data.result["result"];
        } else {
            results_out["statusIsOK"] = false;
            results_out["message"] = `Status was not 200 (OK). response code = ${res.status}. Word to check: '${guess}'`;
        }

    } catch (e) {
        results_out["statusIsOK"] = false;
        results_out["message"] = `An unexpected error (${e.message}) occurred while connecting to game server. Word to check: '${guess}'`;
    }

    return results_out;

}


function postMessage(inMsg, inClass) {

    // remove all classes
    $("#messages").removeClass();
    $("#messages").addClass(inClass).text(inMsg);

}


function guessIsValid(guess) {

    // The player made a guess, but is the guess valid?
    // Guessed word should be at least 3 characters, no spaces between letters. Leading and 
    //  trailing spaces are removed.
    // Guess should not have been played aready.

    // UI should restricts guess text box to minimum of 3 alphabetical characters 
    //  A-Za-z only (pattern "[A-Za-z]{3,}"), and it worked in straight html. Not so much
    //  once JavaScript is attached.

    // clear messages
    postMessage("", "");

    // regex validator - from beginning, ^, a-z, A-Z, minimum of 3 characters.

    let validator = new RegExp("^[a-zA-Z]{3,}")

    if (validator.test(guess)) {
        if (wordsPlayed.has(guess)) {
            // word was already played / was found in wordPlayed list
            postMessage(`'${guess}' was already guessed.`, "error");

            return false;
        } else {
            // guess is not in the wordPlayed list
            return true;
        }

    } else {
        postMessage(`'${guess}' must be at least 3 alphabetical characters (a - z, A - Z) without embedded spaces.`, "error");
        return false;
    }

}

async function handleGuess(event) {

    // The player made a guess and clicked the guess button. 
    // Get the word they entered, send it to the server for processing.


    event.preventDefault();

    let guess = $("#guess").val().toUpperCase().trim();

    if (guessIsValid(guess)) {

        // first time for the word in guess (list was checked in guessIsValid).
        wordsPlayed.add(guess);

        wordCheck = await checkWord(guess);

        if (wordCheck.statusIsOK) {

            $("#all-guesses").removeClass("hidden");

            let idSuffix = checkResults[wordCheck.result]["idSuffix"]

            $(`#list-${idSuffix}`).removeClass("hidden");
            $(`#words-${idSuffix}`).text(`${$(`#words-${idSuffix}`).text()}${checkResults[wordCheck.result]["comma"]}${guess}`);

            score = score + (guess.length * checkResults[wordCheck.result]["scoreAdjustor"]);
            $("#score").text(`Score: ${score}`);
            checkResults[wordCheck.result]["comma"] = ", ";

        } else {
            // an error occurred. display the message.
            //$("#messages").text(wordCheck.message);
            postMessage(wordCheck.message, "error")
        }

    }

    // Clear guess
    $("#guess").val("");

}

function wordListVisibility() {

    // Determines which word lists have values should not be hidden.
    for (obj_key of Object.keys(checkResults)) {
        // checkResults list aided in the loading of the word lists during
        //  game play. It has the keys for the three list types and the 
        //  object contains the pieces to access each html page element.
        let idSuffix = checkResults[obj_key]["idSuffix"]
        if ($(`#words-${idSuffix}`).text().length > 0) {
            $(`#list-${idSuffix}`).removeClass("hidden");

            // Make the all-guesses div visible.
            $("#all-guesses").removeClass("hidden");
        }
    }

}

async function newGame() {

    window.location = ROOT_GAME;

}


// waits for the DOM to load
$(function () {

    // Start the timer only when there is a button with id "submit-guess" on the page
    if ($("#submit-guess").length === 1) {
        let duration = 60 * 0.5;

        const display = document.querySelector('#time');
        startTimer(duration, display);

        // listener for click of the submit guess button
        $("#submit-guess").on("click", handleGuess);

    } else {

        if ($("#new-game").length === 1) {
            // We have the 'game over' page displayed. 
            // The page has the word list added, but the lists are hidden. We need
            //  to make the proper lists visible. The guess input box needs to get
            //  disabled as well. Finally, we need to add game over!
            wordListVisibility();
            postMessage("< < <  GAME   OVER  > > >", "game-over");

            // // Disable the input
            // $("#guess").prop("disabled", true);

            // listener for click of the submit guess button
            $("#new-game").on("click", newGame);
        }

    }

});