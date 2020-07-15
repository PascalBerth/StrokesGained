import pandas as pd
import os
from dateutil import parser
import re

# Variables init
Baseline_data = pd.read_csv("data.csv").set_index('Code')           # Get baseline data into dataframe, index is the shot code
Baseline_set = '90'
lcourses = []


def main_menu():
    create_course_list()
    print()
    print('-= MAIN MENU =-')
    print()
    print("%s. %s" % (1, 'Add new round from file'))
    print("%s. %s" % (2, 'Add new round from editor'))
    print("%s. %s" % (3, 'Course Editor'))
    print("%s. %s" % (4, 'Test One shot'))
    print("%s. %s" % (5, 'Stats'))
    print("%s. %s" % (6, 'Test Code'))
    print("%s. %s" % ('Q', 'Quit'))

    menu_item = input("\nChoose: ")

    if menu_item == '1': add_round_file()
    if menu_item == '2': add_round_editor()
    if menu_item == '3': course_editor()
    if menu_item == '4': test_shot()
    if menu_item == '5': stats_viewer()
    if menu_item == '6': test_code()
    if menu_item == 'q' or menu_item == 'Q': quit()                 # Quit with Q

    main_menu()                                                     # Reset if invalid choice


def test_code():  # To test codes quickly
    print(create_shotdb())


def test_shot():  # Test one shot for SG
    print('\nShot codes: t = tee, f = frairway, r = rough, s = sand, g = green', '   Press Q to quit')

    shot1 = input('\nInitial Shot Code: ')

    if shot1 == 'q' or shot1 == 'Q':  # Quit with Q
        main_menu()

    if not shot_valid(shot1):
        print('Invalid Shot Code: ' + str(shot1))
        test_shot()

    shot2 = input('Landing Shot Code: ')

    if shot2 == 'q' or shot2 == 'Q':  # Quit with Q
        main_menu()

    if not shot_valid(shot2):
        print('Invalid Shot Code: ' + str(shot2))
        test_shot()

    print('Strokes Gained (' + str(Baseline_set) + '): ', round(Baseline_data.loc[shot1, Baseline_set] - Baseline_data.loc[shot2, Baseline_set] - 1, 3))  # Calculation for strokes gained
    print()
    test_shot()


def add_round_file():  # Add info from round.txt
    with open('round.txt') as f:  # Get the round.txt data to a list
        vlround = f.readlines()

    vlround = [x.strip() for x in vlround]  # Remove new lines

    vdate = parser.parse(input("\nEnter date: "))  # get datetime from input string
    vdate = vdate.date()  # Keep only the date from datetime

    print('\nCourses list:')

    for x in range(len(lcourses)):
        print(x + 1, '-', lcourses[x])

    vcourse = input("\nChoose Course: ")  # Select Course from list
    vcourse = lcourses[int(vcourse) - 1]

    add_round(vdate, vcourse, vlround)  # Pass variables to add the round shots to database


def add_round_editor():  # Enter info line per line
    vdate = parser.parse(input("\nEnter date: "))  # get datetime from input string
    vdate = vdate.date()  # Keep only the date from datetime

    print('\nCourses list:')

    for x in range(len(lcourses)):
        print(x + 1, '-', lcourses[x])

    vcourse = input("\nChoose Course: ")

    vcourse = lcourses[int(vcourse) - 1]

    course_data = pd.read_csv('./Courses/' + vcourse + '.csv').set_index('Hole')  # Get the course data to a dataframe
    round_data = []

    for label, row in course_data.iterrows():               # loop the dataframe   label = hole# (index)    row = row info
        s = str(course_data.loc[label, 'Distance']) + 't'   # get the hole distance for the first shot code
        print('Hole ' + str(label) + ':')                   # Hole #
        print(s + ' Start')                                 # Shot code to start
        round_data.append(s)                                # Add the starting shot to shot list

        s_input = ''                                        # Init the input variable

        while s_input != 'h':                               # loop until holed
            s_input = input('Next Shot: ')                  # get the next shot code from user

            if shot_valid(s_input):                         # test shot validity
                if 'h' in s_input:
                    if s_input != 'h':                      # if input is not only h  ex.: 12gh = 12g + holed
                        s_input = s_input[:-1]              # remove the h
                        round_data.append(s_input)          # add the correct code to the list
                        s_input = 'h'                       # set the input as h to skip to next hole
                else:
                    round_data.append(s_input)              # if no h, add the shot and stay in same hole
            else:
                print('Invalid Shot Code: ' + str(s_input))

    vlround = round_data
    vlround = [x.strip() for x in vlround]

    add_round(vdate,vcourse,vlround)  # Pass variables to add the round shots to database


def add_round(vdate,vcourse,vlround):  # Add round info to the Shots Database

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

        # if 'p' in next_shot_code:
        #     next_shot_code = next_shot_code[:-1]  # remove the p
        #     strokes_gained = Baseline_data.loc[shot_code, '90'] - Baseline_data.loc[next_shot_code, '90'] - 2  # Calculation for strokes gained and add one shot for penalty
        # else:
        #     strokes_gained = Baseline_data.loc[shot_code, '90'] - Baseline_data.loc[next_shot_code, '90'] - 1  # Calculation for strokes gained

        round_data.append([vdate, vcourse, vlround[x], current_hole, current_shot, course_data.loc[current_hole, 'Par']])  # Create list of shots data
        current_shot += 1

    round_df = pd.DataFrame(round_data, columns=['Date', 'Course', 'ShotCode', 'Hole #', 'Shot #', 'Par']).set_index('Date')  # Create dataframe from list
    round_df.to_csv('ShotDB.csv', mode='a', header=False)  # Append to shot database


def course_editor():
    print('TBD')
    main_menu()


def stats_viewer():
    print('\n')
    print("%s. %s" % (1, 'View Last Round'))
    print("%s. %s" % (2, 'Choose recent round'))
    print("%s. %s" % (3, 'Last 5 rounds'))
    print("%s. %s" % (4, 'This year stats (Detailed)'))
    print("%s. %s" % (5, 'Overall (Detailed)'))
    print("%s. %s" % ('Q', 'Quit'))

    menu_item = input("\nChoose: ")

    if menu_item == '1': show_stats('1')
    if menu_item == '2': show_stats('recent')
    if menu_item == '3': show_stats('5')
    if menu_item == '4': show_stats('year')
    if menu_item == '5': show_stats('all')
    if menu_item == 'q' or menu_item == 'Q': quit()

    main_menu()  # Reset if invalid choice


def show_stats(p):
    shotdb = pd.read_csv('./ShotDB.csv')

    # Add SG to shotdb2

    vlround = shotdb['ShotCode']

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


    if p == '1':
        date = shotdb['Date'].max()

        category = []

        for label, row in shotdb.iterrows():
            category.append(get_category(row['ShotCode']))
        shotdb['ShotType'] = category
        shotdb.to_csv('test.csv')

        lshot_types = ['Drive', 'Long (+231 yds)', 'Long Approach (176 - 230 yds)', 'Medium Approach (126 - 175 yds)',
                       'Short Approach (81 - 125 yds)', 'Pitching (21 - 80 yds)', 'Around the Green (0 - 20 yds)',
                       'Fairway Bunker', 'Greenside Bunker', 'Putting']

        for x in lshot_types:  # Get Strokes Gained per shot
            if not shotdb.loc[(shotdb['Date'] == date) & (
                    shotdb['ShotType'] == x), 'StrokesGained'].count() == 0:  # if a shot type has no occurence, skip it
                print('{:<32s}{:<7s}{:>3d}{:>9s}{:>7.2f}{:>9s}{:>7.2f}{:>9s}{:>7.2f}{:>9s}{:>7.2f}'.format(x,
                      '   Count:', shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].count(),
                      '   Avg:', round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].mean(), 2),
                      '   Worst:', round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].min(), 2),
                      '   Best:', round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].max(), 2),
                      '   Total:', round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].sum(), 2)))

    if p == 'all':

        category = []

        for label, row in shotdb.iterrows():
            category.append(get_category_detailed(row['ShotCode']))
        shotdb['ShotType'] = category
        shotdb.to_csv('test.csv')

        lshot_types = ['Drive', 'Long (+231 yds)', 'Approach (201 - 230 yds)',
                       'Approach (181 - 200 yds)', 'Approach (161 - 180 yds)', 'Approach (141 - 160 yds)',
                       'Approach (121 - 140 yds)', 'Approach (101 - 120 yds)', 'Approach (81 - 100 yds)',
                       'Pitching (51 - 80 yds)', 'Pitching (21 - 50 yds)', 'Around the Green (11 - 20 yds)',
                       'Around the Green (0 - 10 yds)', 'Fairway Bunker', 'Greenside Bunker', 'Putting (+30 ft)',
                       'Putting (21 - 30 ft)', 'Putting (12 - 20 ft)', 'Putting (6 - 12 ft)', 'Putting (-5 ft)'
                       ]

        for x in lshot_types:  # Get Strokes Gained per shot
            if not shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].count() == 0:  # if a shot type has no occurence, skip it
                print('{:<32s}{:<7s}{:>3d}{:>9s}{:>7.2f}{:>9s}{:>7.2f}{:>9s}{:>7.2f}{:>9s}{:>7.2f}'.format(x, '   Count:', shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].count(),
                      '   Avg:', round(shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].mean(), 2),
                      '   Worst:', round(shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].min(), 2),
                      '   Best:', round(shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].max(), 2),
                      '   Total:', round(shotdb.loc[(shotdb['ShotType'] == x), 'StrokesGained'].sum(), 2)))

    if p == '5':
        col_one_list = shotdb['Date'].tolist()
        col_one_list = pd.Series(col_one_list).drop_duplicates().tolist()
        col_one_list.sort()
        print(col_one_list)

        #shotdb.nlargest(2, ['Date'])
        #print(shotdb)

        startdate = ''
        enddate = ''
        category = []

        # for label, row in shotdb.iterrows():
        #     category.append(get_category(row['ShotCode']))
        # shotdb['ShotType'] = category
        # shotdb.to_csv('test.csv')
        #
        # lshot_types = ['Drive', 'Long (+231 yds)', 'Long Approach (176 - 230 yds)', 'Medium Approach (126 - 175 yds)',
        #                'Short Approach (81 - 125 yds)', 'Pitching (21 - 80 yds)', 'Around the Green (0 - 20 yds)',
        #                'Fairway Bunker', 'Greenside Bunker', 'Putting']
        #
        # for x in lshot_types:  # Get Strokes Gained per shot
        #     if not shotdb.loc[(shotdb['Date'] == date) & (
        #             shotdb['ShotType'] == x), 'StrokesGained'].count() == 0:  # if a shot type has no occurence, skip it
        #         print(x, ' - Count:',
        #               shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].count(),
        #               '   Avg:',
        #               round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].mean(),
        #                     2), '   Worst:',
        #               round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].min(), 2),
        #               '   Best:',
        #               round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].max(), 2),
        #               '   Total:',
        #               round(shotdb.loc[(shotdb['Date'] == date) & (shotdb['ShotType'] == x), 'StrokesGained'].sum(), 2))


def shot_valid(code):  # Determine if shot is valid, if shot code exist in baseline data shot code

    if 'h' in code:  # test if h present in code
        if code != 'h':  # if the code is not h only, remove the h
            code = code[:-1]  # Remove the h from the code

    if code in Baseline_data.index:
        return True
    else:
        return False


def get_category(code):
    dist = int(re.sub(r"\D", "", code))

    if 't' in code:
        if dist >= 231: return 'Drive'
        return get_distance(dist)

    if 'f' in code or 'r' in code:
        if dist >= 231: return 'Long (+231 yds)'
        return get_distance(dist)

    if 's' in code:
        if dist >= 50: return 'Fairway Bunker'
        else: return 'Greenside Bunker'

    if 'g' in code:
        return 'Putting'


def get_category_detailed(code):
    dist = int(re.sub(r"\D", "", code))

    if 't' in code:
        if dist >= 231: return 'Drive'
        return get_distance_detailed(dist)

    if 'f' in code or 'r' in code:
        if dist >= 231: return 'Long (+231 yds)'
        return get_distance_detailed(dist)

    if 's' in code:
        if dist >= 50:
            return 'Fairway Bunker'
        else:
            return 'Greenside Bunker'

    if 'g' in code:
        if dist >= 30: return 'Putting (+30 ft)'
        if dist in range(21, 30): return 'Putting (21 - 30 ft)'
        if dist in range(12, 21): return 'Putting (12 - 20 ft)'
        if dist in range(6, 12): return 'Putting (6 - 12 ft)'
        if dist <= 5: return 'Putting (-5 ft)'


def get_distance_detailed(dist):
    if dist in range(201, 231): return 'Approach (201 - 230 yds)'
    if dist in range(181, 201): return 'Approach (181 - 200 yds)'
    if dist in range(161, 181): return 'Approach (161 - 180 yds)'
    if dist in range(141, 161): return 'Approach (141 - 160 yds)'
    if dist in range(121, 141): return 'Approach (121 - 140 yds)'
    if dist in range(101, 121): return 'Approach (101 - 120 yds)'
    if dist in range(81, 101): return 'Approach (81 - 100 yds)'
    if dist in range(51, 81): return 'Pitching (51 - 80 yds)'
    if dist in range(21, 51): return 'Pitching (21 - 50 yds)'
    if dist in range(11, 21): return 'Around the Green (11 - 20 yds)'
    if dist in range(0, 11): return 'Around the Green (0 - 10 yds)'


def get_distance(dist):
    if dist in range(231, 800): return 'Long (+231 yds)'
    if dist in range(176, 231): return 'Long Approach (176 - 230 yds)'
    if dist in range(126, 176): return 'Medium Approach (126 - 175 yds)'
    if dist in range(81, 126): return 'Short Approach (81 - 125 yds)'
    if dist in range(21, 81): return 'Pitching (21 - 80 yds)'
    if dist in range(0, 21): return 'Around the Green (0 - 20 yds)'


def create_course_list():  # Create list of existing courses
    global lcourses
    lcourses = []
    for r, d, f in os.walk('./Courses'):
        for files in f:
            lcourses.append(files[:-4])


def create_shotdb():
    shotdb = pd.read_csv('./ShotDB.csv')

    sg_list = []
    for x in range(len(shotdb['ShotCode'])):
        shot_code = shotdb.loc[x, 'ShotCode']
        try:                                                        # count as holed if next shot is on tee or last shot
            next_shot_code = shotdb.loc[x + 1, 'ShotCode']
        except KeyError:
            next_shot_code = 'holed'                                # No next shot = holed
        if 't' in next_shot_code:
            next_shot_code = 'holed'                                # Holed is SG 0 in data

        if 'p' in shot_code: shot_code = shot_code[:-1]             # if p in shot code, remove it

        if 'p' in next_shot_code:                                   # if p (penality) in next shot code, remove it and add one stroke to calculation
            next_shot_code = next_shot_code[:-1]
            sg = Baseline_data.loc[shot_code, Baseline_set] - Baseline_data.loc[
                next_shot_code, Baseline_set] - 2                   # Calculation for strokes gained and add one shot for penalty
        else:
            sg = Baseline_data.loc[shot_code, Baseline_set] - Baseline_data.loc[
                next_shot_code, Baseline_set] - 1                   # Calculation for strokes gained

        sg = round(sg, 3)                                           # Keep only 3 digit

        sg_list.append(sg)

    shotdb['SG'] = sg_list
    shotdb.to_csv('test.csv')
    return shotdb


main_menu()

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
