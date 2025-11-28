from flask import Flask, request, render_template, redirect, session, url_for
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import pandas as pd
from ml_model import WinPredictionModel

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key here

# API Key
API_KEY = ''
lol_watcher = LolWatcher(API_KEY)
riot_watcher = RiotWatcher(API_KEY)

# Region settings
# Platform routing (e.g., euw1, na1) for Summoner, League, Spectator
PLATFORM_REGION = 'euw1' 
# Regional routing (e.g., americas, asia, europe) for Account, Match
REGIONAL_ROUTING = 'europe'

ml_model = WinPredictionModel()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/summoner', methods=['POST'])
def get_summoner():
    riot_id_input = request.form['riot_id']
    
    if '#' not in riot_id_input:
        return render_template('home.html', error="Invalid Riot ID format. Use Name#Tag")

    game_name, tag_line = riot_id_input.split('#', 1)
    
    try:
        # Use RiotWatcher for Account API
        account = riot_watcher.account.by_riot_id(REGIONAL_ROUTING, game_name, tag_line)
        
        session['puuid'] = account['puuid']
        session['game_name'] = account['gameName']
        session['tag_line'] = account['tagLine']
        
        # Get summoner details for profile icon
        summoner = lol_watcher.summoner.by_puuid(PLATFORM_REGION, account['puuid'])
        session['profile_icon_id'] = summoner['profileIconId']
        session['summoner_level'] = summoner['summonerLevel']
        
        return redirect(url_for('match_history'))
    except ApiError as err:
        print(f"DEBUG: API Error encountered: {err}")
        if err.response.status_code == 404:
            return render_template('home.html', error="Riot ID not found.")
        else:
            return render_template('home.html', error=f"API Error: {err.response.status_code}")

@app.route('/match_history')
def match_history():
    if 'puuid' not in session:
        return redirect(url_for('home'))

    puuid = session['puuid']
    try:
        # Fetch last 20 Solo Ranked matches (queue=420)
        matches = lol_watcher.match.matchlist_by_puuid(REGIONAL_ROUTING, puuid, queue=420, count=20)
        
        return render_template('match_history.html', matches=matches, game_name=session.get('game_name'), tag_line=session.get('tag_line'))
    except ApiError as err:
        return render_template('home.html', error=f"Error fetching matches: {err.response.status_code}")

@app.route('/analyze_matches', methods=['POST'])
def analyze_matches():
    if 'puuid' not in session:
        return redirect(url_for('home'))

    puuid = session['puuid']
    # Fetch last 20 Solo Ranked matches (queue=420)
    matches_ids = lol_watcher.match.matchlist_by_puuid(REGIONAL_ROUTING, puuid, queue=420, count=20)
    
    matches_data = []
    
    total_matches = 0
    wins = 0
    
    # Initialize aggregated stats with all features from ML model
    aggregated_stats = {feature: 0 for feature in ml_model.feature_columns}

    for match_id in matches_ids:
        try:
            match_details = lol_watcher.match.by_id(REGIONAL_ROUTING, match_id)
            matches_data.append(match_details)
            
            participants = match_details['info']['participants']
            for participant in participants:
                if participant['puuid'] == puuid:
                    total_matches += 1
                    if participant['win']:
                        wins += 1
                    
                    for feature in aggregated_stats:
                        if feature in participant:
                            aggregated_stats[feature] += participant[feature]
                        elif 'challenges' in participant and feature in participant['challenges']:
                            aggregated_stats[feature] += participant['challenges'][feature]
                    break
        except ApiError:
            continue

    # Averages
    averages = {k: (v / total_matches if total_matches > 0 else 0) for k, v in aggregated_stats.items()}
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

    # Train ML Model
    train_result = ml_model.train(matches_data, puuid)
    
    # Predict based on averages
    win_probability = ml_model.predict_win_probability(averages)

    # Use latest Data Dragon version (hardcoded for reliability)
    ddragon_version = "14.23.1"

    return render_template(
        'analysis.html',
        total_matches=total_matches,
        win_rate=win_rate,
        averages=averages,
        win_probability=win_probability,
        feature_importance=train_result.get('feature_importance', []),
        game_name=session.get('game_name'),
        tag_line=session.get('tag_line'),
        profile_icon_id=session.get('profile_icon_id'),
        ddragon_version=ddragon_version
    )

if __name__ == "__main__":
    app.run(debug=True)
