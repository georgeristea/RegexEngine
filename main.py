#!/usr/bin/env python
# import sys
# import pickle

from regex import RegEx
from myParser import MyParser
from test import *


if __name__ == "__main__":
    valid = (len(sys.argv) == 4 and sys.argv[1] in ["RAW", "TDA"]) or \
            (len(sys.argv) == 3 and sys.argv[1] == "PARSE")
    if not valid:
        sys.stderr.write(
            "Usage:\n"
            "\tpython3 main.py RAW <regex-str> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py TDA <tda-file> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py PARSE <regex-str>\n"
        )
        sys.exit(1)

    if sys.argv[1] == "TDA":
        tda_file = sys.argv[2]
        with open(tda_file, "rb") as fin:
            parsed_regex = pickle.loads(fin.read())
    else:
        regex_string = sys.argv[2]

        myObj = MyParser();
        test = Test();
        parsed_regex = myObj.parse(regex_string);


        if sys.argv[1] == "PARSE":
            print(str(parsed_regex))
            sys.exit(0)

        regular_expr = myObj.convert_to_re(parsed_regex);
        nfa = test.re_to_nfa(regular_expr);
        #nfa.to_graphviz().render(quiet_view=True, cleanup=True);
        dfa = test.convert_nfa_to_dfa(nfa);
        #dfa.to_graphviz().render(quiet_view = True, cleanup = True);


    with open(sys.argv[3], "r") as fin:
        content = fin.readlines()

    for word in content:
        print(test.start_DFA(dfa, word));
        pass


