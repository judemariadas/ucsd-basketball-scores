import xml.etree.ElementTree as ET
import pandas as pd
import os
import argparse

UCSD_TEAM_NAME = "UC San Diego"

def calc_pct(made, attempted):
    try:
        made = int(made)
        attempted = int(attempted)
        return round((made / attempted) * 100, 1) if attempted else 0.0
    except:
        return 0.0

def parse_game_info(root):
    venue = root.find('venue')
    return {
        'game_id': venue.get('gameid', ''),
        'date': venue.get('date', ''),
        'time': venue.get('time', ''),
        'location': venue.get('location', ''),
        'attendance': venue.get('attend', ''),
        'visitor_team': venue.get('visname', ''),
        'home_team': venue.get('homename', ''),
        'neutral_game': venue.get('neutralgame', 'N'),
        'postseason': venue.get('postseason', 'N')
    } if venue is not None else {}

def parse_ucsd_players(root):
    players = []
    for team in root.findall('team'):
        if team.get('name') != UCSD_TEAM_NAME:
            continue
        for player in team.findall('player'):
            if player.get('name') == 'TEAM':
                continue
            stats = player.find('stats')
            player_data = {
                'team_name': team.get('name'),
                'home_away': team.get('vh'),
                'player_name': player.get('name', ''),
                'player_number': player.get('uni', ''),
                'position': player.get('pos', ''),
                'games_started': player.get('gs', '0'),
                'minutes': stats.get('min', '0') if stats is not None else '0',
                'points': stats.get('tp', '0') if stats is not None else '0',
                'fgm': stats.get('fgm', '0') if stats is not None else '0',
                'fga': stats.get('fga', '0') if stats is not None else '0',
                'fgm3': stats.get('fgm3', '0') if stats is not None else '0',
                'fga3': stats.get('fga3', '0') if stats is not None else '0',
                'ftm': stats.get('ftm', '0') if stats is not None else '0',
                'fta': stats.get('fta', '0') if stats is not None else '0',
                'rebounds': stats.get('treb', '0') if stats is not None else '0',
                'offensive_rebounds': stats.get('oreb', '0') if stats is not None else '0',
                'defensive_rebounds': stats.get('dreb', '0') if stats is not None else '0',
                'assists': stats.get('ast', '0') if stats is not None else '0',
                'steals': stats.get('stl', '0') if stats is not None else '0',
                'blocks': stats.get('blk', '0') if stats is not None else '0',
                'turnovers': stats.get('to', '0') if stats is not None else '0',
                'personal_fouls': stats.get('pf', '0') if stats is not None else '0',
            }
            players.append(player_data)
    return players

def export_to_csv(players, game_info, output_path):
    df = pd.DataFrame(players)
    df['First Name'] = df['player_name'].apply(lambda x: x.split(',')[1].strip() if ',' in x else x)
    df['Last Name'] = df['player_name'].apply(lambda x: x.split(',')[0].strip() if ',' in x else '')
    df['Date'] = game_info.get('date', '')
    df['Time'] = game_info.get('time', '')
    df['opponent'] = game_info['visitor_team'] if game_info['home_team'] == UCSD_TEAM_NAME else game_info['home_team']
    df['home_away'] = df['home_away'].apply(lambda x: 'Home' if x == 'H' else 'Away')
    df['neutral_game'] = 'Yes' if game_info.get('neutral_game') == 'Y' else 'No'
    df['postseason'] = 'Yes' if game_info.get('postseason') == 'Y' else 'No'
    df['games_started'] = df['games_started'].apply(lambda x: 'Yes' if x == '1' else 'No')
    df['field_goal_percentage'] = df.apply(lambda r: calc_pct(r['fgm'], r['fga']), axis=1)
    df['three_point_percentage'] = df.apply(lambda r: calc_pct(r['fgm3'], r['fga3']), axis=1)
    df['free_throw_percentage'] = df.apply(lambda r: calc_pct(r['ftm'], r['fta']), axis=1)

    df = df.rename(columns={
        'minutes': 'minutes_played',
        'fgm': 'field_goals_made',
        'fga': 'field_goals_attempted',
        'fgm3': 'three_pointers_made',
        'fga3': 'three_pointers_attempted',
        'ftm': 'free_throws_made',
        'fta': 'free_throws_attempted',
    })

    final_cols = [
        'First Name', 'Last Name', 'Date', 'Time', 'home_away', 'opponent',
        'neutral_game', 'postseason', 'player_number', 'position',
        'games_started', 'minutes_played', 'points', 'field_goals_made',
        'field_goals_attempted', 'three_pointers_made',
        'three_pointers_attempted', 'free_throws_made', 'free_throws_attempted',
        'rebounds', 'offensive_rebounds', 'defensive_rebounds', 'assists',
        'steals', 'blocks', 'turnovers', 'personal_fouls',
        'field_goal_percentage', 'three_point_percentage',
        'free_throw_percentage'
    ]

    df = df[final_cols]
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} UCSD player rows to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('xml_file', help='Path to basketball XML file')
    parser.add_argument('--output', default='ucsd_output.csv', help='CSV output path')
    args = parser.parse_args()

    tree = ET.parse(args.xml_file)
    root = tree.getroot()

    game_info = parse_game_info(root)
    players = parse_ucsd_players(root)

    if not players:
        print("No UCSD players found in the XML file. Check that the team name matches exactly.")
        return

    export_to_csv(players, game_info, args.output)

if __name__ == "__main__":
    main()