import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from feat import feature_list



feature_dict = {i[0][7:]:i for i in feature_list}

st.header("EDA EPL")

def choose_season():
    appointment = st.slider(
    "Выберите сезоны:",
    min_value=2013,
    max_value=2023,
    value=(2021, 2023),
    step=1)

    return appointment

#Выбор сезонов
season_player = choose_season()


tab1, tab2, tab3 = st.tabs(["Игроки", "Клубы", "Игры"])

df_pl = pd.read_csv('eda_data/players_stat.csv')
df_cl = pd.read_csv('eda_data/clubs_stat.csv')
df_gm = pd.read_csv('eda_data/games.csv', low_memory=False)



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
    list_feat_agg = st.multiselect(
    'Выберите интересующие вас признаки',
    ['name_display', '_wins', '_losses', '_draws', '_appearances', 'per_wins',
      '_yellow_card', '_touches', '_total_pass', '_accurate_pass', '_blocked_pass', '_dispossessed',
      '_fouls'],
    ['name_display', '_wins', '_losses', '_draws', '_appearances', 'per_wins'])

    #Вывод таблицы
    st.write(df_player_gr[list_feat_agg].head(10))

    st.subheader('Построение графика зависимости')

    #Признаки для построения графика зависимости
    col_player_distr = ['age', '_accurate_cross', '_accurate_pass', '_aerial_lost', '_aerial_won',
                 '_appearances', '_backward_pass', '_blocked_pass', '_dispossessed', '_draws',
                 '_duel_lost', '_duel_won', '_effective_head_clearance', '_fouls', '_fwd_pass',
                 '_head_pass', '_head_pass', '_interception', '_losses', '_mins_played', '_wins',
                 '_yellow_card', '_touches']
    
    #Мультиселект для графика
    list_player_distr = st.multiselect(
    'Выберите два признака для построения графика зависимости',
    col_player_distr,
    ['_wins', '_fouls'])

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
    list_club_agg = st.multiselect(
    'Выберите интересующие вас признаки',
    ['club_name', '_wins',  '_draws', '_duel_won', '_duel_lost', '_diving_save', '_saves', '_possession_percentage', '_interception', '_total_pass', '_goals'],
    ['club_name', '_wins', '_goals' ,'_draws', '_saves', '_total_pass', '_possession_percentage'])

    #Вывод таблицы
    st.write(df_club_gr[list_club_agg].head(3))


    #Признаки для построения графика зависимости
    col_club_distr = ['_wins',  '_draws', '_duel_won', '_duel_lost', '_diving_save', '_saves', '_possession_percentage',
                         '_interception', '_total_pass', '_goals', '_aerial_lost', '_aerial_won', '_big_chance_created', '_big_chance_missed',
                         '_challenge_lost', '_total_offside', '_total_tackle']

    #Мультиселект для графика
    list_club_distr = st.multiselect(
    'Выберите два признака для построения графика зависимости',
    col_club_distr,
    ['_wins', '_total_tackle'])

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
    


    st.write(df_games_temp)


    st.subheader('Диаграмма рассеяния')

    select_box = st.selectbox(
    "Выберите признак для построения диаграммы",
    feature_dict.keys(),
    index=None,
    placeholder="Выберите признак",
    )
    if select_box != None:
        fig = plt.figure()
        ax = sns.scatterplot(data=df_games, x=feature_dict[select_box][0], y=feature_dict[select_box][1], hue='team_1_hue')
        st.pyplot(fig)