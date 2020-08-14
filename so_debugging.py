import re

def test(regex, string):
    print(bool(re.fullmatch(regex, string)))

# This makes sense and works correctly
test(r'.*[a-zA-Z].*', '12b4')      # True
test(r'(?!.*[a-zA-Z].*)', '12b4')  # False

# This doesn't make sense
test(r'.*[a-zA-Z].*', '1234')      # False
test(r'(?!.*[a-zA-Z].*)', '1234')  # False!! Why?
