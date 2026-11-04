"""Local HTTP adapter for the existing L6 engine and JSON storage."""
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from app.engine.runner import ExperimentConfig, run_simulation
from app.models.automaton import AutomatonDefinition
from app.storage.experiment_storage import load_experiment, save_experiment
from app.storage.json_storage import DEFAULT_SAVE_DIR, load_transition, save_transition
from app.validators.validation_service import validate_configuration

AUTOMATA_DIR = Path(__file__).resolve().parents[2] / 'automata'
BUILTINS = ('game_of_life', 'brians_brain', 'forest_fire', 'cyclic_automaton', 'crystal_growth')


class Configuration(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    automaton: AutomatonDefinition
    initial_state: list[list[str]]
    experiment: ExperimentConfig = ExperimentConfig()


class SaveRequest(Configuration):
    final_state: list[list[str]]
    history: list[list[list[str]]] | None = None


def checked(config: Configuration) -> Configuration:
    validation = validate_configuration(config.automaton, config.initial_state)
    if not validation['valid']:
        raise HTTPException(422, detail=validation['errors'])
    return config


def builtin(identifier: str) -> Configuration:
    if identifier not in BUILTINS:
        raise HTTPException(404, 'Automaton not found.')
    return checked(Configuration.model_validate(json.loads((AUTOMATA_DIR / f'{identifier}.json').read_text(encoding='utf-8'))))


def execute(config: Configuration) -> dict:
    checked(config)
    result = run_simulation(config.initial_state, config.automaton, config.experiment)
    return {**config.model_dump(), **result}


def create_app(save_dir: Path = DEFAULT_SAVE_DIR) -> FastAPI:
    app = FastAPI(title='CelLab L6', version='1.0')
    app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

    @app.exception_handler(RequestValidationError)
    async def request_error(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={'error': {'message': 'Invalid request.', 'details': [{'field': '.'.join(map(str, e['loc'])), 'message': e['msg']} for e in exc.errors()]}})

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={'error': {'message': exc.detail if isinstance(exc.detail, str) else 'Configuration validation failed.', 'details': exc.detail if isinstance(exc.detail, list) else []}})

    @app.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={'error': {'message': 'Operation failed. Check the local backend configuration.'}})

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    @app.get('/api/automata')
    def discovery():
        return [{'id': key, **builtin(key).automaton.model_dump(exclude={'rules'})} for key in BUILTINS]

    @app.get('/api/automata/{identifier}', response_model=Configuration)
    def load(identifier: str):
        return builtin(identifier)

    @app.post('/api/configurations/validate', response_model=Configuration)
    def custom(config: Configuration):
        return checked(config)

    @app.post('/api/simulations/run', response_model=SaveRequest)
    def run(config: Configuration):
        return execute(config)

    @app.post('/api/simulations/next', response_model=SaveRequest)
    def step(config: Configuration):
        return execute(config.model_copy(update={'experiment': ExperimentConfig(generations=1, retain_history=config.experiment.retain_history)}))

    @app.post('/api/simulations/run-all', response_model=list[SaveRequest])
    def run_all():
        return [execute(builtin(key).model_copy(update={'experiment': ExperimentConfig()})) for key in BUILTINS[:4]]

    @app.post('/api/experiments', status_code=201)
    def save(record: SaveRequest):
        checked(record)
        expected = run_simulation(record.initial_state, record.automaton, record.experiment)
        if expected != {'final_state': record.final_state, 'history': record.history}:
            raise HTTPException(422, 'Result does not match the requested experiment.')
        if record.experiment.generations == 1 and not record.experiment.retain_history:
            path = save_transition(record.automaton, record.initial_state, record.final_state, save_dir)
        else:
            path = save_experiment(record.automaton, record.initial_state, record.experiment, expected, save_dir)
        return {'id': path.stem, 'message': 'Experiment saved.'}

    @app.get('/api/experiments')
    def saves():
        return [{'id': p.stem} for p in sorted(save_dir.glob('*.json')) if re.fullmatch(r'[A-Za-z0-9_-]+', p.stem) and not p.is_symlink()]

    @app.get('/api/experiments/{identifier}', response_model=SaveRequest)
    def recover(identifier: str):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', identifier):
            raise HTTPException(400, 'Invalid save identifier.')
        path = save_dir / f'{identifier}.json'
        if path.is_symlink() or not path.is_file():
            raise HTTPException(404, 'Saved experiment not found.')
        try:
            header = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(header, dict) and 'format' in header:
                record = load_experiment(path)
            else:
                record = load_transition(path)
                record = {**record, 'experiment': ExperimentConfig().model_dump(), 'final_state': record['next_state'], 'history': None}
            return {key: record[key] for key in ('automaton', 'initial_state', 'experiment', 'final_state', 'history')}
        except (OSError, ValueError, KeyError, TypeError):
            raise HTTPException(422, 'Saved record is invalid or unreadable.') from None

    return app


app = create_app()
