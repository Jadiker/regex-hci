from lark import Lark

# TODO add in "<sep>"
parser = Lark('''
    start : r

    ?r : c?
       | starts_with
       | ends_with
       | contain
       | concat
       | or
       | and
       | repeat
       | repeat_at_least
       | repeat_range

    ?c : number_class
       | non_zero_number_class
       | letter_class
       | lowercase_class
       | uppercase_class
       | any_class
       | alphanumerical_class
       | number
       | letter

    k : INT
    number: "<" INT ">"
    letter: "<" LETTER ">"
    number_class          : "<num>"
    non_zero_number_class : "<num1-9>"
    letter_class          : "<let>"
    lowercase_class       : "<low>"
    uppercase_class       : "<cap>"
    any_class             : "<any>"
    alphanumerical_class  : "<alphanum>"

    starts_with     : "startswith(" r ")"
    ends_with       : "endswith(" r ")"
    contain         : "contain(" r ")"
    concat          : "concat(" r "," r ")"
    or              : "or(" r "," r ")"
    and             : "and(" r "," r ")"
    repeat          : "repeat(" r "," k ")"
    repeat_at_least : "repeatatleast(" r "," k ")"
    repeat_range    : "repeatrange(" r "," k "," k ")"

    %import common.INT
    %import common.LETTER
''')

INPUT_STRING = "or(contain(<2>),<let>)"
# INPUT_STRING = "concat(repeatatleast(<let>,1),<C>)"

parse_tree = parser.parse(INPUT_STRING)
# print(parse_tree.pretty())

# if bounded is True, will ensure that the entire regex is encompassed in such a way that adding an operation will apply the operation to the entire regex.
# for example, `abc` is not bounded because the `*` in `abc*` would only operate on the `c`.
# however, `(?:abc)` is bounded because `(?:abc)*` would operate on all of `abc`
def construct_regex(tree, bounded=False):
    def bound(regex):
        '''Puts bounds on the regex if bounded is true'''
        return f"(?:{regex})" if bounded else regex

    operation = tree.data

    if operation == "k":
        raise ValueError("k should never be an operation - something is wrong with the code - an earlier function should have just grabbed the value, not called `construct_regex` on a 'k' operation.")

    if operation == "number":
        # turn the number Token into a string
        return str(tree.children[0])

    if operation == "letter":
        # turn the letter Token into a string
        return str(tree.children[0])

    if operation == "number_class":
        return "[0-9]"

    if operation == "non_zero_number_class":
        return "[1-9]"

    if operation == "letter_class":
        return "[a-zA-Z]"

    if operation == "lowercase_class":
        return "[a-z]"

    if operation == "uppercase_class":
        return "[A-Z]"

    if operation == "any_class":
        return "."

    if operation == "alphanumerical_class":
        return "[0-9a-zA-Z]"

    if operation == "start":
        return construct_regex(tree.children[0], bounded=bounded)

    if operation == "starts_with":
        regex = construct_regex(tree.children[0], bounded=False)
        regex = regex + ".*"
        return bound(regex)

    if operation == "ends_with":
        regex = construct_regex(tree.children[0], bounded=False)
        regex = ".*" + regex
        return bound(regex)

    if operation == "contain":
        regex = construct_regex(tree.children[0], bounded=False)
        regex = ".*" + regex + ".*"
        return bound(regex)

    if operation == "concat":
        child1, child2 = tree.children
        regex = construct_regex(child1, bounded=False) + construct_regex(child2, bounded=False)
        return bound(regex)

    if operation == "or":
        child1, child2 = tree.children
        regex = construct_regex(child1, bounded=True) + "|" + construct_regex(child2, bounded=True)
        return bound(regex)

    if operation == "and":
        child1, child2 = tree.children
        regex = f"(?={construct_regex(child1, bounded=False)})(?={construct_regex(child2, bounded=False)})"
        return bound(regex)

    if operation == "repeat":
        r_tree, k_tree = tree.children
        repeatable_regex = construct_regex(r_tree, bounded=False)
        # k's child will be a token that we can convert to a string.
        amount = int(str(k_tree.children[0]))
        # repeat the regex the given amount of times and then make any more repetitions optional
        regex = repeatable_regex * amount
        return bound(regex)

    if operation == "repeat_at_least":
        r_tree, k_tree = tree.children
        repeatable_regex = construct_regex(r_tree, bounded=False)
        operationable_regex = construct_regex(r_tree, bounded=True)
        # k's child will be a token that we can convert to a string.
        amount = int(str(k_tree.children[0]))
        if amount == 0:
            regex = operationable_regex + "*"
        elif amount == 1:
            regex = operationable_regex + "+"
        else:
            # repeat the regex the given amount of times and then make any more repetitions optional
            regex = (repeatable_regex * amount) + f"{operationable_regex}*"
        return bound(regex)


    if operation == "repeat_range":
        r_tree, k1_tree, k2_tree = tree.children
        repeatable_regex = construct_regex(r_tree, bounded=False)
        # k's child will be a token that we can convert to a string.
        start = int(str(k1_tree.children[0]))
        end = int(str(k2_tree.children[0]))
        assert start < end, f"{start} >= {end} in repeat_range(<some regex>, {start}, {end})"
        regex = ""
        optional = False
        for amount in range(start, end + 1):
            if amount == 0:
                optional = True
            else:
                regex += "(?:" + (repeatable_regex * amount) + ")|"

        # take off the trailing "|"
        regex = regex[:-1]
        if optional:
            regex = f"(?:{regex})?"

        return bound(regex)



        # repeat the regex the given amount of times and then make any more repetitions optional
        regex = (repeatable_regex * amount) + f"{operationable_regex}*"
        return bound(regex)

    print(f"Didn't know what to do for:\n{operation}\n(Putting in a '<something>')")
    return "<something>"

print(construct_regex(parse_tree))
