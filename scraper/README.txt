To use:
  1. Create api_key.txt in this directory and put your API key in it
  2. Run riotapi_seed.py
  3. Input the names of the seed files separated by commas (matches1.json, matches2.json, etc provided by Riot at https://developer.riotgames.com/docs/getting-started)
  4. Run riotapi_scrape.py
  5. Input number of summoners to crawl or a negative number to crawl infinitely
  6. Output will be saved to MLData_*****.csv (***** will be some timestamp)