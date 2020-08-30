# webpipeliner

This project is a web frontend of the GUI version of [https://github.com/CCBR/Pipeliner](Pipeliner).

The web app is in the project folder.

Weekly progress reports are in the progress folder.

To run the app:
1. Clone the repo
2. `cd webpipeliner`
3. (Optional)
    1. create virtual environment: `python3 -m venv <path to your venv>`
    2. then activate: `source <path to your venv>/bin/activate`
3. Install requirements.txt: `pip install -r requirements.txt`
4. `flask run` (no debug) or `py webpipeliner.py` (debug)
5. Open [http://localhost:5000](http://localhost:5000)
6. Have fun!
7. Ctrl-C in terminal to quit (and `deactivate` if you used a virtual env)

## Screenshots
### About page
![The about page](/screenshots/about.png)
### Basic information page
![The basics page](/screenshots/basics.png)
### Specific details page
![The details page](/screenshots/details.png)
### After submitting
![The about page after submitting](/screenshots/submit.png)