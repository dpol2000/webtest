def normalize(string):
    """ Deletes spaces and uppercases the string """
    if string[-1] == '.':
        string2 = string[:-1]
    else:
        string2 = string
    return string2.replace(" ", "").upper()