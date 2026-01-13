from flask import Flask, redirect, url_for, session, request, jsonify, render_template, flash
from markupsafe import Markup
from flask_oauthlib.client import OAuth
from bson.objectid import ObjectId

import pprint
import os
import time
import pymongo
import sys
 
app = Flask(__name__)

app.debug = False #Change this to False for production
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done debugging

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)
oauth.init_app(app) #initialize the app to be able to make requests for user information

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

#Connect to database
url = os.environ["MONGO_CONNECTION_STRING"]
client = pymongo.MongoClient(url)
db = client[os.environ["MONGO_DBNAME"]]
collection = db['Wins'] #TODO: put the name of the collection here

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#context processors run before templates are rendered and add variable(s) to the template's context
#context processors must return a dictionary
#this context processor adds the variable logged_in to the conext for all templates
@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')

#redirect to GitHub's OAuth page and confirm callback URL
@app.route('/login')
def login(): 
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out.')
    return redirect('/')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        flash('Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args), 'error')      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            flash('You were successfully logged in as ' + session['user_data']['login'] + '.')
        except Exception as inst:
            session.clear()
            print(inst)
            flash('Unable to login, please try again.', 'error')
    return render_template('page1.html')


@app.route('/page1')
def renderPage1():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
    else:
        user_data_pprint = '';
    return render_template('page1.html',dump_user_data=user_data_pprint)
    
@app.route('/play', methods=['GET', 'POST'])
def play_button():
    return redirect(url_for('renderPage2'))

@app.route('/page2', methods=['GET', 'POST'])
def renderPage2():
    if request.method == 'POST':
            user = session['user_data']
            post = {
                    "td1": request.form['td1'],
                    "td2": request.form['td2'],
                    "td3": request.form['td3'],
                    "td4": request.form['td4'],
                    "td5": request.form['td5'],
                    "td6": request.form['td6'],
                    "td7": request.form['td7'],
                    "td8": request.form['td8'],
                    "td9": request.form['td9'],
                    }
            collection.insert_one(post)
    return render_template('page2.html')
    
    
    
# the pymongo.DESCENDING checks the newest doc    
doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])

# Win combinations
win_combinations = [
    ("td1", "td2", "td3"), ("td4", "td5", "td6"), ("td7", "td8", "td9"), # Rows
    ("td1", "td4", "td7"), ("td2", "td5", "td8"), ("td3", "td6", "td9"), # Columns
    ("td1", "td5", "td9"), ("td3", "td5", "td7")                       # Diagonals
]

def check_winner(doc):
    for p1, p2, p3 in win_combinations:# the p's mean position
        v1 = (doc.get(p1) or "").lower()
        v2 = (doc.get(p2) or "").lower()
        v3 = (doc.get(p3) or "").lower()

        #Each value is checked in order to find and make sure that is a win
        if v1 == v2 == v3 and v1 in ["x", "o"]:
            return f"Player {v1.upper()} wins!"
            
    return "No winner found."

print(check_winner(doc))    
'''
@app.route('/wins')
def player_wins():
if 'winner' in session and session['winner']in['X','O']:
collection.update_one(
{'_id: 1'},
{"$inc":{f"{session['winner']}_wins":1}}
)
session.pop('winner')
x_wins = collection.find_one({'_id': 1}) or {'x_wins': 0}
o_wins = collection.find_one({'_id': 1}) or {'o_wins': 0}

return render_template('page1.html, x_wins=x_wins, o_wins=o_wins')

'''

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']


if __name__ == '__main__':
    app.run()