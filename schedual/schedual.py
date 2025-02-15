from pulp import *
import pandas as pd
from IPython.display import display, HTML
from collections import defaultdict


class schedule:
    def __init__(self):
        self.problem = LpProblem("Schedule_Table", LpMinimize)
        self.days = list(range(1, 6))  # Days 1-5
        self.hours = list(range(1, 11))  # Hours 1-10
        self.halls = list(range(101, 106))  # Halls 101-105
        self.courses = list("abcdefghi")
        self.available_days = {
            'a': [1, 2], 'b': [2, 3], 'c': [1, 2, 3], 'd': [1, 3],
            'e': [1, 2], 'f': [2, 3], 'g': [1, 2, 3], 'h': [1, 3], 'i': [2, 3]
        }
        self.professors = {
            "dr.A": ['a', 'b', 'c'], "dr.D.": ['d', 'e', 'f'],
            "dr.X": ['g', 'h'], "dr.Z": ['i']
        }
        self.departments = {
            "IT": ['a', 'b', 'c', 'd'], "Auto": ['e', 'f', 'g', 'h', 'i']
        }
        self.course_hours = {
            'a': 2, 'b': 1, 'c': 3, 'd': 2, 'e': 1,
            'f': 3, 'g': 2, 'h': 1, 'i': 3
        }
        self.choices = None

    def create_variables(self):
        self.choices = LpVariable.dicts(
            "slot",
            (self.days, self.hours, self.halls, self.courses),
            cat="Binary"
        )

    def constrain_start_hours(self):
        for course in self.courses:
            duration = self.course_hours[course]
            max_start = 10 - duration + 1
            for day in self.days:
                for hall in self.halls:
                    for sh in self.hours:
                        if sh > max_start:
                            self.problem += self.choices[day][sh][hall][course] == 0

    def objective_function(self, day_weight=50, hour_weight=50):
        self.problem += lpSum(
            (d * day_weight + sh * hour_weight) * self.choices[d][sh][hall][course]
            for d in self.days
            for sh in self.hours
            for hall in self.halls
            for course in self.courses
        )

    def add_no_overlap_constraints(self):
        for d in self.days:
            for hall in self.halls:
                for current_h in self.hours:
                    overlapping_vars = []
                    for course in self.courses:
                        duration = self.course_hours[course]
                        for sh in self.hours:
                            if sh <= current_h < sh + duration:
                                overlapping_vars.append(self.choices[d][sh][hall][course])
                    self.problem += lpSum(overlapping_vars) <= 1

    def only_slot(self):
        for course in self.courses:
            total = lpSum(
                self.choices[day][sh][hall][course]
                for day in self.days
                for sh in self.hours
                for hall in self.halls
            )
            self.problem += total == 1

    def constrain_days(self):
        for course, days_allowed in self.available_days.items():
            for day in self.days:
                if day not in days_allowed:
                    for sh in self.hours:
                        for hall in self.halls:
                            self.problem += self.choices[day][sh][hall][course] == 0

    def constrain_departments(self):
        for dept, courses in self.departments.items():
            for day in self.days:
                for current_h in self.hours:
                    dept_vars = []
                    for course in courses:
                        duration = self.course_hours[course]
                        for sh in self.hours:
                            if sh <= current_h < sh + duration:
                                for hall in self.halls:
                                    dept_vars.append(self.choices[day][sh][hall][course])
                    self.problem += lpSum(dept_vars) <= 1

    def constrain_pro(self):
        for prof, courses in self.professors.items():
            for day in self.days:
                for current_h in self.hours:
                    prof_vars = []
                    for course in courses:
                        duration = self.course_hours[course]
                        for sh in self.hours:
                            if sh <= current_h < sh + duration:
                                for hall in self.halls:
                                    prof_vars.append(self.choices[day][sh][hall][course])
                    self.problem += lpSum(prof_vars) <= 1

    def solution_to_dataframe(self):
        course_to_professor = {course: prof for prof, courses in self.professors.items() for course in courses}
        schedule_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for day in self.days:
            for sh in self.hours:
                for hall in self.halls:
                    for course in self.courses:
                        if self.choices[day][sh][hall][course].value() == 1:
                            duration = self.course_hours[course]
                            prof = course_to_professor[course]
                            for h in range(sh, sh + duration):
                                if h > 10:
                                    continue
                                schedule_dict[day][h][hall].append(f"{course} ({prof})")

        list_of_dfs = []
        for dept, courses in self.departments.items():
            dept_df = pd.DataFrame(index=self.days, columns=self.hours, dtype=str)
            dept_df.index.name = f'Day/Hour - {dept}'
            for day in self.days:
                for hour in self.hours:
                    entries = []
                    for hall in self.halls:
                        if hall in schedule_dict[day][hour]:
                            for entry in schedule_dict[day][hour][hall]:
                                if entry[0] in courses:
                                    entries.append(f"{entry} (Hall {hall})")
                    dept_df.at[day, hour] = "<br>".join(entries) if entries else ""
            list_of_dfs.append(dept_df)
        return list_of_dfs


# class schedule :
#     def __init__(self):
#         self.problem : LpProblem = LpProblem("Schedule_Table", LpMinimize)
#         self.days :list = list(range(1,6))  # 7 day per week
#         self.hours :list = list(range(1,9))
#         self.halls :list = list(range(101,106))
#         self.courses = list("abcdefghi")
#         self.available_days : dict = {
#                                             'a': [1, 2],
#                                             'b': [2, 3],
#                                             'c': [1, 2, 3],
#                                             'd': [1, 3],
#                                             'e': [1, 2],
#                                             'f': [2, 3],
#                                             'g': [1, 2, 3],
#                                             'h': [1, 3],
#                                             'i': [2, 3]
#                                         }
#         self.professors : dict = {
#                                         "dr.A":['a','b','c'],
#                                         "dr.D.":['d','e','f'],
#                                         "dr.X":['g','h'],
#                                         "dr.Z":['i']
#                                         }
#         self.departments : dict = {
#                                 "IT":['a','b','c','d'],
#                                 "Auto":['e','f','g','h','i'],
#                                 }
#         self.choices : LpVariable = None
        
#         pass
    
#     def create_variables(self):
#         """Creates the LpVariables based on current parameters."""
#         self.choices = LpVariable.dicts(
#             "slot",
#             (self.days, self.hours, self.halls, self.courses),
#             cat="Binary"
#         )
    
#     def objective_function(self,day_wheight:int = 50,hour_wheight:int= 50):
#         self.problem += lpSum((d*day_wheight + h*hour_wheight) * self.choices[d][h][hall][course]
#                       for d in self.days
#                       for h in self.hours
#                       for hall in self.halls
#                       for course in self.courses
#                       )
#     def add_no_overlap_constraints(self):
#         """
#         Adds constraints to ensure no two courses are scheduled in the same time slot (day, hour, hale).
#         """
#         for d in self.days:
#             for h in self.hours:
#                 for hall in self.halls:
#                     self.problem += lpSum(self.choices[d][h][hall][c] for c in self.courses) <= 1
#     def only_slot(self):
#         """Adds constraints to ensure each course must be scheduled exactly once
#         """
#         for course in self.courses:
#             self.problem += lpSum(self.choices[day][hour][hall][course] for hour in self.hours for day in self.days for hall in self.halls) == 1
#     def constrain_days(self):
#         # Add constraints to restrict every course to his available days only
#         for c in self.available_days:
#             for d in self.days :
#                 if d not in self.available_days[c] :
#                     for h in self.hours:
#                         for hall in self.halls:
#                             self.problem += self.choices[d][h][hall][c] == 0 
                            
#     def constrain_departments(self):
#         """Ensures only 1 course per department can be taught in the same hall and time slot"""
#         for dept, courses in self.departments.items():
#             for day in self.days:
#                 for hour in self.hours:
#                     # Sum over all halls for the department's courses at this day and hour
#                     dept_vars = [
#                         self.choices[day][hour][hall][course]
#                         for hall in self.halls
#                         for course in courses
#                     ]
#                     self.problem += lpSum(dept_vars) <= 1
#     def constrain_pro(self):
#         # For each professor, ensure they don't teach multiple courses simultaneously
#         for prof, courses in self.professors.items():
#             for day in self.days:
#                 for hour in self.hours:
#                     # Collect all possible teaching assignments for this prof in this time slot
#                     time_slot_vars = [
#                         self.choices[day][hour][hall][course]
#                         for course in courses
#                         for hall in self.halls
#                     ]
#                     # Add constraint: ≤1 course taught per time slot
#                     self.problem += lpSum(time_slot_vars) <= 1
                    
#     def solution_to_dataframe(self):
#         # Create reverse mapping from courses to professors
#         course_to_professor = {}
#         for prof, courses in self.professors.items():
#             for course in courses:
#                 course_to_professor[course] = prof

#         # Initialize a list to store department-specific DataFrames
#         list_of_dfs = []

#         # Iterate over each department and its courses
#         for department, courses_in_dept in self.departments.items():
#             # Initialize empty DataFrame for the department
#             dept_df = pd.DataFrame(
#                 index=self.days,
#                 columns=self.hours,
#                 dtype=str
#             )
#             dept_df.index.name = f'Day/Hour - {department}'

#             # Fill the DataFrame with schedule information for the department's courses
#             for day in self.days:
#                 for hour in self.hours:
#                     entries = []
#                     for hall in self.halls:
#                         for course in courses_in_dept:
#                             if course in self.courses and self.choices[day][hour][hall][course].value() == 1:
#                                 prof = course_to_professor.get(course, "Unknown")
#                                 entries.append(f"{course} ({hall}) - {prof}")
#                     # Join multiple entries with newline if same timeslot
#                     dept_df.at[day, hour] = "<br>".join(entries) if entries else ""

#             # Append the department DataFrame to the list
#             list_of_dfs.append(dept_df)

#         return list_of_dfs
