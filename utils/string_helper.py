from fnmatch import fnmatch


def wildcard(txt, pattern, case_insensitive=True):
    if txt == pattern:
        return True
    else:
        return fnmatch(txt.lower(), pattern.lower()) if case_insensitive else fnmatch(txt, pattern)


def wildcard_match_count(list_txt, pattern, case_insensitive=True):
    count = 0
    for txt in list_txt:
        if wildcard(txt, pattern, case_insensitive):
            count += 1
    return count


def wildcard_has_match(list_txt, pattern, case_insensitive=True):
    for txt in list_txt:
        if wildcard(txt, pattern, case_insensitive):
            return True
    return False


def equals_case_insensitive(string1, string2):
    return string1.lower() == string2.lower()


def join(list_of_string, separator):
    return separator.join(list_of_string)
