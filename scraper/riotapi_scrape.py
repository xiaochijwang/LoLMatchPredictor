from urllib2 import Request, URLError, urlopen
import csv
import json
import time
import riotapi_record

VERBOSE = True
REQUEST_URL = 'https://na.api.pvp.net'
ITERATED_MATCHES_FILE = 'iterated_matches.csv'
ITERATED_SUMMONERS_FILE = 'iterated_summoners.csv'
QUEUED_SUMMONERS_FILE = 'queued_summoners.csv'
OUTPUT_FILE_PREFIX = 'MLData'
ALLOWED_TYPES = ['RANKED_SOLO_5x5', 'RANKED_TEAM_5x5', 'TEAM_BUILDER_DRAFT_RANKED_5x5']

# Get API key
f = open('api_key.txt', 'r')
API_KEY = f.readline().strip()
f.close()
print 'API key: ' + API_KEY

def load_csv_list(csv_file):
	loaded_list = []
	try:
		f = open(csv_file, 'r')
		loaded_list = list(csv.reader(f))[0]
		f.close()
	except Exception, e:
		print 'Error loading ' + csv_file + ':' + str(e)
	return loaded_list

def save_csv_list(csv_file, save_list):
	f = open(csv_file, 'w')
	f.write(','.join(save_list))
	f.close()

def save_all(verbose):
	save_csv_list(ITERATED_MATCHES_FILE, iterated_matches)
	save_csv_list(ITERATED_SUMMONERS_FILE, iterated_summoners)
	save_csv_list(QUEUED_SUMMONERS_FILE, queued_summoners)
	if verbose:
		print 'Updated ' + ITERATED_MATCHES_FILE + ',' + ITERATED_SUMMONERS_FILE + ',' + QUEUED_SUMMONERS_FILE

iterated_matches = load_csv_list(ITERATED_MATCHES_FILE)
print 'Loaded ' + str(len(iterated_matches)) + ' iterated match(es)'
iterated_summoners = load_csv_list(ITERATED_SUMMONERS_FILE)
print 'Loaded ' + str(len(iterated_summoners)) + ' iterated summoner(s)'
queued_summoners = load_csv_list(QUEUED_SUMMONERS_FILE)
print 'Loaded ' + str(len(queued_summoners)) + ' queued summoner(s)'

num_summoners = int(raw_input('Number of summoners to crawl: '))

start_time = time.time()

# CSV header
output_file = open(OUTPUT_FILE_PREFIX + '_' + str(start_time) + '.csv', "wb+")
f = csv.writer(output_file)
f.writerow(["match_id", "winner", 
	"p1_champion", "p1_mastery", 
	"p2_champion", "p2_mastery",
	"p3_champion", "p3_mastery",
	"p4_champion", "p4_mastery",
	"p5_champion", "p5_mastery",
	"p6_champion", "p6_mastery",
	"p7_champion", "p7_mastery",
	"p8_champion", "p8_mastery",
	"p9_champion", "p9_mastery",
	"p10_champion", "p10_mastery"])

try:
	while queued_summoners and num_summoners != 0:
		summoner_id = queued_summoners.pop(0)
		if summoner_id not in iterated_summoners:
			num_summoners = num_summoners - 1
			print 'Crawling match list for summoner ID: ' + summoner_id
			
			while True:
				try:
					match_list = json.loads(urlopen(Request(REQUEST_URL + '/api/lol/na/v2.2/matchlist/by-summoner/' + summoner_id + '?rankedQueues=' + ','.join(ALLOWED_TYPES) + '&seasons=SEASON2016&beginIndex=0&endIndex=5&api_key=' + API_KEY)).read())
					if match_list['totalGames'] > 0:
						for match in match_list['matches']:
							match_id = str(match['matchId'])
							if match_id not in iterated_matches:
								print '  Crawling match ID: ' + match_id
								
								while True:
									try:
										match = json.loads(urlopen(Request(REQUEST_URL + '/api/lol/na/v2.2/match/' + match_id + '?includeTimeline=false&api_key=' + API_KEY)).read())
										
										# Do match processing here
										f.writerow(riotapi_record.getMLData(match, API_KEY))
										
										new_summoners = []
										for participant in match['participantIdentities']:
											new_summoner_id = str(participant['player']['summonerId'])
											if new_summoner_id != summoner_id and new_summoner_id not in iterated_summoners and new_summoner_id not in queued_summoners:
												queued_summoners.append(new_summoner_id)
												new_summoners.append(new_summoner_id)
										print '    Added summoner IDs: ' + str(new_summoners)
										iterated_matches.append(match_id)
										save_all(False)
										break
									except URLError, e:
										if e.code != 429 and VERBOSE:
											print 'URLError ' + str(e.code) + ' crawling match ID ' + match_id + ': ' + str(e) + '\nRetrying match ID ' + match_id + '...'
											if e.code == 404 or e.code == 403:
												break
											print 'Retrying match ID ' + match_id + '...'
										time.sleep(10.0)
									except Exception, ex:
										print 'Error crawling match ID ' + match_id + ': ' + str(ex) + '\nMatch ID ' + match_id + ' will be ignored'
										break
														
					iterated_summoners.append(summoner_id)
					save_all(False)
					break
				except URLError, e:
					if e.code != 429 and VERBOSE:
						print 'URLError ' + str(e.code) + ' crawling match list for summoner ID ' + summoner_id + ': ' + str(e)
						if e.code == 404 or e.code == 403:
							break
						print 'Retrying summoner ID ' + summoner_id + '...'
					time.sleep(10.0)
				except Exception, ex:
					print 'Error crawling match list for summoner ID ' + summoner_id + ': ' + str(ex) + '\nSummoner ID ' + summoner_id + ' will be ignored'
					break
				
except Exception, e:
	print e
	save_all(VERBOSE)

save_all(VERBOSE)
output_file.close()
print 'Saved to ' + OUTPUT_FILE_PREFIX + '_' + str(start_time) + '.csv'
print 'Completed in ' + str((time.time()-start_time)/60) + ' minute(s)'