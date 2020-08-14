import re

def test(regex, string):
    print(bool(re.fullmatch(regex, string)))

# test('(?!.*[a-zA-Z].*)', '{234')

test(r'.*[a-zA-Z].*', '1234')
test(r'(?!.*[a-zA-Z].*)', '1234')
test(r'.*[a-zA-Z].*', '12b4')
test(r'(?!.*[a-zA-Z].*)', '12b4')

# test('.*[a-zA-Z].*', '{234')
# test('.*[a-zA-Z].*', '34b4')
