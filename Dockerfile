# 베이스 이미지로 공식 Python 런타임을 사용합니다.
FROM python:3.13-slim

# 컨테이너 내 작업 디렉토리를 설정합니다.
WORKDIR /app

# requirements.txt를 복사하고 의존성을 설치합니다.
# 코드 전체를 복사하기 전에 의존성을 먼저 설치하여 Docker의 레이어 캐시를 활용합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 코드를 작업 디렉토리로 복사합니다.
COPY . .

# 앱이 실행될 포트를 5000번으로 지정합니다.
EXPOSE 5000

# 앱을 실행하는 명령어를 정의합니다.
CMD ["python", "app.py"]
