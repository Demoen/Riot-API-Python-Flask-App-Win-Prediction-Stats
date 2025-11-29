from flask import Flask, request, render_template, redirect, session, url_for
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import pandas as pd
from ml_model import WinPredictionModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# API Key
API_KEY = os.getenv('RIOT_API_KEY')
lol_watcher = LolWatcher(API_KEY)
riot_watcher = RiotWatcher(API_KEY)

# Region settings
# Platform routing (e.g., euw1, na1) for Summoner, League, Spectator
PLATFORM_REGION = os.getenv('PLATFORM_REGION', 'euw1')
# Regional routing (e.g., americas, asia, europe) for Account, Match
REGIONAL_ROUTING = os.getenv('REGIONAL_ROUTING', 'europe')

ml_model = WinPredictionModel()

@app.route('/')
def home():
    return render_template('home.html', selected_region='euw')

@app.route('/summoner', methods=['POST'])
def get_summoner():
    riot_id_input = request.form['riot_id']
    selected_region = request.form.get('region', 'euw')
    
    # Region mapping
    region_config = {
        'euw': {'platform': 'euw1', 'routing': 'europe'},
        'eune': {'platform': 'eun1', 'routing': 'europe'},
        'na': {'platform': 'na1', 'routing': 'americas'},
        'kr': {'platform': 'kr', 'routing': 'asia'},
        'br': {'platform': 'br1', 'routing': 'americas'},
        'lan': {'platform': 'la1', 'routing': 'americas'},
        'las': {'platform': 'la2', 'routing': 'americas'},
        'oce': {'platform': 'oc1', 'routing': 'sea'},
        'tr': {'platform': 'tr1', 'routing': 'europe'},
        'ru': {'platform': 'ru', 'routing': 'europe'},
        'jp': {'platform': 'jp1', 'routing': 'asia'},
    }
    
    platform_region = region_config[selected_region]['platform']
    regional_routing = region_config[selected_region]['routing']
    
    if '#' not in riot_id_input:
        return render_template('home.html', error="Invalid Riot ID format. Use Name#Tag", selected_region=selected_region)

    game_name, tag_line = riot_id_input.split('#', 1)
    
    try:
        # Use RiotWatcher for Account API
        account = riot_watcher.account.by_riot_id(regional_routing, game_name, tag_line)
        
        session['puuid'] = account['puuid']
        session['game_name'] = account['gameName']
        session['tag_line'] = account['tagLine']
        session['platform_region'] = platform_region
        session['regional_routing'] = regional_routing
        
        # Get summoner details for profile icon
        summoner = lol_watcher.summoner.by_puuid(platform_region, account['puuid'])
        session['profile_icon_id'] = summoner['profileIconId']
        session['summoner_level'] = summoner['summonerLevel']
        
        return redirect(url_for('match_history'))
    except ApiError as err:
        print(f"DEBUG: API Error encountered: {err}")
        if err.response.status_code == 404:
            return render_template('home.html', error="Riot ID not found.", selected_region=selected_region)
        else:
            return render_template('home.html', error=f"API Error: {err.response.status_code}", selected_region=selected_region)

@app.route('/match_history')
def match_history():
    if 'puuid' not in session:
        return redirect(url_for('home'))

    puuid = session['puuid']
    regional_routing = session.get('regional_routing', REGIONAL_ROUTING)
    
    try:
        # Fetch last 20 Solo Ranked matches (queue=420)
        matches = lol_watcher.match.matchlist_by_puuid(regional_routing, puuid, queue=420, count=20)
        
        return render_template('match_history.html', matches=matches, game_name=session.get('game_name'), tag_line=session.get('tag_line'))
    except ApiError as err:
        return render_template('home.html', error=f"Error fetching matches: {err.response.status_code}", selected_region='euw')

@app.route('/analyze_matches', methods=['POST'])
def analyze_matches():
    if 'puuid' not in session:
        return redirect(url_for('home'))

    puuid = session['puuid']
    regional_routing = session.get('regional_routing', REGIONAL_ROUTING)
    
    # Fetch last 20 Solo Ranked matches (queue=420)
    matches_ids = lol_watcher.match.matchlist_by_puuid(regional_routing, puuid, queue=420, count=20)
    
    matches_data = []
    
    total_matches = 0
    wins = 0
    
    # Initialize aggregated stats with all features from ML model
    aggregated_stats = {feature: 0 for feature in ml_model.feature_columns if feature != 'kda'}
    total_kills = 0
    total_deaths = 0
    total_assists = 0

    for match_id in matches_ids:
        try:
            match_details = lol_watcher.match.by_id(regional_routing, match_id)
            matches_data.append(match_details)
            
            participants = match_details['info']['participants']
            for participant in participants:
                if participant['puuid'] == puuid:
                    total_matches += 1
                    if participant['win']:
                        wins += 1
                    
                    # Aggregate kills, deaths, assists for KDA calculation
                    total_kills += participant.get('kills', 0)
                    total_deaths += participant.get('deaths', 0)
                    total_assists += participant.get('assists', 0)
                    
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
    
    # Calculate average KDA
    averages['kda'] = (total_kills + total_assists) / total_deaths if total_deaths > 0 else total_kills + total_assists
    averages['kills'] = total_kills / total_matches if total_matches > 0 else 0
    averages['deaths'] = total_deaths / total_matches if total_matches > 0 else 0
    averages['assists'] = total_assists / total_matches if total_matches > 0 else 0
    
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

    # Train ML Model (with weighted samples prioritizing recent games)
    train_result = ml_model.train(matches_data, puuid)
    
    # Calculate weighted averages for win probability prediction
    # Most recent game gets 4x weight, games 2-5 get 2x weight, rest get 1x weight
    weighted_averages = ml_model.calculate_weighted_averages(matches_data, puuid)
    
    # Use weighted averages if available, otherwise fall back to regular averages
    prediction_stats = weighted_averages if weighted_averages else averages
    
    # Predict based on weighted averages (prioritizing recent performance)
    win_probability = ml_model.predict_win_probability(prediction_stats)

    # Analyze Player Mood (New Feature)
    player_moods = ml_model.analyze_player_mood(matches_data, puuid)

    # Use latest Data Dragon version (hardcoded for reliability)
    ddragon_version = "14.23.1"

    return render_template(
        'analysis.html',
        total_matches=total_matches,
        win_rate=win_rate,
        averages=averages,
        win_probability=win_probability,
        feature_importance=train_result.get('feature_importance', []),
        category_importance=train_result.get('category_importance', []),
        top_differentiators=train_result.get('top_differentiators', []),
        performance_insights=train_result.get('performance_insights', {}),
        player_moods=player_moods,
        game_name=session.get('game_name'),
        tag_line=session.get('tag_line'),
        profile_icon_id=session.get('profile_icon_id'),
        ddragon_version=ddragon_version
    )

if __name__ == "__main__":
    app.run(debug=True)
