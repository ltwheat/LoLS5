#C:\Python33\python

import datetime
import math
import json
import pymongo
from urllib import request

ltwheat_summ_id = 28767867
ltwheat_region = 'na'
ltwheat_api_key = "b9de0d75-2404-48c1-b085-6ef961492a38"

mongo_host = "localhost"
mongo_port = 27017

##### TODO #####
# 1) Long-term goal: I need to store all this info as Python objects, rather
#    than raw data. So a lot of this stuff is gonna have to change, and we'll
#    also need some actual classes and a api-to-class constructor, but for now,
#    I'm just hitting the API for everything and dealing with the raw data.
# 2) Make generic api call method, to fail if non-200 status code or json
def make_generic_request(url, api_key=None):
    # Default to Lt Wheat
    if api_key == None:
        api_key = ltwheat_api_key

    # Make request
    url += "?api_key={0}".format(api_key)
    try:
        response = request.urlopen(url)
    except HTTPError as e:
        print("Error: Status code {0}; {1}".format(e.code, e.reason))
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
    match_id = latest_match['matchId']
    # TODO: Get timeline data (as optional arg?)
    match_url = "https://na.api.pvp.net/api/lol/" \
                "{0}/v2.2/match/{1}".format(ltwheat_region,
                                            match_id)
    return make_generic_request(match_url)

def get_champ_by_id(champ_id):
    champion_url = "https://na.api.pvp.net/api/lol/static-data/" \
                   "{0}/v1.2/champion/{1}".format(ltwheat_region, champ_id)
    resp = make_generic_request(champion_url)
    return resp["name"]

def get_match_champs(match):
    participants = match['participants']
    champs = []
    for participant in participants:
        champ = get_champ_by_id(participant['championId'])
        champs.append(champ)
    return champs

def get_match_participant(match, summ_id=ltwheat_summ_id):
    participant = None
    participant_id = get_participant_id(match, summ_id)
    for p in match['participants']:
        if p['participantId'] == participant_id:
            participant = p
    return participant

def get_match_winner(match):
    winner = None
    for team in match['teams']:
        if team['winner'] == True:
            winner = team['teamId']
    return winner

def get_participant_id(match, summ_id=ltwheat_summ_id):
    participant_idents = match['participantIdentities']
    participant_id = -1
    for ident in participant_idents:
        if ident['player']['summonerId'] == summ_id:
            participant_id = ident['participantId']
    return participant_id

def is_winner(match, summ_id=ltwheat_summ_id):
    participant = get_match_participant(match, summ_id)
    winning_team_id = get_match_winner(match)
    won = participant['teamId'] == winning_team_id
    return won

def match_synopsis(match, summ_id=ltwheat_summ_id):
    outcome = "Win"
    if not is_winner(match):
        outcome = "Loss"
    participant = get_match_participant(match)
    champ = get_champ_by_id(participant['championId'])
    match_creation = math.floor(match['matchCreation']/1000)
    date_time_played = datetime.datetime.fromtimestamp(match_creation)
    synopsis = "{0} as {1}, {2}".format(outcome, champ, date_time_played)
    return synopsis
    
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

def store_last_match():
    match = get_last_match()
    try:
        client = pymongo.MongoClient()
        #DB_NAME = client.DB_NAME
        #matches = DB_NAME.matches
        # TODO: catch DuplicateKeyError
        #db_match_id = matches.insert(match)
    except pymongo.errors.ConnectionFailure:
        print("Could not connect to database")
    
if __name__ == '__main__':
    # TODO: This should return a short synopsis of last game, ie "Win as Jinx",
    #       maybe date/duration, etc
    match = get_last_match()

    synopsis = match_synopsis(match)
    print("Last match:")
    print(synopsis)
