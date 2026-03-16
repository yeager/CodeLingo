"""Tutorial-system med svenska programmeringslektioner.

Hanterar laddning, visning och validering av steg-för-steg-lektioner
för barn som lär sig programmera.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TutorialStep:
    """Ett steg i en lektion."""
    instruction: str
    code_hint: str = ""
    expected_output: str = ""
    explanation: str = ""


@dataclass
class Challenge:
    """En utmaning i slutet av en lektion."""
    prompt: str
    validator: str = "output_not_empty"
    hint: str = ""


@dataclass
class Tutorial:
    """En komplett lektion."""
    id: str
    title: str
    description: str
    age_group: str = "8-16"
    steps: list[TutorialStep] = field(default_factory=list)
    challenges: list[Challenge] = field(default_factory=list)
    category: str = "grundläggande"


# Inbyggda tutorials (används om JSON-filer inte hittas)
BUILTIN_TUTORIALS = [
    Tutorial(
        id="01_hej_varlden",
        title="Hej, världen!",
        description="Skriv ditt allra första program",
        age_group="8-10",
        category="grundläggande",
        steps=[
            TutorialStep(
                instruction="Välkommen till CodeLingo! Låt oss skriva ditt "
                           "första program.\n\nSkriv detta i editorn:",
                code_hint='skriv("Hej, världen!")',
                expected_output="Hej, världen!\n",
                explanation="<b>skriv()</b> skriver text på skärmen.\n"
                          "Texten måste vara inom citattecken.",
            ),
            TutorialStep(
                instruction="Bra jobbat! Nu ska vi skriva ut flera saker.\n\n"
                          "Prova att skriva:",
                code_hint='skriv("Jag heter CodeLingo")\n'
                         'skriv("Jag kan programmera!")',
                expected_output="Jag heter CodeLingo\nJag kan programmera!\n",
                explanation="Du kan ha flera <b>skriv()</b>-kommandon.\n"
                          "Varje <b>skriv()</b> skriver på en ny rad.",
            ),
        ],
        challenges=[
            Challenge(
                prompt="Kan du skriva ut ditt eget namn?",
                validator="output_not_empty",
                hint='Använd skriv("ditt namn här")',
            ),
        ],
    ),
    Tutorial(
        id="02_variabler",
        title="Variabler - spara saker",
        description="Lär dig använda variabler för att spara värden",
        age_group="8-12",
        category="grundläggande",
        steps=[
            TutorialStep(
                instruction="En variabel är som en låda där du kan spara saker.\n\n"
                          "Prova detta:",
                code_hint='namn = "Ada"\nskriv(namn)',
                expected_output="Ada\n",
                explanation="<b>namn</b> är en variabel. Vi sparade texten "
                          '"Ada" i den.\nSedan skrev vi ut den med '
                          "<b>skriv()</b>.",
            ),
            TutorialStep(
                instruction="Variabler kan också spara tal!\n\nProva:",
                code_hint='ålder = 10\nskriv("Jag är", ålder, "år gammal")',
                expected_output="Jag är 10 år gammal\n",
                explanation="Variabler kan spara <b>tal</b> (utan citattecken)\n"
                          "och <b>text</b> (med citattecken).",
            ),
            TutorialStep(
                instruction="Du kan räkna med variabler!\n\nProva:",
                code_hint="a = 5\nb = 3\nskriv(a + b)\nskriv(a * b)",
                expected_output="8\n15\n",
                explanation="<b>+</b> adderar tal\n"
                          "<b>*</b> multiplicerar tal\n"
                          "<b>-</b> subtraherar och <b>/</b> dividerar.",
            ),
        ],
        challenges=[
            Challenge(
                prompt="Skapa två variabler med ditt förnamn och efternamn,\n"
                      "och skriv ut dem tillsammans!",
                validator="output_not_empty",
                hint='förnamn = "Ditt"\nefternamn = "Namn"\n'
                    'skriv(förnamn, efternamn)',
            ),
        ],
    ),
    Tutorial(
        id="03_villkor",
        title="Villkor - om och annars",
        description="Lär dig fatta beslut i kod med om/annars",
        age_group="10-14",
        category="grundläggande",
        steps=[
            TutorialStep(
                instruction="Med <b>om</b> kan datorn fatta beslut!\n\n"
                          "Prova detta:",
                code_hint='ålder = 12\nom ålder >= 10:\n    skriv("Du är stor!")',
                expected_output="Du är stor!\n",
                explanation="<b>om</b> kontrollerar ett villkor.\n"
                          "Om villkoret är sant körs koden innanför.\n"
                          "Glöm inte <b>:</b> och <b>mellanslag</b> (indrag)!",
            ),
            TutorialStep(
                instruction="Vi kan lägga till <b>annars</b> för vad som "
                          "händer om villkoret är falskt:\n\nProva:",
                code_hint='poäng = 7\nom poäng >= 5:\n    skriv("Godkänt!")\n'
                         'annars:\n    skriv("Försök igen!")',
                expected_output="Godkänt!\n",
                explanation="<b>annars</b> körs om villkoret INTE är sant.\n"
                          "Prova att ändra poäng till 3 och kör igen!",
            ),
        ],
        challenges=[
            Challenge(
                prompt="Skriv ett program som kontrollerar om ett tal\n"
                      "är positivt, negativt eller noll!",
                validator="output_not_empty",
                hint="Använd om/eller_om/annars med tal > 0, tal < 0",
            ),
        ],
    ),
    Tutorial(
        id="04_loopar",
        title="Loopar - upprepa saker",
        description="Lär dig upprepa kod med för och medan",
        age_group="10-14",
        category="grundläggande",
        steps=[
            TutorialStep(
                instruction="En <b>för</b>-loop upprepar kod ett visst antal "
                          "gånger.\n\nProva:",
                code_hint='för i i omfång(5):\n    skriv("Hej!", i)',
                expected_output="Hej! 0\nHej! 1\nHej! 2\nHej! 3\nHej! 4\n",
                explanation="<b>för</b>-loopen kör koden 5 gånger.\n"
                          "<b>i</b> är en räknare som börjar på 0.\n"
                          "<b>omfång(5)</b> ger talen 0, 1, 2, 3, 4.",
            ),
            TutorialStep(
                instruction="En <b>medan</b>-loop fortsätter så länge "
                          "villkoret är sant:\n\nProva:",
                code_hint='tal = 1\nmedan tal <= 5:\n    skriv(tal)\n    '
                         "tal = tal + 1",
                expected_output="1\n2\n3\n4\n5\n",
                explanation="<b>medan</b>-loopen kollar villkoret varje varv.\n"
                          "Glöm inte att ändra variabeln inuti loopen,\n"
                          "annars får du en oändlig loop!",
            ),
        ],
        challenges=[
            Challenge(
                prompt="Skriv en loop som skriver ut alla jämna tal\n"
                      "från 2 till 20!",
                validator="output_not_empty",
                hint="Använd för i i omfång(2, 21, 2):",
            ),
        ],
    ),
    Tutorial(
        id="05_funktioner",
        title="Funktioner - egna kommandon",
        description="Skapa dina egna kommandon med funktioner",
        age_group="12-16",
        category="avancerat",
        steps=[
            TutorialStep(
                instruction="En <b>funktion</b> är ett eget kommando du skapar.\n\n"
                          "Prova:",
                code_hint='funktion hälsa(namn):\n    skriv("Hej,", namn, "!")\n\n'
                         'hälsa("Alice")\nhälsa("Bob")',
                expected_output="Hej, Alice !\nHej, Bob !\n",
                explanation="<b>funktion</b> skapar ett nytt kommando.\n"
                          "<b>namn</b> är en parameter - information "
                          "funktionen behöver.\n"
                          "Du anropar funktionen med dess namn och ().",
            ),
            TutorialStep(
                instruction="Funktioner kan <b>returnera</b> värden:\n\nProva:",
                code_hint="funktion dubbla(tal):\n    returnera tal * 2\n\n"
                         "resultat = dubbla(7)\nskriv(resultat)",
                expected_output="14\n",
                explanation="<b>returnera</b> skickar tillbaka ett värde.\n"
                          "Du kan spara det i en variabel.",
            ),
        ],
        challenges=[
            Challenge(
                prompt="Skapa en funktion som beräknar arean av en rektangel\n"
                      "(bredd * höjd) och testa den!",
                validator="output_not_empty",
                hint="funktion area(bredd, höjd):\n"
                    "    returnera bredd * höjd",
            ),
        ],
    ),
]


class TutorialManager:
    """Hanterar laddning och navigering av tutorials."""

    def __init__(self, data_dir: str | None = None):
        self._tutorials: list[Tutorial] = []
        self._data_dir = data_dir
        self._load_tutorials()

    def _load_tutorials(self):
        """Ladda tutorials från JSON-filer eller använd inbyggda."""
        if self._data_dir:
            tutorial_dir = Path(self._data_dir) / "tutorials"
            if tutorial_dir.exists():
                for json_file in sorted(tutorial_dir.glob("*.json")):
                    try:
                        tutorial = self._load_json_tutorial(json_file)
                        self._tutorials.append(tutorial)
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Varning: Kunde inte ladda {json_file}: {e}")

        if not self._tutorials:
            self._tutorials = BUILTIN_TUTORIALS.copy()

    def _load_json_tutorial(self, path: Path) -> Tutorial:
        """Ladda en tutorial från JSON-fil."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        steps = [
            TutorialStep(
                instruction=s["instruction"],
                code_hint=s.get("code_hint", ""),
                expected_output=s.get("expected_output", ""),
                explanation=s.get("explanation", ""),
            )
            for s in data.get("steps", [])
        ]

        challenges = [
            Challenge(
                prompt=c["prompt"],
                validator=c.get("validator", "output_not_empty"),
                hint=c.get("hint", ""),
            )
            for c in data.get("challenges", [])
        ]

        return Tutorial(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            age_group=data.get("age_group", "8-16"),
            steps=steps,
            challenges=challenges,
            category=data.get("category", "grundläggande"),
        )

    def get_all(self) -> list[Tutorial]:
        """Hämta alla tutorials."""
        return self._tutorials

    def get_by_id(self, tutorial_id: str) -> Tutorial | None:
        """Hämta en tutorial med ID."""
        for t in self._tutorials:
            if t.id == tutorial_id:
                return t
        return None

    def check_output(self, step: TutorialStep, actual_output: str) -> bool:
        """Kontrollera om output matchar förväntat resultat."""
        if not step.expected_output:
            return len(actual_output.strip()) > 0

        # Normalisera whitespace för jämförelse
        expected = step.expected_output.strip()
        actual = actual_output.strip()
        return actual == expected

    def validate_challenge(self, challenge: Challenge, output: str) -> bool:
        """Validera en utmaning."""
        if challenge.validator == "output_not_empty":
            return len(output.strip()) > 0
        if challenge.validator == "output_contains_number":
            return any(c.isdigit() for c in output)
        return len(output.strip()) > 0
