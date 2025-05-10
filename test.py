# old test
import pandas as pd
from  schedual.schedual import *
df = pd.read_csv("tables/collage - ict.csv")
df1 = df[df['Semester'] == 1]
data = {"dr":{},"dep":{}}
for i in df1['Professor'].unique():
    data['dr'][i]=tuple(df1[df1['Professor']==i]['Course'].unique())
for i in df1['Year'].unique():
    data['dep'][i]=tuple(df1[df1['Year']==i]['Course'].unique())
    # print("-----")
available_days: dict = {
    'Dr. Alicia Chen':       [1, 3, 5],
    'Dr. Marcus Johnson':    [2, 4, 6],
    'Dr. Emily Wong':        [1, 2, 4],
    'Dr. Robert Taylor':     [3, 5],
    'Dr. Sarah Martinez':    [1, 2, 3],
    'Dr. David Lee':         [2, 4],
    'Dr. Thomas Wilson':     [1, 3, 6],
    'Dr. Rachel Green':      [4, 5, 6],
    'Dr. Jennifer Lopez':    [2, 3, 6],
    'Dr. James White':       [1, 5],
    'Dr. Christopher Davis': [2, 4, 5],
    'Dr. Olivia Clark':      [3, 6],
    'Dr. Lisa Anderson':     [1, 4, 6],
    'Dr. Michael Brown':     [2, 3, 4, 5]
}
_={}
for d , days in available_days.items():
    for _d , cs in data['dr'].items():
        for c in cs:
            if d == _d:
                _[c] = days 
data['available_days'] =_
courses_hours = {
    'Intro. to Cyber Security': 1,
    'IT Essentials': 2,
    'Technical English 1': 2,
    'Mathematics 1': 2,
    'Physics': 2,
    'Programming Essentials in Python': 2,
    'Linux Essentials': 2,
    'Programming Essentials in C++': 2,
    'Web Programming I': 1,
    'Introduction to DB': 2,
    'Digital Engineering': 2,
    'Operating System': 2,
    'Advanced Programming in C': 2,
    'Data Communication': 2,
    'Java Programming II': 1,
    'Computer Architecture': 2,
    'Microprocessor': 2,
    'Computer Graphics': 2,
    'CCNA R&S II': 2,
    'Network Administration': 2,
    'Mobile Programming II': 1,
    'IoT Architecture & Protocols/IoT Programming': 2,
    'Artificial Intelligence': 2,
    'Windows Programming I': 1,
    'Signal Processing': 2,
    'CCNA R&S IV': 2,
    'CCNA Cybersecurity Operations': 2,
    'Server Administration': 2,
    'Encryption Algorithm': 2
}

data
available_days: dict = {
    'Dr. Alicia Chen':       [1, 3, 5],
    'Dr. Marcus Johnson':    [2, 4, 6],
    'Dr. Emily Wong':        [1, 2, 4],
    'Dr. Robert Taylor':     [3, 5],
    'Dr. Sarah Martinez':    [1, 2, 3],
    'Dr. David Lee':         [2, 4],
    'Dr. Thomas Wilson':     [1, 3, 6],
    'Dr. Rachel Green':      [4, 5, 6],
    'Dr. Jennifer Lopez':    [2, 3, 6],
    'Dr. James White':       [1, 5],
    'Dr. Christopher Davis': [2, 4, 5],
    'Dr. Olivia Clark':      [3, 6],
    'Dr. Lisa Anderson':     [1, 4, 6],
    'Dr. Michael Brown':     [2, 3, 4, 5]
}
_={}
for d , days in available_days.items():
    for _d , cs in data['dr'].items():
        for c in cs:
            if d == _d:
                _[c] = days 
data['available_days'] =_
courses_hours
def main(display_dfs:bool= False,day_weight=100,hour_weight=10):
    table = schedule()
    table.halls = [101, 115, 208, 209, 210, 303, 325, 326, 327, 329]
    table.courses= sorted(list(data['available_days'].keys()))
    table.available_days = data['available_days']
    table.professors = data['dr']
    table.departments = data['dep']
    table.course_hours = courses_hours
    
    table.create_variables()
    
    table.constrain_days()
    table.only_slot()
    table.add_no_overlap_constraints()
    table.constrain_pro()
    table.constrain_departments()
    table.objective_function(hour_weight,hour_weight)

    table.problem.solve()
    if 1 == table.problem.status and display_dfs: 
        print("dataframe is ready")
        for i in table.solution_to_dataframe():
            display(HTML(i.to_html(escape=False))) 
            table.save_department_schedules_to_csv(filename_prefix="table")
        
    else:
        print("No valid schedule found",table.problem.status)
    return table.solution_to_dataframe()
dfs =main(True)
