import re

def test(regex, string):
    print(bool(re.fullmatch(regex, string)))

test(r'(?!.*f).*g', 'efig')
