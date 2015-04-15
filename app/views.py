from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, mongo
from forms import SearchForm
import common_data as cd
from analyze import analyze_match
import riotwatcher
import json

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
@app.route('/<val>', methods=['GET', 'POST'])
def index(val=None):
    form = SearchForm()
    
    exception = None
    
    if form.validate_on_submit():
        return redirect('/{0}'.format(form.match_id.data))
        
    # Default to a game to make it easier for them
    if val == None:
        ids = []
        try:
            ids = cd.watcher.get_game_ids()
        except Exception:
            pass #Assume the endpoint no longer exists
        if not ids:
            val = 1786135028 #Some random URF game
        else:
            val = ids[-1]

    try:
        match_id = int(val)
    except ValueError:
        # We hope this is a summoner name 
        try:
            summoner = cd.watcher.get_summoners(names=[val])
            summoner_id = summoner.values()[0]["id"]
            matches = cd.watcher.get_match_history(summoner_id)
            match_id = matches["matches"][-1]["matchId"]
        except Exception as e:
            # Several things could have gone wrong. Either way just present an error
            exception = e
        
    if not exception:
        cursor = mongo.db.matches.find({"matchId" : match_id})
        match = None
        if cursor.count() > 0:
            match = cursor[0]
        if not match:
            try:
                match = cd.watcher.get_match(match_id=match_id, include_timeline=True)
                mongo.db.matches.insert(match)
            except Exception as e:
                exception = e
                
    if exception:
        if exception == riotwatcher.error_503 or \
            exception == riotwatcher.error_500:
            error_desc = "server error. Try again later."
        elif exception == riotwatcher.error_404:
            error_desc = "an invalid match or summoner name."
        else:
            error_desc = "unknown error. Please try a different match."
        
        return render_template('error.html', form=form, error=error_desc)
    else:
        cursor = mongo.db.analyses.find({"matchId" : match_id})
        frames = None
        if cursor.count() > 0:
            frames = cursor[0]
        if not frames:
            frames = analyze_match(match)
            frames["matchId"] = match_id
            
            jsonnish = json.dumps(frames)
            frames = json.loads(jsonnish)
            mongo.db.analyses.insert(frames)
        
        player_movement = {pid : frames[str(pid)] for pid in range(1,11)}
        
        return render_template('index.html',
                               frames=player_movement,
                               champs=frames["champs"],
                               hulls=frames["hulls"],
                               form=form)
