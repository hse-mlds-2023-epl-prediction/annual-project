import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from feat import feature_list
import numpy as np
import os
from api_client import make_request
import requests


feature_dict = {i[0][7:]:i for i in feature_list}

st.header("HSE EPL ML Project")

def choose_season():
    appointment = st.slider(
    "Выберите сезоны:",
    min_value=2019,
    max_value=2023,
    value=(2021, 2023),
    step=1)

    return appointment

#Выбор сезонов
season_player = choose_season()


tab1, tab2, tab3, tab4 = st.tabs(["Игроки", "Клубы", "Игры", "Предсказания результатов матчей"])

df_pl = pd.read_csv(os.path.join(os.path.dirname(__file__)) + '/data/players_stat.csv')
df_cl = pd.read_csv(os.path.join(os.path.dirname(__file__)) + '/data/clubs_stat.csv')
df_gm = pd.read_csv(os.path.join(os.path.dirname(__file__)) + '/data/games.csv', low_memory=False)



with tab1:
    st.header("Статистика по игрокам")

    st.subheader('Топ 10 игроков')

    #Выбор признака по которму сортировать игроков
    feat_player_agg = st.radio(
    "Выберите признак, по которому подбирать топ",
    key="visibility",
    options=["количество побед", "процент побед", "победные голы"])


    st.write(f'Топ 10 игроков за сезоны {season_player} по  признаку: {feat_player_agg}')
    dict_feat_agg_play = {'количество побед': '_wins', "процент побед": 'per_wins', 'победные голы': '_winning_goal'}


    df_player = df_pl[(df_pl['season']>=season_player[0]) & (df_pl['season']<=season_player[1])] #Датасет по нужным сезонам
    df_player_gr = df_player.groupby(by='name_display', as_index=False).sum().sort_values(by=dict_feat_agg_play[feat_player_agg], ascending=False)

    #Выбор нужных признаков
    
    map_feat_players = {
        'name_display': 'Имя игрока',
        '_wins': 'Побед',
        '_losses': 'Поражений',
        '_draws': 'Ничьих',
        '_appearances': 'Игр',
        'per_wins': 'Процент побед',
        '_yellow_card': 'Желтые карточки',
        '_touches': 'Касаний',
        '_total_pass': 'Передач',
        '_accurate_pass': 'Точных передач',
        '_blocked_pass': 'Заблокированных передач',
        '_dispossessed': 'Потерь',
        '_fouls': 'Фолов',
            }

    df_player_gr.rename(columns=map_feat_players, inplace=True)

    list_feat_agg = st.multiselect(
    'Выберите интересующие вас признаки',
    map_feat_players.values(),
    ['Имя игрока', 'Побед', 'Поражений', 'Ничьих', 'Игр', 'Процент побед'])

    #Вывод таблицы
    st.write(df_player_gr[list_feat_agg].head(10))

    st.subheader('Построение графика зависимости')

    #Признаки для построения графика зависимости
    col_player_distr = ['age', '_accurate_cross', '_accurate_pass', '_aerial_lost', '_aerial_won',
                 '_appearances', '_backward_pass', '_blocked_pass', '_dispossessed', '_draws',
                 '_duel_lost', '_duel_won', '_effective_head_clearance', '_fouls', '_fwd_pass',
                 '_head_pass', '_head_pass', '_interception', '_losses', '_mins_played', '_wins',
                 '_yellow_card', '_touches']
    
    map_dict_player_distr = {
        'age': 'Возраст',
        '_wins': 'Побед',
        '_losses': 'Поражений',
        '_draws': 'Ничьих',
        '_appearances': 'Игр',
        'per_wins': 'Процент побед',
        '_yellow_card': 'Желтые карточки',
        '_touches': 'Касаний',
        '_total_pass': 'Передач',
        '_accurate_pass': 'Точных передач',
        '_blocked_pass': 'Заблокированных передач',
        '_dispossessed': 'Потерь',
        '_fouls': 'Фолов',
            }
    
    df_player.rename(columns=map_dict_player_distr, inplace=True)

    #Мультиселект для графика
    list_player_distr = st.multiselect(
    'Выберите два признака для построения графика зависимости',
    map_dict_player_distr.values(),
    ['Побед', 'Передач'])

    

    #Построение графика
    if len(list_player_distr) >= 2:
        fig = plt.figure()
        ax = sns.lineplot(data=df_player, x=list_player_distr[0], y=list_player_distr[1])
        st.pyplot(fig)

with tab2:
    st.header("Статистика по клубам")

    st.subheader('Топ 3 клуба')

    #Выбор признака по которму сортировать игроков
    feat_club_agg = st.radio(
    "Выберите признак, по которому подбирать топ клубы",
    key="club",
    options=["количество побед", "количество голов"])

    st.write(f'Топ 3 клуба за сезоны {season_player} по  признаку: {feat_club_agg}')
    dict_feat_agg_club = {'количество побед': '_wins', 'количество голов': '_goals'}


    df_club = df_cl[(df_cl['season']>=season_player[0]) & (df_cl['season']<=season_player[1])] #Датасет по нужным сезонам
    df_club_gr = df_club.groupby(by='club_name', as_index=False).sum().sort_values(by=dict_feat_agg_club[feat_club_agg], ascending=False)



    #Выбор нужных признаков
    map_feat_club = {
        'club_name': 'Клуб',
        '_wins': 'Побед',
        '_draws': 'Ничьих',
        '_duel_won': 'Выигранных дуэлей',
        '_duel_lost': 'Проигранных дуэлей',
        '_saves': 'Сэйвов',
        '_possession_percentage': 'Владение мячом',
        '_interception': 'Перехватов',
        '_total_pass': 'Передач',
        '_goals': 'Голов',
            }

    list_club_agg = st.multiselect(
    'Выберите интересующие вас признаки',
    map_feat_club.values(),
    ['Клуб', 'Побед', 'Голов' ,'Ничьих', 'Сэйвов', 'Передач', 'Владение мячом'])

    #Вывод таблицы
    df_club_gr.rename(columns=map_feat_club, inplace=True)
    st.write(df_club_gr[list_club_agg].head(3))


    #Признаки для построения графика зависимости
    map_dict_club_distr = {
        '_wins': 'Побед',
        '_draws': 'Ничьих',
        '_duel_won': 'Выигранных дуэлей',
        '_duel_lost': 'Проигранных дуэлей',
        '_saves': 'Сэйвов',
        '_possession_percentage': 'Владение мячом',
        '_interception': 'Перехватов',
        '_total_pass': 'Передач',
        '_goals': 'Голов',
        '_aerial_lost': 'Потерь в воздухе',
        '_aerial_won': 'Выигранных в воздухе',
        '_big_chance_created': 'Созданных больших шансов',
        '_big_chance_missed': 'Пропущенных больших шансов',
        '_challenge_lost': 'Проигранных челенджей',
        '_total_offside': 'Офсайдов',
        '_total_tackle': 'Отборов',
            }
    
    col_club_distr = map_dict_club_distr.values()
    df_club.rename(columns=map_dict_club_distr, inplace=True)

    #Мультиселект для графика
    list_club_distr = st.multiselect(
    'Выберите два признака для построения графика зависимости',
    col_club_distr,
    ['Побед', 'Отборов'])

    #Построение графика
    if len(list_club_distr) >= 2:
        fig = plt.figure()
        ax = sns.lineplot(data=df_club, x=list_club_distr[0], y=list_club_distr[1])
        st.pyplot(fig)

with tab3:
    st.header("Статистика по играм")

    st.subheader('Сравнительная статистика команд')

    #Выбор команд
    list_club_game = st.multiselect(
    'Выберите две команды',
    ['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford',
       'Brighton and Hove Albion', 'Burnley', 'Cardiff City', 'Chelsea',
       'Crystal Palace', 'Everton', 'Fulham', 'Huddersfield Town',
       'Hull City', 'Leeds United', 'Leicester City', 'Liverpool',
       'Luton Town', 'Manchester City', 'Manchester United',
       'Middlesbrough', 'Newcastle United', 'Norwich City',
       'Nottingham Forest', 'Queens Park Rangers', 'Sheffield United',
       'Southampton', 'Stoke City', 'Sunderland', 'Swansea City',
       'Tottenham Hotspur', 'Watford', 'West Bromwich Albion',
       'West Ham United', 'Wolverhampton Wanderers'],
    ['Arsenal', 'Manchester United'])


    df_games = df_gm[(df_gm['gameweek_compSeason_label']>=season_player[0]) & (df_gm['gameweek_compSeason_label']<=season_player[1])] #Датасет по нужным сезонам
    df_games_temp = df_games[((df_games['teams_team_1_name']==list_club_game[0]) & (df_games['teams_team_2_name']==list_club_game[1]))|\
                             ((df_games['teams_team_1_name']==list_club_game[1]) & (df_games['teams_team_2_name']==list_club_game[0]))]\
                             .groupby(by=['teams_team_1_name', 'teams_team_2_name', ], as_index=False).sum()\
                             [['teams_team_1_name', 'teams_team_2_name', 'team_1_wins', 'team_2_wins', 'draw']]
    
    df_games_temp.rename(columns={'teams_team_1_name': 'Команда (h)', 'teams_team_2_name': 'Команда (g)',
                                   'team_1_wins': 'Победы команды (h)', 'team_2_wins': 'Победы команды (g)', 'draw': 'Ничьи'}, inplace=True)

    st.write(df_games_temp)


    st.subheader('Диаграмма рассеяния')

    map_feature_dict = {
        'Точных передач': 'accurate_pass',
        'Касаний': 'touches',
        'Передач': 'total_pass',
        'Владение мячом': 'possession_percentage',
        'Длинных передач': 'total_long_balls',
        'Передач в атакующей трети': 'total_fwd_zone_pass',
        'Касаний в штрафной': 'touches_in_opp_box',
        'Входов в финальную треть': 'final_third_entries',
        'Точных кроссов': 'accurate_cross',
        'Кроссов': 'total_cross',
        'Передач в финальной трети': 'total_final_third_passes',
        'Успешных длинных передач': 'long_pass_own_to_opp_success',
        'Потерь мяча': 'poss_lost_all',        
        'Входов в штрафную': 'pen_area_entries',
        'Передач влево': 'passes_left',
        'Точных длинных передач': 'accurate_long_balls',
        'Точных кроссов без угловых': 'accurate_cross_nocorner',
        'Ударов в штрафной': 'attemps_ibox',
        'Ударов': 'total_scoring_att',
        'Перехватов': 'interception',
        'Выигранных перехватов': 'interception_won',
        'Выигранных отборов': 'won_tackle',
        'Проигранных дуэлей': 'duel_lost',
        'Потерь угловых': 'lost_corners',
        'Запусков': 'total_launches',
        'Отбивок': 'total_clearance',
        'Сэйвов': 'saves',
        'Сэйвов лежа': 'diving_save',
        'Проигранных челенджей': 'challenge_lost',
        'Потерь': 'dispossessed',
        'Неудачных касаний': 'unsuccesful_touch',
        'Отбивок от ворот': 'goal_kicks',
        'Точных отбивок от ворот': 'accurate_goal_kicks',
        'Отбивок головой': 'head_clearance',
        'Эффективных отбивок головой': 'effective_head_clearance',
        'Выигранных в воздухе': 'aerial_won',
        'Желтых карточек': 'total_yel_card',
        'Промахов в штрафной': 'att_ibox_miss',
        'Угловых': 'corner_taken',
        'Выигранных угловых': 'won_corners',
        'Заблокированных результативных кроссов': 'effectve_blocked_cross',
        'Заблокированных кроссов': 'blocked_cross',
        'Фолов в финальной трети': 'fouled_final_third',
        'Точных отбросов вратаря': 'accurate_keeper_throws',
        'Заблокированных ударов в штрафной': 'att_ibox_blocked',
            }

    select_box = st.selectbox(
    "Выберите признак для построения диаграммы",
    map_feature_dict.keys(),
    index=None,
    placeholder="Выберите признак",
    )

    df_games['team_1_hue'] = np.where(df_games['team_1_hue'] == 1, 'Победа', np.where(df_games['team_1_hue'] == 2, 'Поражение', 'Ничья'))
    df_games.rename(columns={'team_1_hue': 'Результат матча'}, inplace=True)
    

    if select_box != None:
        fig = plt.figure()
        ax = sns.scatterplot(data=df_games, x=feature_dict[map_feature_dict[select_box]][0], y=feature_dict[map_feature_dict[select_box]][1], hue='Результат матча')
        ax.set_xlabel('Домашняя команда')
        ax.set_ylabel('Гостевая команда')
        st.pyplot(fig)

    with tab4:
        r = requests.get('http://localhost/games-predict').json()

        df_req = pd.DataFrame(r)

        st.write(df_req)
