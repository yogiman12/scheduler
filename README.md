# 🧠 JUST ASK ChatGPT – Course Scheduler

---

## 💡 Philosophy

**Love the hard way.**  
This tool was built to simplify the complex task of scheduling university courses using constraint-solving, all with a touch of joy. ✨

---

## 🚀 Installation

Make sure you have Python installed, then run:

```bash
pip install pandas pulp ipython
```

> 📝 No need to install `collections` or `json` — they’re part of Python’s standard library!

---

## 📦 How to Use

1. Place a file named `data.json` in the same directory as the code.
2. Run the script.
3. Get a beautifully structured schedule. ✨

---

## 📄 Structure of `data.json` (🛑 Must Follow This Format)

The `data.json` file should contain **4 sections**:

### 1. `courses_data`

Defines the list of all courses to be scheduled.

```json
"courses_data": {
  "columns": ["course", "lecture", "department_n_year", "professor", "assistant", "lecs rooms", "labs rooms", "section"],
  "data": [
    ["Programming Essentials in Python", 2, "1", "Dr. David Lee", "Yara", "all", ["A104", "A105"], 3]
  ]
}
```

**Fields Explained:**

- `course`: Name of the course
- `lecture`: Number of lecture hours
- `section`: Number of section/lab hours
- `professor`: Professor’s full name
- `assistant`: Assistant’s name
- `lecs rooms`: List of lecture rooms (can be `"all"`, a single string like `"A101"`, or a list like `["A101", "A102"]`)
- `labs rooms`: Same format as `lecs rooms`, but for lab/section rooms
- `department_n_year`: The department and year for this course, e.g., `"3s"` or `"1"`

---

### 2. `work_days`

Contains availability for professors and assistants.

```json
"work_days": {
  "columns": ["name", "type", "days"],
  "data": [
    ["Dr. David Lee", "professor", [1, 2, 4]],
    ["Yara", "assistant", [1, 2, 3, 4, 5, 6]]
  ]
}
```

- `name`: Full name of the staff
- `type`: `"professor"` or `"assistant"`
- `days`: List of available days (e.g., `[1, 2, 3]`)

---

### 3. `department_groups`

Specifies the number of groups per department/year.

```json
"department_groups": {
  "department": ["1", "2", "3s", "3n", "4s", "4n"],
  "group_count": [1, 2, 2, 2, 1, 2]
}
```

- `department`: Department+year identifiers
- `group_count`: How many student groups exist per department

---

### 4. `study_places`

Room availability for lectures and labs.

```json
"study_places": {
  "halls": ["A104", "A105", "A106", "A204"],
  "labs": ["A326", "A327", "A210", "A208"]
}
```

---

## 📤 Output Format

After processing, the generated schedule will look like:

```json
{
  "departments": {
    "1": [
      {
        "day": 1,
        "hours": {
          "1": [
            {
              "course": "Programming Essentials in Python",
              "type": "lec",
              "professor": "Dr. David Lee",
              "hall": "A104"
            },
            {
              "course": "Programming Essentials in Python",
              "type": "sec",
              "professor": "Yara",
              "hall": "A105",
              "group": 1
            }
          ]
        }
      }
    ]
  }
}
```

---

## 📎 Notes

- You **must** use real Python lists, not stringified ones (e.g., `["A101"]`, not `"['A101']"`).
- See `data.json` for a full working example.
- Output is structured by department, then day, then hour.

---

## 🎉 Go Forth and Schedule with Style!

(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧  
Have fun turning chaos into clean timetables.