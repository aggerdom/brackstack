from brackstack4 import *
from gui_interface import tk_display_text

def test_nesting_depths(userstring):
    parser = Parser(userstring)
    for token_type_name, left,right in BRACKET_PAIRS:
        parser.add_pair_that_affects_depth(token_type_name,left,right)
    for token_type_name, left,right in REQ_ESCAPE_TO_INC_NESTING_DEPTH:
        parser.add_pair_that_freezes_depth(token_type_name,left,right)
    return parser.get_nesting_depths()

def test_constructor_recognizes_default_pairs(userstring,nesting_depths):
    pairs_that_affect_depth = BRACKET_PAIRS
    pairs_that_freeze_depth = REQ_ESCAPE_TO_INC_NESTING_DEPTH
    parser = Parser(userstring,
                    pairs_that_affect_depth=pairs_that_affect_depth,
                    pairs_that_freeze_depth=pairs_that_freeze_depth)
    assert parser.get_nesting_depths()==nesting_depths, "Parsing {} == {} with default bracket pairs failed".format(userstring,nesting_depths)

def test_constructor_recognizes_default_pairs_tests():
    assert test_nesting_depths("hello") == [0,0,0,0,0]
    assert test_nesting_depths('((') == [0,1]
    assert test_nesting_depths('()') == [0,0]
    assert test_nesting_depths(")") == [0]
    assert test_nesting_depths("))") == [0,0]
    assert test_nesting_depths(')(a') == [0,0,1], "starting with right"
    assert test_nesting_depths('())') == [0,0,0], "probably not popping correctly"
    assert test_nesting_depths('(a)') == [0,1,0], "Single nested char"
    assert test_nesting_depths(')b)') == [0,0,0]
    assert test_nesting_depths("('hello") == [0,1,1,1,1,1,1]
    assert test_nesting_depths("('hello)") == [0,1,1,1,1,1,1,1]
    assert test_nesting_depths("('hello)'") == [0,1,1,1,1,1,1,1,1]
    assert test_nesting_depths("('hello)')") == [0,1,1,1,1,1,1,1,1,0]
    assert test_nesting_depths("(((foo)]))") == [0,1,2,3,3,3,2,2,1,0]
    assert test_nesting_depths("'''foo'") == [0,0,0,0,0,0,0]

def test_gui():
    tk_display_text()

def test():
    # simple
    assert test_nesting_depths("hello") == [0,0,0,0,0]
    assert test_nesting_depths('((') == [0,1]
    assert test_nesting_depths('()') == [0,0]
    assert test_nesting_depths(")") == [0]
    assert test_nesting_depths("))") == [0,0]
    assert test_nesting_depths(')(a') == [0,0,1], "starting with right"
    assert test_nesting_depths('())') == [0,0,0], "probably not popping correctly"
    assert test_nesting_depths('(a)') == [0,1,0], "Single nested char"
    assert test_nesting_depths(')b)') == [0,0,0]
    test_constructor_recognizes_default_pairs("('hello"   ,[0,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)"  ,[0,1,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)'" ,[0,1,1,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)')",[0,1,1,1,1,1,1,1,1,0])
    test_constructor_recognizes_default_pairs("(((foo)]))",[0,1,2,3,3,3,2,2,1,0])
    test_constructor_recognizes_default_pairs("'''foo'"   ,[0,0,0,0,0,0,0])
    test_constructor_recognizes_default_pairs("hello"     ,[0,0,0,0,0])
    test_constructor_recognizes_default_pairs('(('        ,[0,1])
    test_constructor_recognizes_default_pairs('()'        ,[0,0])
    test_constructor_recognizes_default_pairs(")"         ,[0])
    test_constructor_recognizes_default_pairs("))"        ,[0,0])
    test_constructor_recognizes_default_pairs(')(a'       ,[0,0,1],)
    test_constructor_recognizes_default_pairs('())'       ,[0,0,0],)
    test_constructor_recognizes_default_pairs('(a)'       ,[0,1,0],)
    test_constructor_recognizes_default_pairs(')b)'       ,[0,0,0])
    test_constructor_recognizes_default_pairs("('hello"   ,[0,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)"  ,[0,1,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)'" ,[0,1,1,1,1,1,1,1,1])
    test_constructor_recognizes_default_pairs("('hello)')",[0,1,1,1,1,1,1,1,1,0])
    test_constructor_recognizes_default_pairs("(((foo)]))",[0,1,2,3,3,3,2,2,1,0])
    test_constructor_recognizes_default_pairs("'''foo'"   ,[0,0,0,0,0,0,0])