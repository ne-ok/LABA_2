# Выполнила: Паскида Оксана
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing by Maria Ostapenko")

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_get_users():
    client.post(
        "/register/", json={"username": "string", "email": "string@example.com", "full_name": "Test User",
                            "password": "string123"}, )
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert any(user["username"] == "string" for user in data)


def test_create_user():
    response = client.post(
        "/register/", json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User",
                            "password": "password123"}, )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"


# 1. Тестирование регистрации пользователя
def test_register_new_user():
    # Пытаемся зарегистрировать пользователя с существующим username
    response = client.post("/register/", json={"username": "testuser", "email": "newemail@example.com",
                                               "full_name": "Duplicate User", "password": "password123"}, )
    assert response.status_code == 400
    assert "Username or Email already registered" in response.text


# 2. Тестирование аутентификации
def test_login_success():
    # Успешная аутентификация
    response = client.post(
        "/token", data={"username": "testuser", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    # Неправильные учетные данные
    response = client.post(
        "/token", data={"username": "testuser", "password": "wrongpassword"},
        headers={"content-type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect username or password" in response.text


# 3. Тестирование получения пользователей
def test_get_users_me():
    # Сначала получаем токен
    login_response = client.post(
        "/token", data={"username": "testuser", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"})
    token = login_response.json()["access_token"]

    # Затем запрашиваем /users/me с токеном
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# 4. Тестирование обновления пользователя
def test_update_user():
    # Получаем токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]

    # Получаем ID пользователя
    users_response = client.get("/users/")
    user_id = next(user["id"] for user in users_response.json() if user["username"] == "testuser")

    # Обновляем данные
    update_response = client.put(
        f"/users/{user_id}",
        json={"full_name": "Updated Name", "email": "updated@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated Name"
    assert update_response.json()["email"] == "updated@example.com"


# 5. Тестирование удаления пользователя
def test_delete_user():
    # Создаем временного пользователя для удаления
    temp_user = {
        "username": "todelete",
        "email": "todelete@example.com",
        "full_name": "To Delete",
        "password": "password123"
    }
    client.post("/register/", json=temp_user)

    # Получаем его токен и ID
    login_response = client.post(
        "/token",
        data={"username": "todelete", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]

    users_response = client.get("/users/")
    user_id = next(user["id"] for user in users_response.json() if user["username"] == "todelete")

    # Удаляем пользователя
    delete_response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200

    # Пытаемся удалить повторно
    repeat_delete = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert repeat_delete.status_code == 404


# 6. Тестирование работы CORS
def test_cors():
    # Проверяем, что CORS разрешает запросы с любого origin (*)
    response = client.get("/", headers={"Origin": "http://any-domain.com"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
