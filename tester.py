import sys
import re
from typing import Dict, Callable

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

SUCCESSES = "successes"
FAILURES = "failures"

# a Python regex
Regex = str
# a regex in the DSL
Dsl = str
# path to a file containing all the cases to test on
CasesFileName = str
# the structure of examples, which is created by how the cases are parsed
Examples = Dict[str, Dict[str, bool]]

class TestCase:
    def __init__(self, test_case_list):
        self.name = test_case_list[0]
        self.dsl: Dsl = test_case_list[1][0]
        self.examples: Examples = test_case_list[2]

    def __str__(self):
        return f"<TestCase named '{self.name}' and with DSL '{self.dsl}' with {len(self.examples)} example sets>"

def test_regex(r: Regex, examples: Examples):
    success_cases = []
    failure_cases = []
    example_set: Dict[str: bool]
    for example_set in examples.values():
        example: str
        should_match: bool
        for example, should_match in example_set.items():
            matched = bool(re.fullmatch(r, example))
            # print(f"Regex '{r}' matching '{example}' was {matched} and it should be {should_match}")
            if matched == should_match:
                success_cases.append(example)
            else:
                failure_cases.append(example)
    return success_cases, failure_cases


def parse_cases_file(cases_file_name: CasesFileName):
    with open(cases_file_name) as cases_file:
        ans = []
        test_case = []
        for line in cases_file:
            line = line.strip()
            if line:
                if line.startswith("***") and line.endswith("***"):
                    if test_case:
                        ans.append(TestCase(test_case))
                    test_case = []
                    test_case.append(line[3:-3])
                else:
                    line = line.replace("true", "True")
                    line = line.replace("false", "False")
                    examples = eval(line)
                    # print(examples)
                    test_case.append(examples)
        if test_case:
            ans.append(TestCase(test_case))
    return ans

def test_regex_synthesizer(synthesizer: Callable[[Dsl], Regex], cases_file_name: CasesFileName, verbose=True):
    ans = {}
    test_cases = parse_cases_file(cases_file_name)
    for test_case in test_cases:
        dsl: Dsl = test_case.dsl
        r: Regex = synthesizer(dsl)
        examples: Examples = test_case.examples
        successes, failures = test_regex(r, examples)
        assert dsl not in ans, f"The DSL '{dsl}' was tested on twice in the same file, which is currently not supported"
        ans[dsl] = {SUCCESSES: successes, FAILURES: failures}
        assert failures or successes
        if failures and verbose:
            for failure in failures:
                print(f"The regex '{r}' failed to behave like the DSL '{dsl}' on the string '{failure}'")
    print("Testing complete!")
    return ans

if __name__ == "__main__":
    from regex_synthesizer import construct_regex
    CASES_FILE = "edited_test_cases.txt"
    test_results = test_regex_synthesizer(construct_regex, CASES_FILE)
    success_total = 0
    failure_total = 0
    for dsl, results in test_results.items():
        success_total += len(results[SUCCESSES])
        failure_total += len(results[FAILURES])

    print(f"{success_total} cases passed, {failure_total} cases failed.")
