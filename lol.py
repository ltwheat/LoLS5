#C:\Python33\python

import datetime
import json
import math
import time
#TODO: why does db.collection.update replace everything
#      instead of actually updating???
from urllib import request
from urllib.error import HTTPError

# Allow for non-mongo functionality w/o module installed
try:
    import pymongo
except ImportError:
    print("Could not import pymongo--errors may occur")

ltwheat_summ_id = 28767867
ltwheat_region = 'na'
ltwheat_api_key = "b9de0d75-2404-48c1-b085-6ef961492a38"
ltwheat_api_rate_limit = 1

mongo_host = "localhost"
mongo_port = 27017

raw_lol_db_name = "lol_s5"
raw_solo_q_coll_name = "solo_ranked_5x5"

##### TODO #####
#THIS THING IS A MESS. But I'm itching to play LoL, so I'll deal later.
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
    # TODO: This needs to be rethought if we're gonna be passing in args
    url += "?api_key={0}".format(api_key)
    try:
        print("Hitting {0}".format(url))
        response = request.urlopen(url)
    except HTTPError as e:
        print("Error: Status code {0}; {1}".format(e.code, e.reason))
        return
    data = response.read()
    return json.loads(data.decode())

def get_last_match():
    all_matches = get_matches()
    latest_match = None
    latest_time = 0
    for match in all_matches:
        if match['matchCreation'] > latest_time:
            latest_time = match['matchCreation']
            latest_match = match
    return latest_match

def get_champ_by_id(champ_id):
    champion_url = "https://na.api.pvp.net/api/lol/static-data/" \
                   "{0}/v1.2/champion/{1}".format(ltwheat_region, champ_id)
    resp = make_generic_request(champion_url)
    return resp["name"]

def get_match_by_id(match_id):
    match_url = "https://na.api.pvp.net/api/lol/" \
                "{0}/v2.2/match/{1}".format(ltwheat_region,
                                            match_id)
    return make_generic_request(match_url)

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
    ## 5) Figure out if there's an option to get data from previous seasons
    match_history = make_generic_request(match_history_url)
    matches = []
    history_matches = match_history['matches']
    for h_match in history_matches:
        matches.append(get_match_by_id(h_match['matchId']))
        time.sleep(ltwheat_api_rate_limit)
    return matches

### Mongodb notes ###
#   1) Connection/Client -> Database -> Collection
#      b) client=pymongo.MongoClient()
#         db=pymongo.database.Database(client, "db_name")
#         db.coll_name.insert({"sample":"dict"})
#      b) client=pymongo.MongoClient()
#         db=client['db_name']
#         coll=db['coll_name']
#         coll.insert({"sample":"dict"})
#   2) Collection won't actually exist until data is inserted
#   3) Commonly used gets:
#      a) coll/conn.database_names()# returns all db names
#      b) db.collection_names()# returns all collection names in db
#      c) coll.find_one()# returns (random?) single item from coll
#      d) list(coll.find())# returns everything in coll. Must be cast
def store_raw_match(match):
    try:
        client = pymongo.MongoClient()
        # Automatically connects or creates if nonexistent
        db = client[raw_lol_db_name]
        coll = db[raw_solo_q_coll_name]
        # TODO: This check loops through every match in the db but I feel like
        #       that probably won't scale? Should we keep a separate coll of
        #       just match ids?
        match_id = match['matchId']
        for db_match in list(coll.find()):
            if match_id == db_match['matchId']:
                err_msg = "Match with id {0} already found in " \
                           "collection".format(match_id)
                raise pymongo.errors.DuplicateKeyError(err_msg)
        db_match_id = coll.insert(match)
        print("Stored match of id {0}:".format(match['matchId']))
        print(match_synopsis(match))
        return db_match_id
    except pymongo.errors.ConnectionFailure:
        print("Could not connect to database")
    except pymongo.errors.DuplicateKeyError as dke:
        print(dke)
    
if __name__ == '__main__':
    match = get_last_match()

    synopsis = match_synopsis(match)
    print("Last match:")
    print(synopsis)
