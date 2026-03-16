"""Svenska → Python nyckelordsmappningar.

Detta är den enda källan till sanning för alla översättningar
mellan svenska programmeringsord och Python-nyckelord.
"""

# Svenska nyckelord → Python nyckelord
KEYWORDS: dict[str, str] = {
    "om": "if",
    "annars": "else",
    "eller_om": "elif",
    "medan": "while",
    "för": "for",
    "i": "in",
    "funktion": "def",
    "returnera": "return",
    "sant": "True",
    "falskt": "False",
    "och": "and",
    "eller": "or",
    "inte": "not",
    "ingen": "None",
    "klass": "class",
    "importera": "import",
    "från": "from",
    "som": "as",
    "försök": "try",
    "utom": "except",
    "slutligen": "finally",
    "med": "with",
    "avbryt": "break",
    "fortsätt": "continue",
    "godkänn": "pass",
    "ge": "yield",
    "är": "is",
    "höj": "raise",
    "global": "global",
}

# Svenska inbyggda funktioner → Python builtins
BUILTINS: dict[str, str] = {
    "skriv": "print",
    "längd": "len",
    "omfång": "range",
    "inmatning": "input",
    "heltal": "int",
    "decimaltal": "float",
    "text": "str",
    "lista": "list",
    "ordbok": "dict",
    "typ": "type",
    "sortera": "sorted",
    "summa": "sum",
    "min_värde": "min",
    "max_värde": "max",
    "absolut": "abs",
    "boolesk": "bool",
    "mängd": "set",
    "tuppel": "tuple",
    "uppräkning": "enumerate",
    "zippa": "zip",
    "karta": "map",
    "filtrera": "filter",
}

# Omvända mappningar för felmeddelande-översättning
REVERSE_KEYWORDS: dict[str, str] = {v: k for k, v in KEYWORDS.items()}
REVERSE_BUILTINS: dict[str, str] = {v: k for k, v in BUILTINS.items()}

# Alla svenska ord som ska översättas (nyckelord + builtins)
ALL_SWEDISH: dict[str, str] = {**KEYWORDS, **BUILTINS}
ALL_REVERSE: dict[str, str] = {**REVERSE_KEYWORDS, **REVERSE_BUILTINS}

# Svenska felmeddelanden
ERROR_MESSAGES: dict[str, str] = {
    "SyntaxError": "Syntaxfel",
    "NameError": "Namnfel",
    "TypeError": "Typfel",
    "ValueError": "Värdefel",
    "IndexError": "Indexfel",
    "KeyError": "Nyckelfel",
    "ZeroDivisionError": "Divisionfel (division med noll)",
    "AttributeError": "Attributfel",
    "ImportError": "Importfel",
    "FileNotFoundError": "FilInteFunnenFel",
    "RuntimeError": "Körningsfel",
    "RecursionError": "Rekursionsfel",
    "TimeoutError": "Tidsgränsfel",
    "IndentationError": "Indenteringsfel",
    "is not defined": "är inte definierad",
    "invalid syntax": "ogiltig syntax",
    "unexpected indent": "oväntat indrag",
    "expected an indented block": "förväntade ett indraget block",
}
