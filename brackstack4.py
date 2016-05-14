# coding: utf-8
__author__ = 'Alex Gerdom'
import re
from collections import namedtuple
import itertools

BRACKET_PAIRS = (
    ("paren", "(", ")"),
    ("brace", "[", "]"),
    ("curlybrace", "{", "}"),
)

REQ_ESCAPE_TO_INC_NESTING_DEPTH = (
    ("triple double quote", '"""', '"""'),
    ("triple single quote", "'''", "'''"),
    ("single quote", "'", "'"),
    ("double quote", '"', '"'),
)


class BracketTokenType(object):

    def __init__(self, bracket_type, left_bracket, right_bracket):
        self.bracket_type = bracket_type
        self.left_bracket = left_bracket
        self.right_bracket = right_bracket
        self.left_bracket_re = re.escape(left_bracket)
        self.right_bracket_re = re.escape(right_bracket)
        self.left_len = len(self.left_bracket)
        self.right_len = len(self.right_bracket)

    def __repr__(self):
        template = "Bracket(left_bracket='{}', right_bracket='{}')"
        return template.format(self.left_bracket, self.right_bracket)

    def left_match(self,s):
        """Check whether the left bracket of the pair matches the start of some string s"""
        return re.match(self.left_bracket_re,s)

    def right_match(self,s):
        """Check whether the right bracket of the pair matches the start of some string s"""
        return re.match(self.right_bracket_re,s)


class Parser(object):
    """docstring for Parser"""

    def __init__(self,userstring,pairs_that_affect_depth=None,
        pairs_that_freeze_depth=None,ignore_pairs_needing_escape=False):
        self.pairs_that_affect_depth = []
        self.pairs_that_freeze_depth = []
        self.bracket_stack = []
        self.depths = []
        self.needed_to_unfreeze_ = None # bracket type of last freezing token
        self.tokens = []
        self.userstring = userstring
        self.string_ = userstring # string_being_parsed
        self.ignore_pairs_needing_escape = ignore_pairs_needing_escape
        # if pairs of brackets/quotes/ect are supplied when the parser is instantiated,
        # add the pairs recognized by the parser
        if pairs_that_affect_depth is not None:
            for token_type_name, left, right in pairs_that_affect_depth:
                self.add_pair_that_affects_depth(token_type_name,left,right)
        if pairs_that_freeze_depth is not None:
            for token_type_name, left,right in pairs_that_freeze_depth:
                self.add_pair_that_freezes_depth(token_type_name,left,right)

    def add_pair_that_affects_depth(self, token_type, left, right):
        tokentype_ = BracketTokenType(token_type, left, right)
        self.pairs_that_affect_depth.append(tokentype_)

    def add_pair_that_freezes_depth(self, token_type, left, right):
        tokentype_ = BracketTokenType(token_type, left, right)
        self.pairs_that_freeze_depth.append(tokentype_)

    def advance_string_nchars(self,nchars):
        self.string_ = self.string_[nchars:]

    def add_depth_n_m_times(self,n,m):
        self.depths.extend([n for _ in range(m)])

    def parse_until_unfrozen(self):
        # print("parse_until_unfrozen")
        match_found = False
        if self.needed_to_unfreeze_ is not None:
            while (self.needed_to_unfreeze_.right_match(self.string_) is None):
                if self.string_=='':
                    # print("returning")
                    return
                else:
                    # print("checking {} for {}, depths={}".format(self.string_,self.needed_to_unfreeze_,self.depths))
                    # print(self.string_, self.depths)
                    self.add_depth_n_m_times(self.cur_depth,1)
                    self.advance_string_nchars(1)
            # print(self.string_, self.depths)
            # add depths that many times
            self.add_depth_n_m_times(self.cur_depth, self.needed_to_unfreeze_.right_len)
            self.advance_string_nchars(self.needed_to_unfreeze_.right_len)
            self.needed_to_unfreeze_ = None
            match_found = True
        return match_found
        # check for any freezing tokens

    
    def check_for_freezing_delim(self):
        match_found = False
        # if currently frozen
        for freezing_token in self.pairs_that_freeze_depth:
            if freezing_token.left_match(self.string_):
                # print('freezing @ {}'.format(freezing_token), self.depths)
                self.needed_to_unfreeze_ = freezing_token
                self.add_depth_n_m_times(self.cur_depth,freezing_token.left_len)
                # print("b4 advance",self.string_)
                self.advance_string_nchars(freezing_token.left_len)
                # print("after advance",self.string_)
                match_found = True
                break
        return match_found

    def check_for_left_bracket_match(self):
        match_found = False
        # Check all of the left brackets to see if they match
        for token_type in self.pairs_that_affect_depth:
            if token_type.left_match(self.string_):
                self.add_depth_n_m_times(self.cur_depth,token_type.left_len)
                self.cur_depth += 1
                self.advance_string_nchars(token_type.left_len)
                self.bracket_stack.append(token_type)
                match_found = True
        return match_found

    def check_for_right_bracket_match(self):
        match_found = False
        if len(self.bracket_stack) > 0:
            if self.bracket_stack[-1].right_match(self.string_):
                self.cur_depth -= 1
                self.add_depth_n_m_times(self.cur_depth,self.bracket_stack[-1].right_len)
                self.advance_string_nchars(self.bracket_stack[-1].right_len)
                self.bracket_stack.pop()
                match_found = True
        return match_found

    def get_nesting_depths(self):
        self.cur_depth = 0
        while self.string_:
            # print(self.string_, self.depths)
            # steps = iter(("checking_freeze","checking_left_bracket","checking_right_bracket"))
            match_found = False
            if not self.ignore_pairs_needing_escape:
                if self.needed_to_unfreeze_ is not None:
                    success = self.parse_until_unfrozen()
                    continue
                else:
                    match_found = self.check_for_freezing_delim()
            if not match_found:
                match_found = self.check_for_left_bracket_match()
            if not match_found:
                match_found = self.check_for_right_bracket_match()
            if not match_found:
                self.depths.append(self.cur_depth)
                self.advance_string_nchars(1)
        # print('returning',self.depths)
        return self.depths




