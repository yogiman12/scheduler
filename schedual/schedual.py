from pulp import *
import pandas as pd
from IPython.display import display, HTML
from collections import defaultdict


class schedule:
    def __init__(self):
        self.df_groups = None
        self.df_courses = None
        self.problem = LpProblem("Schedule_Table", LpMinimize)
        self.days = list(range(1, 6))  # Days 1-5
        self.hours = list(range(1, 11))  # Hours 1-10
        self.halls = []  # Will be populated with actual room names
        # self.labs = []  add it in feature
        self.courses = []
        self.available_days = {}
        self.Professor_days = {}
        self.professors = {}
        self.departments = {}
        self.course_hours = {}
        self.choices = None
        self.allowed_rooms = {}  # Maps course to list of allowed halls

    @staticmethod
    def parse_rooms(room_data):
        if isinstance(room_data, list):
            return list(set(room_data)) if room_data else 'all'
        return 'all'

    def load_data(self, json_file_path: str = "data.json") -> None:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            
        self.df_courses = pd.DataFrame(data=data['courses_data']['data'],columns=data['courses_data']['columns'])
        self.df_groups= pd.DataFrame(data['department_groups'])
        
        df_days =pd.DataFrame(data=data['work_days']['data'],columns=data['work_days']['columns'])
        place = data['study_places']
        self.halls = [*place['halls'],*place['labs']] # change it  in indeviuual vars
        self.Professor_days = df_days.set_index('name')['days'].to_dict()


    def handle_data(self) -> dict:
        # self.df_courses = pd.read_csv(csv_filepath)  # replace it with json 
        
        # df['Section'] = df['Tutorial'] + df['Lab / workshop']
        # First pass: Collect all rooms and course room info
        all_rooms = set()
        course_room_info = {}
        grouped = self.df_courses.groupby('course_name')
        for course_name, group in grouped:
            first_row = group.iloc[0]
            lec_rooms = self.parse_rooms(first_row['lecs rooms'])
            lab_rooms = self.parse_rooms(first_row['labs rooms'])
            course_room_info[course_name] = {'lec': lec_rooms, 'lab': lab_rooms}
            if lec_rooms != 'all':
                all_rooms.update(lec_rooms)
            if lab_rooms != 'all':
                all_rooms.update(lab_rooms)
        self.halls = sorted(list(all_rooms))
        
        # Second pass: Process courses and assign allowed rooms
        self.allowed_rooms = {}
        for course_name, group in grouped:
            first_row = group.iloc[0]
            lecture = first_row['lecture_length']
            professor = first_row['teacher_name']
            assistant = first_row['assistant_name']
            section = first_row['section_length']
            years = group['department_n_year'].unique()
            
            # Process lecture
            course_lec = f"{course_name}|lec"
            self.courses.append(course_lec)
            self.available_days[course_lec] = self.Professor_days[professor]
            lec_rooms_info = course_room_info[course_name]['lec']
            allowed_lec = self.halls if lec_rooms_info == 'all' else lec_rooms_info
            self.allowed_rooms[course_lec] = allowed_lec
            
            if professor not in self.professors:
                self.professors[professor] = set()
            self.professors[professor].add(course_lec)
            self.course_hours[course_lec] = lecture
            
            # Process section
            if section != 0:
                course_sec = f"{course_name}|sec"
                self.courses.append(course_sec)
                self.available_days[course_sec] = self.Professor_days[assistant]
                lab_rooms_info = course_room_info[course_name]['lab']
                allowed_lab = self.halls if lab_rooms_info == 'all' else lab_rooms_info
                self.allowed_rooms[course_sec] = allowed_lab
                
                if assistant not in self.professors:
                    self.professors[assistant] = set()
                self.professors[assistant].add(course_sec)
                self.course_hours[course_sec] = section
            
            # Add to departments
            for year in years:
                if year not in self.departments:
                    self.departments[year] = set()
                self.departments[year].add(course_lec)
                if section != 0:
                    self.departments[year].add(course_sec)
        return self.departments
    
    def duplicate_sections_for_department(self, department, num_groups):
        """
        Duplicates lab sections (sec) for a given department (year) based on the number of groups required.
        
        For each section in the department, creates (num_groups - 1) duplicates to accommodate multiple groups.
        Each duplicate is treated as a separate course with the same constraints except for scheduling time.
        
        Parameters
        ----------
        department : int
            The department (year) for which sections need duplication.
        num_groups : int
            The total number of groups required for each section in the department.
        
        Returns
        -------
        None
        """
        num_groups = int(num_groups)
        department = str(department)
        if num_groups < 1:
            raise ValueError("Number of groups must be at least 1")
        
        # No need to duplicate if only 1 group is required
        if num_groups == 1:
            return
        
        # Get all sections in the department (courses ending with "|sec")
        sections = [course for course in self.departments.get(department, set()) if course.endswith("|sec")]
        
        for original_section in sections:
            # Create (num_groups - 1) duplicates
            for i in range(1, num_groups):
                new_course = f"{original_section}_{i}"
                
                # Skip if the new course already exists
                if new_course in self.courses:
                    continue
                
                # Add new course to the courses list
                self.courses.append(new_course)
                
                # Copy available days from the original section
                self.available_days[new_course] = self.available_days[original_section].copy()
                
                # Copy allowed rooms from the original section
                self.allowed_rooms[new_course] = self.allowed_rooms.get(original_section, [])
                
                # Set the same course hours (duration) as the original
                self.course_hours[new_course] = self.course_hours[original_section]
                
                # Find the professor (assistant) for the original section
                assistant = None
                for prof, courses in self.professors.items():
                    if original_section in courses:
                        assistant = prof
                        break
                if assistant is not None:
                    self.professors[assistant].add(new_course)
                else:
                    # Handle case where original section has no assigned professor (unlikely if data is correct)
                    pass
                
                # Add the new course to the department's set of courses
                if department in self.departments:
                    self.departments[department].add(new_course)
                else:
                    # If the department doesn't exist, create a new entry (though this shouldn't happen if called correctly)
                    self.departments[department] = {new_course}


    def create_variables(self):
        self.choices = LpVariable.dicts(
            "slot",
            (self.days, self.hours, self.halls, self.courses),
            cat="Binary"
        )

    def constrain_rooms(self):
        for course in self.courses:
            allowed = self.allowed_rooms.get(course, [])
            for hall in self.halls:
                if hall not in allowed:
                    for day in self.days:
                        for sh in self.hours:
                            self.problem += self.choices[day][sh][hall][course] == 0

    # Include other existing methods (constrain_start_hours, add_no_overlap_constraints, etc.) here
            
    def objective_function(self, day_weight=50, hour_weight=50):
        self.problem += lpSum(
            (d * day_weight + sh * hour_weight) * self.choices[d][sh][hall][course]
            for d in self.days
            for sh in self.hours
            for hall in self.halls
            for course in self.courses
        )

    def create_variables(self) -> None:
        """
        Creates a dictionary of binary variables for scheduling slots.
        
        This method initializes a PuLP variable dictionary where each variable represents
        a slot allocation decision.
        The variables are binary, indicating whether a
        particular combination of day, hour, hall, and course is chosen.
        
        The variables are structured as:
        - Indexing: (day, hour, hall, course)
        - Each variable is binary (0 or 1)
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
            Sets the `choices` attribute with the initialized variables.
        
        Raises
        ------
        AttributeError
            If any of the required instance attributes (days, hours, halls, courses) are not defined.
        """
        if not all(hasattr(self, attr) for attr in ["days", "hours", "halls", "courses"]):
            raise AttributeError("Required attributes not set")
            
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
                                course_name = entry.split(" (")[0]
                                if course_name in courses:
                                    entries.append(f"{entry} (Hall {hall})")
                    dept_df.at[day, hour] = "<br>".join(entries) if entries else ""
            list_of_dfs.append(dept_df)
        return list_of_dfs
    def solution_to_json(self):
        """
        Converts the schedule solution to a JSON structure.
        """
        course_to_professor = {course: prof for prof, courses in self.professors.items() for course in courses}
        schedule_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        # Populate schedule_dict
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

        # Build JSON structure
        schedule_json = {"departments": {}}
        
        for dept, dept_courses in self.departments.items():
            dept_key = str(dept)
            dept_schedule = []
            
            for day in self.days:
                day_schedule = {
                    "day": day,
                    "hours": {str(hour): [] for hour in self.hours}
                }
                
                for hour in self.hours:
                    hour_entries = []
                    
                    # Check all halls for this hour
                    for hall in self.halls:
                        for entry in schedule_dict[day][hour].get(hall, []):
                            # Parse course components
                            course_part, professor_part = entry.split(" (", 1)
                            professor = professor_part.split(")", 1)[0].strip()
                            course_name, session_type_full = course_part.split("|", 1)
                            
                            # Reconstruct original course identifier
                            original_course = f"{course_name}|{session_type_full.split('_')[0]}"  # lec/sec
                            
                            # Only include if course belongs to this department
                            if original_course not in dept_courses:
                                continue
                                
                            # Handle group numbering
                            session_type = "lec"
                            group = None
                            if "sec" in session_type_full:
                                session_type = "sec"
                                if "_" in session_type_full:
                                    _, group_str = session_type_full.split("_", 1)
                                    group = int(group_str) + 1  # sec_0 → group 1
                                else:
                                    group = 1  # base section
                            
                            hour_entries.append({
                                "course": course_name,
                                "type": session_type,
                                "professor": professor,
                                "hall": hall,
                                "group": group
                            })
                    
                    day_schedule["hours"][str(hour)] = hour_entries
                
                dept_schedule.append(day_schedule)
            
            schedule_json["departments"][dept_key] = dept_schedule
        
        return schedule_json

    def save_schedule_to_json(self, filename="schedule.json"):
        """Saves the JSON schedule to a file"""
        schedule_data = self.solution_to_json()
        with open(filename, 'w') as f:
            json.dump(schedule_data, f, indent=2)
            
            
def main(display_dfs=False):
    table = schedule()
    table.load_data('data.json')
    table.handle_data()
    for i , row in list(table.df_groups.iterrows()):
        table.duplicate_sections_for_department(row['department'],row['group_count'])
    table.create_variables()
    table.constrain_start_hours()
    table.constrain_days()
    table.only_slot()
    table.add_no_overlap_constraints()
    table.constrain_pro()
    table.constrain_departments()
    table.constrain_rooms()
    table.objective_function(100, 100)

    status = table.problem.solve()
    if status == LpStatusOptimal:
        table.save_schedule_to_json()
    if status == LpStatusOptimal and display_dfs:
        print("Schedule found:")
        for df in table.solution_to_dataframe():
            display(HTML(df.to_html(escape=False)))
    else:
        # print("No valid schedule found.", LpStatus[status])
        # for df in table.solution_to_dataframe():
        #     display(HTML(df.to_html(escape=False)))
        pass

if __name__ == '__main__':
    main()