# CelLab – AI Interaction Log
## Deliverable 2 (L6) – Cellular Automata Modeling

**AI Assistant:** ChatGPT (OpenAI)
**Project:** CelLab – Cellular Automata Simulator
**Purpose:** Modeling, implementing, testing and documenting a generic cellular automata system.

---

### 1. Deliverable requirements

**User:** Analizează cerințele pentru Livrabilul 2. Vreau să implementăm strict ce cere profesorul, fără funcționalități suplimentare.

**ChatGPT:** Conform cerințelor L6, sistemul trebuie să modeleze starea și regulile unui automat, parametrii experimentului și salvarea/recuperarea stărilor. Testarea presupune citirea generației curente, aplicarea regulilor și generarea unei singure generații noi, pe minimum 2–3 automate diferite.

**User:** Vreau un motor generic. Automatele să fie definite în fișiere JSON, nu să scriem cod Python separat pentru fiecare.

**ChatGPT:** Vom separa definițiile automatelor de motorul de tranziții. Structura va include `models`, `validators`, `engine`, `storage` și `automata`. Motorul va interpreta regulile din JSON indiferent de automatul selectat.

### 2. Data models – `automaton.py` și `rule.py`

**User:** Hai să definim modelele pentru automate și reguli folosind Pydantic.

**ChatGPT:** Pentru fiecare automat avem nevoie de nume, dimensiuni, stări, vecinătate, comportamentul implicit și lista regulilor. Putem defini modelul astfel:

```python
class AutomatonDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=100)
    width: int = Field(ge=1, le=100)
    height: int = Field(ge=1, le=100)
    states: list[str] = Field(min_length=2)
    neighborhood: NeighborhoodType = "moore"
    boundary: BoundaryType = "fixed"
    default: DefaultBehavior = "keep"
    rules: list[TransitionRule] = Field(default_factory=list)
```

**User:** Cum reprezentăm condițiile regulilor?

**ChatGPT:** O regulă are starea sursă, destinația și condițiile asupra vecinilor. Operatorii suportati sunt `==`, `!=`, `<`, `<=`, `>` și `>=`.

```python
class NeighborCondition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: str = Field(min_length=1)
    operator: ComparisonOperator
    value: int = Field(ge=0, le=8)


class TransitionRule(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        populate_by_name=True
    )

    from_state: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    conditions: list[NeighborCondition] = Field(default_factory=list)
```

### 3. Structural and semantic validation

**User:** Vreau să verificăm că JSON-urile conțin configurații valide și că regulile nu sunt contradictorii.

**ChatGPT:** Vom folosi `validate_initial_state()` pentru verificarea matricei și `validate_automaton()` pentru verificarea regulilor.

Validarea urmărește dimensiunile matricei, stările necunoscute, duplicatele, condițiile imposibile și conflictele dintre reguli.

**User:** Vreau un singur punct de intrare pentru validare.

**ChatGPT:** Funcția `validate_configuration()` combină verificările structurale și semantice și returnează un rezultat uniform:

```python
{
    "valid": True,
    "errors": []
}
```

Pentru o configurație invalidă, `errors` conține câmpul problematic și descrierea erorii.

### 4. Generic simulation engine – `simulator.py`

**User:** Implementează motorul generic astfel încât să putem rula toate automatele fără să modificăm algoritmul.

**ChatGPT:** Motorul va conține trei funcții principale: `get_neighbors()`, `evaluate_condition()` și `next_generation()`.

Pentru vecinătățile Moore și von Neumann, folosim deplasări relative față de celula curentă:

```python
if neighborhood == "moore":
    offsets = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
elif neighborhood == "von_neumann":
    offsets = [
        (-1, 0),
        (0, -1), (0, 1),
        (1, 0)
    ]
```

**User:** Cum verificăm condițiile pe baza numărului de vecini?

**ChatGPT:** Numărăm vecinii aflați într-o anumită stare și aplicăm operatorul specificat în JSON.

```python
count = neighbors.count(condition.state)

if operator == "==":
    return count == value
if operator == ">=":
    return count >= value
if operator == "<":
    return count < value
```

**User:** Tranzițiile trebuie calculate pe baza aceleiași generații, nu să modificăm matricea în timp ce o parcurgem.

**ChatGPT:** `next_generation()` construiește o matrice nouă. Pentru fiecare celulă verifică regulile aplicabile și păstrează starea actuală dacă nicio regulă nu se potrivește.

```python
for rule in definition.rules:
    if rule.from_state != current_state:
        continue

    if all(
        evaluate_condition(neighbors, condition)
        for condition in rule.conditions
    ):
        applicable_destinations.add(rule.to)
```

### 5. Automata configurations – JSON

**User:** Vreau să folosim automate din exemplele profesorului, iar toate să fie definite în JSON.

**ChatGPT:** Vom configura Game of Life, Brian's Brain și Forest Fire. Fiecare JSON include definiția automatului și `initial_state`.

De exemplu, Forest Fire:

```json
{
  "from": "TREE",
  "to": "FIRE",
  "conditions": [
    {
      "state": "FIRE",
      "operator": ">=",
      "value": 1
    }
  ]
}
```

**User:** Hai să mai introducem un automat mai complex, fără să modificăm motorul.

**ChatGPT:** Putem folosi Cyclic Cellular Automaton, cu patru stări și reguli ciclice. O celulă trece la următoarea stare când are cel puțin doi vecini aflați deja în acea stare.

```json
{
  "from": "2",
  "to": "3",
  "conditions": [
    {
      "state": "3",
      "operator": ">=",
      "value": 2
    }
  ]
}
```

### 6. State storage and recovery – `json_storage.py`

**User:** Trebuie să avem salvarea și recuperarea stărilor pentru L6. Ce salvăm mai exact?

**ChatGPT:** Salvăm definiția automatului, generația curentă și generația nouă, împreună cu un identificator unic și data execuției.

```python
data = {
    "run_id": run_id,
    "created_at": datetime.now().isoformat(),
    "automaton": definition.model_dump(by_alias=True),
    "initial_state": current_grid,
    "next_state": next_grid
}
```

**User:** Cum recuperăm o simulare salvată?

**ChatGPT:** Funcția `load_transition()` citește fișierul JSON și verifică datele. În meniul principal, utilizatorul poate selecta o salvare prin numărul ei din lista afișată.

### 7. Main application – `main.py`

**User:** Nu am un `main.py`. Vreau ca aplicația să pornească de acolo, nu din `demo.py`.

**ChatGPT:** Vom crea `backend/main.py`. Acesta încarcă automatul selectat, validează configurația, apelează motorul și afișează generația curentă și următoarea generație.

```python
def run_automaton(filename, ask_to_save=True):
    path = AUTOMATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    validation = validate_configuration(
        data["automaton"],
        data["initial_state"]
    )

    if not validation["valid"]:
        return

    definition = AutomatonDefinition.model_validate(
        data["automaton"]
    )

    current_grid = data["initial_state"]
    next_grid = next_generation(current_grid, definition)
```

**User:** Vreau să pot alege un automat sau să le rulez pe toate.

**ChatGPT:** Meniul include cele patru automate, opțiunea `Run ALL`, recuperarea unei salvări și ieșirea din program.

```python
AUTOMATA = {
    "1": "game_of_life.json",
    "2": "brians_brain.json",
    "3": "forest_fire.json",
    "4": "cyclic_automaton.json"
}
```

### 8. Automated testing – `test_l6.py`

**User:** Vreau teste pentru toate automatele, dar și pentru salvare și recuperare.

**ChatGPT:** Folosim Pytest pentru a verifica faptul că motorul produce matrici valide pentru fiecare configurație.

```python
@pytest.mark.parametrize(
    "filename",
    [
        "game_of_life.json",
        "brians_brain.json",
        "forest_fire.json",
        "cyclic_automaton.json"
    ]
)
def test_automata_generate_next_state(filename):
    definition, grid = load_example(filename)
    result = next_generation(grid, definition)

    assert len(result) == definition.height
    assert all(len(row) == definition.width for row in result)
```

**User:** Testăm și dacă generația curentă rămâne nemodificată?

**ChatGPT:** Da, putem verifica faptul că motorul construiește o nouă matrice:

```python
original = [row.copy() for row in grid]

next_generation(grid, definition)

assert grid == original
```

**User:** Vreau să verificăm și că datele salvate pot fi recuperate.

**ChatGPT:** Testul folosește un director temporar și compară datele recuperate cu cele originale:

```python
file_path = save_transition(
    definition, grid, result, save_dir=tmp_path
)

recovered = load_transition(file_path)

assert recovered["initial_state"] == grid
assert recovered["next_state"] == result
```

### 9. Debugging and execution

**User:** La `python -m pytest -v` primesc `ModuleNotFoundError: No module named 'app'`.

**ChatGPT:** Comanda este executată din rădăcina proiectului, în timp ce pachetul `app` se află în `backend`. Rulează testele din directorul `backend`:

```powershell
cd backend
python -m pytest -v
```

**User:** Gata, toate testele au trecut. Pot să fac push pe GitHub?

**ChatGPT:** Da. Verifică fișierele urmărite de Git, apoi creează commit-ul și fă push pe branch-ul curent. Directoarele `.venv`, `.idea`, cache-urile Python și salvările generate local trebuie excluse prin `.gitignore`.

### 10. Project documentation

**User:** Creează un README și verifică dacă trebuie alte documente pentru Livrabilul 2.

**ChatGPT:** README-ul va include descrierea proiectului, funcționalitățile L6, cele patru automate, structura directoarelor, instalarea, comenzile de rulare, testarea, salvarea și recuperarea stărilor.

Nu este necesar un document separat pentru fiecare modul. Interacțiunile cu asistentul AI pot fi arhivate separat, în documentația proiectului.

---

**Note:** This document is a condensed, reconstructed record of the development conversation. Code excerpts are representative of the discussed implementation; some user questions and assistant explanations have been reformulated for clarity. It is not a verbatim chat export.