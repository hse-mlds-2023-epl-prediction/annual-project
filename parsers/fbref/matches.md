В датасете [matches.csv](https://disk.yandex.ru/d/YIcEaynFiCYhxQ) представлена информация по матчам EPL с сезона 2014-2015 по 2023-2024.
Данные были собраны с сайта fbref.com

Таблица содержит следующие колонки:

| Название колонки                              | Расшифровка                                                                                            |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------|
| fbref_match_id                                | id матча с сайта fbref                                                                                 |
| season                                        | сезон в формате, start_year-end_year, например - 2014-2015                                             |
| match_week                                    | Номер игровой недели в сезона                                                                          |
| match_date                                    | Дата игры                                                                                              |
| match_time                                    | Время игры по локальному времени                                                                       |
| home_team_name                                | Название команды, которая играет дома                                                                  |
| away_team_name                                | Название команды, которая играет на выезде                                                             |
| score                                         | Счет с формате 1:2                                                                                     |
| match_result                                  | H - выйграла команда играющая дома <br/>D - ничья <br/> A - выйграла команда, которая играла на выезде |
| home_team_score                               | Кол-во мячей, которая забила команда играющая дома                                                     |
| away_team_score                               | Кол-во мячей, которая забила команда играющая на выезде                                                |
| venue                                         | Стадион                                                                                                |
| venue_city                                    | Город                                                                                                  |
| attendance                                    | Кол-во зрителей                                                                                        |
| referee                                       | Судья                                                                                                  |
| (home_team/away_team)_manager                 | Тренер                                                                                                 |
| (home_team/away_team)_captain_name            | Капитан                                                                                                |
| (home_team/away_team)_captain_fbref_id        | id капитана на fbref                                                                                   |
| (home_team/away_team)_possession_percent      | Процент владения мячем                                                                                 |
| (home_team/away_team)_passing_total_count     | Кол-во пасов                                                                                           |
| (home_team/away_team)_passing_accuracy_count  | Кол-во точных пасов                                                                                    |
| (home_team/away_team)_accuracy_percent        | Процент точных пасов                                                                                   |
| (home_team/away_team)_shots_on_target_percent | Процент точных ударов по воротам                                                                       |
| (home_team/away_team)_shots_on_target_count   | Кол-во точных ударов по воротам                                                                        |
| (home_team/away_team)_shots_total_count       | Кол-во ударов по воротам                                                                               |
| (home_team/away_team)_saves_percent           | Процент сейвов                                                                                         |
| (home_team/away_team)_saves_count             | Кол-во сейвов                                                                                          |
| (home_team/away_team)_saves_attempt           | Кол-во попыток сделать сейв                                                                            |
| (home_team/away_team)_yellow_cards_count      | Кол-во желтых карточек                                                                                 |
| (home_team/away_team)_red_cards_count         | Кол-во красных карточек                                                                                |
| (home_team/away_team)_fouls                   | Кол-во фолов                                                                                           |
| (home_team/away_team)_corners                 | Кол-во угловых                                                                                         |
| (home_team/away_team)_touches                 | Кол-во касаний мячем                                                                                   |
| (home_team/away_team)_interceptions           | Кол-во перехватов                                                                                      |
| (home_team/away_team)_aerials_won             | Кол-во выйгранных верховых дуэлей                                                                      |
| (home_team/away_team)_offsides                | Кол-во офсайдов                                                                                        |
| (home_team/away_team)_goal_kicks              | Кол-во ударов от ворот                                                                                 |
| (home_team/away_team)_throw_ins               | Кол-во вводов мяча из за боковой линии                                                                 |
| (home_team/away_team)_long_balls              | Кол-во длинных передач                                                                                 |