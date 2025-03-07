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
                                # Extract the full course name (e.g., "h" or "ii" from "h (dr.X)" or "ii (dr.Z)")
                                course_name = entry.split(" (")[0]
                                if course_name in courses:
                                    entries.append(f"{entry} (Hall {hall})")
                    dept_df.at[day, hour] = "<br>".join(entries) if entries else ""
            list_of_dfs.append(dept_df)
        return list_of_dfs
    
    def save_department_schedules_to_csv(self, output_dir="schedules", filename_prefix="schedule"):
        """
        Generates separate CSV files for each department with every hour slot.
        Format: Course, Professor, Day, Hour, Hall
        """
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        course_to_professor = {course: prof for prof, courses in self.professors.items() for course in courses}
        
        # Collect all time slots for courses
        all_slots = []
        for day in self.days:
            for start_hour in self.hours:
                for hall in self.halls:
                    for course in self.courses:
                        if self.choices[day][start_hour][hall][course].value() == 1:
                            duration = self.course_hours[course]
                            # Add a row for each hour the course occupies
                            for hour in range(start_hour, start_hour + duration):
                                if hour > 10:  # Skip if exceeds max hours
                                    continue
                                all_slots.append({
                                    "Course": course,
                                    "Professor": course_to_professor[course],
                                    "Day": day,
                                    "Hour": hour,
                                    "Hall": hall
                                })

        # Create DataFrame with all slots
        all_df = pd.DataFrame(all_slots)
        
        # Generate department-specific files
        department_dfs = {}
        for dept, courses in self.departments.items():
            dept_df = all_df[all_df['Course'].isin(courses)]
            dept_df = dept_df.sort_values(['Day', 'Hour', 'Hall'])
            
            safe_dept = dept.replace(" ", "_").replace("/", "_")
            filename = os.path.join(output_dir, f"{filename_prefix}_{safe_dept}.csv")
            dept_df.to_csv(filename, index=False)
            department_dfs[dept] = dept_df
        
        return department_dfs