# 간단한 사용자 및 할 일 관리 API

## 설명
이 프로젝트는 사용자 및 할 일 목록을 관리하기 위한 간단한 API를 구현합니다. 데이터 지속성을 위해 인메모리 데이터베이스를 사용하므로, 외부 데이터베이스 구성 없이 쉽게 설정하고 실행할 수 있습니다. 인증은 JWT(JSON 웹 토큰)를 통해 처리됩니다.

## 기능
*   **사용자 관리**: 새로운 사용자 등록, 로그인, 사용자별 정보 접근.
*   **할 일 관리**: 인증된 사용자와 관련된 할 일 항목 생성, 조회, 업데이트, 삭제.
*   **인메모리 데이터베이스**: 모든 데이터는 메모리에 저장되며, 애플리케이션 재시작 시 초기화됩니다.
*   **JWT 인증**: 토큰 기반 인증을 사용하여 API 엔드포인트를 보호합니다.

## 기술 스택
*   **Python**: 프로그래밍 언어
*   **Flask**: 웹 프레임워크
*   **Flask-RESTx**: Flask에 REST API 구축을 위한 지원을 추가하는 확장.
*   **Flask-JWT-Extended**: Flask 애플리케이션에 JWT 지원을 추가하는 Flask 확장.

## 설정 지침

1.  **저장소 복제**:
    ```bash
    git clone <repository_url>
    cd v3 # 또는 프로젝트 디렉토리 이름
    ```

2.  **가상 환경 생성 및 활성화**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **의존성 설치**:
    ```bash
    pip install -r requirements.txt
    ```

## 애플리케이션 실행

1.  **가상 환경이 활성화되어 있는지 확인**:
    ```bash
    source venv/bin/activate
    ```

2.  **Flask 애플리케이션 실행**:
    ```bash
    python app.py
    ```
    애플리케이션은 일반적으로 `http://127.0.0.1:5000/`에서 실행됩니다.

## API 엔드포인트

모든 API 엔드포인트는 `/api`로 시작합니다.

### 인증

#### 1. 사용자 등록
*   **엔드포인트**: `POST /api/register`
*   **설명**: 새로운 사용자를 등록합니다.
*   **요청 본문**:
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
*   **응답**:
    ```json
    {
        "message": "User registered successfully"
    }
    ```

#### 2. 사용자 로그인
*   **엔드포인트**: `POST /api/login`
*   **설명**: 기존 사용자로 로그인하고 액세스 토큰을 반환합니다. 이 토큰은 보호된 엔드포인트에 접근하는 데 사용되어야 합니다.
*   **요청 본문**:
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
*   **응답**:
    ```json
    {
        "access_token": "eyJ..."
    }
    ```

#### 액세스 토큰 사용 방법:
로그인 후 `access_token`을 받게 됩니다. 이 토큰을 보호된 모든 엔드포인트에 대한 후속 요청의 `Authorization` 헤더에 `Bearer <access_token>` 형식으로 포함해야 합니다.

**`curl`을 사용한 예시**:
```bash
curl -X GET \
  -H "Authorization: Bearer eyJ..." \
  http://127.0.0.1:5000/api/user
```

### 사용자 관리

#### 1. 사용자 정보 가져오기 (보호됨)
*   **엔드포인트**: `GET /api/user`
*   **설명**: 현재 인증된 사용자의 정보를 검색합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **응답**:
    ```json
    {
        "id": "user_id",
        "username": "your_username"
    }
    ```

### 할 일 관리 (보호됨)

모든 할 일 엔드포인트는 유효한 JWT 액세스 토큰이 필요합니다.

#### 1. 할 일 생성
*   **엔드포인트**: `POST /api/todos`
*   **설명**: 인증된 사용자를 위한 새로운 할 일 항목을 생성합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **요청 본문**:
    ```json
    {
        "title": "장보기",
        "description": "우유, 계란, 빵"
    }
    ```
*   **응답**:
    ```json
    {
        "id": "todo_id",
        "title": "장보기",
        "description": "우유, 계란, 빵",
        "completed": false
    }
    ```

#### 2. 모든 할 일 가져오기
*   **엔드포인트**: `GET /api/todos`
*   **설명**: 인증된 사용자의 모든 할 일 항목을 검색합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **응답**:
    ```json
    [
        {
            "id": "todo_id_1",
            "title": "장보기",
            "description": "우유, 계란, 빵",
            "completed": false
        },
        {
            "id": "todo_id_2",
            "title": "강아지 산책시키기",
            "description": "아침 산책",
            "completed": true
        }
    ]
    ```

#### 3. 특정 할 일 가져오기
*   **엔드포인트**: `GET /api/todos/<todo_id>`
*   **설명**: ID로 단일 할 일 항목을 검색합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **응답**:
    ```json
    {
        "id": "todo_id",
        "title": "장보기",
        "description": "우유, 계란, 빵",
        "completed": false
    }
    ```

#### 4. 할 일 업데이트
*   **엔드포인트**: `PUT /api/todos/<todo_id>`
*   **설명**: 기존 할 일 항목을 업데이트합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **요청 본문**:
    ```json
    {
        "title": "유기농 식료품 구매",
        "description": "유기농 우유, 계란, 빵",
        "completed": true
    }
    ```
*   **응답**:
    ```json
    {
        "id": "todo_id",
        "title": "유기농 식료품 구매",
        "description": "유기농 우유, 계란, 빵",
        "completed": true
    }
    ```

#### 5. 할 일 삭제
*   **엔드포인트**: `DELETE /api/todos/<todo_id>`
*   **설명**: 할 일 항목을 삭제합니다.
*   **인증**: 유효한 JWT 액세스 토큰이 필요합니다.
*   **응답**:
    ```json
    {
        "message": "Todo deleted successfully"
    }
    ```

## 테스트
유닛 테스트를 실행하려면 `pytest`를 사용하세요:
```bash
pytest
```