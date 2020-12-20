#FLASK_APP=chat.py 
#flask run 

import json
from datetime import datetime
from flask import Flask, render_template, request, g, redirect, url_for, session, flash, abort

app = Flask(__name__) #initialize flask app

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default',
))
app.config.from_envvar('CHAT_SETTINGS', silent=True)

#create username and password database 
user_info = {} 
#create list for messages 
chat_room_info = {}
allChatRooms = {}
global currentChatRoom 
currentChatRoom = ""
current_chat_room_info = {}



#that g that we imported above is a variable that exists within the application scope
#g gives us a global location within all of our functions to store information
#global data DURING request, not during sessions
@app.before_request
def before_request():
	g.user = None #create user and set it to none
	if 'username' in session: #is the user logged in?
		username = session['username']
		g.user = username
	else:
		g.user = None
		#pull the user who is logged in and put it in g.user


@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if 'username' in session: #if the user is logged in.. send them to homepage
        return redirect(url_for('homepage'))
    error = None #track error 
    if request.method == 'POST': #you want to send something to the server
        user = request.form['username'] #get their username
        password = request.form['password'] #get their password 
        if user not in user_info: #if it doesn't match any in the database 
            error = 'This username is not in the system' 
        #check if the password matches 
        elif user_info[user]!=password: #check their password
            error = 'Invalid password' #doesn't match 
        else: 
            flash('You were logged in')
            session['username']=request.form['username'] #log them in
            return redirect(url_for('homepage')) #send them to the home page
    return render_template('login.html', error=error) #print their error 

@app.route('/registration', methods=['GET', 'POST'])
def register():
	if 'username' in session: #if user is logged in, go to their timeline 
		return redirect(url_for('homepage'))
	error = None #keep track of error 
	if request.method == 'POST':
		if not request.form['username']: #if the user didn't enter a username
			error = 'You did not enter a username, enter one to register!'
		elif not request.form['password']: #if the user didn't enter a password
			error = 'You did not enter a password, enter one to register!'
		elif request.form['username'] in user_info: #if the username is already taken
			error = 'The username is already taken'
		else:
			flash('Successfully registered, now log in!')
			user_info[request.form['username']] = request.form['password']
			return redirect(url_for('login')) #send them to the login page 
	return render_template('registration.html', error=error) #if everything else failed, print their error


@app.route("/")
def default():
	return redirect(url_for('homepage')) #returns table

#does the same thing as before
@app.route("/new_message/<chatName>", methods=["POST"])
def add(chatName):
	chatName = chatName.strip()
	if chatName not in allChatRooms.keys(): 
		flash("You are seeing this message because a chat room has been deleted")
		return json.dumps(["The chat room was deleted. Click anywhere to be redirected."])
	else:
		currentChatRoom = chatName
		current_chat_room_info[session['username']] = currentChatRoom
		chatRoomIDDictionary = allChatRooms[chatName]
		messages = chatRoomIDDictionary["Messages: "]
		messages.append([session['username'] + ":"])
		messages.append([request.form["one"]])
		return json.dumps(messages)

@app.route("/messages/<chatName>", methods=["GET"])
def dumpmessages(chatName):
	chatName = chatName.strip()
	if chatName not in allChatRooms.keys(): 
		return json.dumps(["The chat room was deleted. Click anywhere to be redirected."])
	else: 
		currentChatRoom = chatName
		current_chat_room_info[session['username']] = currentChatRoom
		chatRoomID = chatName
		chatRoomIDDictionary = allChatRooms[chatRoomID]
		messages = chatRoomIDDictionary["Messages: "]
		#dumps the messages list as JSON and sends it to the server
		return json.dumps(messages)

@app.route("/users/<chatName>", methods=["GET"])
def dumpusers(chatName):
	chatName = chatName.strip()
	#dumps the messages list as JSON and sends it to the server
	chatRoomID = chatName
	chatRoomIDDictionary = allChatRooms[chatRoomID]
	users = chatRoomIDDictionary["Username: "]
	return json.dumps(users)

@app.route("/newChat", methods=["GET", "POST"])
def newChat(): 
	newdict = {}
	error = None 
	if 'username' not in session: 
		abort(401)
	if request.method == "POST": 
		if not request.form["chatName"]:
			error: "You did not enter a group name, try again"
		else: 
			chatRoomName = request.form["chatName"].strip()
			newdict["Name: "] = request.form["chatName"].strip()
			newdict["Messages: "] = []
			newdict["Username: "] = []
			newdict["Creator: "] = session['username']
			allChatRooms[chatRoomName] = newdict
			return render_template("messages.html", messages=newdict["Messages: "], chatRoomName=chatRoomName, users=newdict["Username: "]) #returns table
	return render_template('newChat.html', error=error)

@app.route("/showChatRoom/<chatRoomName>", methods=["GET", "POST"])
def showChatRoom(chatRoomName): 
	#currentChatRoom = currentChatRoom
	print(current_chat_room_info[session['username']])
	global currentChatRoom 
	if not chatRoomName in allChatRooms.keys(): 
		flash("You are seeing this message because a chat room has been deleted")
		return redirect(url_for('homepage'))
	else: 
		if current_chat_room_info[session['username']] == None:
			chatRoomIDDictionary = allChatRooms[chatRoomName]
			currentChatRoom = chatRoomName 
			current_chat_room_info[session['username']] = currentChatRoom
			messages = chatRoomIDDictionary["Messages: "]
			return render_template("messages.html", messages=messages, chatRoomName=chatRoomName) #returns table
		else: 
			flash ("You are already in a chat room sorry")
			return redirect(url_for('homepage'))

@app.route("/deleteChatRoom/<chatRoomName>", methods=["GET", "POST"])
def deleteChatRoom(chatRoomName): 
	error = None
	chatRoomIDDictionary = allChatRooms[chatRoomName]
	creator = chatRoomIDDictionary["Creator: "]
	if creator == session['username']:
		messages = chatRoomIDDictionary["Messages: "]
		messages.append("This chat room has been deleted!")
		json.dumps(messages)
		del allChatRooms[chatRoomName]
		flash("You are seeing this message because a chat room has been deleted")
		return redirect(url_for('homepage'))
	else: 
		error = "Sorry, you didn't create that chat room so you can't delete it."
	return render_template("homepage.html", allChatRooms=allChatRooms, error=error)
	


@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.pop('username', None) #make them log out as far as the server is concerned 
	return redirect(url_for('login'))


@app.route("/homepage", methods=["GET", "POST"])
def homepage():
    if 'username' in session:
        currentChatRoom = None
        current_chat_room_info[session['username']] = currentChatRoom
        return render_template("homepage.html", allChatRooms=allChatRooms) #returns table
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
	app.run()
