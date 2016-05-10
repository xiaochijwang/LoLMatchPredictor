from urllib2 import Request, URLError, urlopen
import json
import time

VERBOSE = True

def getMLData(parsed_json, api_key):
	participantIdentities = parsed_json['participantIdentities']
	participants = parsed_json['participants']

	p_info = []

	for i in range(0, len(participantIdentities)):
		player_id = str(participantIdentities[i]['player']['summonerId'])
		champion_id = str(participants[i]['championId'])

		while True:
			try:
				mastery = json.loads(urlopen(Request('https://na.api.pvp.net/championmastery/location/na1/player/' + player_id + '/champion/' + champion_id + '?api_key=' + api_key)).read())
				p_info.extend((champion_id, mastery['championPoints']))
				break				
			except URLError, e:
				if e.code != 429 and VERBOSE:
					print 'URLError ' + str(e.code) + ' getting mastery for player ID ' + player_id + ' in match ID ' + str(parsed_json['matchId']) + ': ' + str(e)
					if e.code == 404 or e.code == 403:
						break
					print 'Retrying...'
				time.sleep(10.0)
			except Exception, ex:
				print 'Error getting mastery for player ID ' + player_id + ' in match ID ' + str(parsed_json['matchId']) + ': ' + str(ex) + '\nSkipped'
				break

	game_info = [parsed_json['matchId'],parsed_json['teams'][0]['winner']] + p_info
	return game_info