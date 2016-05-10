import json
import time

OUTPUT_FILE = 'queued_summoners.csv'

seed_files = raw_input('Enter seed file names separated by comma: ').split(',')

start_time = time.time()
queued_summoners = []
for seed_file in seed_files:
	try:
		f = open(seed_file.strip(), 'r')
		seed_data = json.load(f, encoding='ISO-8859-1')
		for seed_match in seed_data['matches']:
			for seed_participant in seed_match['participantIdentities']:
				summoner_id = str(seed_participant['player']['summonerId'])
				if summoner_id not in queued_summoners:
					queued_summoners.append(summoner_id)
		print 'Loaded ' + seed_file
		f.close()
	except Exception, e:
		print 'Error loading ' + seed_file + ':' + str(e)

f = open(OUTPUT_FILE, 'w')
f.write(','.join(queued_summoners))
f.close()
print 'Saved to queued_summoners.txt'
print 'Completed in ' + str(time.time()-start_time) + ' second(s)'