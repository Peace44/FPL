import asyncio
from aiohttp import ClientSession
import re
import pandas as pd
import math



day = int(input("Provide the day value (1 to 31): "))
month = int(input("Provide the month value (1 to 12): "))
year = int(input("Provide the year value: "))
hour = int(input("Provide the hour value (0 to 23): "))
minute = int(input("Provide the minute value (0 to 59): "))

timestr = "%02d'%02d'%4d-%02d:%02d" %(day, month, year, hour, minute)
fileToUpdate = "data/" + timestr + "/players_stats.csv"

players_df = pd.read_csv(fileToUpdate)
players_df.set_index('id', inplace=True, drop=False)



players_info_url = "https://fantasy.premierleague.com/api/element-summary/{}/"
async def fetch_player_update(id, gws, players_aPts_dicts):
    async with ClientSession() as session:
        async with session.get(players_info_url.format(id)) as response:
            try:
                player_info_data = await response.json(content_type=None)
                player_history = player_info_data['history']
                
                players_aPts_dicts[-1][id] = 0
                for i in range(len(gws)):
                    gwPts = 0
                    for history in player_history:
                        if history['round'] == gws[i]:
                            gwPts += history['total_points']
                    players_aPts_dicts[i][id] = gwPts
                    players_aPts_dicts[-1][id] += gwPts

            except Exception as e:
                print(e)
                print(f"\nThere was a problem fetching update for player {id}\n")



async def main(ids, gws, players_aPts_dicts):
    async with asyncio.TaskGroup() as group:
        for id in ids:
            group.create_task(fetch_player_update(id, gws, players_aPts_dicts))
            


update = input("\n\n\nUpdate [Y/n]?   ")
if update.lower()[0] == 'y':
    colsToUpdate = [col for col in players_df.columns.values if "gw" in col]
    gwsToUpdate = [int(gw) for gw in re.findall(r'\d+', ' '.join(colsToUpdate))]
    colsToUpdate.append('tot_aPts')
    players_aPts_dicts = [{} for col in colsToUpdate]

    asyncio.run(main(players_df['id'], gwsToUpdate, players_aPts_dicts))

    for i in range(len(colsToUpdate)):
        players_df[colsToUpdate[i]] = players_df['id'].map(players_aPts_dicts[i])

    players_df['tot_aPts-xPts(avgAdv)'] = players_df['tot_aPts'] - players_df['xPts(avgAdv)']

    PHI = 1.61803398874989484820
    phis = [PHI**i for i in range(0, 7)]
    A, B, C, D, E, F, G = phis

    players_df.loc[                                                  (players_df['tot_aPts-xPts(avgAdv)'] <  -G), 'nxtGWsPtsTrend'] = '7↓'
    players_df.loc[(-G <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -F), 'nxtGWsPtsTrend'] = '6↓'
    players_df.loc[(-F <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -E), 'nxtGWsPtsTrend'] = '5↓'
    players_df.loc[(-E <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -D), 'nxtGWsPtsTrend'] = '4↓'
    players_df.loc[(-D <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -C), 'nxtGWsPtsTrend'] = '3↓'
    players_df.loc[(-C <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -B), 'nxtGWsPtsTrend'] = '2↓'
    players_df.loc[(-B <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <  -A), 'nxtGWsPtsTrend'] = '1↓'
    players_df.loc[(-A <= players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +A), 'nxtGWsPtsTrend'] = '~'
    players_df.loc[(+A <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +B), 'nxtGWsPtsTrend'] = '1↑'
    players_df.loc[(+B <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +C), 'nxtGWsPtsTrend'] = '2↑'
    players_df.loc[(+C <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +D), 'nxtGWsPtsTrend'] = '3↑'
    players_df.loc[(+D <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +E), 'nxtGWsPtsTrend'] = '4↑'
    players_df.loc[(+E <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +F), 'nxtGWsPtsTrend'] = '5↑'
    players_df.loc[(+F <  players_df['tot_aPts-xPts(avgAdv)']) & (players_df['tot_aPts-xPts(avgAdv)'] <= +G), 'nxtGWsPtsTrend'] = '6↑'
    players_df.loc[(+G <  players_df['tot_aPts-xPts(avgAdv)'])                                                  , 'nxtGWsPtsTrend'] = '7↑'

    players_df.to_csv(fileToUpdate, index=False)

    print("\n\n\n")
    print(f"7↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '7↓')].index)} players")
    print(f"6↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '6↓')].index)} players")
    print(f"5↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '5↓')].index)} players")
    print(f"4↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '4↓')].index)} players")
    print(f"3↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '3↓')].index)} players")
    print(f"2↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '2↓')].index)} players")
    print(f"1↓ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '1↓')].index)} players")
    print(f" ~ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] ==  '~')].index)} players")
    print(f"1↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '1↑')].index)} players")
    print(f"2↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '2↑')].index)} players")
    print(f"3↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '3↑')].index)} players")
    print(f"4↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '4↑')].index)} players")
    print(f"5↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '5↑')].index)} players")
    print(f"6↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '6↑')].index)} players")
    print(f"7↑ ==> {len(players_df.loc[(players_df['nxtGWsPtsTrend'] == '7↑')].index)} players")
    print("\n\n\n")
    print(f"∑|tot_aPts-xPts(avgAdv)| = {players_df['tot_aPts-xPts(avgAdv)'].abs().sum()}")
    print("\n\n\n")

    print(f"{len(players_aPts_dicts[0])} updates made out of {len(players_df)} total players!!!")


# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'MCI')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'ARS')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'LIV')].head(37).to_string(index=False))
# print("\n\n\n")
# print(players_df.loc[(players_df['team'] == 'SOU')].head(37).to_string(index=False))
# print("\n\n\n")
