# CelLab – Cellular Automata Simulator

## Descriere

CelLab este un sistem pentru modelarea și simularea automatelor celulare bidimensionale.

Proiectul folosește un motor generic care citește definițiile automatelor din fișiere JSON, validează stările și regulile și calculează generația următoare.

Regulile fiecărui automat sunt definite în JSON, fără implementări Python separate pentru fiecare automat.

Această versiune corespunde Livrabilului 2 (L6) al proiectului de Inteligență Artificială.

## Funcționalități implementate – Livrabilul 2

- Reprezentarea automatelor prin matrice 2D.
- Definirea stărilor și regulilor de tranziție în JSON.
- Validarea structurală și semantică a configurațiilor.
- Vecinătăți Moore și von Neumann.
- Aplicarea sincronă a regulilor.
- Generarea unei singure generații următoare.
- Selectarea unui automat sau rularea tuturor.
- Salvarea și recuperarea stărilor în fișiere JSON.
- Testarea automată a rezultatelor.

## Automate disponibile

| Automat | Stări | Descriere |
|---|---|---|
| Game of Life | DEAD, ALIVE | Naștere, supraviețuire și moarte în funcție de vecini |
| Brian's Brain | OFF, FIRING, DYING | Tranziții între trei stări |
| Forest Fire | EMPTY, TREE, FIRE | Propagarea deterministă a focului |
| Cyclic Cellular Automaton | 0, 1, 2, 3 | Tranziții ciclice bazate pe numărul vecinilor |

Toate automatele folosesc același motor de simulare.

## Tehnologii

- Python 3.14
- Pydantic 2
- Pytest
- JSON pentru definiții și persistență

## Structura proiectului

```text
Cell_Labs/
├── .gitignore
├── README.md
└── backend/
    ├── main.py
    ├── requirements.txt
    ├── app/
    │   ├── models/
    │   │   ├── automaton.py
    │   │   └── rule.py
    │   ├── validators/
    │   │   ├── automaton_validator.py
    │   │   └── validation_service.py
    │   ├── engine/
    │   │   └── simulator.py
    │   └── storage/
    │       └── json_storage.py
    ├── automata/
    │   ├── game_of_life.json
    │   ├── brians_brain.json
    │   ├── forest_fire.json
    │   └── cyclic_automaton.json
    ├── saved_runs/
    └── tests/
        ├── test_models.py
        ├── test_initial_state.py
        ├── test_semantic_validation.py
        ├── test_validation_service.py
        └── test_l6.py
```

## Instalare

Instrucțiunile următoare sunt pentru Windows și PowerShell.

### 1. Cerințe

Instalați Python 3.14 și Git.

Verificați:

```powershell
py -3.14 --version
git --version
```

### 2. Clonarea repository-ului

```powershell
git clone https://github.com/EnachescuAlexandra/Cell_Labs.git
cd Cell_Labs
```

### 3. Crearea mediului virtual

Din rădăcina proiectului:

```powershell
py -3.14 -m venv .venv
```

### 4. Instalarea dependențelor

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

Verificați bibliotecile:

```powershell
.\.venv\Scripts\python.exe -c "import pydantic, pytest; print('Dependencies OK')"
```

Rezultat așteptat:

```text
Dependencies OK
```

## Rularea aplicației

Din rădăcina proiectului:

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

Meniul principal:

```text
========== CELLLAB - L6 ==========
1. Game of Life
2. Brian's Brain
3. Forest Fire
4. Cyclic Cellular Automaton
5. Run ALL
6. Recover saved simulation
0. Exit

Select option:
```

Introduceți numărul opțiunii și apăsați Enter.

### Rularea unui automat

Selectați una dintre opțiunile 1–4.

Programul:
1. Încarcă definiția și matricea inițială din JSON.
2. Validează configurația.
3. Aplică regulile prin motorul generic.
4. Afișează starea curentă și următoarea stare.
5. Permite salvarea tranziției.

### Rularea tuturor automatelor

Selectați opțiunea `5`.

Programul execută consecutiv toate cele patru automate, fără modificarea codului motorului.

În acest mod, rezultatele sunt afișate fără solicitarea salvării.

## Exemplu – Forest Fire

Starea inițială:

```text
TREE TREE TREE
TREE FIRE TREE
TREE TREE TREE
```

După o tranziție:

```text
FIRE FIRE FIRE
FIRE EMPTY FIRE
FIRE FIRE FIRE
```

Celula FIRE devine EMPTY, iar celulele TREE cu minimum un vecin FIRE devin FIRE.

Tranzițiile sunt sincrone: toate celulele sunt calculate folosind aceeași matrice curentă.

## Formatul configurațiilor

Fiecare automat este definit printr-un fișier JSON care conține:

- `automaton.name`: numele automatului
- `width`, `height`: dimensiunile matricei
- `states`: stările posibile
- `neighborhood`: tipul vecinătății
- `boundary`: politica marginilor
- `default`: comportamentul implicit
- `rules`: regulile de tranziție
- `initial_state`: matricea inițială

Fiecare regulă definește starea sursă (`from`), starea destinație (`to`) și condițiile pentru aplicare (`conditions`).

Toate condițiile unei reguli trebuie să fie adevărate.

O listă goală de condiții reprezintă o tranziție necondiționată.

Dacă nicio regulă nu se aplică, celula își păstrează starea curentă.

Pentru această versiune sunt suportate automate deterministe, sincrone, cu stări discrete și vecinătăți locale.

## Salvare și recuperare

După rularea individuală a unui automat, programul întreabă:

```text
Save transition? (y/n):
```

Introduceți `y` pentru salvare.

Se creează un fișier JSON în `backend/saved_runs/`.

Fișierul conține:
- ID-ul salvării
- Data și ora
- Definiția automatului
- Starea inițială
- Starea rezultată

Pentru recuperare, selectați opțiunea `6` din meniul principal.

Programul afișează fișierele salvate. Introduceți numărul corespunzător simulării dorite.

Stările sunt încărcate din fișier, fără recalcularea tranziției.

## Rularea testelor

Din directorul `backend`:

```powershell
..\.venv\Scripts\python.exe -m pytest -v
```

Pentru testele specifice Livrabilului 2:

```powershell
..\.venv\Scripts\python.exe -m pytest tests/test_l6.py -v
```

Rezultatul așteptat pentru versiunea cu patru automate este:

```text
9 passed
```

Testele verifică:
- Validarea configurațiilor
- Generarea corectă a stării următoare
- Funcționarea celor patru automate
- Păstrarea matricei originale
- Salvarea și recuperarea datelor




