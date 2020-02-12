
import argparse


class FilterCondition(object):
    OPERATORS = {
        '==',
        '!=',
        '>',
        '>=',
        '<',
        '<=',
        'and',
        'or'
    }

    def __init__(self, tokens):
        self.tokens = tokens

def positive_int_type(val):
    intval = int(val)
    if intval <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive integer" % value)
    return intval

def main():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('--workers', type=positive_int_type, default=1)
    parser.add_argument('--mode', choices={'crawler', 'ucrawler', 'user'}, default='user')
    parser.add_argument('--source', required=True, help='HTTP link to firebase')
    parser.add_argument('--filter', nargs='+', help='A series of tokens representing a condition in python syntax')
    args = parser.parse_args()

    

if __name__ == "__main__":
    main()
