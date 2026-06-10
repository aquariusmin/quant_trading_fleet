# ⚡ Quant Trading Fleet

**Quant Trading Fleet**는 한국 투자 증권(KIS)과 바이낸스(Binance)를 통합 관리하는 풀스택 자동 매매 플랫폼입니다. 기존의 파이썬 기반 CLI 봇들을 현대적인 웹 대시보드로 통합하여, 실시간 모니터링, 봇 제어, 매매 내역 관리 및 전략 파라미터 조정을 한 곳에서 수행할 수 있습니다.

## ✨ 주요 기능

- **통합 대시보드:** KIS(국내/해외 주식) 및 바이낸스(가상화폐 선물)의 잔고를 실시간으로 확인합니다.
- **실시간 봇 제어:** KOSPI 변동성 돌파, 미주 돌파, 크립토 돌파, 듀얼 모멘텀 봇을 웹 UI에서 클릭 한 번으로 실행/중지합니다.
- **자동화된 매매 기록:** 모든 체결 내역은 SQLite DB에 영구 저장되어 언제든지 복기할 수 있습니다.
- **동적 전략 설정:** 코드 수정 없이 웹 상에서 `K-값`, 투자 금액 등 핵심 파라미터를 즉시 변경하여 적용할 수 있습니다.
- **안정성 중심 설계:** 타임존(KST) 동기화, 중복 매수 방지 로직, 에러 방어 코드가 적용되어 실전 매매에 최적화되어 있습니다.

## 🏗️ 기술 스택

- **Backend:** FastAPI (Python 3.11), SQLAlchemy (ORM)
- **Frontend:** React, TypeScript, Vite, Vanilla CSS
- **Database:** SQLite (로컬 파일 기반, 영구 저장)
- **Container:** Docker, Docker Compose (멀티 스테이지 빌드)
- **Brokers:** CCXT (Binance), KIS API Wrapper

## 🚀 시작하기

### 1. 환경 설정
`.env` 파일을 생성하고 API 키를 입력합니다:
```bash
cp .env.example .env
# .env 파일을 열어 실제 키 값으로 수정하세요.
```

### 2. 어플리케이션 실행
Docker Compose를 사용하여 전체 시스템을 빌드하고 실행합니다:
```bash
docker compose up --build -d
```

### 3. 접속
브라우저를 열고 다음 주소로 접속하세요:
👉 **http://localhost:8000**

## 📂 프로젝트 구조

- `backend/`: FastAPI API 서버 및 비동기 봇 매니저 로직
- `frontend/`: React 대시보드 어플리케이션
- `brokers/`: KIS 및 바이낸스 API 통신 인터페이스 (매매 기록 로깅 포함)
- `strategies/`: 변동성 돌파 및 듀얼 모멘텀 전략 로직
- `config/`: 환경 변수 및 DB 기반 동적 설정 관리
- `logs/`: API 토큰 캐시 및 시스템 로그 저장

## ⚠️ 주의 사항
- 본 프로젝트는 투자 보조 도구이며, 모든 투자 결과에 대한 책임은 사용자 본인에게 있습니다.
- 처음 실행 시에는 반드시 `Settings` 탭에서 **Mock/Testnet** 모드임을 확인한 후 테스트 거래부터 시작하는 것을 권장합니다.
