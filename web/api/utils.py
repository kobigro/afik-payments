
CLASS_NAME_TO_ID = {
    'א': 1,
    'ב': 2,
    'ג': 3,
    'ד': 4,
    'ה': 5,
    'ו': 6,
    'ז': 7,
    'ח': 8,
    'ט': 9,
    'י': 10,
    'יא': 11,
    'יב': 12
}
def get_class_id(class_name):
    return CLASS_NAME_TO_ID.get(class_name)