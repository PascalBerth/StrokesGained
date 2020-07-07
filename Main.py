import pandas as pd
import os
from dateutil import parser

# Variables init
Baseline_data = pd.read_csv("data.csv").set_index('Code')  # Get baseline data into dataframe, index is the shot code
lcourses = []


def create_course_list():  # Create list of existing courses
    global lcourses
    lcourses = []
    for r, d, f in os.walk('./Courses'):
        for files in f:
            lcourses.append(files[:-4])


def main_menu():
    create_course_list()
    print('\n')
    print("%s. %s" % (1, 'Add new round from file'))
    print("%s. %s" % (2, 'Add new round from editor'))
    print("%s. %s" % (3, 'Course Editor'))
    print("%s. %s" % (4, 'Test One shot'))
    print("%s. %s" % (5, 'Stats'))
    print("%s. %s" % ('Q', 'Quit'))

    menu_item = input("\nChoose: ")

    if menu_item == '1': add_round_file()
    if menu_item == '2': add_round_editor()
    if menu_item == '3': course_editor()
    if menu_item == '4': test_shot()
    if menu_item == '5': stats_viewer()
    if menu_item == 'q' or menu_item == 'Q': quit()

    main_menu()  # Reset if invalid choice


def test_shot():
    print('\nShot codes: t = tee, f = frairway, r = rough, s = sand, g = green', '   Press Q to quit')

    shot1 = input('\nInitial Shot Code: ')

    if not shot_valid(shot1):
        print('Invalid Shot Code: ' + str(shot1))
        test_shot()

    shot2 = input('Landing Shot Code: ')

    if not shot_valid(shot2):
        print('Invalid Shot Code: ' + str(shot2))
        test_shot()

    if shot1 == 'q' or shot1 == 'Q':
        main_menu()

    if shot2 == 'q' or shot2 == 'Q':
        main_menu()

    print('Strokes Gained PGA :', ' ', round(Baseline_data.loc[shot1, 'PGA'] - Baseline_data.loc[shot2, 'PGA'] - 1, 3))  # Calculation for strokes gained
    print()
    test_shot()


def add_round_file():
    with open('round.txt') as f:  # Get the round.txt data to a list
        vlround = f.readlines()

    vlround = [x.strip() for x in vlround]  # Remove new lines

    vdate = parser.parse(input("\nEnter date: "))

    print('\nCourses list:')

    for x in range(len(lcourses)):
        print(x+1, '-', lcourses[x])

    vcourse = input("\nChoose Course: ")

    vcourse = lcourses[int(vcourse)-1]

    round_data = []
    course_data = pd.read_csv('./Courses/' + vcourse + '.csv').set_index('Hole')

    current_hole = 0
    current_shot = 1

    for x in range(len(vlround)):

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
            strokes_gained = Baseline_data.loc[shot_code, 'PGA'] - Baseline_data.loc[next_shot_code, 'PGA'] - 2  # Calculation for strokes gained and add one shot for penalty
        else:
            strokes_gained = Baseline_data.loc[shot_code, 'PGA'] - Baseline_data.loc[next_shot_code, 'PGA'] - 1  # Calculation for strokes gained

        round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, course_data.loc[current_hole, 'Par'], Baseline_data.loc[shot_code, 'Description'], round(Baseline_data.loc[shot_code, 'PGA'], 3), round(strokes_gained,3)])  # Create list of shots data
        current_shot += 1

    round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par', 'ShotType', 'PGA Avg', 'StrokesGained']).set_index('Date')  # Create dataframe from list
    round_df.to_csv('ShotDB.csv', mode='a', header=False)


def add_round_editor():
    vdate = parser.parse(input("\nEnter date: "))
    print(vdate)

    print('\nCourses list:')

    for x in range(len(lcourses)):
        print(x + 1, '-', lcourses[x])

    vcourse = input("\nChoose Course: ")

    vcourse = lcourses[int(vcourse) - 1]

    course_data = pd.read_csv('./Courses/' + vcourse + '.csv').set_index('Hole')
    round_data = []

    for label, row in course_data.iterrows():
        s = str(course_data.loc[label, 'Distance'])+'t'
        print('Hole ' + str(label) + ':')
        print(s + ' Start')
        round_data.append(s)

        s_input = ''

        # TODO: make sure input is valid shot code
        while s_input != 'h':
            s_input = input('Next Shot: ')

            if shot_valid(s_input):
                if 'h' in s_input:
                    if s_input != 'h':
                        s_input = s_input[:-1]
                        round_data.append(s_input)
                        s_input = 'h'
                else:
                    round_data.append(s_input)
            else:
                print('Invalid Shot Code: ' + str(s_input))

    current_hole = 0
    current_shot = 1

    vlround = round_data
    vlround = [x.strip() for x in vlround]

    round_data = []

    print(vlround)

    for x in range(len(vlround)):

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

        print(shot_code,next_shot_code)

        if 'p' in next_shot_code:
            next_shot_code = next_shot_code[:-1]  # remove the p
            strokes_gained = Baseline_data.loc[shot_code, 'PGA'] - Baseline_data.loc[next_shot_code, 'PGA'] - 2  # Calculation for strokes gained and add one shot for penalty
        else:
            strokes_gained = Baseline_data.loc[shot_code, 'PGA'] - Baseline_data.loc[next_shot_code, 'PGA'] - 1  # Calculation for strokes gained

        round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, course_data.loc[current_hole, 'Par'], Baseline_data.loc[shot_code, 'Description'], round(Baseline_data.loc[shot_code, 'PGA'], 3), round(strokes_gained, 3)])  # Create list of shots data
        current_shot += 1

    print(round_data)

    round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par', 'ShotType', 'PGA Avg', 'StrokesGained']).set_index('Date')  # Create dataframe from list
    round_df.to_csv('ShotDB.csv', mode='a', header=False)


def course_editor():
    print(3)


def stats_viewer():
    print(4)


def shot_valid(code):
    if 'h' in code :
        return True

    if not code[:-1].isnumeric():
        return False

    if not any(s in code for s in ('t', 's', 'f', 'g', 'r')):
        return False



    return True


main_menu()

# source = 'round.txt'
#     with open(source) as f:
#         vlround = f.readlines()
#     vlround = [x.strip() for x in vlround]
#     print(vlround)
#     vdate = input("\nEnter Date: ")
#     vcourse = input("\nEnter Course: ")
#
#     #  Initiate Variables
#     round_data = []
#     current_hole = 0
#     current_shot = 1
#     good_shots = 0
#     bad_shots = 0
#     compare_score = 'PGA'  # Choices: PGA, 80, 90, 100, Par (Estimated from PGA + x%)
#     course_data = pd.read_csv('./Courses/RiveSud.csv').set_index('Hole')  # Get Course data into dataframe, index is the hole #
#
#     for x in range(len(vlround)):  # Loop all the shots
#         if 't' in vlround[x]:  # Change hole and reset shot count when on a tee
#             current_hole += 1
#             current_shot = 1
#
#         try:  # count as holed if next shot is on tee or last shot
#             next_shot_code = vlround[x + 1]
#         except IndexError:
#             next_shot_code = 'holed'  # Means last shot of the round, out of range: Holed is SG 0 in data
#         if 't' in next_shot_code:
#             next_shot_code = 'holed'  # Next shot on tee (next hole) = holed is SG 0 in data
#
#         if 'p' in vlround[x]:  # Determine the current shot code
#             shot_code = vlround[x][:-1]  # remove the p from the shot code and add a shot for the penality
#             current_shot += 1
#         else:
#             shot_code = vlround[x]
#
#         if 'p' in next_shot_code:
#             next_shot_code = next_shot_code[:-1]  # remove the p
#             SG = Baseline_data.loc[shot_code, compare_score] - Baseline_data.loc[next_shot_code, compare_score] - 2  # Calculation for strokes gained and add one shot for penalty
#         else:
#             SG = Baseline_data.loc[shot_code, compare_score] - Baseline_data.loc[next_shot_code, compare_score] - 1  # Calculation for strokes gained
#
#         if SG > 0.2 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a good shot if SG is over 0.2, exclude putting
#             good_shots += 1
#         if SG < -0.6 and not Baseline_data.loc[shot_code,'Description'] == 'Putting':  # Add a bad shot if SG is less  -0.6, exclude putting
#             bad_shots += 1
#
#         round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, course_data.loc[current_hole, 'Par'], Baseline_data.loc[shot_code,'Description'],Baseline_data.loc[shot_code,compare_score], SG])  # Create list of shots data
#         current_shot += 1
#
#     round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par', 'ShotType', 'PGA Avg', 'StrokesGained'])  # Create dataframe from list
#
#     lshot_types = ['Drive', 'Long (+231 yds)', 'Long Approach (176 - 230 yds)', 'Medium Approach (126 - 175 yds)', 'Short Approach (81 - 125 yds)', 'Pitching (21 - 80 yds)', 'Around the Green (0 - 20 yds)', 'Bunker', 'Putting']  # Different shot types
#
#     for x in lshot_types:  # Get Strokes Gained per shot
#         print(x, ',Count:', round(round_df['StrokesGained'][round_df['ShotType'] == x].count(), 2), ',Avg:', round(round_df['StrokesGained'][round_df['ShotType'] == x].mean(), 2), ',Worst:', round(round_df['StrokesGained'][round_df['ShotType'] == x].min(), 2), ',Best:', round(round_df['StrokesGained'][round_df['ShotType'] == x].max(), 2), ',Total:', round(round_df['StrokesGained'][round_df['ShotType'] == x].sum(), 2))
#
#     total_shots = 0
#     for x in range(len(course_data)):  # Get scores per hole for the round
#         print('Hole #', x + 1, ' - ', round_df['Shot #'][round_df['Hole #'] == x + 1].max())
#         total_shots += round_df['Shot #'][round_df['Hole #'] == x + 1].max()
#
#     score = total_shots - course_data['Par'].sum()
#     score = '+' + str(score)
#     print('Total:', total_shots,' ',score,' Good Shots:',good_shots, ' Flobbed Shots:', bad_shots)  # Print total score for the round
#
#     round_df.to_csv('out.csv')
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
# # TODO
# # TODO
# # TODO
# # TODO
# # TODO  Produce Reports: last Round, last 5 Rounds, last 10 rounds, Overall
# # TODO
# # TODO
# # TODO
# # TODO
