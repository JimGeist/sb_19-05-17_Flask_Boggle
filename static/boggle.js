const API_ROOT = "http://127.0.0.1:5000/api/"

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

    postMessage("< < <  GAME   OVER  > > >", "game-over");
    // $("#messages").removeClass("error").addClass("game-over").text("< < <  GAME   OVER  > > >");
    //$("#messages").text("< < <  GAME   OVER  > > >");

    $("#submit-guess").prop("disabled", true);

    await setScore(score);

    score = score;

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
            // add one second so that the count down starts at the full duration
            // example 05:00 not 04:59
            start = Date.now() + 1000;
            throughOnce = true;
        } else {
            if (throughOnce) {
                display.textContent = "00:00";
                clearInterval(intervalHandle);
                gameOver();
            }
        }

    };
    // we don't want to wait a full second before the timer starts
    timer();
    let intervalHandle = setInterval(timer, 1000);
    // timeRemaining = false;
}


async function setScore(inScore) {

    /** function synopsis:
     *   makes a ??post request?? to save the score??
     */

    results_out = {
        "statusIsOK": null,
        "result": null,
        "message": null
    }

    try {
        const res = await axios.put(`${API_ROOT}game_over?score=${score}`);

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


async function checkWord(guess) {

    /** function synopsis:
     *   function calls the server to check the guessed word.
     * 
     *   Server will reply with a JSON response which contains either a 
     *   dictionary of {“result”: “ok”}, {“result”: “not-on-board”}, or {“result”: “not-word”}.
     *   
     *   API_ROOT = http://127.0.0.1/api/
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
        const res = await axios.get(`${API_ROOT}check_word?word=${guess}`);

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
            console.log(`handleGuess: statusIsOK: ${wordCheck.statusIsOK}, result: ${wordCheck.result}.`)

            $("#all-guesses").removeClass("hidden");

            let sfx = checkResults[wordCheck.result]["idSuffix"]

            $(`#list-${sfx}`).removeClass("hidden");
            $(`#words-${sfx}`).text(`${$(`#words-${sfx}`).text()}${checkResults[wordCheck.result]["comma"]}${guess}`);

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

// waits for the DOM to load
$(function () {

    let duration = 60 * 0.25;

    const display = document.querySelector('#time');
    startTimer(duration, display);

    // listener for click of the submit guess button
    $("#submit-guess").on("click", handleGuess);

});