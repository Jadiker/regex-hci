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
       | non_zero_number_class
       | letter_class
       | lowercase_class
       | uppercase_class
       | any_class
       | alphanumerical_class
       | number
       | letter

    k : INT

    number_class          : "<num>"
    non_zero_number_class : "<num1-9>"
    letter_class          : "<let>"
    lowercase_class       : "<low>"
    uppercase_class       : "<cap>"
    any_class             : "<any>"
    alphanumerical_class  : "<alphanum>"

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

def construct_regex(tree):
    operation = tree.data
    if operation == "start":
        return construct_regex(tree.children[0])
    if operation == "concat":
        child1, child2 = tree.children
        return construct_regex(child1) + construct_regex(child2)
    if operation == "repeat_at_least":
        r_tree, k_tree = tree.children
        repeatable_regex = construct_regex(r_tree)
        # k's child will be a token that we can convert to a string.
        amount = int(str(k_tree.children[0]))
        # repeat the regex the given amount of times and then make any more repetitions optional
        return (repeatable_regex * amount) + f"(?:{repeatable_regex})*"

    if operation == "letter_class":
        return "[a-zA-Z]"

    if operation == "letter":
        # turn the letter Token into a string
        return str(tree.children[0])

    print(f"Didn't know what to do for:\n{tree}\n(Putting in a '<something>')")
    return "<something>"

regex = construct_regex(parse_tree)
print(regex)

# print(parse_tree.data)
# print(type(parse_tree.data))
# print(parse_tree.children)
# print(dir(parse_tree))

# print(type(parse_tree))
#
# print(list(parse_tree.iter_subtrees_topdown()))
#
# print("LOOP")
# for thing in parse_tree.iter_subtrees_topdown():
#     # print(thing)
#     print(thing.data)
#     # print("children:")
#     # print(thing.children)
#     # print("children done")
#     # if thing.data == "k":
#     #     print(thing)
#     #     print(thing.children[0])
#     #     print(type(thing.children[0]))
#     # # print(type(thing))
