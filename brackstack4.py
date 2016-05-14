# coding: utf-8
__author__ = 'Alex Gerdom'
import re
from collections import namedtuple
import itertools
from gui_interface import App


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
    """
    Class to represent a type of bracket or sequence pairs and provide regex methods to check if the start of a
    string matches a token of that type.
    """

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
    """
    Parser to convert a string (currently assumed to be a single line) to a nested
    form. After adding what tokens to recognize as increasing nesting depth, and which 
    characters freeze nesting level (that is require being unescaped before the nesting
    level is allowed to change (e.g. triple quotes in python)), calling its get_multiline_nested_string
    method will return a nested representation of a user provided string.

    > string_to_parse = "A(b(c))"
    > p = Parser(string_to_parse,pairs_that_affect_depth=<SOMETHING>,pairs_that_freeze_depth=<SOMETHING>)
    > multiline_string = p.get_multiline_nested_string()
    > print(multiline_string)
         c   
       b( )  
     A(    ) 
    """

    def __init__(self,userstring,pairs_that_affect_depth=None,
        pairs_that_freeze_depth=None,ignore_pairs_needing_escape=False):
        self.userstring = userstring
        self.depths = [] # how deeply nested each character in the string is
        # (configuration) lists of BracketTokenTypes that affect parsing of the string
        self.pairs_that_affect_depth = []
        self.pairs_that_freeze_depth = []
        self.ignore_pairs_needing_escape = ignore_pairs_needing_escape
        # (for use in getting nesting depths)
        self._string = userstring # a copy of the user's string that is consumed during parsing
        self._cur_depth = 0 # Tracks the current depth of nesting
        self._bracket_stack = [] # token types of left brackets yet to be matched with right brackets
        self._needed_to_unfreeze = None # bracket type of last freezing token
        # if pairs of brackets/quotes/ect are supplied when the parser is instantiated,
        # add the pairs recognized by the parser
        if pairs_that_affect_depth is not None:
            for token_type_name, left, right in pairs_that_affect_depth:
                self.add_pair_that_affects_depth(token_type_name,left,right)
        if pairs_that_freeze_depth is not None:
            for token_type_name, left,right in pairs_that_freeze_depth:
                self.add_pair_that_freezes_depth(token_type_name,left,right)

    # ====================================================================================================
    # =======  Helper functions that construct and add token types that control parsing behavior
    # ====================================================================================================

    def add_pair_that_affects_depth(self, token_type, left, right):
        tokentype_ = BracketTokenType(token_type, left, right)
        self.pairs_that_affect_depth.append(tokentype_)

    def add_pair_that_freezes_depth(self, token_type, left, right):
        """Takes the name of a set of braces or character sequences, the left brace/seqence, and the right brace/sequence of the pair
        and constructs their BracketTokenType Class (primarily used for its regex methods)"""
        tokentype_ = BracketTokenType(token_type, left, right)
        self.pairs_that_freeze_depth.append(tokentype_)

    # ====================================================================================================
    # =======  Primary exposed function: 
    # ====================================================================================================

    def get_multiline_nested_string(self, nest_downwards=False):
        """
        Get a multiline representation of the parsed string with seperate lines representing higher or
        lower levels of nesting. 

        :param nest_downwards: If true, higher levels of nesting will print below the baseline (level 0).
        """
        self.get_nesting_depths()
        depths = self.depths
        levels = [[] for _ in range(max(depths)+1)]
        for lvl,c in zip(depths,self.userstring):
            for i in range(len(levels)):
                if lvl == i:
                    levels[i].append(c)
                else:
                    levels[i].append(' ')
        levels = [''.join(lvl) for lvl in levels]
        if nest_downwards:
            return '\n'.join([lvl for lvl in levels])
        else:
            return '\n'.join([lvl for lvl in levels[::-1]])

    # ====================================================================================================
    # =======  Helper functions that construct and add token types that control parsing behavior
    # ====================================================================================================

    def get_nesting_depths(self):
        """Returns how deeply nested each character in the string is"""
        # The body of this function should only run once.
        # If it has previously run just return the nesting depths. 
        # Otherwise parse a copy of the string
        if len(self.depths) > 0:
            return self.depths
        self._cur_depth = 0
        while self._string:
            match_found = False
            # ============== Steps that Freezing/Unfreeze nesting level ==================
            if not self.ignore_pairs_needing_escape:
                if self._needed_to_unfreeze is not None:
                    # If there is a bracket/sequence needed to unfreeze the nesting level
                    # attempt to find a matching unfreezing character sequence.
                    # If unsuccessful the while loop will terminate as the string has been consumed
                    success = self._parse_until_unfrozen()
                    continue
                else:
                    match_found = self._check_for_freezing_delim()
            # =============== Steps that increase/decrease nesting level =================
            if not match_found:
                match_found = self._check_for_left_bracket_match()
            if not match_found:
                match_found = self._check_for_right_bracket_match()
            # =============== Step for if neither of the above steps have been taken =====
            if not match_found:
                self.depths.append(self._cur_depth)
                self._advance_string_nchars(1)
        return self.depths

    # ==================================================
    # =======  Helper functions for internal processing
    # ==================================================

    def _advance_string_nchars(self,nchars):
        """Helper function to advance the parser n-steps"""
        self._string = self._string[nchars:]

    def _add_depth_n_m_times(self,n,m):
        """Helper function to add a depth n, m-times to the character depths"""
        self.depths.extend([n for _ in range(m)])

    # ==========================================
    # =======  Steps in parsing the string
    # ==========================================
    def _parse_until_unfrozen(self):
        """If a freezing token has previously occured, parse the string until either an unfreezing token is encountered 
        or the string is fully consumed.

        Returns True if an unfreezing token is encountered.
        Returns False if there isn't already a frozen token that needs escaped.
        Returns None if no unfreezing token is encountered before the string is fully consumed"""
        match_found = False
        if self._needed_to_unfreeze is not None:
            # Parse until unfrozed
            while (self._needed_to_unfreeze.right_match(self._string) is None):
                if self._string=='':
                    return None
                else:
                    self._add_depth_n_m_times(self._cur_depth,1)
                    self._advance_string_nchars(1)
            # for the length of the unfreezing token
            self._add_depth_n_m_times(self._cur_depth, self._needed_to_unfreeze.right_len)
            self._advance_string_nchars(self._needed_to_unfreeze.right_len)
            self._needed_to_unfreeze = None
            match_found = True
        return match_found
    
    def _check_for_freezing_delim(self):
        match_found = False
        # Check all of the left freezing bracket/sequences to see if they match
        for freezing_token in self.pairs_that_freeze_depth:
            if freezing_token.left_match(self._string):
                self._needed_to_unfreeze = freezing_token
                self._add_depth_n_m_times(self._cur_depth,freezing_token.left_len)
                self._advance_string_nchars(freezing_token.left_len)
                match_found = True
                break
        return match_found

    def _check_for_left_bracket_match(self):
        match_found = False
        # Check all of the left brackets to see if they match
        for token_type in self.pairs_that_affect_depth:
            if token_type.left_match(self._string):
                self._add_depth_n_m_times(self._cur_depth,token_type.left_len)
                self._cur_depth += 1
                self._advance_string_nchars(token_type.left_len)
                self._bracket_stack.append(token_type)
                match_found = True
        return match_found

    def _check_for_right_bracket_match(self):
        match_found = False
        if len(self._bracket_stack) > 0:
            if self._bracket_stack[-1].right_match(self._string):
                self._cur_depth -= 1
                self._add_depth_n_m_times(self._cur_depth,self._bracket_stack[-1].right_len)
                self._advance_string_nchars(self._bracket_stack[-1].right_len)
                self._bracket_stack.pop()
                match_found = True
        return match_found


def stackbrack(string,nest_downwards=False, pairs_that_affect_depth = BRACKET_PAIRS, pairs_that_freeze_depth = REQ_ESCAPE_TO_INC_NESTING_DEPTH):
    """
    > string_to_parse = "A(b(c))"
    > print(stackbrack(string_to_parse))
         c   
       b( )  
     A(    ) 

    :param string: String to be nested
    :param pairs_that_affect_depth:
    :param pairs_that_freeze_depth:
    :return: A multiline string with one line per level of nesting
    """
    parser = Parser(string, pairs_that_affect_depth=pairs_that_affect_depth, pairs_that_freeze_depth=pairs_that_freeze_depth)
    nested_string = parser.get_multiline_nested_string(nest_downwards=nest_downwards)
    return nested_string



def display_in_gui(string):
    tk_display_text(string)

def demo():
    print("_"*10,"Brackstack Demo", "_"*10)
    while True:
        userstring = input("Enter a string:")
        if userstring == "":
            continue
        else:
            print(stackbrack(userstring))

if __name__ == '__main__':
    demo()