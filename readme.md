# Flask Riot API Analyzer

This is a Python Flask application that uses the Riot API to analyze the match history and provide predictions for League of Legends summoners.

## Prerequisites

Before running the application, make sure you have the following:

- Python 3.x installed on your system.
- Flask and pandas Python packages installed.
- Riot API key (Get it from the [Riot Developer Portal](https://developer.riotgames.com/)).

## Installation

1. Clone the repository or download the files.
2. Install the required Python packages using the following command:

   ```
   pip install flask pandas riotwatcher
   ```

3. Open the `app.py` file and replace `'your_secret_key'` with your own secret key in the line `app.secret_key = 'your_secret_key'`.
4. Replace your Riot API key in the line `lol_watcher = LolWatcher('YOUR RIOT API KEY')`.
5. Save the file.

## Usage

To run the application, execute the following command in your terminal or command prompt:

```
python app.py
```

Once the Flask server is running, open your web browser and visit `http://localhost:5000` to access the application.

## Screenshots

![Screenshot 1](screenshot_1.png)

![Screenshot 2](screenshot_2.png)

![Screenshot 3](screenshot_3.png)

## How It Works

1. The home page (`home.html`) allows you to enter the summoner name.
2. Upon submitting the summoner name, the application retrieves the match history of the summoner using the Riot API and displays it on the `match_history.html` page.
3. The `analyze_matches` route analyzes the match history and calculates various statistics such as average kills, deaths, assists, gold earned, etc.
4. It then performs analysis and prediction based on the aggregated data, using weights assigned to each factor and maximum values for normalization.
5. The calculated probability of winning is displayed on the `analysis.html` page.

## License

This project is licensed under the [MIT License](LICENSE).