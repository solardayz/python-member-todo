# DynamoDB 데이터 모델링 문서

이 문서는 Todo List API 서버에서 사용하는 DynamoDB 테이블의 데이터 모델링을 상세히 설명합니다. PynamoDB를 사용하여 정의된 `UserModel`과 `TodoModel`의 스키마, 속성, 기본 키 및 Global Secondary Index (GSI)에 초점을 맞춥니다.

## 1. 데이터 모델 (Data Model)

### 1.1 사용자 객체 (User): `UserModel`

`UserModel`은 사용자 정보를 저장하는 DynamoDB 테이블의 스키마를 정의합니다.

*   **`id`** (string): 고유 식별자 (Partition Key). UUID로 생성됩니다.
*   **`username`** (string, required): 사용자 ID. `username_index` (Global Secondary Index)의 Partition Key로 사용됩니다.
*   **`email`** (string, required): 사용자 이메일.
*   **`password_hash`** (string, required): 해싱된 비밀번호. **절대 평문(Plain Text)으로 저장하지 않음.**
*   **`created_at`** (datetime): 사용자 생성 시간.
*   **`updated_at`** (datetime): 사용자 정보 마지막 업데이트 시간.

### 1.2 할 일 객체 (Todo): `TodoModel`

`TodoModel`은 할 일 항목 정보를 저장하는 DynamoDB 테이블의 스키마를 정의합니다.

*   **`id`** (string): 고유 식별자 (Partition Key). UUID로 생성됩니다.
*   **`user_id`** (string, required): 할 일을 소유한 사용자의 ID. `user_id_index` (Global Secondary Index)의 Partition Key로 사용됩니다.
*   **`description`** (string, required): 할 일의 상세 설명.
*   **`status`** (string, required): 할 일의 상태 (예: `pending`, `completed`).
*   **`created_at`** (datetime): 할 일 생성 시간. `user_id_index`의 Sort Key로 사용됩니다.
*   **`updated_at`** (datetime): 할 일 정보 마지막 업데이트 시간.

## 2. DynamoDB 테이블 및 인덱스 상세

애플리케이션은 두 개의 주요 DynamoDB 테이블을 사용하며, 효율적인 데이터 조회를 위해 Global Secondary Index (GSI)를 활용합니다.

### 2.1 `users` 테이블 (PynamoDB: `UserModel`)

*   **Primary Key**:
    *   **Partition Key**: `id`
        *   각 사용자를 고유하게 식별하는 데 사용됩니다.
*   **Global Secondary Index (GSI)**: `username_index`
    *   **Partition Key**: `username`
    *   **목적**: 사용자 이름(`username`)을 기반으로 사용자를 빠르게 조회하기 위함입니다. `username`은 고유해야 하므로, 이 인덱스를 통해 특정 사용자 이름에 해당하는 사용자 정보를 효율적으로 찾을 수 있습니다.

### 2.2 `todos` 테이블 (PynamoDB: `TodoModel`)

*   **Primary Key**:
    *   **Partition Key**: `id`
        *   각 할 일 항목을 고유하게 식별하는 데 사용됩니다.
*   **Global Secondary Index (GSI)**: `user_id_index`
    *   **Partition Key**: `user_id`
    *   **Sort Key**: `created_at`
    *   **목적**: 특정 사용자의 모든 할 일 항목을 조회하고, 이들을 생성 시간(`created_at`) 순으로 정렬하는 데 사용됩니다. 이를 통해 사용자는 자신의 할 일 목록을 최신순 또는 오래된순으로 효율적으로 관리할 수 있습니다.

## 3. PynamoDB 사용

이 프로젝트는 Python에서 DynamoDB와 상호작용하기 위해 `PynamoDB` 라이브러리를 사용합니다. `PynamoDB`는 DynamoDB 테이블을 Python 클래스로 매핑하여 ORM(Object-Relational Mapping)과 유사한 방식으로 데이터를 다룰 수 있게 해줍니다. 이를 통해 개발자는 DynamoDB의 복잡한 API 호출 대신 Python 객체 지향적인 방식으로 데이터를 조작할 수 있습니다.
