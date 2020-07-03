import pandas as pd
import os

Baseline_data = pd.read_csv("data.csv").set_index('Code')  # Get baseline data into dataframe, index is the shot code


def create_course_list():
    global lcourses
    lcourses = []
    for r, d, f in os.walk('./Courses'):  # Create list of existing courses
        for files in f:
            file, ext = os.path.splitext(os.path.join('./Courses', files))
            lcourses.append(files[:-4])


menu_list = ['Add new round from file', 'Add new round from editor', 'List courses', 'Stats']


def main_menu():
    for idx, tables in enumerate(menu_list):
        print("%s. %s" % (idx + 1, tables))
    get_list(menu_list)



def get_list(li):
    menu_choice = int(input("\nPick a number:")) - 1
    # If choose is not a valid index in list, print error and return empty string
    if menu_choice < 0 or menu_choice > (len(li) - 1):
        print('Invalid Choice')
        return ''
    if menu_choice == 1-1:
        add_round_file()
    if menu_choice == 2-1:
        add_round_editor()
    if menu_choice == 3-1:
        course_editor()
    if menu_choice == 4-1:
        stats_viewer()



def add_round_file():
    source = 'round.txt'
    with open(source) as f:
        vlround = f.readlines()
    vlround = [x.strip() for x in vlround]
    print(vlround)
    vdate = input("\nEnter Date: ")
    vcourse = input("\nEnter Course: ")

    #  Initiate Variables
    round_data = []
    current_hole = 0
    current_shot = 1
    good_shots = 0
    bad_shots = 0
    compare_score = 'PGA'  # Choices: PGA, 80, 90, 100, OriginalPGA
    course_data = pd.read_csv('./Courses/RiveSud.csv').set_index('Hole')  # Get Course data into dataframe, index is the hole #

    for x in range(len(vlround)):  # Loop all the shots
        print(x)
        if 't' in vlround[x]:  # Change hole and reset shot count when on a tee
            current_hole += 1
            current_shot = 1

        try:  # count as holed if next shot is on tee or last shot
            next_shot_code = vlround[x + 1]
        except IndexError:
            next_shot_code = 'holed'  # Means last shot of the round, out of range: Holed is SG 0 in data
        if 't' in next_shot_code:
            next_shot_code = 'holed'  # Next shot on tee (next hole) = holed is SG 0 in data

        if 'p' in vlround[x]:  # Determine the current shot code
            shot_code = vlround[x][:-1]  # remove the p from the shot code and add a shot for the penality
            current_shot += 1
        else:
            shot_code = vlround[x]

        if 'p' in next_shot_code:
            next_shot_code = next_shot_code[:-1]  # remove the p
            SG = Baseline_data.loc[shot_code, compare_score] - Baseline_data.loc[next_shot_code, compare_score] - 2  # Calculation for strokes gained and add one shot for penalty
        else:
            SG = Baseline_data.loc[shot_code, compare_score] - Baseline_data.loc[next_shot_code, compare_score] - 1  # Calculation for strokes gained

        if SG > 0.2 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a good shot if SG is over 0.2, exclude putting
            good_shots += 1
        if SG < -0.6 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a bad shot if SG is less  -0.6, exclude putting
            bad_shots += 1

        round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, course_data.loc[current_hole, 'Par'], Baseline_data.loc[shot_code,'Description'],Baseline_data.loc[shot_code,compare_score], SG])  # Create list of shots data
        current_shot += 1

    round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par', 'ShotType', 'PGA Avg', 'StrokesGained'])  # Create dataframe from list

    lshot_types = ['Drive', 'Long (+231 yds)', 'Approach (101 - 230 yds)', 'Approach (21 - 100 yds)', 'Around the Green (0 - 20 yds)', 'Bunker', 'Putting']  # Different shot types

    for x in lshot_types:  # Get Strokes Gained per shot
        print(x, ' - Count:', round(round_df['StrokesGained'][round_df['ShotType'] == x].count(),2), '   Avg:', round(round_df['StrokesGained'][round_df['ShotType'] == x].mean(),2),'   Worst:', round(round_df['StrokesGained'][round_df['ShotType'] == x].min(),2), '   Best:', round(round_df['StrokesGained'][round_df['ShotType'] == x].max(),2), '   Total:', round(round_df['StrokesGained'][round_df['ShotType'] == x].sum(),2))

    total_shots = 0
    for x in range(len(course_data)):  # Get scores per hole for the round
        print('Hole #', x + 1, ' - ', round_df['Shot #'][round_df['Hole #'] == x + 1].max())
        total_shots += round_df['Shot #'][round_df['Hole #'] == x + 1].max()

    score = total_shots - course_data['Par'].sum()
    score = '+' + str(score)
    print('Total:', total_shots,' ',score,' Good Shots:',good_shots, ' Flobbed Shots:', bad_shots)  # Print total score for the round

    round_df.to_csv('out.csv')

def add_round_editor():
    print(2)


def course_editor():
    print(3)


def stats_viewer():
    print(4)


main_menu()

# Course_data = pd.read_csv('./Courses/' + get_list(lcourses)+'.csv').set_index('Hole')  # Get Course data into dataframe, index is the hole #
# print(Course_data)

#
# Compare_score = 'PGA'  # Choices: PGA, 80, 90, 100, OriginalPGA
#
# Baseline_data = pd.read_csv("data.csv").set_index('Code')  # Get baseline data into dataframe, index is the shot code
# Course_data = pd.read_csv("./Courses/RiveSud.csv").set_index('Hole')  # Get Course data into dataframe, index is the hole #
#
# # Read last round file into list and remove new line character
# with open('round.txt') as f:
#     vlround = f.readlines()
# vlround = [x.strip() for x in vlround]
#
# vdate = vlround[0]  # first line is date
# vcourse = vlround[1]  # second line is course name
# vlround = vlround[2:]  # remove the 2 first line to keep shot data only
#
#
# #  Initiate Variables
# round_data = []
# current_hole = 0
# current_shot = 1
# good_shots = 0
# bad_shots = 0
#
# for x in range(len(vlround)):  # Loop all the shots
#     if 't' in vlround[x]:  # Change hole and reset shot count when on a tee
#         current_hole += 1
#         current_shot = 1
#
#     try:  # count as holed if next shot is on tee or last shot
#         next_shot_code = vlround[x + 1]
#     except IndexError:
#         next_shot_code = 'holed'  # Holed is SG 0 in data
#     if 't' in next_shot_code:
#         next_shot_code = 'holed'  # Holed is SG 0 in data
#
#
#     if 'p' in vlround[x]:  # Determine the current shot code
#         shot_code = vlround[x][:-1]  # remove the p from the shot code and add a shot for the penality
#         current_shot += 1
#     else:
#         shot_code = vlround[x]
#
#     if 'p' in next_shot_code:
#         next_shot_code = next_shot_code[:-1]  # remove the p
#         SG = Baseline_data.loc[shot_code, Compare_score] - Baseline_data.loc[next_shot_code, Compare_score] - 2  # Calculation for strokes gained and add one shot for penalty
#     else:
#         SG = Baseline_data.loc[shot_code, Compare_score] - Baseline_data.loc[next_shot_code, Compare_score] - 1  # Calculation for strokes gained
#
#     if SG > 0.2 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a good shot if SG is over 0.2, exclude putting
#         good_shots += 1
#     if SG < -0.6 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a bad shot if SG is less  -0.6, exclude putting
#         bad_shots += 1
#
#     round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, Course_data.loc[current_hole, 'Par'], Baseline_data.loc[shot_code,'Description'],Baseline_data.loc[shot_code,Compare_score], SG])  # Create list of shots data
#     current_shot += 1
#
# round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par', 'ShotType', 'PGA Avg', 'StrokesGained'])  # Create dataframe from list
#
# lshot_types = ['Drive', 'Long (+231 yds)', 'Approach (101 - 230 yds)', 'Approach (21 - 100 yds)', 'Around the Green (0 - 20 yds)', 'Bunker', 'Putting']  # Different shot types
#
# for x in lshot_types:  # Get Strokes Gained per shot
#     print(x, ' - Count:', round(round_df['StrokesGained'][round_df['ShotType'] == x].count(),2), '   Avg:', round(round_df['StrokesGained'][round_df['ShotType'] == x].mean(),2),'   Worst:', round(round_df['StrokesGained'][round_df['ShotType'] == x].min(),2), '   Best:', round(round_df['StrokesGained'][round_df['ShotType'] == x].max(),2), '   Total:', round(round_df['StrokesGained'][round_df['ShotType'] == x].sum(),2))
#
# total_shots = 0
# for x in range(len(Course_data)):  # Get scores per hole for the round
#     print('Hole #', x + 1, ' - ', round_df['Shot #'][round_df['Hole #'] == x + 1].max())
#     total_shots += round_df['Shot #'][round_df['Hole #'] == x + 1].max()
#
# score = total_shots - Course_data['Par'].sum()
# score = '+' + str(score)
# print('Total: ', total_shots,' ',score,' Good Shots: ',good_shots, ' Flobbed Shots: ', bad_shots)  # Print total score for the round
#
# round_df.to_csv('out.csv')
#
# #  Date, Course, Hole x Score, Hole x FiR, Hole x GiR, Hole x Putts, Total Score, Compared to Par, FiR %, GiR %, Putts Total, Putts Avg.
#
#
# # TODO  tool to create round.csv if round.csv doesn't exist
# # TODO  read round file into list line1=date line2=course then shotscode
# # TODO  Create database of shots  shotdatabase = date, course, shot code, hole#, shot#, par, type, SG-(CompareScore)
# # TODO
# # TODO
# # TODO
# # TODO
# # TODO  Produce Reports: last Round, last 5 Rounds, last 10 rounds, Overall
# # TODO
# # TODO
# # TODO
# # TODO
