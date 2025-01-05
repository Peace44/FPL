import math
import os
import sys
import numpy as np
from numpy import float64
from numpy import power as pow
import requests
import pandas as pd
import time
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
import copy

general_info_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
upcoming_fixtures_url = "https://fantasy.premierleague.com/api/fixtures/?future=1"
gameweeks_info_url = "https://fantasy.premierleague.com/api/event/{}/live/"

response = requests.get(general_info_url)
general_info_data = response.json()

teams = general_info_data['teams']
positions = general_info_data['element_types']
players = general_info_data['elements']

teams_dict = {team['id']:team['short_name'] for team in teams}
positions_dict = {position['id']:position['singular_name_short'] for position in positions}
players_dict = {player['id']:player for player in players}

# print('\n\n\n')
# print(teams_dict)
# print('\n\n\n')
# print(positions_dict)
# print('\n\n\n')
# print(players_dict)
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
response = requests.get(upcoming_fixtures_url)
upcoming_fixtures_data = response.json()
nxtGW = upcoming_fixtures_data[0]['event']
print(f"\n\n\nThe next gameweek is GW{nxtGW}\n")

gws = []
if input(f"Do you want to simulate a particular gameweek?\nAnswer 'no' if you want to simulate in advance many contiguous gameweeks starting from the next.\n[Y/n]?   ").lower()[0] == 'y':
    gwToSimulate = int(input(f"\nWhich one? Enter a number in the range [1, {nxtGW}]:    "))
    gws.append(gwToSimulate)
else:
    nberOfGWsInAdvance = int(input(f"\nHow many gameweeks do you want to simulate in advance ( <= 5 )?   "))
    if nberOfGWsInAdvance not in range(1, 5+1):
        sys.exit("\n\n\n    !Bye-\n-Bye!\n\n\n")
    gws.append(nxtGW) 
    if nberOfGWsInAdvance >= 2:
        gws.append(nxtGW + 1)
    if nberOfGWsInAdvance >= 3:
        gws.append(nxtGW + 2)
    if nberOfGWsInAdvance >= 4:
        gws.append(nxtGW + 3)
    if nberOfGWsInAdvance == 5:
        gws.append(nxtGW + 4)

refGW = min(gws)
events = general_info_data['events']
refGWstart = datetime.strptime(events[refGW-1]['deadline_time'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=90)
form_refGW = min(
    [
        event['id'] 
        for event in events 
        if event['finished'] and (refGWstart - (datetime.strptime(event['deadline_time'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=90))) <= timedelta(days=30)
    ]
) ### form_refGW is the 1st GW to consider when calculating a player's form!
form_refGWstart = datetime.strptime(events[form_refGW-1]['deadline_time'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=90)

print('\n\n\n')
# print(f"nxtGW = {nxtGW}\nrefGW = {refGW}")
print(f"form_refGW = {form_refGW}")
# print(f"{refGWstart-form_refGWstart}")
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
response = requests.get(fixtures_url)
fixtures_data = response.json()

matches_played_dict = {k: 0 for k in teams_dict.values()}
goals_for_dict = {k: [] for k in teams_dict.values()}
goals_against_dict = {k: [] for k in teams_dict.values()}
goal_diff_dict = {k: [] for k in teams_dict.values()}
clean_sheets_dict= {k: 0 for k in teams_dict.values()}
teams_fixturesPtsFor_dict = {t: [{} for gwk in range(1, refGW)] for t in teams_dict.values()}
teams_fixturesPtsAgainst_dict = {t: [{} for gwk in range(1, refGW)] for t in teams_dict.values()}
teams_fixturesPtsDiff_dict = {t: [] for t in teams_dict.values()}

for fixture in fixtures_data:
    if not fixture["finished"] or fixture["event"] >= max(gws):
        continue;

    home_team = teams_dict[fixture["team_h"]]
    away_team = teams_dict[fixture["team_a"]]

    home_team_score = fixture["team_h_score"]
    away_team_score = fixture["team_a_score"]

    matches_played_dict[home_team] += 1
    goals_for_dict[home_team].append(home_team_score)
    goals_against_dict[home_team].append(away_team_score)
    goal_diff_dict[home_team].append(home_team_score - away_team_score)

    if away_team_score == 0:
        clean_sheets_dict[home_team] += 1
        
    matches_played_dict[away_team] += 1
    goals_for_dict[away_team].append(away_team_score)
    goals_against_dict[away_team].append(home_team_score)
    goal_diff_dict[away_team].append(away_team_score - home_team_score)

    if home_team_score == 0:
        clean_sheets_dict[away_team] += 1

    fixture_id = fixture['id']
    if fixture['event'] in range(1, refGW):
        teams_fixturesPtsFor_dict[home_team][fixture['event'] - 1][fixture_id] = 0
        teams_fixturesPtsFor_dict[away_team][fixture['event'] - 1][fixture_id] = 0
        teams_fixturesPtsAgainst_dict[home_team][fixture['event'] - 1][fixture_id] = away_team
        teams_fixturesPtsAgainst_dict[away_team][fixture['event'] - 1][fixture_id] = home_team

teams_fixturesDefPts_dict = copy.deepcopy(teams_fixturesPtsFor_dict)
teams_fixturesAttPts_dict = copy.deepcopy(teams_fixturesPtsFor_dict)

# print('\n\n\n')
# print(matches_played_dict)
# print('\n\n\n')
# print(goals_for_dict)
# print('\n\n\n')
# print(goals_against_dict)
# print('\n\n\n')
# print(goal_diff_dict)
# print('\n\n\n')
# print(clean_sheets_dict)
# print('\n\n\n')
# print(teams_fixturesPtsFor_dict)
# print('\n\n\n')
# print(teams_fixturesPtsAgainst_dict)
# print('\n\n\n')
# print(teams_fixturesPtsDiff_dict)
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
prvGWsPtsTrendAvailability = False
if input(f"\n\n\nDo you have previous gameweeks (nxtGWs)PtsTrends data [Y/n]?   ").lower()[0] == 'y':
    prvGWsPtsTrendAvailability = True

if prvGWsPtsTrendAvailability:
    print("\nWhat's the DATETIME from which the data can be fetched from?")
    day = int(input("Provide the day value (1 to 31): "))
    month = int(input("Provide the month value (1 to 12): "))
    year = int(input("Provide the year value: "))
    hour = int(input("Provide the hour value (0 to 23): "))
    minute = int(input("Provide the minute value (0 to 59): "))
    timestr = "%02d'%02d'%4d-%02d:%02d" %(day, month, year, hour, minute)
    prvGWsPtsTrend_file = "data/" + timestr + "/players_stats.csv"
    try:
        prvGWsPtsTrend_df = pd.read_csv(prvGWsPtsTrend_file)[['id', 'nxtGWsPtsTrend']].set_index('id', drop=False)
        prvGWsPtsTrend_dict = prvGWsPtsTrend_df.to_dict()['nxtGWsPtsTrend']
    except Exception as e:
        print(f"\n{e}\n")
        prvGWsPtsTrendAvailability = False

# print('\n\n\n')
# print(prvGWsPtsTrend_dict)
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
def golden_sum(gold, silver=None, bronze=None, symmetric=False, invertArgs=False):
    PHI = 0.61803398874989484820

    if invertArgs:
        if silver is None:
            return golden_sum(gold)
        elif bronze is None:
            return golden_sum(silver, gold)
        else:
            return golden_sum(bronze, silver, gold)
    
    if silver is None:
        return gold
    elif bronze is None:
        return PHI*gold + (1-PHI)*silver
    else:
        if symmetric:
            return golden_sum(golden_sum(gold, bronze), silver) # This is equivalent to returning ~(.382*gold + .236*bronze + .382*silver)~ which is symmetric! The philosophy here is that the 1st parameter should be goldy (gold or a gold alloy) and the 2nd parameter not goldy!
        return golden_sum(gold, golden_sum(silver, bronze))   ### This is equivalent to returning ~(.618*gold + .236*silver + .146*bronze)~ which is not symmetric! The philosophy here is that the more valuable/important the parameter, the higher its coefficient!



def calculate_central_tendency_and_deviation(arr, type="mean"):
    if len(arr) == 0:
        return 0.0, 0.0
    if type == "median":
        median = np.median(arr) 
        deviations_from_median = np.abs(arr - median)
        med_devs = np.median(deviations_from_median)
        return median, med_devs
    else:
        mean = np.mean(arr)
        deviations_from_mean = np.abs(arr - mean)
        mean_devs = np.mean(deviations_from_mean)
        return mean, mean_devs



def Z(series, type="standard"): ### Z-score of series
    if type == 'modified':
        med, med_devs = calculate_central_tendency_and_deviation(series, "median")
        return np.zeros_like(series) if med_devs == 0 else ((series - med) / med_devs).round(11)
    else:
        return ((series - series.mean())/series.std()).round(11)
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
players_stats = []
for player in players:
    player_dict = {}
    player_dict['id'] = player['id']
    player_dict['1st_name'] = player['first_name']
    player_dict['2nd_name'] = player['second_name']
    player_dict['position'] = positions_dict[player['element_type']] 
    player_dict['team'] = teams_dict[player['team']]  
    if prvGWsPtsTrendAvailability:
        player_dict['prvGWsPtsTrend'] = prvGWsPtsTrend_dict.get(player_dict['id'], '?')
    else:
        player_dict['prvGWsPtsTrend'] = '?'
    player_dict['web_name'] = player['web_name'] + f" ({player_dict['position']}, {player_dict['prvGWsPtsTrend']})"
    players_stats.append(player_dict)
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
players_fixturesPts_dict = {}
players_fixturesMinutes_dict = {}
players_fixturesGoalsScored_dict = {}
players_fixturesGoalsConceded_dict = {}
players_fixturesOwnGoals_dict = {}
players_fixturesAssists_dict = {}
players_fixturesCleanSheets_dict = {}
players_fixturesSaves_dict = {}
players_fixturesPenaltiesSaved_dict = {}
players_fixturesPenaltiesMissed_dict = {}
players_fixturesYellowCards_dict = {}
players_fixturesRedCards_dict = {}
players_fixturesBonus_dict = {}

for gw in range(1, refGW): ### fetch per-gameweek data for all players
    response = requests.get(gameweeks_info_url.format(gw))
    gwData = response.json()
    elements = gwData['elements']
    for element in elements:
        player_id = element['id']
        if player_id not in players_fixturesPts_dict:
            players_fixturesPts_dict[player_id] = [[],[]]
            players_fixturesMinutes_dict[player_id] = [[],[]]
            players_fixturesGoalsScored_dict[player_id] = [[],[]]
            players_fixturesGoalsConceded_dict[player_id] = [[],[]]
            players_fixturesOwnGoals_dict[player_id] = [[],[]]
            players_fixturesAssists_dict[player_id] = [[],[]]
            players_fixturesCleanSheets_dict[player_id] = [[],[]]
            players_fixturesSaves_dict[player_id] = [[],[]]
            players_fixturesPenaltiesSaved_dict[player_id] = [[],[]]
            players_fixturesPenaltiesMissed_dict[player_id] = [[],[]]
            players_fixturesYellowCards_dict[player_id] = [[],[]]
            players_fixturesRedCards_dict[player_id] = [[],[]]
            players_fixturesBonus_dict[player_id] = [[],[]]
        player_team = teams_dict[players_dict[player_id]['team']]
        player_position = positions_dict[players_dict[player_id]['element_type']]
        element_stats = element['stats']
        gwMinutes = element_stats['minutes']
        if gwMinutes == 0:
            players_fixturesPts_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPts_dict[player_id][1].append(None)
            players_fixturesMinutes_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesMinutes_dict[player_id][1].append(None)
            players_fixturesGoalsScored_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesGoalsScored_dict[player_id][1].append(None)
            players_fixturesGoalsConceded_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesGoalsConceded_dict[player_id][1].append(None)
            players_fixturesOwnGoals_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesOwnGoals_dict[player_id][1].append(None)
            players_fixturesAssists_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesAssists_dict[player_id][1].append(None)
            players_fixturesCleanSheets_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesCleanSheets_dict[player_id][1].append(None)
            players_fixturesSaves_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesSaves_dict[player_id][1].append(None)
            players_fixturesPenaltiesSaved_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPenaltiesSaved_dict[player_id][1].append(None)
            players_fixturesPenaltiesMissed_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPenaltiesMissed_dict[player_id][1].append(None)
            players_fixturesYellowCards_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesYellowCards_dict[player_id][1].append(None)
            players_fixturesRedCards_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesRedCards_dict[player_id][1].append(None)
            players_fixturesBonus_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesBonus_dict[player_id][1].append(None)
        else:
            gwFixtures = element['explain']
            for gwFixture in gwFixtures: ### sometimes we have 2ble gameweeks!
                fixture_id = gwFixture['fixture']
                fixture_stats = gwFixture['stats']
                fixture_pts = sum(fixture_stat['points'] for fixture_stat in fixture_stats)
                fixture_minutes = fixture_stats[0]['value'] if fixture_stats[0]['identifier'] == 'minutes' else None
                #-------THE CODE BELOW CAN ONLY WORK BEFORE THERE ARE 2BLE GAMEWEEKS-------------------------------#
                fixture_goals_scored = element_stats['goals_scored']
                fixture_goals_conceded = element_stats['goals_conceded']
                fixture_own_goals = element_stats['own_goals']
                fixture_assists = element_stats['assists']
                fixture_clean_sheets = element_stats['clean_sheets']
                fixture_saves = element_stats['saves']
                fixture_penalties_saved = element_stats['penalties_saved']
                fixture_penalties_missed = element_stats['penalties_missed']
                fixture_yellow_cards = element_stats['yellow_cards']
                fixture_red_cards = element_stats['red_cards']
                fixture_bonus = element_stats['bonus']
                #-------THE CODE ABOVE CAN ONLY WORK BEFORE THERE ARE 2BLE GAMEWEEKS-------------------------------#
                if fixture_minutes > 0: ### if the player actually played in that fixture        
                    players_fixturesPts_dict[player_id][0].append(fixture_pts) if gw < form_refGW else players_fixturesPts_dict[player_id][1].append(fixture_pts)
                    players_fixturesMinutes_dict[player_id][0].append(fixture_minutes) if gw < form_refGW else players_fixturesMinutes_dict[player_id][1].append(fixture_minutes)
                    players_fixturesGoalsScored_dict[player_id][0].append(fixture_goals_scored) if gw < form_refGW else players_fixturesGoalsScored_dict[player_id][1].append(fixture_goals_scored)
                    players_fixturesGoalsConceded_dict[player_id][0].append(fixture_goals_conceded) if gw < form_refGW else players_fixturesGoalsConceded_dict[player_id][1].append(fixture_goals_conceded)
                    players_fixturesOwnGoals_dict[player_id][0].append(fixture_own_goals) if gw < form_refGW else players_fixturesOwnGoals_dict[player_id][1].append(fixture_own_goals)
                    players_fixturesAssists_dict[player_id][0].append(fixture_assists) if gw < form_refGW else players_fixturesAssists_dict[player_id][1].append(fixture_assists)
                    players_fixturesCleanSheets_dict[player_id][0].append(fixture_clean_sheets) if gw < form_refGW else players_fixturesCleanSheets_dict[player_id][1].append(fixture_clean_sheets)
                    players_fixturesSaves_dict[player_id][0].append(fixture_saves) if gw < form_refGW else players_fixturesSaves_dict[player_id][1].append(fixture_saves)
                    players_fixturesPenaltiesSaved_dict[player_id][0].append(fixture_penalties_saved) if gw < form_refGW else players_fixturesPenaltiesSaved_dict[player_id][1].append(fixture_penalties_saved)
                    players_fixturesPenaltiesMissed_dict[player_id][0].append(fixture_penalties_missed) if gw < form_refGW else players_fixturesPenaltiesMissed_dict[player_id][1].append(fixture_penalties_missed)
                    players_fixturesYellowCards_dict[player_id][0].append(fixture_yellow_cards) if gw < form_refGW else players_fixturesYellowCards_dict[player_id][1].append(fixture_yellow_cards)
                    players_fixturesRedCards_dict[player_id][0].append(fixture_red_cards) if gw < form_refGW else players_fixturesRedCards_dict[player_id][1].append(fixture_red_cards)
                    players_fixturesBonus_dict[player_id][0].append(fixture_bonus) if gw < form_refGW else players_fixturesBonus_dict[player_id][1].append(fixture_bonus)
                else:
                    players_fixturesPts_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPts_dict[player_id][1].append(None)
                    players_fixturesMinutes_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesMinutes_dict[player_id][1].append(None)
                    players_fixturesGoalsScored_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesGoalsScored_dict[player_id][1].append(None)
                    players_fixturesGoalsConceded_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesGoalsConceded_dict[player_id][1].append(None)
                    players_fixturesOwnGoals_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesOwnGoals_dict[player_id][1].append(None)
                    players_fixturesAssists_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesAssists_dict[player_id][1].append(None)
                    players_fixturesCleanSheets_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesCleanSheets_dict[player_id][1].append(None)
                    players_fixturesSaves_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesSaves_dict[player_id][1].append(None)
                    players_fixturesPenaltiesSaved_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPenaltiesSaved_dict[player_id][1].append(None)
                    players_fixturesPenaltiesMissed_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesPenaltiesMissed_dict[player_id][1].append(None)
                    players_fixturesYellowCards_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesYellowCards_dict[player_id][1].append(None)
                    players_fixturesRedCards_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesRedCards_dict[player_id][1].append(None)
                    players_fixturesBonus_dict[player_id][0].append(None) if gw < form_refGW else players_fixturesBonus_dict[player_id][1].append(None)
                if fixture_id in teams_fixturesPtsFor_dict[player_team][gw-1]:
                    teams_fixturesPtsFor_dict[player_team][gw-1][fixture_id] += fixture_pts
                    (teams_fixturesDefPts_dict if player_position in ['GKP', 'DEF'] else teams_fixturesAttPts_dict)[player_team][gw-1][fixture_id] += fixture_pts

players_fixturesPlayedPts_dict = {player_id: [pts for pts in (fixturesPts[0] + fixturesPts[1]) if pts is not None] for player_id, fixturesPts in players_fixturesPts_dict.items()}
players_fixturesPlayedMinutes_dict = {player_id: [mins for mins in (fixturesMins[0] + fixturesMins[1]) if mins is not None] for player_id, fixturesMins in players_fixturesMinutes_dict.items()}
players_fixturesPlayedGoalsScored_dict = {player_id: [gs for gs in (fixturesGS[0] + fixturesGS[1]) if gs is not None] for player_id, fixturesGS in players_fixturesGoalsScored_dict.items()}
players_fixturesPlayedGoalsConceded_dict = {player_id: [gc for gc in (fixturesGC[0] + fixturesGC[1]) if gc is not None] for player_id, fixturesGC in players_fixturesGoalsConceded_dict.items()}
players_fixturesPlayedOwnGoals_dict = {player_id: [ogs for ogs in (fixturesOGS[0] + fixturesOGS[1]) if ogs is not None] for player_id, fixturesOGS in players_fixturesOwnGoals_dict.items()}
players_fixturesPlayedAssists_dict = {player_id: [assists for assists in (fixturesAssists[0] + fixturesAssists[1]) if assists is not None] for player_id, fixturesAssists in players_fixturesAssists_dict.items()}
players_fixturesPlayedCleanSheets_dict = {player_id: [cs for cs in (fixturesCS[0] + fixturesCS[1]) if cs is not None] for player_id, fixturesCS in players_fixturesCleanSheets_dict.items()}
players_fixturesPlayedSaves_dict = {player_id: [svs for svs in (fixturesSVS[0] + fixturesSVS[1]) if svs is not None] for player_id, fixturesSVS in players_fixturesSaves_dict.items()}
players_fixturesPlayedPenaltiesSaved_dict = {player_id: [ps for ps in (fixturesPS[0] + fixturesPS[1]) if ps is not None] for player_id, fixturesPS in players_fixturesPenaltiesSaved_dict.items()}
players_fixturesPlayedPenaltiesMissed_dict = {player_id: [pm for pm in (fixturesPM[0] + fixturesPM[1]) if pm is not None] for player_id, fixturesPM in players_fixturesPenaltiesMissed_dict.items()}
players_fixturesPlayedYellowCards_dict = {player_id: [ycs for ycs in (fixturesYCS[0] + fixturesYCS[1]) if ycs is not None] for player_id, fixturesYCS in players_fixturesYellowCards_dict.items()}
players_fixturesPlayedRedCards_dict = {player_id: [rcs for rcs in (fixturesRCS[0] + fixturesRCS[1]) if rcs is not None] for player_id, fixturesRCS in players_fixturesRedCards_dict.items()}
players_fixturesPlayedBonus_dict = {player_id: [bpts for bpts in (fixturesBPts[0] + fixturesBPts[1]) if bpts is not None] for player_id, fixturesBPts in players_fixturesBonus_dict.items()}

players_formFixturesPts_dict = {player_id: [0 if pts is None else pts for pts in fixturesPts[1]] for player_id, fixturesPts in players_fixturesPts_dict.items()}
players_formFixturesMinutes_dict = {player_id: [0 if mins is None else mins for mins in fixturesMins[1]] for player_id, fixturesMins in players_fixturesMinutes_dict.items()}
players_formFixturesGoalsScored_dict = {player_id: [0 if gs is None else gs for gs in fixturesGS[1]] for player_id, fixturesGS in players_fixturesGoalsScored_dict.items()}
players_formFixturesGoalsConceded_dict = {player_id: [0 if gc is None else gc for gc in fixturesGC[1]] for player_id, fixturesGC in players_fixturesGoalsConceded_dict.items()}
players_formFixturesOwnGoals_dict = {player_id: [0 if ogs is None else ogs for ogs in fixturesOGS[1]] for player_id, fixturesOGS in players_fixturesOwnGoals_dict.items()}
players_formFixturesAssists_dict = {player_id: [0 if assists is None else assists for assists in fixturesAssists[1]] for player_id, fixturesAssists in players_fixturesAssists_dict.items()}
players_formFixturesCleanSheets_dict = {player_id: [0 if cs is None else cs for cs in fixturesCS[1]] for player_id, fixturesCS in players_fixturesCleanSheets_dict.items()}
players_formFixturesSaves_dict = {player_id: [0 if svs is None else svs for svs in fixturesSVS[1]] for player_id, fixturesSVS in players_fixturesSaves_dict.items()}
players_formFixturesPenaltiesSaved_dict = {player_id: [0 if ps is None else ps for ps in fixturesPS[1]] for player_id, fixturesPS in players_fixturesPenaltiesSaved_dict.items()}
players_formFixturesPenaltiesMissed_dict = {player_id: [0 if pm is None else pm for pm in fixturesPM[1]] for player_id, fixturesPM in players_fixturesPenaltiesMissed_dict.items()}
players_formFixturesYellowCards_dict = {player_id: [0 if ycs is None else ycs for ycs in fixturesYCS[1]] for player_id, fixturesYCS in players_fixturesYellowCards_dict.items()}
players_formFixturesRedCards_dict = {player_id: [0 if rcs is None else rcs for rcs in fixturesRCS[1]] for player_id, fixturesRCS in players_fixturesRedCards_dict.items()}
players_formFixturesBonus_dict = {player_id: [0 if bpts is None else bpts for bpts in fixturesBPts[1]] for player_id, fixturesBPts in players_fixturesBonus_dict.items()}

#---------------------------------------------------------------------------------------------------------#
gkp_GS_pts = 10
def_GS_pts = 6
mid_GS_pts = 5
fwd_GS_pts = 4
#---------------------------------------------------------------------------------------------------------#
gkp_GC_pts = def_GC_pts = -1/2
mid_GC_pts = fwd_GC_pts = 0
#---------------------------------------------------------------------------------------------------------#
gkp_OG_pts = def_OG_pts = mid_OG_pts = fwd_OG_pts = -2
#---------------------------------------------------------------------------------------------------------#
gkp_A_pts = def_A_pts = mid_A_pts = fwd_A_pts = 3
#---------------------------------------------------------------------------------------------------------#
gkp_CS_pts = def_CS_pts = 4
mid_CS_pts = 1
fwd_CS_pts = 0
#---------------------------------------------------------------------------------------------------------#
gkp_S_pts = 1/3
def_S_pts = mid_S_pts = fwd_S_pts = 0
#---------------------------------------------------------------------------------------------------------#
gkp_PS_pts = def_PS_pts = mid_PS_pts = fwd_PS_pts = 5
#---------------------------------------------------------------------------------------------------------#
gkp_PM_pts = def_PM_pts = mid_PM_pts = fwd_PM_pts = -2
#---------------------------------------------------------------------------------------------------------#
gkp_YC_pts = def_YC_pts = mid_YC_pts = fwd_YC_pts = -1
#---------------------------------------------------------------------------------------------------------#
gkp_RC_pts = def_RC_pts = mid_RC_pts = fwd_RC_pts = -3
#---------------------------------------------------------------------------------------------------------#
gkp_BP_pts = def_BP_pts = mid_BP_pts = fwd_BP_pts = 1
#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#
action_pts_dict = { 
    'GKP': {
        'GS':   gkp_GS_pts, 
        'GC':   gkp_GC_pts, 
        'OG':   gkp_OG_pts, 
        'A':    gkp_A_pts, 
        'CS':   gkp_CS_pts, 
        'S':    gkp_S_pts, 
        'PS':   gkp_PS_pts, 
        'PM':   gkp_PM_pts, 
        'YC':   gkp_YC_pts, 
        'RC':   gkp_RC_pts,
        'BP':   gkp_BP_pts
    },
    'DEF': {
        'GS':   def_GS_pts, 
        'GC':   def_GC_pts, 
        'OG':   def_OG_pts, 
        'A':    def_A_pts, 
        'CS':   def_CS_pts, 
        'S':    def_S_pts, 
        'PS':   def_PS_pts, 
        'PM':   def_PM_pts, 
        'YC':   def_YC_pts, 
        'RC':   def_RC_pts,
        'BP':   def_BP_pts
    },
    'MID': {
        'GS':   mid_GS_pts, 
        'GC':   mid_GC_pts, 
        'OG':   mid_OG_pts, 
        'A':    mid_A_pts, 
        'CS':   mid_CS_pts, 
        'S':    mid_S_pts, 
        'PS':   mid_PS_pts, 
        'PM':   mid_PM_pts, 
        'YC':   mid_YC_pts, 
        'RC':   mid_RC_pts,
        'BP':   mid_BP_pts
    },
    'FWD': {
        'GS':   fwd_GS_pts, 
        'GC':   fwd_GC_pts, 
        'OG':   fwd_OG_pts, 
        'A':    fwd_A_pts, 
        'CS':   fwd_CS_pts, 
        'S':    fwd_S_pts, 
        'PS':   fwd_PS_pts, 
        'PM':   fwd_PM_pts, 
        'YC':   fwd_YC_pts, 
        'RC':   fwd_RC_pts,
        'BP':   fwd_BP_pts
    }
}
#---------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------------------------------------#
for player_dict in players_stats:
    player_id = player_dict['id']
    #---------------------------------------------------------------------------------------------------------#
    player_fixturesPlayedPts = players_fixturesPlayedPts_dict.get(player_id, [])
    player_fixturesPlayedMinutes = players_fixturesPlayedMinutes_dict.get(player_id, [])
    player_fixturesPlayedGoalsScored = players_fixturesPlayedGoalsScored_dict.get(player_id, [])
    player_fixturesPlayedGoalsConceded = players_fixturesPlayedGoalsConceded_dict.get(player_id, [])
    player_fixturesPlayedOwnGoals = players_fixturesPlayedOwnGoals_dict.get(player_id, [])
    player_fixturesPlayedAssists = players_fixturesPlayedAssists_dict.get(player_id, [])
    player_fixturesPlayedCleanSheets = players_fixturesPlayedCleanSheets_dict.get(player_id, [])
    player_fixturesPlayedSaves = players_fixturesPlayedSaves_dict.get(player_id, [])
    player_fixturesPlayedPenaltiesSaved = players_fixturesPlayedPenaltiesSaved_dict.get(player_id, [])
    player_fixturesPlayedPenaltiesMissed = players_fixturesPlayedPenaltiesMissed_dict.get(player_id, [])
    player_fixturesPlayedYellowCards = players_fixturesPlayedYellowCards_dict.get(player_id, [])
    player_fixturesPlayedRedCards = players_fixturesPlayedRedCards_dict.get(player_id, [])
    player_fixturesPlayedBonus = players_fixturesPlayedBonus_dict.get(player_id, [])
    #---------------------------------------------------------------------------------------------------------#
    player_dict['tot_pts'] = np.sum(player_fixturesPlayedPts, dtype=int)
    player_dict['tot_MP'] = np.sum(player_fixturesPlayedMinutes, dtype=int)
    player_dict['tot_GS'] = np.sum(player_fixturesPlayedGoalsScored, dtype=int)
    player_dict['tot_GC'] = np.sum(player_fixturesPlayedGoalsConceded, dtype=int)
    player_dict['tot_OG'] = np.sum(player_fixturesPlayedOwnGoals, dtype=int)
    player_dict['tot_A'] = np.sum(player_fixturesPlayedAssists, dtype=int)
    player_dict['tot_CS'] = np.sum(player_fixturesPlayedCleanSheets, dtype=int)
    player_dict['tot_S'] = np.sum(player_fixturesPlayedSaves, dtype=int)
    player_dict['tot_PS'] = np.sum(player_fixturesPlayedPenaltiesSaved, dtype=int)
    player_dict['tot_PM'] = np.sum(player_fixturesPlayedPenaltiesMissed, dtype=int)
    player_dict['tot_YC'] = np.sum(player_fixturesPlayedYellowCards, dtype=int)
    player_dict['tot_RC'] = np.sum(player_fixturesPlayedRedCards, dtype=int)
    player_dict['tot_BP'] = np.sum(player_fixturesPlayedBonus, dtype=int)
    #---------------------------------------------------------------------------------------------------------#
    player_dict['fxtrs_plyd'] = len(player_fixturesPlayedPts)
    player_dict['fxtrs_not_plyd'] = matches_played_dict[player_dict['team']] - player_dict['fxtrs_plyd']
    player_fixturesNotPlayedX = player_dict['fxtrs_not_plyd'] * [0]
    #---------------------------------------------------------------------------------------------------------#
    player_formFixturesPts = players_formFixturesPts_dict.get(player_id, [])
    player_formFixturesMinutes = players_formFixturesMinutes_dict.get(player_id, [])
    player_formFixturesGoalsScored = players_formFixturesGoalsScored_dict.get(player_id, [])
    player_formFixturesGoalsConceded = players_formFixturesGoalsConceded_dict.get(player_id, [])
    player_formFixturesOwnGoals = players_formFixturesOwnGoals_dict.get(player_id, [])
    player_formFixturesAssists = players_formFixturesAssists_dict.get(player_id, [])
    player_formFixturesCleanSheets = players_formFixturesCleanSheets_dict.get(player_id, [])
    player_formFixturesSaves = players_formFixturesSaves_dict.get(player_id, [])
    player_formFixturesPenaltiesSaved = players_formFixturesPenaltiesSaved_dict.get(player_id, [])
    player_formFixturesPenaltiesMissed = players_formFixturesPenaltiesMissed_dict.get(player_id, [])
    player_formFixturesYellowCards = players_formFixturesYellowCards_dict.get(player_id, [])
    player_formFixturesRedCards = players_formFixturesRedCards_dict.get(player_id, [])
    player_formFixturesBonus = players_formFixturesBonus_dict.get(player_id, [])
    #######################################################################################################################################################################################################################    
    player_dict['med_formPts'], player_dict['MedAbsDev(formPts)'] = calculate_central_tendency_and_deviation(player_formFixturesPts, "median")
    player_dict['avg_formPts'], player_dict['MeanAbsDev(formPts)'] = calculate_central_tendency_and_deviation(player_formFixturesPts, "mean") ### avg_formPts is a player's average score per match, calculated from all matches played by his club in the last 30 days.
    player_dict['StdDev(formPts)'] = np.std(player_formFixturesPts) if len(player_formFixturesPts) > 0 else 0

    player_dict['med_formMP'], player_dict['MedAbsDev(formMP)'] = calculate_central_tendency_and_deviation(player_formFixturesMinutes, "median")
    player_dict['avg_formMP'], player_dict['MeanAbsDev(formMP)'] = calculate_central_tendency_and_deviation(player_formFixturesMinutes, "mean")
    player_dict['StdDev(formMP)'] = np.std(player_formFixturesMinutes) if len(player_formFixturesMinutes) > 0 else 0

    player_dict['med_formGS'], player_dict['MedAbsDev(formGS)'] = calculate_central_tendency_and_deviation(player_formFixturesGoalsScored, "median")
    player_dict['avg_formGS'], player_dict['MeanAbsDev(formGS)'] = calculate_central_tendency_and_deviation(player_formFixturesGoalsScored, "mean")
    player_dict['StdDev(formGS)'] = np.std(player_formFixturesGoalsScored) if len(player_formFixturesGoalsScored) > 0 else 0

    player_dict['med_formGC'], player_dict['MedAbsDev(formGC)'] = calculate_central_tendency_and_deviation(player_formFixturesGoalsConceded, "median")
    player_dict['avg_formGC'], player_dict['MeanAbsDev(formGC)'] = calculate_central_tendency_and_deviation(player_formFixturesGoalsConceded, "mean")
    player_dict['StdDev(formGC)'] = np.std(player_formFixturesGoalsConceded) if len(player_formFixturesGoalsConceded) > 0 else 0

    player_dict['med_formOG'], player_dict['MedAbsDev(formOG)'] = calculate_central_tendency_and_deviation(player_formFixturesOwnGoals, "median")
    player_dict['avg_formOG'], player_dict['MeanAbsDev(formOG)'] = calculate_central_tendency_and_deviation(player_formFixturesOwnGoals, "mean")
    player_dict['StdDev(formOG)'] = np.std(player_formFixturesOwnGoals) if len(player_formFixturesOwnGoals) > 0 else 0

    player_dict['med_formA'], player_dict['MedAbsDev(formA)'] = calculate_central_tendency_and_deviation(player_formFixturesAssists, "median")
    player_dict['avg_formA'], player_dict['MeanAbsDev(formA)'] = calculate_central_tendency_and_deviation(player_formFixturesAssists, "mean")
    player_dict['StdDev(formA)'] = np.std(player_formFixturesAssists) if len(player_formFixturesAssists) > 0 else 0

    player_dict['med_formCS'], player_dict['MedAbsDev(formCS)'] = calculate_central_tendency_and_deviation(player_formFixturesCleanSheets, "median")
    player_dict['avg_formCS'], player_dict['MeanAbsDev(formCS)'] = calculate_central_tendency_and_deviation(player_formFixturesCleanSheets, "mean")
    player_dict['StdDev(formCS)'] = np.std(player_formFixturesCleanSheets) if len(player_formFixturesCleanSheets) > 0 else 0

    player_dict['med_formS'], player_dict['MedAbsDev(formS)'] = calculate_central_tendency_and_deviation(player_formFixturesSaves, "median")
    player_dict['avg_formS'], player_dict['MeanAbsDev(formS)'] = calculate_central_tendency_and_deviation(player_formFixturesSaves, "mean")
    player_dict['StdDev(formS)'] = np.std(player_formFixturesSaves) if len(player_formFixturesSaves) > 0 else 0

    player_dict['med_formPS'], player_dict['MedAbsDev(formPS)'] = calculate_central_tendency_and_deviation(player_formFixturesPenaltiesSaved, "median")
    player_dict['avg_formPS'], player_dict['MeanAbsDev(formPS)'] = calculate_central_tendency_and_deviation(player_formFixturesPenaltiesSaved, "mean")
    player_dict['StdDev(formPS)'] = np.std(player_formFixturesPenaltiesSaved) if len(player_formFixturesPenaltiesSaved) > 0 else 0

    player_dict['med_formPM'], player_dict['MedAbsDev(formPM)'] = calculate_central_tendency_and_deviation(player_formFixturesPenaltiesMissed, "median")
    player_dict['avg_formPM'], player_dict['MeanAbsDev(formPM)'] = calculate_central_tendency_and_deviation(player_formFixturesPenaltiesMissed, "mean")
    player_dict['StdDev(formPM)'] = np.std(player_formFixturesPenaltiesMissed) if len(player_formFixturesPenaltiesMissed) > 0 else 0

    player_dict['med_formYC'], player_dict['MedAbsDev(formYC)'] = calculate_central_tendency_and_deviation(player_formFixturesYellowCards, "median")
    player_dict['avg_formYC'], player_dict['MeanAbsDev(formYC)'] = calculate_central_tendency_and_deviation(player_formFixturesYellowCards, "mean")
    player_dict['StdDev(formYC)'] = np.std(player_formFixturesYellowCards) if len(player_formFixturesYellowCards) > 0 else 0

    player_dict['med_formRC'], player_dict['MedAbsDev(formRC)'] = calculate_central_tendency_and_deviation(player_formFixturesRedCards, "median")
    player_dict['avg_formRC'], player_dict['MeanAbsDev(formRC)'] = calculate_central_tendency_and_deviation(player_formFixturesRedCards, "mean")
    player_dict['StdDev(formRC)'] = np.std(player_formFixturesRedCards) if len(player_formFixturesRedCards) > 0 else 0

    player_dict['med_formBP'], player_dict['MedAbsDev(formBP)'] = calculate_central_tendency_and_deviation(player_formFixturesBonus, "median")
    player_dict['avg_formBP'], player_dict['MeanAbsDev(formBP)'] = calculate_central_tendency_and_deviation(player_formFixturesBonus, "mean")
    player_dict['StdDev(formBP)'] = np.std(player_formFixturesBonus) if len(player_formFixturesBonus) > 0 else 0
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    player_dict['med_pts/fxtr'], player_dict['MedAbsDev(pts/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPts + player_fixturesNotPlayedX, "median")
    player_dict['avg_pts/fxtr'], player_dict['MeanAbsDev(pts/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPts + player_fixturesNotPlayedX, "mean") ### avg_pts/fxtr is a player's average score per match, calculated from all matches played by his club throughout the whole season.
    player_dict['StdDev(pts/fxtr)'] = np.std(player_fixturesPlayedPts + player_fixturesNotPlayedX) if len(player_fixturesPlayedPts + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_MP/fxtr'], player_dict['MedAbsDev(MP/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedMinutes + player_fixturesNotPlayedX, "median")
    player_dict['avg_MP/fxtr'], player_dict['MeanAbsDev(MP/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedMinutes + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(MP/fxtr)'] = np.std(player_fixturesPlayedMinutes + player_fixturesNotPlayedX) if len(player_fixturesPlayedMinutes + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_GS/fxtr'], player_dict['MedAbsDev(GS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsScored + player_fixturesNotPlayedX, "median")
    player_dict['avg_GS/fxtr'], player_dict['MeanAbsDev(GS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsScored + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(GS/fxtr)'] = np.std(player_fixturesPlayedGoalsScored + player_fixturesNotPlayedX) if len(player_fixturesPlayedGoalsScored + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_GC/fxtr'], player_dict['MedAbsDev(GC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsConceded + player_fixturesNotPlayedX, "median")
    player_dict['avg_GC/fxtr'], player_dict['MeanAbsDev(GC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsConceded + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(GC/fxtr)'] = np.std(player_fixturesPlayedGoalsConceded + player_fixturesNotPlayedX) if len(player_fixturesPlayedGoalsConceded + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_OG/fxtr'], player_dict['MedAbsDev(OG/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedOwnGoals + player_fixturesNotPlayedX, "median")
    player_dict['avg_OG/fxtr'], player_dict['MeanAbsDev(OG/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedOwnGoals + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(OG/fxtr)'] = np.std(player_fixturesPlayedOwnGoals + player_fixturesNotPlayedX) if len(player_fixturesPlayedOwnGoals + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_A/fxtr'], player_dict['MedAbsDev(A/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedAssists + player_fixturesNotPlayedX, "median")
    player_dict['avg_A/fxtr'], player_dict['MeanAbsDev(A/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedAssists + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(A/fxtr)'] = np.std(player_fixturesPlayedAssists + player_fixturesNotPlayedX) if len(player_fixturesPlayedAssists + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_CS/fxtr'], player_dict['MedAbsDev(CS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedCleanSheets + player_fixturesNotPlayedX, "median")
    player_dict['avg_CS/fxtr'], player_dict['MeanAbsDev(CS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedCleanSheets + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(CS/fxtr)'] = np.std(player_fixturesPlayedCleanSheets + player_fixturesNotPlayedX) if len(player_fixturesPlayedCleanSheets + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_S/fxtr'], player_dict['MedAbsDev(S/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedSaves + player_fixturesNotPlayedX, "median")
    player_dict['avg_S/fxtr'], player_dict['MeanAbsDev(S/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedSaves + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(S/fxtr)'] = np.std(player_fixturesPlayedSaves + player_fixturesNotPlayedX) if len(player_fixturesPlayedSaves + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_PS/fxtr'], player_dict['MedAbsDev(PS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesSaved + player_fixturesNotPlayedX, "median")
    player_dict['avg_PS/fxtr'], player_dict['MeanAbsDev(PS/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesSaved + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(PS/fxtr)'] = np.std(player_fixturesPlayedPenaltiesSaved + player_fixturesNotPlayedX) if len(player_fixturesPlayedPenaltiesSaved + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_PM/fxtr'], player_dict['MedAbsDev(PM/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesMissed + player_fixturesNotPlayedX, "median")
    player_dict['avg_PM/fxtr'], player_dict['MeanAbsDev(PM/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesMissed + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(PM/fxtr)'] = np.std(player_fixturesPlayedPenaltiesMissed + player_fixturesNotPlayedX) if len(player_fixturesPlayedPenaltiesMissed + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_YC/fxtr'], player_dict['MedAbsDev(YC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedYellowCards + player_fixturesNotPlayedX, "median")
    player_dict['avg_YC/fxtr'], player_dict['MeanAbsDev(YC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedYellowCards + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(YC/fxtr)'] = np.std(player_fixturesPlayedYellowCards + player_fixturesNotPlayedX) if len(player_fixturesPlayedYellowCards + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_RC/fxtr'], player_dict['MedAbsDev(RC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedRedCards + player_fixturesNotPlayedX, "median")
    player_dict['avg_RC/fxtr'], player_dict['MeanAbsDev(RC/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedRedCards + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(RC/fxtr)'] = np.std(player_fixturesPlayedRedCards + player_fixturesNotPlayedX) if len(player_fixturesPlayedRedCards + player_fixturesNotPlayedX) > 0 else 0

    player_dict['med_BP/fxtr'], player_dict['MedAbsDev(BP/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedBonus + player_fixturesNotPlayedX, "median")
    player_dict['avg_BP/fxtr'], player_dict['MeanAbsDev(BP/fxtr)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedBonus + player_fixturesNotPlayedX, "mean")
    player_dict['StdDev(BP/fxtr)'] = np.std(player_fixturesPlayedBonus + player_fixturesNotPlayedX) if len(player_fixturesPlayedBonus + player_fixturesNotPlayedX) > 0 else 0
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    player_dict['med_pts/fxtr_plyd'], player_dict['MedAbsDev(pts/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPts, "median")
    player_dict['avg_pts/fxtr_plyd'], player_dict['MeanAbsDev(pts/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPts, "mean")
    player_dict['StdDev(pts/fxtr_plyd)'] = np.std(player_fixturesPlayedPts) if len(player_fixturesPlayedPts) > 0 else 0

    player_dict['med_MP/fxtr_plyd'], player_dict['MedAbsDev(MP/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedMinutes, "median")
    player_dict['avg_MP/fxtr_plyd'], player_dict['MeanAbsDev(MP/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedMinutes, "mean")
    player_dict['StdDev(MP/fxtr_plyd)'] = np.std(player_fixturesPlayedMinutes) if len(player_fixturesPlayedMinutes) > 0 else 0

    player_dict['med_GS/fxtr_plyd'], player_dict['MedAbsDev(GS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsScored, "median")
    player_dict['avg_GS/fxtr_plyd'], player_dict['MeanAbsDev(GS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsScored, "mean")
    player_dict['StdDev(GS/fxtr_plyd)'] = np.std(player_fixturesPlayedGoalsScored) if len(player_fixturesPlayedGoalsScored) > 0 else 0

    player_dict['med_GC/fxtr_plyd'], player_dict['MedAbsDev(GC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsConceded, "median")
    player_dict['avg_GC/fxtr_plyd'], player_dict['MeanAbsDev(GC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedGoalsConceded, "mean")
    player_dict['StdDev(GC/fxtr_plyd)'] = np.std(player_fixturesPlayedGoalsConceded) if len(player_fixturesPlayedGoalsConceded) > 0 else 0

    player_dict['med_OG/fxtr_plyd'], player_dict['MedAbsDev(OG/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedOwnGoals, "median")
    player_dict['avg_OG/fxtr_plyd'], player_dict['MeanAbsDev(OG/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedOwnGoals, "mean")
    player_dict['StdDev(OG/fxtr_plyd)'] = np.std(player_fixturesPlayedOwnGoals) if len(player_fixturesPlayedOwnGoals) > 0 else 0

    player_dict['med_A/fxtr_plyd'], player_dict['MedAbsDev(A/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedAssists, "median")
    player_dict['avg_A/fxtr_plyd'], player_dict['MeanAbsDev(A/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedAssists, "mean")
    player_dict['StdDev(A/fxtr_plyd)'] = np.std(player_fixturesPlayedAssists) if len(player_fixturesPlayedAssists) > 0 else 0

    player_dict['med_CS/fxtr_plyd'], player_dict['MedAbsDev(CS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedCleanSheets, "median")
    player_dict['avg_CS/fxtr_plyd'], player_dict['MeanAbsDev(CS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedCleanSheets, "mean")
    player_dict['StdDev(CS/fxtr_plyd)'] = np.std(player_fixturesPlayedCleanSheets) if len(player_fixturesPlayedCleanSheets) > 0 else 0

    player_dict['med_S/fxtr_plyd'], player_dict['MedAbsDev(S/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedSaves, "median")
    player_dict['avg_S/fxtr_plyd'], player_dict['MeanAbsDev(S/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedSaves, "mean")
    player_dict['StdDev(S/fxtr_plyd)'] = np.std(player_fixturesPlayedSaves) if len(player_fixturesPlayedSaves) > 0 else 0

    player_dict['med_PS/fxtr_plyd'], player_dict['MedAbsDev(PS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesSaved, "median")
    player_dict['avg_PS/fxtr_plyd'], player_dict['MeanAbsDev(PS/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesSaved, "mean")
    player_dict['StdDev(PS/fxtr_plyd)'] = np.std(player_fixturesPlayedPenaltiesSaved) if len(player_fixturesPlayedPenaltiesSaved) > 0 else 0

    player_dict['med_PM/fxtr_plyd'], player_dict['MedAbsDev(PM/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesMissed, "median")
    player_dict['avg_PM/fxtr_plyd'], player_dict['MeanAbsDev(PM/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedPenaltiesMissed, "mean")
    player_dict['StdDev(PM/fxtr_plyd)'] = np.std(player_fixturesPlayedPenaltiesMissed) if len(player_fixturesPlayedPenaltiesMissed) > 0 else 0

    player_dict['med_YC/fxtr_plyd'], player_dict['MedAbsDev(YC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedYellowCards, "median")
    player_dict['avg_YC/fxtr_plyd'], player_dict['MeanAbsDev(YC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedYellowCards, "mean")
    player_dict['StdDev(YC/fxtr_plyd)'] = np.std(player_fixturesPlayedYellowCards) if len(player_fixturesPlayedYellowCards) > 0 else 0

    player_dict['med_RC/fxtr_plyd'], player_dict['MedAbsDev(RC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedRedCards, "median")
    player_dict['avg_RC/fxtr_plyd'], player_dict['MeanAbsDev(RC/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedRedCards, "mean")
    player_dict['StdDev(RC/fxtr_plyd)'] = np.std(player_fixturesPlayedRedCards) if len(player_fixturesPlayedRedCards) > 0 else 0

    player_dict['med_BP/fxtr_plyd'], player_dict['MedAbsDev(BP/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedBonus, "median")
    player_dict['avg_BP/fxtr_plyd'], player_dict['MeanAbsDev(BP/fxtr_plyd)'] = calculate_central_tendency_and_deviation(player_fixturesPlayedBonus, "mean")
    player_dict['StdDev(BP/fxtr_plyd)'] = np.std(player_fixturesPlayedBonus) if len(player_fixturesPlayedBonus) > 0 else 0
    #######################################################################################################################################################################################################################
    player_position = player_dict['position']
    
    #-------------------------------------------------------------------------------------------------#
    # print(player_dict['web_name'])
    #-------------------------------------------------------------------------------------------------#
    for i in ['form', '/fxtr', '/fxtr_plyd']:    
        for j in ['med', 'MedAbsDev', 'avg', 'MeanAbsDev', 'StdDev']:
            i_str = ((i == 'form') * (i + 'Pts')) + ((i != 'form') * ('pts' + i))
            ij_str = 'x(' + ((j + '_' + i_str) if (j == 'med' or j == 'avg') else (j + '(' + i_str + ')')) + ')'
            ij_pts = 0
            for k in ['MP', 'GS', 'GC', 'OG', 'A', 'CS', 'S', 'PS', 'PM', 'YC', 'RC', 'BP']:
                ik_str = ((i == 'form') * (i + k)) + ((i != 'form') * (k + i))
                ijk_str = (j + '_' + ik_str) if (j == 'med' or j == 'avg') else (j + '(' + ik_str + ')')
                x = player_dict[ijk_str]
                y = (k == 'MP') * golden_sum((x/30 + 1) * x/180, math.ceil((x/30 + 1) * x/180)) ### math.ceil((x/30 + 1) * x/180) <==> (x > 0 and x < 60) * 1 + (x >= 60) * 2)
                ijk_pts = (x * action_pts_dict[player_position][k]) if k != 'MP' else y
                if j == 'MedAbsDev' or j == 'MeanAbsDev' or j == 'StdDev':
                    ijk_pts = abs(ijk_pts)
                ij_pts += ijk_pts
                #-------------------------------------------------------------------------------------------------#
                # print(ijk_str + ':\t\t' + str(x) + "\t==>\t" + str(ijk_pts) + ' pts')
                #-------------------------------------------------------------------------------------------------#
            player_dict[ij_str] = ij_pts
            #-------------------------------------------------------------------------------------------------#
            # print(ij_str + ':\t\t\t==>\t' + str(ij_pts) + ' pts')
            # abc = ((j + '_' + i_str) if (j == 'med' or j == 'avg') else (j + '(' + i_str + ')'))
            # print(abc + ':\t\t\t==>\t' + str(player_dict[abc]) + ' pts')
            # input()
            #-------------------------------------------------------------------------------------------------#

players_df = pd.DataFrame(players_stats).set_index('id', drop=False)
players_df = players_df.sort_values([
    'team',

    'x(med_formPts)',              'x(avg_formPts)',
    'x(med_pts/fxtr)',             'x(avg_pts/fxtr)',
    'x(med_pts/fxtr_plyd)',        'x(avg_pts/fxtr_plyd)',

    'tot_pts', ### I really hope this is the last sorting criteria!!! I wouldn't like the sorting to resort to the criteria below bcoz they might be problematic!!!

    'x(MedAbsDev(formPts))',       'x(MeanAbsDev(formPts))',          'x(StdDev(formPts))',
    'x(MedAbsDev(pts/fxtr))',      'x(MeanAbsDev(pts/fxtr))',         'x(StdDev(pts/fxtr))',
    'x(MedAbsDev(pts/fxtr_plyd))', 'x(MeanAbsDev(pts/fxtr_plyd))',    'x(StdDev(pts/fxtr_plyd))',
], 
ascending=[
    True, 

    False, False,
    False, False,
    False, False,
    
    False,
    
    False, False, False,
    False, False, False,
    False, False, False,
]) # 'avg_formPts' gives you info on which players might be currently <appearing>/<playing well> or not
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
for home_team in teams_fixturesPtsAgainst_dict:
    for i in range(len(teams_fixturesPtsAgainst_dict[home_team])):
        for fixture_id in teams_fixturesPtsAgainst_dict[home_team][i]:
            away_team = teams_fixturesPtsAgainst_dict[home_team][i][fixture_id]
            away_team_pts = teams_fixturesPtsFor_dict[away_team][i][fixture_id]
            teams_fixturesPtsAgainst_dict[home_team][i][fixture_id] = away_team_pts
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_fixturesPtsFor_dict = {
    team: [list(dictionary.values()) for dictionary in array_of_dictionaries] for team, array_of_dictionaries in teams_fixturesPtsFor_dict.items()
}
teams_fixturesPtsAgainst_dict = {
    team: [list(dictionary.values()) for dictionary in array_of_dictionaries] for team, array_of_dictionaries in teams_fixturesPtsAgainst_dict.items()
}
teams_fixturesDefPts_dict = {
    team: [list(dictionary.values()) for dictionary in array_of_dictionaries] for team, array_of_dictionaries in teams_fixturesDefPts_dict.items()
}
teams_fixturesAttPts_dict = {
    team: [list(dictionary.values()) for dictionary in array_of_dictionaries] for team, array_of_dictionaries in teams_fixturesAttPts_dict.items()
}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_fixturesPtsFor_dict = {
    team: [[item for sublist in list_of_lists[0:form_refGW-1] for item in sublist], [item for sublist in list_of_lists[form_refGW-1:] for item in sublist]] for team, list_of_lists in teams_fixturesPtsFor_dict.items()
}
teams_fixturesPtsAgainst_dict = {
    team: [[item for sublist in list_of_lists[0:form_refGW-1] for item in sublist], [item for sublist in list_of_lists[form_refGW-1:] for item in sublist]] for team, list_of_lists in teams_fixturesPtsAgainst_dict.items()
}
teams_fixturesDefPts_dict = {
    team: [[item for sublist in list_of_lists[0:form_refGW-1] for item in sublist], [item for sublist in list_of_lists[form_refGW-1:] for item in sublist]] for team, list_of_lists in teams_fixturesDefPts_dict.items()
}
teams_fixturesAttPts_dict = {
    team: [[item for sublist in list_of_lists[0:form_refGW-1] for item in sublist], [item for sublist in list_of_lists[form_refGW-1:] for item in sublist]] for team, list_of_lists in teams_fixturesAttPts_dict.items()
}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_formFixturesPtsFor_dict = {team: team_pts[1] for team, team_pts in teams_fixturesPtsFor_dict.items()}
teams_formFixturesPtsAgainst_dict = {team: team_ptsAgainst[1] for team, team_ptsAgainst in teams_fixturesPtsAgainst_dict.items()}
teams_formFixturesDefPts_dict = {team: team_pts[1] for team, team_pts in teams_fixturesDefPts_dict.items()}
teams_formFixturesAttPts_dict = {team: team_pts[1] for team, team_pts in teams_fixturesAttPts_dict.items()}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_fixturesPtsFor_dict = {team: team_pts[0] + team_pts[1] for team, team_pts in teams_fixturesPtsFor_dict.items()}
teams_fixturesPtsAgainst_dict = {team: team_ptsAgainst[0] + team_ptsAgainst[1] for team, team_ptsAgainst in teams_fixturesPtsAgainst_dict.items()}
teams_fixturesDefPts_dict = {team: team_pts[0] + team_pts[1] for team, team_pts in teams_fixturesDefPts_dict.items()}
teams_fixturesAttPts_dict = {team: team_pts[0] + team_pts[1] for team, team_pts in teams_fixturesAttPts_dict.items()}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
teams_fixturesPtsDiff_dict = {
    team: [
        ptsFor - ptsAgainst for ptsFor, ptsAgainst in zip(teams_fixturesPtsFor_dict[team], teams_fixturesPtsAgainst_dict[team])
    ]
    for team in teams_fixturesPtsDiff_dict
}
teams_formFixturesPtsDiff_dict = {
    team: [
        ptsFor - ptsAgainst for ptsFor, ptsAgainst in zip(teams_formFixturesPtsFor_dict[team], teams_formFixturesPtsAgainst_dict[team])
    ]
    for team in teams_formFixturesPtsFor_dict
}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# print(teams_fixturesPtsFor_dict)
# print("\n\n\n")
# print(teams_fixturesPtsAgainst_dict)
# print("\n\n\n")
# print(teams_fixturesPtsDiff_dict)
# print("\n\n\n")

# print(teams_formFixturesPtsFor_dict)
# print("\n\n\n")
# print(teams_formFixturesPtsAgainst_dict)
# print("\n\n\n")
# print(teams_formFixturesPtsDiff_dict)
# print("\n\n\n")

# print(teams_fixturesDefPts_dict)
# print("\n\n\n")
# print(teams_fixturesAttPts_dict)
# print("\n\n\n")

# print(teams_formFixturesDefPts_dict)
# print("\n\n\n")
# print(teams_formFixturesAttPts_dict)
# print("\n\n\n")

# print(players_df.loc[(players_df['team'] == 'MCI')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'ARS')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'LIV')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'SOU')].head(37).to_string(index=False))
# print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
teams_stats_df = pd.DataFrame.from_dict(teams_dict, orient='index', columns=['team']).rename_axis('team_id')

teams_stats_df['matches_played'] = teams_stats_df['team'].map(matches_played_dict)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['fpl_pts'] = teams_stats_df['team'].map(lambda team: np.sum(teams_fixturesPtsDiff_dict.get(team, [])))

teams_stats_df['fpl_avg_pts/match'] = teams_stats_df['team'].map(lambda team: np.mean(teams_fixturesPtsDiff_dict.get(team, [])))
teams_stats_df['fpl_form'] = teams_stats_df['team'].map(lambda team: np.mean(teams_formFixturesPtsDiff_dict.get(team, [])))
teams_stats_df['fpl_avg_xPts'] = golden_sum(teams_stats_df['fpl_avg_pts/match'], teams_stats_df['fpl_form'])
teams_stats_df['Z(fpl_avg_xPts)'] = Z(teams_stats_df['fpl_avg_xPts'], "standard")

teams_stats_df['fpl_med_pts/match'] = teams_stats_df['team'].map(lambda team: np.median(teams_fixturesPtsDiff_dict.get(team, [])))
teams_stats_df['fpl_med_formPts'] = teams_stats_df['team'].map(lambda team: np.median(teams_formFixturesPtsDiff_dict.get(team, [])))
teams_stats_df['fpl_med_xPts'] = golden_sum(teams_stats_df['fpl_med_pts/match'], teams_stats_df['fpl_med_formPts'])
teams_stats_df['Z(fpl_med_xPts)'] = Z(teams_stats_df['fpl_med_xPts'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['def_pts'] = teams_stats_df['team'].map(lambda team: np.sum(teams_fixturesDefPts_dict.get(team, [])))

teams_stats_df['def_avg_pts/match'] = teams_stats_df['team'].map(lambda team: np.mean(teams_fixturesDefPts_dict.get(team, [])))
teams_stats_df['def_form'] = teams_stats_df['team'].map(lambda team: np.mean(teams_formFixturesDefPts_dict.get(team, [])))
teams_stats_df['def_avg_xPts'] = golden_sum(teams_stats_df['def_avg_pts/match'], teams_stats_df['def_form'])
teams_stats_df['Z(def_avg_xPts)'] = Z(teams_stats_df['def_avg_xPts'], "standard")

teams_stats_df['def_med_pts/match'] = teams_stats_df['team'].map(lambda team: np.median(teams_fixturesDefPts_dict.get(team, [])))
teams_stats_df['def_med_formPts'] = teams_stats_df['team'].map(lambda team: np.median(teams_formFixturesDefPts_dict.get(team, [])))
teams_stats_df['def_med_xPts'] = golden_sum(teams_stats_df['def_med_pts/match'], teams_stats_df['def_med_formPts'])
teams_stats_df['Z(def_med_xPts)'] = Z(teams_stats_df['def_med_xPts'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['att_pts'] = teams_stats_df['team'].map(lambda team: np.sum(teams_fixturesAttPts_dict.get(team, [])))

teams_stats_df['att_avg_pts/match'] = teams_stats_df['team'].map(lambda team: np.mean(teams_fixturesAttPts_dict.get(team, [])))
teams_stats_df['att_form'] = teams_stats_df['team'].map(lambda team: np.mean(teams_formFixturesAttPts_dict.get(team, [])))
teams_stats_df['att_avg_xPts'] = golden_sum(teams_stats_df['att_avg_pts/match'], teams_stats_df['att_form'])
teams_stats_df['Z(att_avg_xPts)'] = Z(teams_stats_df['att_avg_xPts']) ### Z-score of att_avg_xPts

teams_stats_df['att_med_pts/match'] = teams_stats_df['team'].map(lambda team: np.median(teams_fixturesAttPts_dict.get(team, [])))
teams_stats_df['att_med_formPts'] = teams_stats_df['team'].map(lambda team: np.median(teams_formFixturesAttPts_dict.get(team, [])))
teams_stats_df['att_med_xPts'] = golden_sum(teams_stats_df['att_med_pts/match'], teams_stats_df['att_med_formPts'])
teams_stats_df['Z(att_med_xPts)'] = Z(teams_stats_df['att_med_xPts'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['goals_for'] = teams_stats_df['team'].map(lambda team: np.sum(goals_for_dict.get(team, [])))

teams_stats_df['avg_GF/match'] = teams_stats_df['team'].map(lambda team: np.mean(goals_for_dict.get(team, [])))
teams_stats_df['Z(avg_GF/match)'] = Z(teams_stats_df['avg_GF/match'], "standard")

teams_stats_df['med_GF/match'] = teams_stats_df['team'].map(lambda team: np.median(goals_for_dict.get(team, [])))
teams_stats_df['Z(med_GF/match)'] = Z(teams_stats_df['med_GF/match'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['goals_against'] = teams_stats_df['team'].map(lambda team: np.sum(goals_against_dict.get(team, [])))

teams_stats_df['avg_GA/match'] = teams_stats_df['team'].map(lambda team: np.mean(goals_against_dict.get(team, [])))
teams_stats_df['Z(avg_GA/match)'] = Z(teams_stats_df['avg_GA/match'], "standard")

teams_stats_df['med_GA/match'] = teams_stats_df['team'].map(lambda team: np.median(goals_against_dict.get(team, [])))
teams_stats_df['Z(med_GA/match)'] = Z(teams_stats_df['med_GA/match'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['goal_diff'] = teams_stats_df['team'].map(lambda team: np.sum(goal_diff_dict.get(team, [])))

teams_stats_df['avg_GD/match'] = teams_stats_df['team'].map(lambda team: np.mean(goal_diff_dict.get(team, [])))
teams_stats_df['Z(avg_GD/match)'] = Z(teams_stats_df['avg_GD/match'], "standard")

teams_stats_df['med_GD/match'] = teams_stats_df['team'].map(lambda team: np.median(goal_diff_dict.get(team, [])))
teams_stats_df['Z(med_GD/match)'] = Z(teams_stats_df['med_GD/match'])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['clean_sheets'] = teams_stats_df['team'].map(clean_sheets_dict)
teams_stats_df['avg_CS/match'] = round(teams_stats_df['clean_sheets'] / teams_stats_df['matches_played'], 11)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df['att_avg_potential'] = golden_sum(teams_stats_df['Z(att_avg_xPts)'], +teams_stats_df['Z(avg_GF/match)'], invertArgs=True)
teams_stats_df['att_med_potential'] = golden_sum(teams_stats_df['Z(att_med_xPts)'], +teams_stats_df['Z(med_GF/match)'], invertArgs=True)

teams_stats_df['def_avg_potential'] = golden_sum(teams_stats_df['Z(def_avg_xPts)'], -teams_stats_df['Z(avg_GA/match)'], invertArgs=True)
teams_stats_df['def_med_potential'] = golden_sum(teams_stats_df['Z(def_med_xPts)'], -teams_stats_df['Z(med_GA/match)'], invertArgs=True)

teams_stats_df['fpl_avg_potential'] = golden_sum(teams_stats_df['Z(fpl_avg_xPts)'], +teams_stats_df['Z(avg_GD/match)'], invertArgs=True)
teams_stats_df['fpl_med_potential'] = golden_sum(teams_stats_df['Z(fpl_med_xPts)'], +teams_stats_df['Z(med_GD/match)'], invertArgs=True)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
teams_stats_df = teams_stats_df.reset_index(drop=True).set_index('team', drop=True)
#####################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
fpl_cols = [
    'matches_played',

    'fpl_pts',

    'fpl_avg_pts/match',
    'fpl_form',
    'fpl_avg_xPts',
    'Z(fpl_avg_xPts)',

    'fpl_med_pts/match',
    'fpl_med_formPts',
    'fpl_med_xPts',
    'Z(fpl_med_xPts)',

    'goal_diff',
    'avg_GD/match',
    'Z(avg_GD/match)',
    'med_GD/match',
    'Z(med_GD/match)',

    'clean_sheets',
    'avg_CS/match',

    'fpl_avg_potential',
    'fpl_med_potential'
]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def_cols = [
    'matches_played',

    'def_pts',

    'def_avg_pts/match',
    'def_form',
    'def_avg_xPts',
    'Z(def_avg_xPts)',

    'def_med_pts/match',
    'def_med_formPts',
    'def_med_xPts',
    'Z(def_med_xPts)',

    'goals_against',
    'avg_GA/match',
    'Z(avg_GA/match)',
    'med_GA/match',
    'Z(med_GA/match)',

    'clean_sheets',
    'avg_CS/match',

    'def_avg_potential',
    'def_med_potential'
]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
att_cols = [
    'matches_played',

    'att_pts',

    'att_avg_pts/match',
    'att_form',
    'att_avg_xPts',
    'Z(att_avg_xPts)',

    'att_med_pts/match',
    'att_med_formPts',
    'att_med_xPts',
    'Z(att_med_xPts)',

    'goals_for',
    'avg_GF/match',
    'Z(avg_GF/match)',
    'med_GF/match',
    'Z(med_GF/match)',

    'clean_sheets',
    'avg_CS/match',

    'att_avg_potential',
    'att_med_potential'
]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
fpl_df = teams_stats_df[fpl_cols].sort_values([
    'med_GD/match', 'fpl_med_pts/match', 'fpl_med_formPts',            
    'avg_GD/match', 'fpl_avg_pts/match', 'fpl_form', ### I really hope these are the last sorting criteria!!!         
    'fpl_pts',
    'avg_CS/match'
], ascending=[
    False, False, False, 
    False, False, False,
    False,
    False
])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def_df = teams_stats_df[def_cols].sort_values([
    'med_GA/match', 'def_med_pts/match', 'def_med_formPts',            
    'avg_GA/match', 'def_avg_pts/match', 'def_form', ### I really hope these are the last sorting criteria!!!         
    'def_pts',
    'avg_CS/match',
], ascending=[
    True, False, False,
    True, False, False,
    False, 
    False
])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
att_df = teams_stats_df[att_cols].sort_values([
    'med_GF/match', 'att_med_pts/match', 'att_med_formPts',            
    'avg_GF/match', 'att_avg_pts/match', 'att_form', ### I really hope these are the last sorting criteria!!!         
    'att_pts',
    'avg_CS/match'
], ascending=[
    False, False, False, 
    False, False, False,
    False,
    False
])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
fpl_teams_stats_df = fpl_df[['fpl_avg_xPts', 'fpl_med_xPts', 'avg_GD/match', 'med_GD/match', 'fpl_avg_potential', 'fpl_med_potential']].reset_index(drop=False)
fpl_teams_stats_df.insert(0, 'fpl_rank', 1 + fpl_teams_stats_df['team'].index)
fpl_teams_stats_df.insert(1, 'fpl_tier', 1 + fpl_teams_stats_df['team'].index//2)
fpl_teams_stats_df = fpl_teams_stats_df.set_index('team', drop=False)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def_teams_stats_df = def_df[['def_avg_xPts', 'def_med_xPts', 'avg_GA/match', 'med_GA/match', 'def_avg_potential', 'def_med_potential']].reset_index(drop=False)
def_teams_stats_df.insert(0, 'def_rank', 1 + def_teams_stats_df['team'].index)
def_teams_stats_df.insert(1, 'def_tier', 1 + def_teams_stats_df['team'].index//2)
def_teams_stats_df = def_teams_stats_df.set_index('team', drop=False)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
att_teams_stats_df = att_df[['att_avg_xPts', 'att_med_xPts', 'avg_GF/match', 'med_GF/match', 'att_avg_potential', 'att_med_potential']].reset_index(drop=False)
att_teams_stats_df.insert(0, 'att_rank', 1 + att_teams_stats_df['team'].index)
att_teams_stats_df.insert(1, 'att_tier', 1 + att_teams_stats_df['team'].index//2)
att_teams_stats_df = att_teams_stats_df.set_index('team', drop=False)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
print(fpl_df)
print("\n\n\n")
print(def_df)
print("\n\n\n")
print(att_df)
print("\n\n\n")
# print(fpl_teams_stats_df)
# print("\n\n\n")
# print(def_teams_stats_df)
# print("\n\n\n")
# print(att_teams_stats_df)
# print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
nxtGWs_fixtures = []
fpl_teamsAdv_dict = {}
def_teamsAdv_dict = {}
att_teamsAdv_dict = {}
teams_nxtGWsNberOfMatches_dict = {}

players_df['fplAdv_nxtGWs'] = players_df['xPts(fplAdv)'] = 0
players_df['defAdv_nxtGWs'] = players_df['xPts(defAdv)'] = 0
players_df['attAdv_nxtGWs'] = players_df['xPts(attAdv)'] = 0
players_df['xPts(avgAdv)'] = 0

for fixture in fixtures_data: # for fixture in upcoming_fixtures_data
    if fixture["event"] in gws:
        fixture_dict = {}

        home_team = teams_dict[fixture['team_h']]
        away_team = teams_dict[fixture['team_a']]
        
        fixture_dict['home_attAdv'] = def_teams_stats_df.loc[away_team, 'def_tier'] - att_teams_stats_df.loc[home_team, 'att_tier']
        fixture_dict['home_defAdv'] = att_teams_stats_df.loc[away_team, 'att_tier'] - def_teams_stats_df.loc[home_team, 'def_tier'] 
        fixture_dict['home_fplAdv'] = fpl_teams_stats_df.loc[away_team, 'fpl_tier'] - fpl_teams_stats_df.loc[home_team, 'fpl_tier']
        
        fixture_dict['home_team'] = home_team
        fixture_dict['away_team'] = away_team
        
        fixture_dict['away_fplAdv'] = -fixture_dict['home_fplAdv']
        fixture_dict['away_defAdv'] = -fixture_dict['home_attAdv']
        fixture_dict['away_attAdv'] = -fixture_dict['home_defAdv']
        
        nxtGWs_fixtures.append(fixture_dict)
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        fpl_teamsAdv_dict[home_team] = fpl_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_fplAdv']
        fpl_teamsAdv_dict[away_team] = fpl_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_fplAdv']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        def_teamsAdv_dict[home_team] = def_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_defAdv']
        def_teamsAdv_dict[away_team] = def_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_defAdv']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        att_teamsAdv_dict[home_team] = att_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_attAdv']
        att_teamsAdv_dict[away_team] = att_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_attAdv']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        fplHomeAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['home_fplAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        fplAwayAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['away_fplAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        defHomeAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['home_defAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        defAwayAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['away_defAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        attHomeAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['home_attAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        attAwayAdv_playerGoldenSum_xPtsParam1 = players_df['x(med_pts/fxtr)'] + (fixture_dict['away_attAdv'] / 9) * players_df['x(MedAbsDev(pts/fxtr))']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        fplHomeAdv_playerGoldenSum_xPtsParam2 = None
        fplAwayAdv_playerGoldenSum_xPtsParam2 = None
        defHomeAdv_playerGoldenSum_xPtsParam2 = None
        defAwayAdv_playerGoldenSum_xPtsParam2 = None
        attHomeAdv_playerGoldenSum_xPtsParam2 = None
        attAwayAdv_playerGoldenSum_xPtsParam2 = None
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        fplHomeAdv_playerGoldenSum_xPtsParam3 = None
        fplAwayAdv_playerGoldenSum_xPtsParam3 = None
        defHomeAdv_playerGoldenSum_xPtsParam3 = None
        defAwayAdv_playerGoldenSum_xPtsParam3 = None
        attHomeAdv_playerGoldenSum_xPtsParam3 = None
        attAwayAdv_playerGoldenSum_xPtsParam3 = None
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        players_df.loc[players_df['team'] == home_team, 'xPts(fplAdv)'] += golden_sum(
            fplHomeAdv_playerGoldenSum_xPtsParam1,
            fplHomeAdv_playerGoldenSum_xPtsParam2,
            fplHomeAdv_playerGoldenSum_xPtsParam3,
        )
        players_df.loc[players_df['team'] == away_team, 'xPts(fplAdv)'] += golden_sum(
            fplAwayAdv_playerGoldenSum_xPtsParam1,
            fplAwayAdv_playerGoldenSum_xPtsParam2,
            fplAwayAdv_playerGoldenSum_xPtsParam3,
        )
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')) & (players_df['team'] == home_team), 'xPts(defAdv)'] += golden_sum(
            defHomeAdv_playerGoldenSum_xPtsParam1,
            defHomeAdv_playerGoldenSum_xPtsParam2,
            defHomeAdv_playerGoldenSum_xPtsParam3,
        )
        players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')) & (players_df['team'] == away_team), 'xPts(defAdv)'] += golden_sum(
            defAwayAdv_playerGoldenSum_xPtsParam1,
            defAwayAdv_playerGoldenSum_xPtsParam2,
            defAwayAdv_playerGoldenSum_xPtsParam3,
        )
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')) & (players_df['team'] == home_team), 'xPts(attAdv)'] += golden_sum(
            attHomeAdv_playerGoldenSum_xPtsParam1,
            attHomeAdv_playerGoldenSum_xPtsParam2,
            attHomeAdv_playerGoldenSum_xPtsParam3,
        )
        players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')) & (players_df['team'] == away_team), 'xPts(attAdv)'] += golden_sum(
            attAwayAdv_playerGoldenSum_xPtsParam1,
            attAwayAdv_playerGoldenSum_xPtsParam2,
            attAwayAdv_playerGoldenSum_xPtsParam3,
        )
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        teams_nxtGWsNberOfMatches_dict[home_team] = teams_nxtGWsNberOfMatches_dict.get(home_team, 0) + 1
        teams_nxtGWsNberOfMatches_dict[away_team] = teams_nxtGWsNberOfMatches_dict.get(away_team, 0) + 1



nxtGWs_fixtures_df = pd.DataFrame(nxtGWs_fixtures)
players_df['xPts(avgAdv)'] = round((players_df['xPts(fplAdv)'] + players_df['xPts(defAdv)'] + players_df['xPts(attAdv)']) / 2, 11)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
fpl_teams_stats_df['fplAdv_nxtGWs'] = fpl_teams_stats_df['team'].map(fpl_teamsAdv_dict)
fpl_teams_stats_df = fpl_teams_stats_df.sort_values(['fplAdv_nxtGWs','fpl_rank'], ascending=[False,True]).dropna(subset=['fplAdv_nxtGWs'])

players_df['fplAdv_nxtGWs'] = players_df['team'].map(fpl_teamsAdv_dict)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def_teams_stats_df['defAdv_nxtGWs'] = def_teams_stats_df['team'].map(def_teamsAdv_dict)
def_teams_stats_df = def_teams_stats_df.sort_values(['defAdv_nxtGWs','def_rank'], ascending=[False,True]).dropna(subset=['defAdv_nxtGWs'])

players_df['defAdv_nxtGWs'] = players_df['team'].map(def_teamsAdv_dict)
players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')), 'defAdv_nxtGWs'] = 0
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
att_teams_stats_df['attAdv_nxtGWs'] = att_teams_stats_df['team'].map(att_teamsAdv_dict)
att_teams_stats_df = att_teams_stats_df.sort_values(['attAdv_nxtGWs','att_rank'], ascending=[False,True]).dropna(subset=['attAdv_nxtGWs'])

players_df['attAdv_nxtGWs'] = players_df['team'].map(att_teamsAdv_dict)
players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')), 'attAdv_nxtGWs'] = 0
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



print("\n\n\n")
print(nxtGWs_fixtures_df.to_string(index=False))
print("\n\n\n")
print(fpl_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(def_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(att_teams_stats_df.to_string(index=False))
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
avg_teams_stats_df = pd.DataFrame().assign(
    team = fpl_teams_stats_df['team'],

    att_rank = att_teams_stats_df['att_rank'],
    def_rank = def_teams_stats_df['def_rank'],
    fpl_rank = fpl_teams_stats_df['fpl_rank'],

    att_tier = att_teams_stats_df['att_tier'],
    def_tier = def_teams_stats_df['def_tier'],
    fpl_tier = fpl_teams_stats_df['fpl_tier'],    
    
    att_avg_potential = att_teams_stats_df['att_avg_potential'],
    def_avg_potential = def_teams_stats_df['def_avg_potential'], 
    fpl_avg_potential = fpl_teams_stats_df['fpl_avg_potential'],
    
    attAdv_nxtGWs = att_teams_stats_df['attAdv_nxtGWs'],
    defAdv_nxtGWs = def_teams_stats_df['defAdv_nxtGWs'],
    fplAdv_nxtGWs = fpl_teams_stats_df['fplAdv_nxtGWs']
).set_index('team', drop=False)

avg_teams_stats_df.insert(2, '∼fpl_rank', avg_teams_stats_df[['att_rank', 'def_rank']].mean(axis=1))
avg_teams_stats_df.insert(4, 'rank_avg', avg_teams_stats_df[['∼fpl_rank', 'fpl_rank']].mean(axis=1))

avg_teams_stats_df.insert(7, '∼fpl_tier', avg_teams_stats_df[['att_tier', 'def_tier']].mean(axis=1))
avg_teams_stats_df.insert(9, 'tier_avg', avg_teams_stats_df[['∼fpl_tier', 'fpl_tier']].mean(axis=1))

avg_teams_stats_df.insert(12, '∼fpl_avg_potential', avg_teams_stats_df[['att_avg_potential', 'def_avg_potential']].mean(axis=1))
avg_teams_stats_df.insert(14, 'avg_potential', avg_teams_stats_df[['∼fpl_avg_potential', 'fpl_avg_potential']].mean(axis=1))

avg_teams_stats_df.insert(17, '∼fplAdv_nxtGWs', avg_teams_stats_df[['attAdv_nxtGWs', 'defAdv_nxtGWs']].mean(axis=1))
avg_teams_stats_df.insert(19, 'avgAdv_nxtGWs', avg_teams_stats_df[['∼fplAdv_nxtGWs', 'fplAdv_nxtGWs']].mean(axis=1))

avg_teams_stats_df = avg_teams_stats_df[['team', 'rank_avg', 'tier_avg', 'avg_potential', 'avgAdv_nxtGWs']]
avg_teams_stats_df = avg_teams_stats_df.sort_values(['avg_potential','rank_avg','tier_avg'], ascending=[False,True,True]).reset_index(drop=True)

avg_teams_stats_df.insert(0, 'avg_rank', 1 + avg_teams_stats_df['team'].index)
avg_teams_stats_df.insert(1, 'avg_tier', 1 + avg_teams_stats_df['team'].index//2)

avg_teams_stats_df = avg_teams_stats_df.sort_values(['avgAdv_nxtGWs','avg_rank'], ascending=[False,True])
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
avg_teams_advanced_stats_df = pd.DataFrame().assign(
    att_rank = att_teams_stats_df['att_rank'],
    def_rank = def_teams_stats_df['def_rank'],
    team = fpl_teams_stats_df['team'],
    att_med_xPts = att_teams_stats_df['att_med_xPts'],
    def_med_xPts = def_teams_stats_df['def_med_xPts'],
    attAdv_nxtGWs = att_teams_stats_df['attAdv_nxtGWs'],
    defAdv_nxtGWs = def_teams_stats_df['defAdv_nxtGWs']
).set_index('team', drop=False)

avg_teams_advanced_stats_df.insert(2, '(def-att)_rank', avg_teams_advanced_stats_df['def_rank'] - avg_teams_advanced_stats_df['att_rank'])
avg_teams_advanced_stats_df.insert(6, '(att-def)_med_xPts', avg_teams_advanced_stats_df['att_med_xPts'] - avg_teams_advanced_stats_df['def_med_xPts'])
avg_teams_advanced_stats_df['(att-def)Adv_nxtGWs'] = avg_teams_advanced_stats_df['attAdv_nxtGWs'] - avg_teams_advanced_stats_df['defAdv_nxtGWs']
avg_teams_advanced_stats_df['#OfMatches_nxtGWs'] = avg_teams_advanced_stats_df['team'].map(teams_nxtGWsNberOfMatches_dict)
avg_teams_advanced_stats_df['(att-def)Adv_nxtGWs/#OfMatches_nxtGWs'] = round(avg_teams_advanced_stats_df['(att-def)Adv_nxtGWs'] / avg_teams_advanced_stats_df['#OfMatches_nxtGWs'], 11)

avg_teams_advanced_stats_df = avg_teams_advanced_stats_df.sort_values(['(att-def)Adv_nxtGWs/#OfMatches_nxtGWs', '(def-att)_rank', '(att-def)_med_xPts'], ascending=[True, True, True]) ### IS THE SORTING ORDER THE BEST? I THINK SO!!! IF NOT, INTERCHANGE '(def-att)_rank' AND '(att-def)_xPts' ###

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
avg_teams_advanced_stats_df['#atts'] = 0
avg_teams_advanced_stats_df['#defs'] = 0 

number_of_playing_teams = avg_teams_advanced_stats_df['#OfMatches_nxtGWs'].notna().sum()
playing_teams_indices = avg_teams_advanced_stats_df[avg_teams_advanced_stats_df['#OfMatches_nxtGWs'].notna()].index
divisor = number_of_playing_teams / 4
avg_teams_advanced_stats_df.loc[playing_teams_indices, '#atts'] = [int(i // divisor) for i in range(len(playing_teams_indices))]
avg_teams_advanced_stats_df.loc[playing_teams_indices, '#defs'] = 3 - avg_teams_advanced_stats_df.loc[playing_teams_indices, '#atts']
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


players_df['#OfMatches_nxtGWs'] = players_df['team'].map(teams_nxtGWsNberOfMatches_dict)

for gw in gws:
    players_df["gw" + str(gw) + "Pts"] = 0
players_df['tot_aPts'] = 0
players_df['tot_aPts-xPts(avgAdv)'] = 0
players_df['nxtGWsPtsTrend'] = '?'



print(avg_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(avg_teams_advanced_stats_df.to_string(index=False))
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
teams_top_fpl_players_dict = {}
teams_top_fpl_players_df = pd.DataFrame()
for team in fpl_teams_stats_df.index:
    team_top_fpl_players = players_df.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','fplAdv_nxtGWs','med_pts/fxtr','xPts(fplAdv)']].head(7).sort_values(['xPts(fplAdv)','med_pts/fxtr','tot_pts'], ascending=[False,False,False]).head(5)   # prime nbers: 11 (max # of players from the same team in a real match) ==> [7 ==> 5] ==> 3 (max # of players from the same team in an fpl game)
    team_top_fpl_players = team_top_fpl_players.round(3)
    teams_top_fpl_players_df = pd.concat([teams_top_fpl_players_df, team_top_fpl_players])
    team_top_fpl_players = [' ==> '.join(i) for i in zip(team_top_fpl_players['web_name'], '(' + team_top_fpl_players['med_pts/fxtr'].map(str) + ', ' + team_top_fpl_players['xPts(fplAdv)'].map(str) + ')')]
    teams_top_fpl_players_dict[team] = team_top_fpl_players
fpl_matrix_df = pd.DataFrame(teams_top_fpl_players_dict).transpose()
fpl_matrix_df.index.name = 'team'
fpl_matrix_df.columns = ['fplPlayer1', 'fplPlayer2','fplPlayer3','fplPlayer4','fplPlayer5']
fpl_matrix_df.insert(loc=0, column='fplAdv_nxtGWs', value=fpl_teams_stats_df['fplAdv_nxtGWs'])
teams_top_fpl_players_df = teams_top_fpl_players_df.loc[teams_top_fpl_players_df['fplAdv_nxtGWs'] >= 0]
teams_top_fpl_players_df_dict = teams_top_fpl_players_df.to_dict('index')



teams_top_defensive_players_dict = {}
teams_top_defensive_players_df = pd.DataFrame() 
defensive_players = players_df[(players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')] # gkps and defs
for team in def_teams_stats_df.index:
    team_top_defensive_players = defensive_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','defAdv_nxtGWs','med_pts/fxtr','xPts(defAdv)']].head(5).sort_values(['xPts(defAdv)','med_pts/fxtr','tot_pts'], ascending=[False,False,False])   # 5 ≈ 11/2  ###> head(3) is commented coz sometimes a top-3 player is injured (& you need a reserve to fill-in)
    team_top_defensive_players = team_top_defensive_players.round(3)
    teams_top_defensive_players_df = pd.concat([teams_top_defensive_players_df, team_top_defensive_players])
    team_top_defensive_players = [' ==> '.join(i) for i in zip(team_top_defensive_players['web_name'], '(' + team_top_defensive_players['med_pts/fxtr'].map(str) + ', ' + team_top_defensive_players['xPts(defAdv)'].map(str) + ')')]
    teams_top_defensive_players_dict[team] = team_top_defensive_players
defensive_matrix_df = pd.DataFrame(teams_top_defensive_players_dict).transpose()
defensive_matrix_df.index.name = 'team'
defensive_matrix_df.columns = ['defPlayer1', 'defPlayer2','defPlayer3','defPlayer4','defPlayer5']
defensive_matrix_df.insert(loc=0, column='defAdv_nxtGWs', value=def_teams_stats_df['defAdv_nxtGWs'])
teams_top_defensive_players_df = teams_top_defensive_players_df.loc[teams_top_defensive_players_df['defAdv_nxtGWs'] >= 0]
teams_top_defensive_players_df_dict = teams_top_defensive_players_df.to_dict('index')



teams_top_attacking_players_dict = {}
teams_top_attacking_players_df = pd.DataFrame() 
attacking_players = players_df[(players_df['position'] == 'MID') | (players_df['position'] == 'FWD')] # mids and fwds
for team in att_teams_stats_df.index:
    team_top_attacking_players = attacking_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','attAdv_nxtGWs','med_pts/fxtr','xPts(attAdv)']].head(5).sort_values(['xPts(attAdv)','med_pts/fxtr','tot_pts'], ascending=[False,False,False])   # 5 ≈ 11/2 ###> head(3) is commented coz sometimes a top 3-player is injured (& you need a reserve to fill-in)
    team_top_attacking_players = team_top_attacking_players.round(3)
    teams_top_attacking_players_df = pd.concat([teams_top_attacking_players_df, team_top_attacking_players])
    team_top_attacking_players = [' ==> '.join(i) for i in zip(team_top_attacking_players['web_name'], '(' + team_top_attacking_players['med_pts/fxtr'].map(str) + ', ' + team_top_attacking_players['xPts(attAdv)'].map(str) + ')')]
    teams_top_attacking_players_dict[team] = team_top_attacking_players
attacking_matrix_df = pd.DataFrame(teams_top_attacking_players_dict).transpose()
attacking_matrix_df.index.name = 'team'
attacking_matrix_df.columns = ['attPlayer1', 'attPlayer2','attPlayer3','attPlayer4','attPlayer5']
attacking_matrix_df.insert(loc=0, column='attAdv_nxtGWs', value=att_teams_stats_df['attAdv_nxtGWs'])
teams_top_attacking_players_df = teams_top_attacking_players_df.loc[teams_top_attacking_players_df['attAdv_nxtGWs'] >= 0]
teams_top_attacking_players_df_dict = teams_top_attacking_players_df.to_dict('index')



decision_matrix_df = avg_teams_stats_df[['team', 'avgAdv_nxtGWs']].set_index('team', drop=True)
decision_matrix_df['#atts'] = avg_teams_advanced_stats_df['#atts']
decision_matrix_df['#defs'] = avg_teams_advanced_stats_df['#defs']
teams_top_players_for_nxtGWs_dict = {}
teams_top_players_df = pd.DataFrame()
for team in decision_matrix_df.index:
    nberOfTeamTopAttPlayers = decision_matrix_df.at[team, '#atts']
    nberOfTeamTopDefPlayers = decision_matrix_df.at[team, '#defs']
    team_top_attacking_players = attacking_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','med_pts/fxtr','xPts(avgAdv)']].head(5).sort_values(['xPts(avgAdv)','med_pts/fxtr','tot_pts'], ascending=[False,False,False]).head(nberOfTeamTopAttPlayers)
    team_top_defensive_players = defensive_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','med_pts/fxtr','xPts(avgAdv)']].head(5).sort_values(['xPts(avgAdv)','med_pts/fxtr','tot_pts'], ascending=[False,False,False]).head(nberOfTeamTopDefPlayers)
    team_top_players_for_nxtGWs = pd.concat([team_top_attacking_players, team_top_defensive_players]).sort_values(['xPts(avgAdv)', 'med_pts/fxtr','tot_pts'], ascending=[False,False,False])
    team_top_players_for_nxtGWs = team_top_players_for_nxtGWs.round(5)
    teams_top_players_df = pd.concat([teams_top_players_df, team_top_players_for_nxtGWs])
    team_top_players_for_nxtGWs = [' ==> '.join(i) for i in zip(team_top_players_for_nxtGWs['web_name'], '(' + team_top_players_for_nxtGWs['med_pts/fxtr'].map(str) + ', ' + team_top_players_for_nxtGWs['xPts(avgAdv)'].map(str) + ')')]
    teams_top_players_for_nxtGWs_dict[team] = team_top_players_for_nxtGWs
teams_top_players_for_nxtGWs_df = pd.DataFrame(teams_top_players_for_nxtGWs_dict).transpose()
teams_top_players_for_nxtGWs_df.columns = ['Player1', 'Player2','Player3']
decision_matrix_df = decision_matrix_df.join(teams_top_players_for_nxtGWs_df)
teams_top_players_df = teams_top_players_df.loc[teams_top_players_df['xPts(avgAdv)'] >= 0]
teams_top_players_df_dict = teams_top_players_df.to_dict('index')



print(fpl_matrix_df)
print("\n\n\n")
print(defensive_matrix_df)
print("\n\n\n")
print(attacking_matrix_df)
print("\n\n\n")
print(decision_matrix_df)
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
def best_team_str(selection_criterion, best_points, best_team):
    if best_team is None:
        return f"\nTHERE'S NO BEST TEAM according to {selection_criterion}!\n"
    
    ans = ""
    
    grouped_team = defaultdict(list)
    for player in best_team:
        grouped_team[player["position"]].append(player)

    ans += f"\nBEST TEAM according to {selection_criterion} [Total " + selection_criterion + ": " + f"{best_points:.11f}]:\n"
    ans += "####################################################################################################################################################################################################################\n"
    for position, players in grouped_team.items():
        str1 = f"#     {position}: "
        ans += str1
        sorted_players = sorted(players, key=lambda x: x[selection_criterion], reverse=True)
        player_strings = [f"{player['web_name']} ({player['team']}) ==> {player[selection_criterion]:.3f}" for player in sorted_players]
        str2 = " /|\ ".join(player_strings)
        ans += str2

        for i in range(len(str1 + str2), 211):
            ans += ' '
        ans += '#\n'
    ans += "####################################################################################################################################################################################################################\n"
    ans += "\n\n\n\n\n"

    return ans



def select_best_team(players, selection_criterion):
    # Organize players by position
    position_map = defaultdict(list)
    for player in players:
        position_map[player["position"]].append(player)
    
    # Sort players in each position by points
    for position in position_map:
        position_map[position] = sorted(position_map[position], key=lambda x: x[selection_criterion], reverse=True)

    # Choose the top goalkeeper
    goalkeeper = position_map['GKP'][:1]

    # Choose the top 5 defenders, 5 midfielders, and 3 forwards
    defenders = position_map['DEF'][:5]
    midfielders = position_map['MID'][:5]
    forwards = position_map['FWD'][:3]
    
    # Select the formation based on the performance of the top players
    # Here we use a simple greedy algorithm that selects the formation with the highest total points
    formations = [
        (3, 4, 3),
        (3, 5, 2),
        (4, 3, 3),
        (4, 4, 2),
        (4, 5, 1),
        (5, 2, 3),
        (5, 3, 2),
        (5, 4, 1),
    ]

    best_formation = None
    best_points = 0

    for formation in formations:
        criterion_points =  sum(float64([player[selection_criterion] for player in goalkeeper])) + \
                            sum(float64([player[selection_criterion] for player in defenders[:formation[0]]])) + \
                            sum(float64([player[selection_criterion] for player in midfielders[:formation[1]]])) + \
                            sum(float64([player[selection_criterion] for player in forwards[:formation[2]]]))

        if criterion_points > best_points:
            best_points = criterion_points
            best_formation = formation
    
    # Select the team based on the best formation
    best_team = (
        goalkeeper +
        defenders[:best_formation[0]] +
        midfielders[:best_formation[1]] +
        forwards[:best_formation[2]]
    ) if best_formation is not None else None

    ans = {
        "selection_criterion": selection_criterion,
        "best_points": best_points,
        "best_team": best_team
    }

    return ans



# players_df_dict = players_df.to_dict('index')
# players_dict_extended = {key : {**players_dict.get(key,{}), **players_df_dict.get(key,{})} for key in set([*players_dict]).union(set([*players_df_dict]))}
# selection_criterion = input("\n\n\nWhich BEST TEAM selection criterion do you want to use?\t")
# best_team = select_best_team(players_dict_extended.values(), selection_criterion)
# print(best_team_str(best_team, selection_criterion))

teams_selections_str = ""

# print("Selected Team according to FPL advantage:")
criterion, best_pts, best_team = select_best_team(teams_top_fpl_players_df_dict.values(), 'xPts(fplAdv)').values()
best_team_str_repr = best_team_str(criterion, best_pts, best_team)
print(best_team_str_repr)
teams_selections_str += best_team_str_repr

# print("Selected Team according to DEFensive advantage:")
criterion, best_pts, best_team = select_best_team(teams_top_defensive_players_df_dict.values(), 'xPts(defAdv)').values()
best_team_str_repr = best_team_str(criterion, best_pts, best_team)
print(best_team_str_repr)
teams_selections_str += best_team_str_repr

# print("Selected Team according to ATTacking advantage:")
criterion, best_pts, best_team = select_best_team(teams_top_attacking_players_df_dict.values(), 'xPts(attAdv)').values()
best_team_str_repr = best_team_str(criterion, best_pts, best_team)
print(best_team_str_repr)
teams_selections_str += best_team_str_repr

# print("Selected Team according to AVeraGe advantage:")
criterion, best_pts, best_team = select_best_team(teams_top_players_df_dict.values(), 'xPts(avgAdv)').values()
best_team_str_repr = best_team_str(criterion, best_pts, best_team)
print(best_team_str_repr)
teams_selections_str += best_team_str_repr
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
timestr = time.strftime("%d'%m'%Y-%H:%M")
folder = "data/" + timestr



def print_to_file(string_to_print, file):
    with open(file, 'w') as f:
        print(string_to_print, file=f)



if input(f"\n\n\nDo you wish to save the results of this fpl simulation/analysis inside the folder '{folder}'  [Y/n]?   ").lower()[0] == 'y':
    folder_path = os.path.join(os.getcwd(), folder)
    os.mkdir(folder_path)

    players_df.to_csv(folder_path + "/players_stats.csv", index=False)
    fpl_teams_stats_df.to_csv(folder_path + "/fpl_teams_stats.csv", index=False)
    def_teams_stats_df.to_csv(folder_path + "/def_teams_stats.csv", index=False)
    att_teams_stats_df.to_csv(folder_path + "/att_teams_stats.csv", index=False)
    avg_teams_stats_df.to_csv(folder_path + "/avg_teams_stats.csv", index=False)
    avg_teams_advanced_stats_df.to_csv(folder_path + "/avg_teams_advanced_stats.csv", index=False)
    nxtGWs_fixtures_df.to_csv(folder_path + "/nxtGWs_fixtures.csv", index=False)
    fpl_matrix_df.to_csv(folder_path + "/fpl_matrix.csv")
    defensive_matrix_df.to_csv(folder_path + "/defensive_matrix.csv")
    attacking_matrix_df.to_csv(folder_path + "/attacking_matrix.csv")
    decision_matrix_df.to_csv(folder_path + "/decision_matrix.csv")
    print_to_file(teams_selections_str, folder_path + "/selected_teams.txt")



print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################
