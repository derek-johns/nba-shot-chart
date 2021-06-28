import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints.leaguestandings import LeagueStandings
from nba_api.stats.endpoints.commonteamroster import CommonTeamRoster
from nba_api.stats.static.teams import find_teams_by_full_name
from nba_api.stats.static.players import find_players_by_full_name
from nba_api.stats.library.parameters import SeasonType, ContextMeasureDetailed
import seaborn as sns

st.title('NBA Shot Chart Visualization')

st.markdown("""
This app produces a visualization of NBA player shots for the specified season. Only includes regular season.
* **Data Source:** [nba-api](https://github.com/swar/nba_api)
""")

st.sidebar.header('User Input')

# Year input
year_arr = [str(f'{i}-{str((i + 1))[-2:]}') for i in reversed(range(1950, 2021))]
selected_year = st.sidebar.selectbox('Year', year_arr)


# Team input
def get_teams_by_year(year):
    df = LeagueStandings(season=year).get_data_frames()[0]
    return list(map(' '.join, zip(df['TeamCity'], df['TeamName'])))


selected_team = st.sidebar.selectbox('Team', sorted(get_teams_by_year(str(selected_year))))


# Player input
def get_players_by_team(team_name):
    team_id = find_teams_by_full_name(team_name)[0]['id']
    team_df = CommonTeamRoster(season=selected_year, team_id=team_id).get_data_frames()[0]
    return list(team_df['PLAYER'])


selected_player = st.sidebar.selectbox('Player', sorted(get_players_by_team(selected_team)))

# Shot Chart setup
shot_df = shotchartdetail.ShotChartDetail(team_id=find_teams_by_full_name(selected_team)[0]['id'],
                                          player_id=find_players_by_full_name(selected_player)[0]['id'],
                                          context_measure_simple=ContextMeasureDetailed.fga,
                                          season_nullable=str(selected_year),
                                          season_type_all_star=SeasonType.regular,
                                          ).get_data_frames()[0]
made_shot_df = shot_df[shot_df['SHOT_MADE_FLAG'] == 1]
missed_shot_df = shot_df[shot_df['SHOT_MADE_FLAG'] == 0]


# Court setup
def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # Use current axis if none provided
    if ax is None:
        ax = plt.gca()

    # Rim
    # Circle (diameter) = 18 in = 7.5 units
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Backboard
    # Rectangle = 6ft = 60 units
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # Free Throw Lane
    # Outer Box
    # Rectangle = 16ft x 19ft = 160 units x 190 units
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    # Inner Box
    # Rectangle = 12ft x 19ft = 120 units x 190 units
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Free Throw Arc (Top)
    # Arc = 12ft x 12ft = 120 units x 120 units
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Free Throw Arc (Bottom)
    # Arc = 12ft x 12ft = 120 units x 120 units
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')

    # Restricted Zone
    # Arc = 8ft x 8ft = 80 units x 80 units
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # 3pt Line
    # Rectangles x2 = 14ft in height = 140 units
    corner1 = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                        color=color)
    corner2 = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)

    # 3pt Arc
    # Arc = 47.5ft x 47.5ft = 475 units x 475 units
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    # Outer Arc
    # Arc = 12ft x 12ft = 120 units x 120 units
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # Inner Arc
    # Arc = 4ft x 4ft = 40 units x 40 units
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner1,
                      corner2, three_arc, center_outer_arc,
                      center_inner_arc]

    # Draw out of bounds line
    # Rectangle = 50ft x 47.5 ft = 500 units x 475 units
    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


# Draw Shot Chart
with sns.axes_style('white'):
    f, ax = plt.subplots(figsize=(8, 7))
    draw_court(ax=ax, outer_lines=True, color='black')
    sns.scatterplot(x='LOC_X', y='LOC_Y', data=missed_shot_df, color='red')
    sns.scatterplot(x='LOC_X', y='LOC_Y', data=made_shot_df, color='green')
    plt.xlim(-300, 300)
    plt.ylim(-100, 500)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
st.set_option('deprecation.showPyplotGlobalUse', False)
st.pyplot()

