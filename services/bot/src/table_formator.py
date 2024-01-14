import prettytable as pt

def format_games_table(json):
    table = pt.PrettyTable(['Home', 'Away', 'Ground'])
    table.align['Home'] = 'l'
    table.align['Away'] = 'l'
    table.align['Ground'] = 'r'

    for item in json:
        table.add_row([item['Home'], item['Away'], item['Ground']])

    return table
