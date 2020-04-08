
import re
from src.data.MetaDataItem import MetaDataItem

single_quote_str_regex = re.compile(r'\'([^\\\']|\\.)*\'')
double_quote_str_regex = re.compile(r'"([^\\"]|\\.)*"')

def is_string_token(token):
    if token[0] == "'":
        match = single_quote_str_regex.match(token)
    elif token[0] == '"':
        match = double_quote_str_regex.match(token)
    else:
        return False
    return match is not None and match.group(0) == token

def is_number_token(token):
    try:
        float(token)
    except ValueError:
        return False
    return True
        
class FilterCondition(object):
    OPERATORS = {
        '==',
        '!=',
        '>',
        '>=',
        '<',
        '<=',
        'and',
        'or',
        '(',
        ')'
    }
    
    VALID_ATTRS = MetaDataItem.attributes()

    def __init__(self, filter_string):
        self.filter_string = filter_string
        tokens = self.tokenize(filter_string)

        self.filter_func = eval('lambda v: ' + " ".join(tokens))
        self.validate_filter()
    
    def __repr__(self) -> str:
        return f"FilterCondition({self.filter_string})"
        
    def get_validated_token(self, token):
        if token in self.VALID_ATTRS:
            return "v['" + token + "']"
        elif not token or token in self.OPERATORS or is_string_token(token) or is_number_token(token):
            return token
        raise SyntaxError("Invalid ID token: " + token)


    def tokenize(self, filter_string):
        tokens = []
        curr_token = ""
        op_token = ""
        
        in_quoted_string = False
        quote_type = None
        
        unenclosed_paren_count = 0
        
        for ch in filter_string:
            if not in_quoted_string:
                if ch in self.OPERATORS:
                    op_token = ch
                    if ch == '(': 
                        unenclosed_paren_count += 1
                    elif ch == ')':
                        unenclosed_paren_count -= 1
                        if unenclosed_paren_count < 0:
                            raise SyntaxError("')' without matching '(' in filter string: " + filter_string)
                            
                elif curr_token and (curr_token[-1] + ch) in self.OPERATORS:
                    op_token = curr_token[-1] + ch
                elif op_token:
                    tokens.append(self.get_validated_token(curr_token[:-len(op_token)]))
                    tokens.append(self.get_validated_token(op_token))
                    curr_token = ""
                    op_token = ""
                    
                    
                    
                if ch.isspace():  
                    tokens.append(self.get_validated_token(curr_token))
                    curr_token = ""
                    continue
                    
                    
            if ch == '"' or ch == "'":
                if not in_quoted_string:
                    in_quoted_string = True
                    quote_type = ch
                elif ch == quote_type:
                    in_quoted_string = False
                    quote_type = None
                   
            
            curr_token += ch
                    
        if in_quoted_string:
            raise SyntaxError("Mismatched quotes in filter string: " + filter_string)
        elif unenclosed_paren_count > 0:
            raise SyntaxError("'(' without matching ')' in filter string: " + filter_string)
            
        tokens.append(self.get_validated_token(curr_token)) 
        return tokens


    def validate_filter(self):
        # Do a test filter to catch any syntax/type errors not captured by tokenization
        data = {}
        for attr in self.VALID_ATTRS:
            data[attr] = self.VALID_ATTRS[attr]();
        self.filter_func(data)


    def filter(self, metadataitems):
        filtered_items = []
        for item in metadataitems:
            if self.filter_func(item.to_json()):
                filtered_items.append(item)
        return filtered_items
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
