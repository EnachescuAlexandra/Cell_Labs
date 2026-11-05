import copy

import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path))


def configuration(client):
    return client.get('/api/automata/game_of_life').json()


def test_discovery_and_loading(client):
    items = client.get('/api/automata').json()
    assert len(items) == 5
    assert items[-1]['id'] == 'crystal_growth'
    for item in items:
        response = client.get('/api/automata/' + item['id'])
        assert response.status_code == 200
        assert len(response.json()['initial_state']) == item['height']
    assert client.get('/api/automata/missing').status_code == 404


def test_step_and_batch_preserve_input(client):
    config = configuration(client)
    original = copy.deepcopy(config)
    one = client.post('/api/simulations/next', json=config).json()
    assert one['experiment']['generations'] == 1
    assert one['history'] is None
    assert one['final_state'] != config['initial_state']
    config['experiment'].update(generations=2, retain_history=True)
    result = client.post('/api/simulations/run', json=config).json()
    assert result['final_state'] == original['initial_state']
    assert len(result['history']) == 3
    assert result['initial_state'] == original['initial_state']


@pytest.mark.parametrize('count', [0, -1, 1.5, True, '2'])
def test_invalid_counts(client, count):
    config = configuration(client)
    config['experiment']['generations'] = count
    response = client.post('/api/simulations/run', json=config)
    assert response.status_code == 422
    assert 'error' in response.json()


@pytest.mark.parametrize('generations,history', [(1, False), (3, False), (3, True)])
def test_save_recover(client, generations, history):
    config = configuration(client)
    config['experiment'].update(generations=generations, retain_history=history)
    result = client.post('/api/simulations/run', json=config).json()
    response = client.post('/api/experiments', json=result)
    assert response.status_code == 201
    identifier = response.json()['id']
    assert {'id': identifier} in client.get('/api/experiments').json()
    assert client.get('/api/experiments/' + identifier).json() == result
    result['final_state'][0][0] = 'ALIVE'
    assert client.post('/api/experiments', json=result).status_code == 422


def test_custom_and_errors(client):
    config = configuration(client)
    assert client.post('/api/configurations/validate', json=config).status_code == 200
    config['initial_state'][0][0] = 'UNKNOWN'
    assert client.post('/api/configurations/validate', json=config).status_code == 422
    config = configuration(client)
    config['automaton']['rules'].append({'from': 'DEAD', 'to': 'DEAD', 'conditions': []})
    assert client.post('/api/configurations/validate', json=config).status_code == 422
    response = client.post('/api/configurations/validate', content='{', headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert client.get('/api/experiments/invalid!').status_code == 400
    assert client.get('/api/experiments/missing').status_code == 404


def test_corrupt_record(client, tmp_path):
    (tmp_path / 'broken.json').write_text('{}')
    assert client.get('/api/experiments/broken').status_code == 422


def test_run_all(client):
    results = client.post('/api/simulations/run-all').json()
    assert len(results) == 4
    assert all(r['experiment']['generations'] == 1 and r['history'] is None for r in results)
    assert all(r['automaton']['name'] != 'Crystal Growth' for r in results)


def test_local_cors(client):
    assert client.get('/api/health', headers={'Origin':'http://localhost:5173'}).headers['access-control-allow-origin'] == 'http://localhost:5173'
    assert 'access-control-allow-origin' not in client.get('/api/health', headers={'Origin':'https://example.org'}).headers
