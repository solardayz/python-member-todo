def test_hello_world(test_client):
    response = test_client.get('/hello')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Hello, World!"
