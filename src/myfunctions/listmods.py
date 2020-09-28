def check_any_match_in_list(self, value, input_list):
    return any(value in word for word in input_list)

def replace_list_value(self, input_list, old_value, new_value):
    new_list = [new_value if x == old_value else x for x in input_list]
    return new_list

def remove_from_list_by_value(self, input_list, value):
    new_list = [x for x in input_list if x != value]
    return new_list

def to_list(_x):
    if not _x:
        return []
    if isinstance(_x, str):
        return [_x]
    if isinstance(_x, tuple):
        return list(_x)
    if isinstance(_x, list):
        return _x
    
def flatten(listobj):
    return [item for sublist in listobj for item in sublist]