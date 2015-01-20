#C:\Python33\python

import pymongo
import json
from urllib import request

ltwheat_summ_id = 28767867
ltwheat_region = 'na'
ltwheat_api_key = "b9de0d75-2404-48c1-b085-6ef961492a38"

mongo_host = "localhost"
mongo_port = 27017

##### TODO #####
# 1) Make generic api call method, to fail if non-200 status code or json
def make_generic_request(url, api_key=None):
    # Default to Lt Wheat
    if api_key == None:
        api_key = ltwheat_api_key

    # Make request
    url += "?api_key={0}".format(api_key)
    response = request.urlopen(url)
    data = response.read()
    return json.loads(data.decode())

def get_last_match():
    all_matches = get_matches()
    latest_match = None
    latest_time = 0
    for match in all_matches['matches']:
        if match['matchCreation'] > latest_time:
            latest_time = match['matchCreation']
            latest_match = match
    return match

def get_champ_by_id(champ_id):
    champion_url = "https://na.api.pvp.net/api/lol/static-data/" \
                   "{0}/v1.2/champion/{1}".format(ltwheat_region, champ_id)
    resp = make_generic_request(champion_url)
    return resp["name"]
    
def get_matches(ranked_queues='',begin_index=-1,end_index=-1,champion_id=-1):
    # TODO:
	# 1) Figure out how to pass in ranked_queues, champID, beginIndex and endIndex as params
	# 2) champion_id should be a comma-separated list, as specified by API docs
	# 3) ranked_queues can only be one of three possible values, so hardcode those somewhere
	# 3a) ranked_queues also comma-separated, see API docs
    match_history_url = "https://na.api.pvp.net/api/lol/"\
                        "{0}/v2.2/matchhistory/{1}".format(ltwheat_region,
                                                           ltwheat_summ_id)
    # TODO: Rules for begin and end index:
    ## 1) integers
    ## 2) begin > -1; end > 0
    ## 3) end > begin
    ## 4) 16 > end - begin (soft limit)
	## 4a) begin serves as anchor--so a request for matches 0 (b) through 30 (e)
	##     returns the same info as 0 through 17.
    return make_generic_request(match_history_url)
    
if __name__ == '__main__':
    # TODO: This should return a short synopsis of last game, ie "Win as Jinx", maybe date/duration, etc
    print("name works")
