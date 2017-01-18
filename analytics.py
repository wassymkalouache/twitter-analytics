import pandas as pd
import numpy as np
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime as dt
from stop_words import get_stop_words


#read the csv
data=pd.read_csv("tweets.csv")

#convert the dates into timestamp type
data['created_at']=pd.to_datetime(data["created_at"],format='%Y-%m-%d %H:%M:%S')
data['date']=data['created_at'].apply(lambda x:dt.datetime.strptime(x.strftime('%m-%Y'),'%m-%Y'))
data['month']=pd.DatetimeIndex(data['created_at']).month
data['hour']=pd.DatetimeIndex(data['created_at']).hour
data['year']=pd.DatetimeIndex(data['created_at']).year
#list of users
users = data["account"].unique()
#dictionary
data_text = pd.DataFrame({"user":users})

from textblob import TextBlob
polarity,subjectivity=[],[]
for tweet in data["text"]:
	polarity.append(TextBlob(tweet).sentiment.polarity)
	subjectivity.append(TextBlob(tweet).sentiment.subjectivity)

data["polarity"]=polarity
data["subjectivity"]=subjectivity

def number_of_tweets(data, account):
	plot=data[data["account"]==account].groupby(["date"]).size().plot(label=account,legend=True,figsize=(8,8))
	plot.set_title('Number of tweets over time')
	fig=plot.get_figure()
	fig.savefig('static/'+account+'.png',bbox_inches='tight')
	plot.clear()
	fig.clear()

def word_cloud(data,account):
	text=''
	for tweet in data["text"][data["account"]==account]:
		text+=tweet
	text_array = re.findall(r"#(\w+)", text)
	text = " ".join(text_array)
	from wordcloud import WordCloud,STOPWORDS
	import matplotlib.pyplot as plt
	wordcloud=WordCloud(stopwords=STOPWORDS,background_color='white',width=1800,height=1400).generate(text)
	plt.imshow(wordcloud)
	plt.axis('off')
	plt.savefig('static/wordcloudhashtag'+account+'.png',bbox_inches='tight')
	plt.clf()

def network_user(data, account):
	import operator
	dict={}
	text=''
	for tweet in data["text"][data["account"]==account]:
		text+=tweet
	text=text.split()

	for word in (text):
		if word.startswith("@"):
			if word in dict:
				dict[word]+=1
			else:
				dict[word]=1

	#get the most tagged people
	dict=sorted(dict.items(),key=operator.itemgetter(1),reverse=True)
	#save them as nodes and edges
	nodes=[]
	edges=[]
	weights=[]
	for i in range(10):
		nodes.append(dict[i][0])
		edges.append((account,dict[i][0]))
		weights.append(dict[i][1])

	import networkx as nx
	simple_network=nx.Graph()

	for i in range(10):
		simple_network.add_node(nodes[i].replace("@","").replace(":",''))
		simple_network.add_edge(account,nodes[i].replace("@","").replace(":",''),weight=weights[i]/sum(weights))

	elarge=[(u,v) for (u,v,d) in simple_network.edges(data=True) if d['weight']>0.1]
	esmall=[(u,v) for (u,v,d) in simple_network.edges(data=True) if d['weight']<=0.1]

	pos=nx.spring_layout(simple_network)
	nx.draw_networkx_nodes(simple_network,pos,node_size=500)
	nx.draw_networkx_edges(simple_network,pos,edgelist=elarge,width=6,edge_color='r')
	nx.draw_networkx_edges(simple_network,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')
	nx.draw_networkx_labels(simple_network,pos,font_size=15,font_family='sans-serif')

	plt.axis('off')
	plt.savefig('static/'+account+"weighted_graph.png",bbox_inches='tight')
	plt.clf()

#get words from URL
def get_words(url):
	import requests
	words = requests.get(url).content.decode('latin-1')
	word_list = words.split('\n')
	index = 0
	while index < len(word_list):
		word = word_list[index]
		if ';' in word or not word:
			word_list.pop(index)
		else:
			index+=1
	return word_list

#compute the sentiment from a string
def pos_neg_ratio(string):
	pos=0
	neg=0
	word_list=string.split()
	index=0
	while index < len(word_list):
		word = word_list[index].lower()
		if word in positive_words:
			pos+=1
		if word in negative_words:
			neg+=1
		index+=1
	if neg==0:
		return 1
	else:
		r=pos/neg
		return r


#Get lists of positive and negative words
p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
positive_words = get_words(p_url)
negative_words = get_words(n_url)

#plot the sentiment analysis by user over month
def sentiment_analysis_over_month(data, account,retweets=True):
	df=data[data["account"]==account]
	if retweets==False:
		df=df[df['text'].apply(is_retweet)==False]
	df['ratio']=pd.DataFrame(df['text'].apply(pos_neg_ratio))
	z=df.groupby(['date']).apply(lambda x: x['ratio'].mean())
	plot=z.plot(label=account,legend=True,figsize=(8,8))
	plot.set_title('Sentiment analysis over month')
	fig=plot.get_figure()
	fig.savefig('static/'+account+'sentiment.png',bbox_inches='tight')
	plot.clear()
	fig.clear()

def subjectivity(data):
	plot=data.groupby("account")["subjectivity"].mean().plot(kind="bar")
	plot.set_title('Subjectivity by user')
	fig=plot.get_figure()
	fig.savefig('static/subjectivity.png',bbox_inches="tight")
	plot.clear()
	fig.clear()

def polarity(data):
	plot=data.groupby("account")["polarity"].mean().plot(kind="bar")
	plot.set_title('Polarity by user')
	fig=plot.get_figure()
	fig.savefig('static/polarity.png',bbox_inches="tight")
	plot.clear()
	fig.clear()

def number_of_tweets_all(data):
	for index,group in data.groupby(['account']):
		group_agg=group.groupby(['month']).size()
		plot=group_agg.plot(label=index,legend=True)
	plot.set_title('Number of tweets over month in 2016')
	fig=plot.get_figure()
	fig.savefig('static/numberoftweets.png',bbox_inches="tight")
	plot.clear()
	fig.clear()


def label_time (hours):
	if hours > 4 and hours <= 10:
		return "Morning"
	elif hours > 10 and hours <= 16:
		return "Afternoon"
	elif hours > 16 and hours <= 24 :
		return "Late Night"
	elif hours >= 0 and hours <= 4:
		return "Late Night"
	return hours

def is_retweet(string):
	if "RT" in string:
		return True
	else:
		return False

#clean a tweet from urls and useless words
def remove_words(text_string):
	import enchant
	from textblob import TextBlob
	d = enchant.Dict("en_US")
	text_stringblob = TextBlob(text_string)
	for word in text_stringblob.words:
		if not d.check(str(word)):
			text_string = text_string.replace(word, '')
	text_string = text_string.replace("b'","").replace('b"',"").replace("RT","").replace("@","").replace("amp","").replace("co", "")
	return text_string

#get the number of tweets according to the time (morning, afternnon or late night)
def time_tweet_plot(data):
	data["create_label"]=data["hour"].apply(lambda row:label_time(row))
	counts=data.groupby(['account','create_label']).size()

	y_list=counts.tolist()
	x_list=[]

	for i in range(0,len(y_list)):
		x_list=x_list+[counts.axes[0][i][0]+" "+counts.axes[0][i][1]]

	y_pos=np.arange(len(y_list))
	bar=plt.bar(y_pos,y_list,align='center',alpha=0.5)

	colors=['r','g','b','c','k','y','m','b']
	color_index=0
	prev=counts.axes[0][0][0]
	bar[0].set_color(colors[color_index])
	for i in range(1,len(y_list)):
		if counts.axes[0][i][0]==prev:
			bar[i].set_color(colors[color_index])
			prev=counts.axes[0][i][0]
		else:
			color_index=(color_index+1)%len(colors)
			bar[i].set_color(colors[color_index])
			prev=counts.axes[0][i][0]

	plt.xticks(y_pos,x_list,rotation='vertical')
	plt.savefig('static/hours.png',bbox_inches="tight")

def save_word_cloud(user,data_text):
	fig, axes = plt.subplots(1, 1)
	row = data_text.loc[data_text['user'] == user]
	for index, row in row.iterrows():
		text_array = re.findall(r"#(\w+)", row['alltweets'])
		text = " ".join(text_array)
		wordcloud = WordCloud(background_color="white").generate(text)
		axes.set_title(row["user"])
		axes.imshow(wordcloud)
		extent = axes.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
		fig.savefig( 'static/'+user+'wordcloudhashtag.png' , bbox_inches=extent)

#Remove punctuation from tweets
def remove_punctuation_upfront(word):
	if word==None:
		return None
	if len(word)==1 and ord(word[0])<ord('A'):
		return None
	if ord(word[0])>=ord('A'):
		return word
	else:
		return remove_punctuation_upfront(word[1:])

def remove_punctuation_back(word):
	if word==None:
		return None
	if len(word)==1 and ord(word[len(word)-1])<ord('A'):
		return None
	if ord(word[len(word)-1])>=ord('A'):
		return word
	else:
		i=len(word)-1
		return remove_punctuation_back(word[:i])

##Return a sorted dictionnary with the frequences of the words used in the buzz tweets
def buzz(df,account):
	stop_words = get_stop_words('en')
	df=df[df["account"]==account]
	m=df["retweets"].mean()
	s=df["retweets"].std()
	df2=df[df["retweets"]>=m+1*s]
	all_text=[]
	for string in df2["text"]:
		string=remove_words(string)
		for word in string.split():
			word=remove_punctuation_back(remove_punctuation_upfront(word.lower()))
			all_text.append(word)
			for i in all_text:
				if i == None or i in stop_words or i=="\\":
					all_text.remove(i)
	wordfreq = dict()
	for w in all_text:
		for w in all_text:
			wordfreq[w]=all_text.count(w)
	dic=sorted(wordfreq.items(), key=lambda t: t[1])
	df3=pd.DataFrame(dic)
	df3=df3[df3[1]>=3]
	df3.columns=["words","frequence"]
	df3["frequence"]=100*df3["frequence"]/(df3["frequence"].sum())
	df4=df3.set_index("words")
	df4.frequence.plot(x="words",kind="pie",legend=False, colormap='Accent', labels=df4.index,title="Pie Chart of the frequent words in Buzz Tweets of %s"%account)
	plt.ylabel('')
	plt.savefig("static/"+account+"pie.png")
	plt.clf()






