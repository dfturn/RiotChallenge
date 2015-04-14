from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, mongo
from forms import SearchForm
import common_data as cd
from test import analyze_match

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/<val>', methods=['GET', 'POST'])
def index(val=1786135028):
    form = SearchForm()
    
    if form.validate_on_submit():
        return redirect('/{0}'.format(form.match_id.data))

    try:
        match_id = int(val)
    except ValueError:
        # We hope this is a summoner name 
        try:
            summoner = cd.watcher.get_summoners(names=[val])
            summoner_id = summoner.values()[0]["id"]
            matches = cd.watcher.get_match_history(summoner_id)
            match_id = matches["matches"][-2]["matchId"] # TODO: Make -1
        except Exception:
            # Several things could have gone wrong. Either way just present an error TODO
            pass
        
    cursor = mongo.db.matches.find({"matchId" : match_id})
    match = None
    if cursor.count() > 0:
        match = cursor[0]
    if not match:
        match = cd.watcher.get_match(match_id=match_id, include_timeline=True)
        mongo.db.matches.insert(match)
        
    frames = analyze_match(match)
    player_movement = {pid : frames[pid] for pid in range(1,11)}
    
    return render_template('index.html',
                           title=match_id,
                           frames=player_movement,
                           champs=frames["champs"],
                           hulls=frames["hulls"],
                           form=form)
