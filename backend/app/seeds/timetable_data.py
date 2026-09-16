# Authoritative Timetable Seed Data for D.G. Tatkare Secondary & Higher Secondary School, Kolad
from app.models.timetable import Weekday

TEACHERS_DATA = [
    {"name": "Mrs. Jadhav S.S.", "class_name": "Class VIII-2"},
    {"name": "Mrs. Jadkar J.P.", "class_name": "Class VIII-1"},
    {"name": "Mrs. Tatkare S.V.", "class_name": None},
    {"name": "Mrs. Mahable A.A.", "class_name": "Class IX-1"},
    {"name": "Mrs. Patil S.D.", "class_name": "Class V-2"},
    {"name": "Mrs. Bhokte P.D.", "class_name": "Class V-1"},
    {"name": "Mrs. Tirmale S.J.", "class_name": None},
    {"name": "Mrs. Dhanavade R.J.", "class_name": "Class X-1"},
    {"name": "Mrs. Solanki J.A.", "class_name": None},
    {"name": "Mrs. Shinde M.M.", "class_name": "Class VII-1"},
    {"name": "Mr. Shende S.T.", "class_name": "Class IX-2"},
    {"name": "Mr. Padavi S.B.", "class_name": "Class VII-2"},
    {"name": "Mr. Thorve S.S.", "class_name": "Class VI-1"},
    {"name": "Ms. Prerna Rajiwade", "class_name": None},
    {"name": "Mrs. Patil", "class_name": None},
    {"name": "Mr. Tirmale S.R.", "class_name": None},
    {"name": "Mr. Hate D.H.", "class_name": None},
    {"name": "Mrs. Deshmukh A.V.", "class_name": "Class VI-2"},
    {"name": "Mrs. Kuthe A.P.", "class_name": "Class X-2"},
]

# Map teacher index (0-based) to list of periods (1 to 9) for Mon-Sat
# Format for each period: list of 6 strings for Mon, Tue, Wed, Thu, Fri, Sat
TIMETABLE_RAW = {
    # 0. Mrs. Jadhav S.S. (Class VIII-2)
    0: {
        1: ["Science 8-II", "Science 8-II", "Science 8-II", "Science 8-II", "Science 8-II", "Science 8-II"],
        2: ["Science 10-I", "Science 10-I", "Science 10-I", "Science 10-I", "Science 10-I", "Science 10-I"],
        3: ["Mathematics 7-II", "Mathematics 7-II", "Mathematics 7-II", "Mathematics 7-II", "Mathematics 7-II", "Mathematics 7-II"],
        4: ["-", "-", "-", "-", "Drawing 8-II", "Drawing 8-II"],
        5: ["-", "-", "-", "Drawing 8-II", "Drawing 8-II", "-"],
        6: ["Mathematics 6-I", "Mathematics 6-I", "Mathematics 6-I", "Mathematics 6-I", "Mathematics 6-I", "-"],
        7: ["-", "-", "W.S 10-I", "-", "W.S 10-I", "-"],
        8: ["-", "-", "Science 10-I", "Science 8-II", "Mathematics 7-II", "-"],
        9: ["Mathematics 6-I", "Mathematics 6-I", "Science 10-I", "Science 8-II", "-", "-"],
    },
    # 1. Mrs. Jadkar J.P. (Class VIII-1)
    1: {
        1: ["English 8-I", "English 8-I", "English 8-I", "English 8-I", "English 8-I", "English 8-I"],
        2: ["English 9-I", "English 9-I", "English 9-I", "English 9-I", "English 9-I", "English 9-I"],
        3: ["English 10-I", "English 10-I", "English 10-I", "English 10-I", "English 10-I", "English 10-I"],
        4: ["English 9-II", "English 9-II", "English 9-II", "English 9-II", "English 9-II", "English 9-II"],
        5: ["English 9-I", "-", "-", "-", "-", "-"],
        6: ["English 10-II", "English 10-II", "English 10-II", "English 10-II", "-", "-"],
        7: ["-", "-", "-", "-", "-", "-"],
        8: ["English 10-II", "English 10-II", "-", "English 10-II", "English 10-II", "-"],
        9: ["Self Defence 9-I", "Self Defence 9-I", "English 9-II", "English 10-I", "-", "-"],
    },
    # 2. Mrs. Tatkare S.V.
    2: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Marathi 5-II"],
        3: ["Marathi 5-I", "Marathi 5-I", "Marathi 5-I", "Marathi 5-I", "Marathi 5-I", "Marathi 5-I"],
        4: ["Marathi 6-I", "Marathi 6-I", "Marathi 6-I", "Marathi 6-I", "Marathi 6-I", "Marathi 6-I"],
        5: ["-", "-", "-", "Environmental Studies-I 5-I", "Environmental Studies-II 5-I", "-"],
        6: ["Environmental Studies-I 5-I", "Environmental Studies-I 5-I", "Environmental Studies-I 5-I", "Environmental Studies-I 5-I", "Environmental Studies-I 5-I", "-"],
        7: ["Hindi 8-II", "Hindi 8-II", "Hindi 8-II", "Hindi 8-II", "Hindi 8-II", "-"],
        8: ["Environmental Studies-II 5-I", "Environmental Studies-II 5-I", "Environmental Studies-II 5-I", "Environmental Studies-II 5-I", "Environmental Studies-II 5-I", "-"],
        9: ["Scout Guide 9-I", "Scout Guide 9-I", "Hindi 8-II", "-", "-", "-"],
    },
    # 3. Mrs. Mahable A.A. (Class IX-1)
    3: {
        1: ["Marathi 9-I", "Marathi 9-I", "Marathi 9-I", "Marathi 9-I", "Marathi 9-I", "Marathi 9-I"],
        2: ["-", "-", "-", "-", "-", "Marathi 10-II"],
        3: ["-", "-", "-", "-", "Marathi 10-II", "Marathi 10-II"],
        4: ["Marathi 10-I", "Marathi 10-I", "Marathi 10-I", "Marathi 10-I", "Marathi 10-I", "Marathi 10-I"],
        5: ["Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Marathi 5-II", "Scout Guide 8-I"],
        6: ["Marathi 7-II", "Marathi 7-II", "Marathi 7-II", "Marathi 7-II", "-", "Scout Guide 8-I"],
        7: ["Marathi 10-II", "Marathi 10-II", "-", "Marathi 9-II", "-", "-"],
        8: ["Marathi 7-II", "W.S 9-II", "W.S 9-II", "-", "-", "-"],
        9: ["-", "Marathi 7-II", "Marathi 10-II", "Marathi 10-II", "-", "-"],
    },
    # 4. Mrs. Patil S.D. (Class V-2)
    4: {
        1: ["Environmental Studies-I 5-II", "Environmental Studies-I 5-II", "Environmental Studies-I 5-II", "Environmental Studies-I 5-II", "Environmental Studies-I 5-II", "Environmental Studies-I 5-II"],
        2: ["Social Science 7-II", "Social Science 7-II", "Social Science 7-II", "Social Science 7-II", "Social Science 7-II", "Social Science 7-II"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["Marathi 6-II", "Marathi 6-II", "Marathi 6-II", "Marathi 6-II", "Marathi 6-II", "Environmental Studies-II 5-II"],
        5: ["P.T. 7-II", "P.T. 7-II", "P.T. 7-II", "-", "-", "-"],
        6: ["-", "-", "-", "-", "P.T. 7-I", "-"],
        7: ["Environmental Studies-II 5-II", "Environmental Studies-II 5-II", "Environmental Studies-II 5-II", "Environmental Studies-II 5-II", "Environmental Studies-II 5-II", "-"],
        8: ["Social Science 6-I", "Social Science 6-I", "Social Science 6-I", "Social Science 6-I", "Social Science 6-I", "-"],
        9: ["Scout Guide 9-I", "Scout Guide 9-I", "Marathi 6-II", "Social Science 6-I", "-", "-"],
    },
    # 5. Mrs. Bhokte P.D. (Class V-1)
    5: {
        1: ["Mathematics 5-I", "Mathematics 5-I", "Mathematics 5-I", "Mathematics 5-I", "Mathematics 5-I", "Mathematics 5-I"],
        2: ["Science 6-I", "Science 6-I", "Science 6-I", "Science 6-I", "Science 6-I", "Science 6-I"],
        3: ["Mathematics 5-II", "Mathematics 5-II", "Mathematics 5-II", "Mathematics 5-II", "Mathematics 5-II", "Mathematics 5-II"],
        4: ["-", "-", "-", "-", "-", "-"],
        5: ["Social Science 6-II", "Social Science 6-II", "Social Science 6-II", "Social Science 6-II", "Social Science 6-II", "-"],
        6: ["-", "-", "-", "-", "Drawing 7-II", "-"],
        7: ["-", "-", "-", "Science 6-I", "Science 6-I", "-"],
        8: ["Mathematics 5-II", "Mathematics 5-II", "Drawing 7-II", "Drawing 7-II", "Social Science 6-II", "-"],
        9: ["Mathematics 5-I", "Mathematics 5-I", "-", "Drawing 7-II", "-", "-"],
    },
    # 6. Mrs. Tirmale S.J.
    6: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["-", "-", "-", "-", "-", "-"],
        3: ["Work Experience 6-I", "Work Experience 6-I", "Drawing 6-I", "Drawing 6-I", "Drawing 6-I", "Drawing 6-I"],
        4: ["Work Experience 5-II", "Work Experience 5-II", "Work Experience 5-II", "Drawing 5-II", "Drawing 5-II", "-"],
        5: ["Work Experience 5-I", "Work Experience 5-I", "Work Experience 5-I", "Work Experience 7-II", "Work Experience 7-II", "-"],
        6: ["Drawing 6-II", "Drawing 6-II", "Drawing 6-II", "Drawing 6-II", "Work Experience 6-II", "-"],
        7: ["Drawing 5-I", "Drawing 5-I", "Drawing 5-I", "P.T. 5-I", "P.T. 5-I", "-"],
        8: ["Work Experience 7-I", "Work Experience 7-I", "-", "Work Experience 6-II", "Drawing 5-II", "-"],
        9: ["P.T. 5-II", "P.T. 5-II", "P.T. 5-II", "P.T. 5-I", "-", "-"],
    },
    # 7. Mrs. Dhanavade R.J. (Class X-1)
    7: {
        1: ["Social Science 10-I", "Social Science 10-I", "Social Science 10-I", "Social Science 10-I", "Social Science 10-I", "Social Science 10-I"],
        2: ["-", "-", "-", "-", "-", "-"],
        3: ["Social Science 9-I", "Social Science 9-I", "Social Science 9-I", "Social Science 9-I", "Social Science 9-I", "Social Science 9-I"],
        4: ["-", "-", "P.T. 10-II", "P.T. 10-II", "P.T. 10-II", "-"],
        5: ["Marathi 8-I", "Marathi 8-I", "Marathi 8-I", "Marathi 8-I", "Marathi 8-I", "-"],
        6: ["Social Science 8-II", "Social Science 8-II", "Social Science 8-II", "Social Science 8-II", "Social Science 8-II", "-"],
        7: ["-", "Social Science 10-I", "-", "-", "-", "-"],
        8: ["Work Experience 8-II", "Work Experience 8-II", "Social Science 8-II", "-", "Marathi 8-I", "-"],
        9: ["Scout Guide 10-I", "Scout Guide 10-I", "-", "Social Science 9-I", "-", "-"],
    },
    # 8. Mrs. Solanki J.A.
    8: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["Science 8-I", "Science 8-I", "Science 8-I", "Science 8-I", "Science 8-I", "Science 8-I"],
        3: ["Science 9-II", "Science 9-II", "Science 9-II", "Science 9-II", "Science 9-II", "Science 9-II"],
        4: ["Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I"],
        5: ["Science 10-II", "Science 10-II", "Science 10-II", "Science 10-II", "Science 10-II", "-"],
        6: ["-", "-", "-", "Science 10-II", "Science 10-II", "-"],
        7: ["Drawing 7-I", "-", "-", "-", "Science 10-II", "-"],
        8: ["Science 8-I", "-", "-", "Science 9-II", "-", "-"],
        9: ["Science 8-I", "-", "Mathematics 7-I", "Science 9-II", "-", "-"],
    },
    # 9. Mrs. Shinde M.M. (Class VII-1)
    9: {
        1: ["Hindi 7-I", "Hindi 7-I", "Hindi 7-I", "Hindi 7-I", "Hindi 7-I", "Hindi 7-I"],
        2: ["-", "-", "-", "-", "-", "-"],
        3: ["Hindi 10-II", "Hindi 10-II", "Hindi 10-II", "Hindi 10-II", "-", "Hindi 10-II"],
        4: ["Hindi 9-I", "Hindi 9-I", "Hindi 9-I", "Hindi 9-I", "Hindi 9-I", "Hindi 9-I"],
        5: ["Hindi 10-I", "Hindi 10-I", "Hindi 10-I", "Hindi 10-I", "Hindi 10-I", "-"],
        6: ["Hindi 9-II", "Hindi 9-II", "Hindi 9-II", "Hindi 9-II", "Hindi 9-II", "-"],
        7: ["Work Experience 8-I", "Work Experience 8-I", "Hindi 10-II", "-", "-", "-"],
        8: ["Hindi 9-II", "Hindi 10-I", "Work Studies 9-I", "Work Studies 9-I", "-", "-"],
        9: ["Self Defence 9-II", "Self Defence 9-II", "-", "-", "-", "-"],
    },
    # 10. Mr. Shende S.T. (Class IX-2)
    10: {
        1: ["Social Science 9-II", "Social Science 9-II", "Social Science 9-II", "Social Science 9-II", "Social Science 9-II", "Social Science 9-II"],
        2: ["-", "Social Science 10-II", "Social Science 10-II", "Social Science 10-II", "Social Science 10-II", "-"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["Social Science 10-II", "Social Science 10-II", "-", "-", "-", "Social Science 10-II"],
        5: ["P.T. 8-II", "P.T. 8-II", "P.T. 8-II", "P.T. 9-I", "P.T. 9-I", "-"],
        6: ["Social Science 8-I", "Social Science 8-I", "Social Science 8-I", "Social Science 8-I", "Social Science 8-I", "-"],
        7: ["P.T. 9-II", "P.T. 9-II", "P.T. 9-II", "P.T. 10-I", "Social Science 9-II", "-"],
        8: ["P.T. 10-I", "P.T. 8-I", "P.T. 8-I", "P.T. 8-I", "P.T. 10-I", "-"],
        9: ["Scout Guide 10-I", "Scout Guide 10-I", "P.T. 9-I", "Social Science 8-I", "-", "-"],
    },
    # 11. Mr. Padavi S.B. (Class VII-2)
    11: {
        1: ["English 7-II", "English 7-II", "English 7-II", "English 7-II", "English 7-II", "English 7-II"],
        2: ["Science 7-I", "Science 7-I", "Science 7-I", "Science 7-I", "Science 7-I", "Science 7-I"],
        3: ["English 8-II", "English 8-II", "English 8-II", "English 8-II", "English 8-II", "English 8-II"],
        4: ["Science 7-II", "Science 7-II", "Science 7-II", "Science 7-II", "Science 7-II", "Science 7-II"],
        5: ["-", "Science 9-I", "-", "-", "-", "-"],
        6: ["-", "-", "-", "-", "-", "-"],
        7: ["Science 9-I", "Science 9-I", "Science 9-I", "Science 9-I", "Science 9-I", "-"],
        8: ["-", "Science 7-II", "Science 7-I", "Science 7-I", "Science 9-I", "-"],
        9: ["Scout Guide 9-I", "Scout Guide 9-I", "Science 7-II", "-", "-", "-"],
    },
    # 12. Mr. Thorve S.S. (Class VI-1)
    12: {
        1: ["English 6-I", "English 6-I", "English 6-I", "English 6-I", "English 6-I", "English 6-I"],
        2: ["English 6-II", "English 6-II", "English 6-II", "English 6-II", "English 6-II", "English 6-II"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["Hindi 5-I", "Hindi 5-I", "Hindi 5-I", "Hindi 5-I", "Hindi 5-I", "Hindi 5-I"],
        5: ["Hindi 6-I", "Hindi 6-I", "Hindi 6-I", "Hindi 6-I", "Hindi 6-I", "-"],
        6: ["Hindi 5-II", "Hindi 5-II", "Hindi 5-II", "Hindi 5-II", "Hindi 5-II", "-"],
        7: ["Hindi 7-II", "Hindi 7-II", "Hindi 7-II", "Hindi 7-II", "Hindi 7-II", "-"],
        8: ["-", "-", "-", "-", "-", "-"],
        9: ["Hindi 7-II", "-", "Hindi 6-I", "Hindi 5-II", "-", "-"],
    },
    # 13. Ms. Prerna Rajiwade
    13: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["English 5-I", "English 5-I", "English 5-I", "English 5-I", "English 5-I", "-"],
        3: ["English 7-I", "English 7-I", "English 7-I", "English 7-I", "English 7-I", "English 7-I"],
        4: ["-", "-", "-", "-", "-", "Science 6-II"],
        5: ["English 5-II", "English 5-II", "English 5-II", "English 5-II", "English 5-II", "-"],
        6: ["-", "-", "-", "-", "-", "-"],
        7: ["Science 6-II", "Science 6-II", "Science 6-II", "Science 6-II", "Science 6-II", "-"],
        8: ["-", "-", "English 5-II", "English 5-II", "-", "-"],
        9: ["Science 6-II", "Science 6-II", "English 5-I", "-", "-", "-"],
    },
    # 14. Mrs. Patil
    14: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["Mathematics 9-II", "Mathematics 9-II", "Mathematics 9-II", "Mathematics 9-II", "Mathematics 9-II", "-"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["-", "-", "-", "-", "-", "-"],
        5: ["-", "-", "-", "-", "-", "-"],
        6: ["Mathematics 10-I", "Mathematics 10-I", "Mathematics 10-I", "Mathematics 10-I", "Mathematics 10-I", "-"],
        7: ["Mathematics 10-I", "-", "Drawing 8-I", "Drawing 8-I", "-", "-"],
        8: ["-", "-", "-", "Mathematics 10-I", "Mathematics 9-II", "-"],
        9: ["-", "Drawing 8-I", "-", "-", "-", "-"],
    },
    # 15. Mr. Tirmale S.R. (Blank schedule)
    15: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["-", "-", "-", "-", "-", "-"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["-", "-", "-", "-", "-", "-"],
        5: ["-", "-", "-", "-", "-", "-"],
        6: ["-", "-", "-", "-", "-", "-"],
        7: ["-", "-", "-", "-", "-", "-"],
        8: ["-", "-", "-", "-", "-", "-"],
        9: ["-", "-", "-", "-", "-", "-"],
    },
    # 16. Mr. Hate D.H.
    16: {
        1: ["-", "-", "-", "-", "-", "-"],
        2: ["W.S 10-II", "-", "-", "-", "-", "-"],
        3: ["-", "-", "-", "-", "-", "-"],
        4: ["Science 7-II", "Science 7-II", "Science 7-II", "Science 7-II", "Science 7-II", "-"],
        5: ["P.T. 8-II", "P.T. 8-II", "P.T. 8-II", "-", "-", "Scout Guide 8-I"],
        6: ["-", "-", "-", "-", "-", "Scout Guide 8-I"],
        7: ["-", "-", "-", "W.S 10-II", "-", "-"],
        8: ["-", "Science 7-II", "-", "-", "-", "-"],
        9: ["Scout Guide 9-II", "Scout Guide 9-II", "Science 7-II", "-", "-", "-"],
    },
    # 17. Mrs. Deshmukh A.V. (Class VI-2)
    17: {
        1: ["Hindi 6-II", "Hindi 6-II", "Hindi 6-II", "Hindi 6-II", "Hindi 6-II", "Hindi 6-II"],
        2: ["-", "-", "-", "-", "-", "-"],
        3: ["Hindi 8-I", "Hindi 8-I", "Hindi 8-I", "Hindi 8-I", "Hindi 8-I", "Hindi 8-I"],
        4: ["Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II", "-", "-"],
        5: ["Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "Mathematics 7-I", "-"],
        6: ["Social Science 7-I", "Social Science 7-I", "Social Science 7-I", "Social Science 7-I", "-", "-"],
        7: ["P.T. 6-I", "P.T. 6-I", "P.T. 6-I", "-", "Social Science 7-I", "-"],
        8: ["P.T. 6-II", "P.T. 6-II", "P.T. 6-II", "-", "Marathi 7-I", "-"],
        9: ["Marathi 8-II", "Marathi 8-II", "-", "Social Science 7-I", "-", "-"],
    },
    # 18. Mrs. Kuthe A.P. (Class X-2)
    18: {
        1: ["Mathematics 10-II", "Mathematics 10-II", "Mathematics 10-II", "Mathematics 10-II", "Mathematics 10-II", "Mathematics 10-II"],
        2: ["Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II", "Mathematics 8-II"],
        3: ["Mathematics 6-II", "Mathematics 6-II", "Mathematics 6-II", "Mathematics 6-II", "Mathematics 6-II", "Mathematics 6-II"],
        4: ["Mathematics 8-I", "Mathematics 8-I", "Mathematics 8-I", "Mathematics 8-I", "Mathematics 8-I", "Mathematics 8-I"],
        5: ["-", "-", "-", "-", "-", "-"],
        6: ["Mathematics 9-I", "Mathematics 9-I", "Mathematics 9-I", "Mathematics 9-I", "Mathematics 9-I", "-"],
        7: ["-", "-", "-", "-", "-", "-"],
        8: ["Mathematics 9-I", "Mathematics 9-I", "Mathematics 10-II", "-", "Mathematics 8-II", "-"],
        9: ["Scout Guide 10-I", "Scout Guide 10-I", "Mathematics 8-I", "Mathematics 6-II", "-", "-"],
    },
}

WEEKDAYS = [
    Weekday.MONDAY,
    Weekday.TUESDAY,
    Weekday.WEDNESDAY,
    Weekday.THURSDAY,
    Weekday.FRIDAY,
    Weekday.SATURDAY,
]

def parse_cell(cell_str: str):
    """
    Parses a cell string like 'Science 8-II' into (subject, class_name, is_free)
    """
    if not cell_str or cell_str.strip() in ["-", "X", ""]:
        return None, None, True
    
    clean = cell_str.strip()
    # Normalize class notations if needed
    parts = clean.rsplit(" ", 1)
    if len(parts) == 2 and any(char.isdigit() for char in parts[1]):
        subject = parts[0].strip()
        class_name = parts[1].strip()
        return subject, class_name, False
    else:
        return clean, None, False
