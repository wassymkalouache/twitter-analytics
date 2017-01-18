from flask import Flask, session, render_template,url_for,request
from flask_wtf import Form
from flask import Flask, session, render_template,url_for,request, flash
from flask_wtf import Form
from wtforms import SelectField, StringField, SubmitField
import pandas as pd
from pathlib import Path
from analytics import number_of_tweets, word_cloud, network_user, label_time, sentiment_analysis_over_month, subjectivity, \
	polarity, number_of_tweets_all, get_words, pos_neg_ratio, \
	is_retweet,  remove_words, time_tweet_plot, save_word_cloud, buzz
from analytics import *
import matplotlib.pyplot as plt
import datetime as dt


app = Flask(__name__,static_url_path = "", static_folder = "static")
app.secret_key = 'A0Zr98slkjdf984jnflskj_sdkfjhT'

def get_homepage_links():
	return [ {"href": url_for('user'), "label":"By user"},  {"href": url_for('allusers'), "label":"All users"},]

#chose the user
class UserForm(Form):
	user = SelectField('Twitter account', choices=list((list(data["account"].unique())[i],list(data["account"].unique())[i]) for i in range(0,len(data["account"].unique()))))

@app.route('/')
def home():
	session["data_loaded"] = True
	return render_template('home.html', links=get_homepage_links())

@app.route("/user", methods=['GET', 'POST'])
def user():
	form = UserForm()
	if form.validate_on_submit():
		account = request.form.get('user')
		path = 'static/'+account+'.png'
		my_file=Path(path)
		#in case the files already exist, no need to generate it again
		if my_file.is_file():
			return render_template('analyticsoutput.html',account=account)

		else:

			#save the fig with number of tweets over time
			number_of_tweets(data, account)

			#save the wordcloud fig for the user
			word_cloud(data, account)

			#save the network graph of the user
			network_user(data,account)

			#save the sentiment analysis over month
			sentiment_analysis_over_month(data,account)

			#save the pie of main words from buzzing tweets
			buzz(data, account)

			return render_template('analyticsoutput.html', account=account)


	return render_template('userparams.html', form=form)

@app.route("/allusers", methods=['GET'])
def allusers():
	path='static/subjectivity.png'
	my_file=Path(path)
	if my_file.is_file():
		return render_template('allusers.html')

	else:

		#Subjectivity
		subjectivity(data)

		#Polarity
		polarity(data)

		#number of tweets all users
		number_of_tweets_all(data)

		# # of tweets according to the time of the day
		time_tweet_plot(data)

		return render_template('allusers.html')


if __name__ == "__main__":
	app.run()
