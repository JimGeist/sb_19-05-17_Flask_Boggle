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

async function handleGuess(event) {

    // The player made a guess and clicked the guess button. 
    // Get the word they entered, send it to the server for processing.

    // UI should restrict guess text box to minimum of 2 alphabetical characters 
    //  A-Za-z only (pattern "[A-Za-z]{2,}").

    event.preventDefault();

    // Clear messages of any messages
    $("#messages").text('');

    let guess = $("#guess").val().toUpperCase();

    if (!(wordsPlayed.has(guess))) {
        // first time for the word in guess.
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
            $("#messages").text(wordCheck.message);
        }

    } else {
        // word in guess was already played.
        $("#messages").text(`'${guess}' was already guessed.`);
    }

    // Clear guess
    $("#guess").val("");

}

// waits for the DOM to load
$(function () {

    //event.preventDefault()
    // listener for click of the submit guess button
    $("#submit-guess").on("click", handleGuess);

});