# sb_19-05-17_Flask_Boggle

## Flask Boggle 

## Assignment Details
Build the Boggle game using Flask and Python on the backend and JavaScript on the front end. Starter code included Boggle.py which creates a random list of letters to use on the game board. Boggle.py includes the logic to check whether a guess is valid and the reading of the word list with questionable words (really, 'BOX' is not a word!). Kudos too for the occasional leaving out .upper().

The assignment entailed displaying the board using the random letters, submitting a guess to the server, validating the guess by ensuring it is a valid word and is on the game board, keeping score, adding a timer, and adding statistics such high score and number of plays. 


### GAME FLOW 
The site root page, **/** serves as the Boggle game starter page. The starter page has the score, timer, number of previous plays, high score, the game board, and a form to make and submit a word guess.  The timer starts immediately when the page loads. The game is over when the time is up . . and that is where things did get a bit crazy!

The bit of writing items to session storage such as number of plays and high score did not make sense because they would not persist beyond the session. A cookie would allow the score and plays to persist, but pages in the original approach were not exchanged, so how to get a final standings into a cookie? Using the session cookie would have definetly been easier!

When the game is over, a put request is made to **/api/save_game** to save the score and played word lists to session storage. When JavaScript receives the '200 OK' from the put request, the active window location is changed to **/game-over** which causes a reload on the front end with the game_over page.

The game-over route has the score and word lists that were saved to the session cookie by the put request when the game ended. The get request for game-over also provides the cookies with the high score and number of plays. The cookies are updated as necessary, the page is refreshed with the updated number of plays and when necessary, the a new high score, and the page is sent. JavaScript updates the visibility of the word lists and waits for click of the 'Start New Game' button. 

And after looking at the 'solution', well, this one was a serious departure from the school's flow. I did learn from this. I think particularly, this was the first case where JavaScript was used on a multi-page application. 'multi' is a stretch too, since the additional game-over page is the base game page, but the JavaScript had to act differently. A possible enhancement is possibly different JavaScript files for the different pages. 

### TESTING
Tests were created for the route calls -- **/**, **/api/check_word?word=xxxx**, **/api/save_game**, and **/game_over** routes. I need to remember that the tests of the routes are to ensure the response (what the player sees) are correct. 

The supporting functions were also tested. get_raw_game_board(), the function that calls make_board() in Boggle.py was not explicitly tested and I am unsure how since make_board always sends back random lists of letters. Plus, we would know if this funtion failed. The testing was interesting because the proper context was needed -- "RuntimeError: Working outside of application context." setUp and tearDown were not used -- perhaps another time.


### ENHANCEMENTS 
- Display of valid words, not on board, and non-words.
- Use of cookies to remember game state between browser sessions instead of relying solely on the session cookie which only exists for the duration of the tab.
- Best effort to keep business logic out of display logic.


### DIFFICULTIES 
Scope management and conceptual difficulties. And remembering all the keys and varying structures getting slogged around until they were all finally combined into a 'game' dictionary. And the caching is a bit maddening. Private / Incognito helped, it was just shocking to see that JavaScript and css pushes were delayed and sometimes refresh worked, and sometimes not. I got into the habit of launching the debugger just to ensure the proper JavaScript file was present. 
JavaScript was not refactored, mostly because of time already spent on this application. 


### TIMING 
- Too many hours!! But this was one where I did learn from my meanderings off the path. And now I have a renewed dislike for Boggle! Words are stupid . . and why is BOX not a word, really??


