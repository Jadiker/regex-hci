from lark import Lark

# TODO add in "<sep>"
parser = Lark('''
    start : r

    ?r : c?
       | start_with
       | end_with
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

    start_with      : "startwith(" r ")"
    end_with        : "endwith(" r ")"
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


def tree_to_regex(tree, bounded=False):
    '''
    Takes a Lark parsing tree of the DSL and returns an equivalent regex string.

    If bounded is True, will ensure that the entire regex is encompassed in such a way
    ...that adding an operation will apply the operation to the entire regex.
    For example, `abc` is not bounded because the `*` in `abc*` would only operate on the `c`.
    However, `(?:abc)` is bounded because the `*` in `(?:abc)*` would operate on all of `abc`.
    '''

    def bound(regex):
        '''Puts bounds on the regex if bounded is true'''
        return f"(?:{regex})" if bounded else regex

    operation = tree.data

    if operation == "k":
        raise ValueError("k should never be an operation - something is wrong with the code - an earlier function should have just grabbed the value, not called `tree_to_regex` on a 'k' operation.")

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
        return tree_to_regex(tree.children[0], bounded=bounded)

    if operation == "start_with":
        regex = tree_to_regex(tree.children[0], bounded=False)
        regex = regex + ".*"
        return bound(regex)

    if operation == "end_with":
        regex = tree_to_regex(tree.children[0], bounded=False)
        regex = ".*" + regex
        return bound(regex)

    if operation == "contain":
        regex = tree_to_regex(tree.children[0], bounded=False)
        regex = ".*" + regex + ".*"
        return bound(regex)

    if operation == "concat":
        child1, child2 = tree.children
        regex = tree_to_regex(child1, bounded=False) + tree_to_regex(child2, bounded=False)
        return bound(regex)

    if operation == "or":
        child1, child2 = tree.children
        regex = tree_to_regex(child1, bounded=True) + "|" + tree_to_regex(child2, bounded=True)
        return bound(regex)

    if operation == "and":
        child1, child2 = tree.children
        regex = f"(?={tree_to_regex(child1, bounded=False)})(?={tree_to_regex(child2, bounded=False)})"
        return bound(regex)

    if operation == "repeat":
        r_tree, k_tree = tree.children
        repeatable_regex = tree_to_regex(r_tree, bounded=False)
        # k's child will be a token that we can convert to a string.
        amount = int(str(k_tree.children[0]))
        # repeat the regex the given amount of times and then make any more repetitions optional
        regex = repeatable_regex * amount
        return bound(regex)

    if operation == "repeat_at_least":
        r_tree, k_tree = tree.children
        repeatable_regex = tree_to_regex(r_tree, bounded=False)
        operationable_regex = tree_to_regex(r_tree, bounded=True)
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
        repeatable_regex = tree_to_regex(r_tree, bounded=False)
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

    raise ValueError(f"Didn't know what to do for operation '{operation}'")

def construct_regex(dsl: str) -> str:
    '''Takes a string in the DSL and converts it to regex'''
    tree = parser.parse(dsl)
    return tree_to_regex(tree)


if __name__ == "__main__":
    INPUT_STRING = "or(contain(<2>),<let>)"
    # INPUT_STRING = "concat(repeatatleast(<let>,1),<C>)"
    # INPUT_STRING = "endwith(endwith(<num1-9>))"

    print(construct_regex(INPUT_STRING))
