from flask import Flask, render_template
from sklearn.naive_bayes import GaussianNB
from urllib2 import Request, URLError, urlopen
import csv
import json
import random
import sys
import time
import traceback
app = Flask(__name__)

API_KEY = 'aba270ce-1ade-45fc-8916-4f61fb926f1e'

champions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 48, 50, 51, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 67, 68, 69, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 89, 90, 91, 92, 96, 98, 99, 101, 102, 103, 104, 105, 106, 107, 110, 111, 112, 113, 114, 115, 117, 119, 120, 121, 122, 126, 127, 131, 133, 134, 136, 143, 150, 154, 157, 161, 201, 202, 203, 222, 223, 236, 238, 245, 254, 266, 267, 268, 412, 420, 421, 429, 432]
champion_names = ['Annie', 'Olaf', 'Galio', 'Twisted Fate', 'Xin Zhao', 'Urgot', 'LeBlanc', 'Vladimir', 'Fiddlesticks', 'Kayle', 'Master Yi', 'Alistar', 'Ryze', 'Sion', 'Sivir', 'Soraka', 'Teemo', 'Tristana', 'Warwick', 'Nunu', 'Miss Fortune', 'Ashe', 'Tryndamere', 'Jax', 'Morgana', 'Zilean', 'Singed', 'Evelynn', 'Twitch', 'Karthus', "Cho'Gath", 'Amumu', 'Rammus', 'Anivia', 'Shaco', 'Dr. Mundo', 'Sona', 'Kassadin', 'Irelia', 'Janna', 'Gangplank', 'Corki', 'Karma', 'Taric', 'Veigar', 'Trundle', 'Swain', 'Caitlyn', 'Blitzcrank', 'Malphite', 'Katarina', 'Nocturne', 'Maokai', 'Renekton', 'Jarvan IV', 'Elise', 'Orianna', 'Wukong', 'Brand', 'Lee Sin', 'Vayne', 'Rumble', 'Cassiopeia', 'Skarner', 'Heimerdinger', 'Nasus', 'Nidalee', 'Udyr', 'Poppy', 'Gragas', 'Pantheon', 'Ezreal', 'Mordekaiser', 'Yorick', 'Akali', 'Kennen', 'Garen', 'Leona', 'Malzahar', 'Talon', 'Riven', "Kog'Maw", 'Shen', 'Lux', 'Xerath', 'Shyvana', 'Ahri', 'Graves', 'Fizz', 'Volibear', 'Rengar', 'Varus', 'Nautilus', 'Viktor', 'Sejuani', 'Fiora', 'Ziggs', 'Lulu', 'Draven', 'Hecarim', "Kha'Zix", 'Darius', 'Jayce', 'Lissandra', 'Diana', 'Quinn', 'Syndra', 'Aurelion Sol', 'Zyra', 'Gnar', 'Zac', 'Yasuo', "Vel'Koz", 'Braum', 'Jhin', 'Kindred', 'Jinx', 'Tahm Kench', 'Lucian', 'Zed', 'Ekko', 'Vi', 'Aatrox', 'Nami', 'Azir', 'Thresh', 'Illaoi', "Rek'Sai", 'Kalista', 'Bard']

def points_to_rank(mastery, limited):
	if mastery == 0:
		return 0
	elif mastery < 1800:
		return 1
	elif mastery < 6000:
		return 2
	elif mastery < 12600:
		return 3
	elif mastery < 21600:
		return 4
	elif mastery < 50000 or limited:
		return 5
	elif mastery < 100000:
		return 6
	else:
		return 7

def get_condensed_name(champion):
	if champion == 'Cho\'Gath':
		return 'Chogath';
	elif champion == 'Fiddlesticks':
		return 'FiddleSticks'
	elif champion == 'Kha\'Zix':
		return 'Khazix'
	elif champion == 'LeBlanc':
		return 'Leblanc'
	elif champion == 'Vel\'Koz':
		return 'Velkoz'
	elif champion == 'Wukong':
		return 'MonkeyKing'
	else:
		return champion.replace(' ', '').replace('\'', '').replace('.', '')

f = open('sanitized_data.csv', 'r')
l = list(csv.reader(f))
labels = []
vectors = []
for r in l:
	labels.append([int(r[0])])
	vectors.append([int(value) for value in r[1:]])
gnb = GaussianNB()
classifier = gnb.fit(vectors, labels)

@app.route('/', methods=['GET'])
def home_page():
	return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='')

@app.route('/summoner/<name>', methods=['GET'])
def search_user(name):
	name = name.replace(' ', '')
	while True:
		try:
			summoner = json.loads(urlopen(Request('https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/' + name + '?api_key=' + API_KEY)).read())
			summoner_id = str(summoner[summoner.keys()[0]]['id'])
			
			while True:
				try:
					match = json.loads(urlopen(Request('https://na.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/NA1/' + summoner_id + '?api_key=' + API_KEY)).read())
					if match['gameMode'] != 'CLASSIC':
						return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Only Classic 5v5 games are currently supported.')
						
					test_vector = [-1] * 260
					summoner_icons = []
					summoner_names = []
					summoner_ids = []
					champions_names = []
					champions_masteries = []
					indicators = []
					background = ''
					for participant in match['participants']:
						summoner_icons.append(participant['profileIconId'])
						summoner_names.append(participant['summonerName'])
						participant_id = participant['summonerId']
						summoner_ids.append(participant_id)
						champion_id = participant['championId']
						champion_index = champions.index(champion_id)
						team_id = participant['teamId']/100-1
						
						if summoner_id == str(participant_id):
							background = get_condensed_name(champion_names[champion_index])
							indicators.append('selected')
						else:
							indicators.append('')
	
						while True:
							try:
								mastery_points = 0
								mastery_response = urlopen(Request('https://na.api.pvp.net/championmastery/location/na1/player/' + str(participant_id) + '/champion/' + str(champion_id) + '?api_key=' + API_KEY)).read()
								if mastery_response and len(mastery_response) > 0:
									mastery_points = json.loads(mastery_response)['championPoints']
								test_vector[team_id*130+champion_index] = mastery_points
								champions_names.append(champion_names[champion_index])
								champions_masteries.append(mastery_points)
								break
							except URLError, e:
								if e.code != 429 and e.code != 500:
									return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error code ' + str(e.code) + ' querying Riot API for champion masteries of match for ' + name + '. Please try again later.')
								time.sleep(2.0)
							except Exception, ex:
								return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error finding champion masteries of match for ' + name + '. Please try again later.')
					
					summoner_ranks = []
					summoner_divisions = []
					summoner_lps = []
					summoner_wins = []
					summoner_losses = []
					while True:
						try:
							rankings = json.loads(urlopen(Request('https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/' + ','.join(map(str, summoner_ids)) + '?api_key=' + API_KEY)).read())
							for id in summoner_ids:
								found = False
								if str(id) in rankings:
									ranking_info = rankings[str(id)]
									for ranking_type in ranking_info:
										if ranking_type['queue'] == 'RANKED_SOLO_5x5':
											for ranking_entry in ranking_type['entries']:
												if ranking_entry['playerOrTeamId'] == str(id):
													summoner_ranks.append(ranking_type['tier'].title())
													summoner_divisions.append(ranking_entry['division'])
													summoner_lps.append(str(ranking_entry['leaguePoints']))
													summoner_wins.append(str(ranking_entry['wins']))
													summoner_losses.append(str(ranking_entry['losses']))
													found = True
								if not found:
									summoner_ranks.append('Unranked')
									summoner_divisions.append('')
									summoner_lps.append('-')
									summoner_wins.append('0')
									summoner_losses.append('0')
							break
						except URLError, e:
							if e.code != 429 and e.code != 500:
								return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error code ' + str(e.code) + ' querying Riot API for player rankings. Please try again later.')
							time.sleep(2.0)
						except Exception, ex:
							return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error finding player rankings. Please try again later.')
					
					prediction = classifier.predict(test_vector)
					probability = gnb.predict_proba(test_vector)
					winner_pred = ''
					winner_prob = 0.0
					if prediction[0] == 0:
						winner_pred = 'blue'
						winner_prob = probability[0][0]*100
					else:
						winner_pred = 'purple'
						winner_prob = probability[0][1]*100
					
					cchampions_names = []
					for champions_name in champions_names:
						cchampions_names.append(get_condensed_name(champions_name))
					
					return render_template('prediction.html',
						in0=indicators[0], in1=indicators[1], in2=indicators[2], in3=indicators[3], in4=indicators[4], in5=indicators[5], in6=indicators[6], in7=indicators[7], in8=indicators[8], in9=indicators[9],
						i0=summoner_icons[0], i1=summoner_icons[1], i2=summoner_icons[2], i3=summoner_icons[3], i4=summoner_icons[4], i5=summoner_icons[5], i6=summoner_icons[6], i7=summoner_icons[7], i8=summoner_icons[8], i9=summoner_icons[9],
						p0=summoner_names[0], p1=summoner_names[1], p2=summoner_names[2], p3=summoner_names[3], p4=summoner_names[4], p5=summoner_names[5], p6=summoner_names[6], p7=summoner_names[7], p8=summoner_names[8], p9=summoner_names[9],
						r0=summoner_ranks[0], r1=summoner_ranks[1], r2=summoner_ranks[2], r3=summoner_ranks[3], r4=summoner_ranks[4], r5=summoner_ranks[5], r6=summoner_ranks[6], r7=summoner_ranks[7], r8=summoner_ranks[8], r9=summoner_ranks[9],
						d0=summoner_divisions[0], d1=summoner_divisions[1], d2=summoner_divisions[2], d3=summoner_divisions[3], d4=summoner_divisions[4], d5=summoner_divisions[5], d6=summoner_divisions[6], d7=summoner_divisions[7], d8=summoner_divisions[8], d9=summoner_divisions[9],
						lp0=summoner_lps[0], lp1=summoner_lps[1], lp2=summoner_lps[2], lp3=summoner_lps[3], lp4=summoner_lps[4], lp5=summoner_lps[5], lp6=summoner_lps[6], lp7=summoner_lps[7], lp8=summoner_lps[8], lp9=summoner_lps[9],
						w0=summoner_wins[0], w1=summoner_wins[1], w2=summoner_wins[2], w3=summoner_wins[3], w4=summoner_wins[4], w5=summoner_wins[5], w6=summoner_wins[6], w7=summoner_wins[7], w8=summoner_wins[8], w9=summoner_wins[9],
						l0=summoner_losses[0], l1=summoner_losses[1], l2=summoner_losses[2], l3=summoner_losses[3], l4=summoner_losses[4], l5=summoner_losses[5], l6=summoner_losses[6], l7=summoner_losses[7], l8=summoner_losses[8], l9=summoner_losses[9],
						c0=champions_names[0], c1=champions_names[1], c2=champions_names[2], c3=champions_names[3], c4=champions_names[4], c5=champions_names[5], c6=champions_names[6], c7=champions_names[7], c8=champions_names[8], c9=champions_names[9],
						cc0=cchampions_names[0], cc1=cchampions_names[1], cc2=cchampions_names[2], cc3=cchampions_names[3], cc4=cchampions_names[4], cc5=cchampions_names[5], cc6=cchampions_names[6], cc7=cchampions_names[7], cc8=cchampions_names[8], cc9=cchampions_names[9],
						m0=champions_masteries[0], m1=champions_masteries[1], m2=champions_masteries[2], m3=champions_masteries[3], m4=champions_masteries[4], m5=champions_masteries[5], m6=champions_masteries[6], m7=champions_masteries[7], m8=champions_masteries[8], m9=champions_masteries[9],
						ma0=points_to_rank(champions_masteries[0], True), ma1=points_to_rank(champions_masteries[1], True), ma2=points_to_rank(champions_masteries[2], True), ma3=points_to_rank(champions_masteries[3], True), ma4=points_to_rank(champions_masteries[4], True), ma5=points_to_rank(champions_masteries[5], True), ma6=points_to_rank(champions_masteries[6], True), ma7=points_to_rank(champions_masteries[7], True), ma8=points_to_rank(champions_masteries[8], True), ma9=points_to_rank(champions_masteries[9], True),
						mb0=points_to_rank(champions_masteries[0], False), mb1=points_to_rank(champions_masteries[1], False), mb2=points_to_rank(champions_masteries[2], False), mb3=points_to_rank(champions_masteries[3], False), mb4=points_to_rank(champions_masteries[4], False), mb5=points_to_rank(champions_masteries[5], False), mb6=points_to_rank(champions_masteries[6], False), mb7=points_to_rank(champions_masteries[7], False), mb8=points_to_rank(champions_masteries[8], False), mb9=points_to_rank(champions_masteries[9], False),
						bg=background, winner_pred=winner_pred, winner_prob=winner_prob, summoner_name=name)
					
				except URLError, e:
					if e.code == 404:
						return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Summoner is currently not in game.')
					if e.code != 429 and e.code != 500:
						return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error code ' + str(e.code) + ' querying Riot API for current match for ' + name + '. Please try again later.')
					time.sleep(2.0)
				except Exception, ex:
					return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error finding current match for ' + name + '. Please try again later.')
					
		except URLError, e:
			if e.code == 404:
				return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Summoner name does not exist.')
			if e.code != 429 and e.code != 500:
				return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error code ' + str(e.code) + ' querying Riot API for summoner ID for ' + name + '. Please try again later.')
			time.sleep(2.0)
		except Exception, ex:
			return render_template('landing.html', bg=get_condensed_name(random.choice(champion_names)), error='Error! Error finding summoner ID for ' + name + '. Please try again later.')

if __name__ == '__main__':
    app.run()
