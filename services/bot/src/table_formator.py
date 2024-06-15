import prettytable as pt


def format_games_table(json):
    table = pt.PrettyTable(['Home', 'Away', 'Ground'])
    table.align['Home'] = 'l'
    table.align['Away'] = 'l'
    table.align['Ground'] = 'r'

    for item in json:
        table.add_row([item['home'], item['away'], item['ground']])

    return table


def format_games_with_predict_table(json):
    table = pt.PrettyTable(['Home', 'Away', 'Predict', 'Proba'])
    table.align['Home'] = 'l'
    table.align['Away'] = 'l'

    for item in json:
        table.add_row(
            [item['home'],
             item['away'],
             item['predict'],
             f'{item["proba"][item["predict"]]:.2f}'
             ]
            )

    return table


def format_stats_table(json):
    table = pt.PrettyTable(['team_name', 'avg_score_home', 'avg_score_away'])
    table.align['team'] = 'l'
    table.align['avg_score_home'] = 'r'
    table.align['avg_score_away'] = 'r'

    for item in json:
        table.add_row(
            [item['team_name'],
             f'{item["avg_score_home"]:.2f}',
             f'{item["avg_score_away"]:.2f}']
            )

    return table
