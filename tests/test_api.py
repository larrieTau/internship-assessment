import os
import io
# Ensure tests run in mock mode: unset any SUNBIRD_API_TOKEN present in the test environment
if 'SUNBIRD_API_TOKEN' in os.environ:
    del os.environ['SUNBIRD_API_TOKEN']

from server import app


def test_health():
    client = app.test_client()
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json() == {'status': 'healthy'}


def test_process_text_mock():
    client = app.test_client()
    payload = {'text': 'Hello world', 'target_language': 'luganda'}
    r = client.post('/api/process-text', json=payload)
    assert r.status_code == 200
    j = r.get_json()
    assert 'pipeline' in j
    assert 'translation' in j['pipeline']


def test_process_audio_mock(tmp_path):
    # create a tiny dummy file to simulate upload
    p = tmp_path / 'sample.wav'
    p.write_bytes(b"\x00\x01\x02\x03")

    client = app.test_client()
    with open(p, 'rb') as f:
        data = {
            'audio': (f, 'sample.wav'),
            'target_language': 'luganda'
        }
        r = client.post('/api/process-audio', data=data, content_type='multipart/form-data')

    assert r.status_code == 200
    j = r.get_json()
    assert 'pipeline' in j
    assert 'transcript' in j['pipeline']
