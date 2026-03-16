# CodeLingo - Programmera på svenska!

CodeLingo är en pedagogisk programmeringsapp designad för barn (8-16 år) som vill lära sig koda på sitt modersmål. Appen låter barn skriva kod med svenska kommandon som automatiskt översätts till Python.

## Funktioner

- **Svensk syntax**: Skriv kod med svenska nyckelord (`skriv`, `om`, `medan`, `funktion`, etc.)
- **Realtidsöversättning**: Se hur din svenska kod översätts till Python
- **Säker kodkörning**: Sandboxad exekvering med RestrictedPython
- **Interaktiva tutorials**: Steg-för-steg-lektioner på svenska
- **Visuell debugger**: Stega igenom koden och se variabler
- **Syntaxhighlighting**: Färgkodad svensk syntax med GtkSourceView
- **Barnvänlig design**: Stora knappar, tydlig text, pedagogiskt gränssnitt

## Svenska nyckelord

| Svenska | Python | Beskrivning |
|---------|--------|-------------|
| `skriv()` | `print()` | Skriv ut text |
| `om` | `if` | Villkor |
| `annars` | `else` | Alternativ |
| `eller_om` | `elif` | Annat villkor |
| `medan` | `while` | Medan-loop |
| `för` | `for` | För-loop |
| `funktion` | `def` | Definiera funktion |
| `returnera` | `return` | Returnera värde |
| `sant` / `falskt` | `True` / `False` | Booleska värden |
| `och` / `eller` | `and` / `or` | Logiska operatorer |
| `längd()` | `len()` | Längd |
| `omfång()` | `range()` | Talföljd |
| `heltal()` | `int()` | Konvertera till heltal |
| `text()` | `str()` | Konvertera till text |

## Exempelkod

```python
# Hej världen!
skriv("Hej, världen!")

# Variabler och villkor
ålder = 12
om ålder >= 10:
    skriv("Du är stor!")
annars:
    skriv("Du är liten!")

# Loopar
för i i omfång(5):
    skriv("Nummer:", i)

# Funktioner
funktion hälsa(namn):
    skriv("Hej,", namn, "!")

hälsa("Alice")
```

## Installation

### Systemkrav

- Python 3.10+
- GTK4
- GtkSourceView 5
- libadwaita

### macOS (Homebrew)

```bash
brew install gtk4 gtksourceview5 libadwaita pygobject3 gobject-introspection
pip install -r requirements.txt
```

### Ubuntu/Debian

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 \
    gir1.2-gtksource-5 gir1.2-adw-1 python3-pip
pip install -r requirements.txt
```

### Fedora

```bash
sudo dnf install python3-gobject gtk4 gtksourceview5 libadwaita \
    python3-pip
pip install -r requirements.txt
```

### Arch Linux

```bash
sudo pacman -S python-gobject gtk4 gtksourceview5 libadwaita python-pip
pip install -r requirements.txt
```

### Installera CodeLingo

```bash
# Klona repot
git clone https://github.com/yourusername/CodeLingo.git
cd CodeLingo

# Installera Python-dependencies
pip install -r requirements.txt

# Installera som paket (valfritt)
pip install -e .

# Kör appen
python -m codelingo.app
# eller efter installation:
codelingo
```

## Utveckling

```bash
# Installera utvecklingsberoenden
pip install -e ".[dev]"

# Kör tester
pytest tests/

# Kör appen direkt
python -m codelingo.app
```

## Projektstruktur

```
CodeLingo/
├── codelingo/              # Huvudpaket
│   ├── __init__.py         # Version och app-ID
│   ├── app.py              # Gtk.Application startpunkt
│   ├── window.py           # Huvudfönster med layout
│   ├── editor.py           # Kodeditor med syntaxhighlighting
│   ├── translator.py       # Svensk→Python översättning
│   ├── runner.py           # Sandboxad kodkörning
│   ├── debugger.py         # Visuell debugger
│   ├── tutorials.py        # Tutorial-system
│   ├── swedish_keywords.py # Nyckelordsmappningar
│   └── output_panel.py     # Output-visning
├── data/
│   ├── codelingo.desktop   # Desktop-fil
│   ├── language-specs/     # GtkSourceView språkdefinition
│   ├── styles/             # CSS-stilar
│   └── icons/              # App-ikon
├── po/                     # Översättningar (gettext)
│   ├── codelingo.pot       # Översättningsmall
│   ├── sv.po               # Svenska översättningar
│   └── LINGUAS             # Stödda språk
├── tests/                  # Testsvit
├── setup.py                # Installationsskript
├── requirements.txt        # Python-beroenden
└── README.md               # Denna fil
```

## Licens

MIT License - se [LICENSE](LICENSE) för detaljer.
