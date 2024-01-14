import prettytable as pt

def format_games_table(json):
    table = pt.PrettyTable(['Home', 'Away', 'Ground'])
    table.align['Home'] = 'l'
    table.align['Away'] = 'l'
    table.align['Ground'] = 'r'

    for item in json:
        table.add_row([item['Home'], item['Away'], item['Ground']])

    return table


def format_games_with_predict_table(json):
    table = pt.PrettyTable(['Home', 'Away', 'Predict', 'Proba'])
    table.align['Home'] = 'l'
    table.align['Away'] = 'l'

    for item in json:
        table.add_row([item['Home'], item['Away'], item['Predict'], f'{item["Proba"]:.2f}'])

    return table

def format_stats_table(json):
    table = pt.PrettyTable(['Team', 'Games', 'Goals'])
    table.align['Team'] = 'l'
    table.align['Games'] = 'r'
    table.align['Goals'] = 'r'

    for item in json:
        table.add_row([item['team'], item['games'], item['goals']])

    return table
