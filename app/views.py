from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, mongo
#from .forms import LoginForm, EditForm, PostForm, SearchForm
import common_data as cd
from test import analyze_match

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:match_id>', methods=['GET', 'POST'])
def index(match_id=1786135028):
    # form = PostForm()
    # if form.validate_on_submit():
        # post = Post(body=form.post.data, timestamp=datetime.utcnow(),
                    # author=g.user)
        # db.session.add(post)
        # db.session.commit()
        # flash('Your post is now live!')
        # return redirect(url_for('index'))
    # posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    # TODO: Make sure we're adhering to the rates, and handle errors
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
                           champs=frames["champs"])

# @app.route('/search', methods=['POST'])
# @login_required
# def search():
    # if not g.search_form.validate_on_submit():
        # return redirect(url_for('index'))
    # return redirect(url_for('search_results', query=g.search_form.search.data))


# @app.route('/search_results/<query>')
# @login_required
# def search_results(query):
    # results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    # return render_template('search_results.html',
                           # query=query,
                           # results=results)
