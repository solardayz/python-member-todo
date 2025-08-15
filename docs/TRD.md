### **기술 요구사항 명세서 (TRD): Todo List API 서버 (v3)**

**1. 시스템 아키텍처 (System Architecture)**

*   Python 기반의 Flask 웹 프레임워크를 사용하여 RESTful API 서버를 구축합니다.
*   Flask-RESTX 라이브러리를 활용하여 API 라우팅, 요청/응답 모델링 및 Swagger UI 자동화를 구현합니다.
*   **사용자 인증 및 인가는 JWT(JSON Web Token)를 기반으로 처리합니다.**
*   **`Flask-JWT-Extended` 라이브러리를 사용하여 JWT의 생성, 검증 및 사용자 식별을 관리합니다.**
*   초기 버전에서는 별도의 데이터베이스 없이, 서버 메모리(In-memory Dictionary/List)를 사용하여 **사용자와 할 일 데이터**를 임시 저장합니다. (서버 재시작 시 데이터 초기화)

**2. 기술 스택 (Technology Stack)**

*   **언어:** Python 3.x
*   **프레임워크/라이브러리:**
    *   `Flask`: 핵심 웹 프레임워크
    *   `Flask-RESTX`: RESTful API 개발 및 문서 자동화
    *   **`Flask-JWT-Extended`**: JWT 기반 인증 구현
    *   **`Werkzeug`**: 비밀번호 해싱(Hashing)에 사용 (Flask 기본 의존성)

**3. API 엔드포인트 명세 (API Endpoint Specification)**

**3.1 인증 (Auth)**
*   **Base URL:** `/auth`

| 기능 | HTTP Method | URL | Request Body (JSON) | Success Response |
| :--- | :--- | :--- | :--- | :--- |
| **회원가입** | `POST` | `/signup` | `{ "username": "string", "password": "string" }` | `201 Created` - `{ "message": "User created successfully" }` |
| **로그인** | `POST` | `/login` | `{ "username": "string", "password": "string" }` | `200 OK` - `{ "access_token": "string" }` |

**3.2 할 일 (Todos)**
*   **Base URL:** `/todos`
*   **공통 요구사항:** 모든 엔드포인트는 HTTP Header에 `Authorization: Bearer <Access-Token>`을 포함해야 합니다.

| 기능 | HTTP Method | URL | Request Body (JSON) | Success Response |
| :--- | :--- | :--- | :--- | :--- |
| **목록 조회** | `GET` | `/` | (없음) | `200 OK` - 해당 사용자의 Todo 리스트 |
| **신규 생성** | `POST` | `/` | `{ "title": "string", "description": "string" }` | `201 Created` - 생성된 Todo 객체 |
| **개별 조회** | `GET` | `/<int:id>` | (없음) | `200 OK` - 해당 ID의 Todo 객체 |
| **수정** | `PUT` | `/<int:id>` | `{ "title": "string", "description": "string", "is_done": boolean }` | `200 OK` - 수정된 Todo 객체 |
| **삭제** | `DELETE` | `/<int:id>` | (없음) | `204 No Content` |

**4. 데이터 모델 (Data Model)**

*   **사용자 객체 (User):**
    *   `id` (integer): 고유 식별자.
    *   `username` (string, required): 사용자 ID.
    *   `password_hash` (string, required): 해싱된 비밀번호. **절대 평문(Plain Text)으로 저장하지 않음.**
*   **할 일 객체 (Todo):**
    *   `id` (integer): 고유 식별자.
    *   **`user_id` (integer): 할 일을 소유한 사용자의 ID.**
    *   `title` (string, required): 할 일의 제목.
    *   `description` (string): 할 일의 상세 설명.
    *   `is_done` (boolean): 완료 여부. 기본값은 `false`.

**5. 에러 처리 (Error Handling)**

*   **401 Unauthorized:** JWT 토큰이 없거나 유효하지 않을 경우.
*   **403 Forbidden:** 자신의 소유가 아닌 데이터에 접근을 시도할 경우 (구현 선택 사항).
*   **404 Not Found:** 요청한 리소스(`id`)가 존재하지 않을 경우.
*   **409 Conflict:** 이미 존재하는 `username`으로 회원가입을 시도할 경우.

**6. 향후 개선 과제 (Future Improvements)**

*   **데이터베이스 연동:** 사용자 데이터의 영구 저장을 위해 SQLite, PostgreSQL 등 RDBMS로 전환.
*   **Refresh Token 도입:** Access Token의 짧은 유효기간을 보완하기 위한 Refresh Token 구현.
