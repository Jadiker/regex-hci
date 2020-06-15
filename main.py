from lark import Lark

parser = Lark('''
    start : r

    ?r : c?
       | starts_with
       | ends_with
       | contains
       | concat
       | or
       | and
       | repeat
       | repeat_at_least
       | repeat_range

    ?c : number_class
       | letter_class
       | lowercase_class
       | uppercase_class
       | any_class
       | alphanumerical_class
       | number
       | letter

    k : INT

    number_class         : "<num>"
    letter_class         : "<let>"
    lowercase_class      : "<low>"
    uppercase_class      : "<cap>"
    any_class            : "<any>"
    alphanumerical_class : "<alphanum>"

    number: "<" INT ">"
    letter: "<" LETTER ">"

    starts_with     : "startswith(" r ")"
    ends_with       : "endswith(" r ")"
    contains        : "contains(" r ")"
    concat          : "concat(" r "," r ")"
    or              : "or(" r "," r ")"
    and             : "and(" r "," r ")"
    repeat          : "repeat(" r "," k ")"
    repeat_at_least : "repeatatleast(" r "," k ")"
    repeat_range    : "repeatrange(" r "," k "," k ")"

    %import common.INT
    %import common.LETTER
''')

parse_tree = parser.parse("concat(repeatatleast(<let>,1),<C>)")
print(parse_tree.pretty())
