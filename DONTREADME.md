1

# JUST ASK ChatGPT

---

## Love hard way

---

### instal

`pip install pandas PULP collections IPython json`  ＼(ﾟｰﾟ＼)

### How to use 

just put `data.json` file in same dir of code  ( ﾉ ﾟｰﾟ)ﾉ

#### 🛑very very important 🛑

json file contain 4 parts :

- courses_data  columns: ["course", "lecture", "department_n_year", "professor", "assistant", "lecs rooms", "labs rooms", "section"]

  - course : name of course
  - lecture: lecture hours
  - section : section hours
  - professor : professor of this course
  - assistant : assistant of this course
  - lecs rooms : can be `all` or spiscfice hall ` A101`  or list `["101","102","103",....``]`
  - labs rooms : same thing but for section ( ´･･)ﾉ(._.`)

  ```

  "courses_data": {
    "columns": ["course", "lecture", "department_n_year", "professor", "assistant", "lecs rooms", "labs rooms", "section"],
    "index": [array of indices],
    "data": [array of course entries] ex : ["Programming Essentials in Python", 2, "1", "Dr. David Lee", "Yara", "all", "['A104', 'A105']", 3]
  }
  ```
- work_days -  name & type & str like list that contain working day ex :`[1,2,3]`  (**must** **be table)**

```

"work_days": {
  "columns": ["name", "type", "days"],
  "index": [array of indices],
  "data": [array of availability entries]
}
```

- department_groups - every department and  how number of groups (**must** **be table)**

```

"department_groups": {
  "department": [list of department IDs],
  "group_count": [corresponding group counts]
}
```

- study_places - contain 2 list halls & labs

```

"study_places": {
  "halls": [list of lecture halls],
  "labs": [list of lab rooms]
}
```

**you can see data.json for real example**

### Output Structure

```
json
{
  "departments": {
    "department_name": [
      {
        "day": 1,
        "hours": {
          "1": [
            {
              "course": "Course Name",
              "type": "lec/sec",
              "professor": "Professor Name",
              "hall": "Room",
              "group": 1  // Only for sections
            }
          ],
          // ... other hours ...
        }
      },
      // ... other days ...
    ]
    // ... other departments ...
  }
}
```



Now go forth and schedule with style! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
