import csv
import os

champions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 48, 50, 51, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 67, 68, 69, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 89, 90, 91, 92, 96, 98, 99, 101, 102, 103, 104, 105, 106, 107, 110, 111, 112, 113, 114, 115, 117, 119, 120, 121, 122, 126, 127, 131, 133, 134, 136, 143, 150, 154, 157, 161, 201, 202, 203, 222, 223, 236, 238, 245, 254, 266, 267, 268, 412, 420, 421, 429, 432]
iterated_matches = []
sanitized = []

for file in os.listdir(os.getcwd()):
	if '.csv' in file and file != 'sanitized_data.csv':
		f = open(file, 'r')
		l = list(csv.reader(f))
		total = len(l) - 1
		processed = 0
		print 'Processed ' + file
		for r in l[1:]:
			if r[0] not in iterated_matches and len(r) == 22:
				data = [-1]*261
				data[0] = 1 if r[1] == 'TRUE' or r[1] == 'True' else 0
				for i in range(2, 11, 2):
					data[champions.index(int(r[i]))+1] = int(r[i+1])
				for i in range(12, 21, 2):
					data[champions.index(int(r[i]))+131] = int(r[i+1])
				iterated_matches.append(r[0])
				sanitized.append(data)
			processed = processed + 1
			if processed % 100 == 0 or processed == total:
				print 'Sanitized ' + str(processed) + '/' + str(total) + ' rows'
		o = open('sanitized_data.csv', 'wb+')
		output = csv.writer(o)
		output.writerows(sanitized)
		o.close()
		f.close()