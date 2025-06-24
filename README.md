# pptx2png

PPT(PPTX) 파일을 PNG 파일로 변환합니다.

PPT를 PNG로 바로 변환할 수 있는 오픈소스 프로젝트를 찾을 수 없었기 때문에

PDF로 변환한 뒤, PDF를 PNG로 변환하는 방식을 사용합니다.

이 과정에서 libreoffice와 pdf2image가 필요했습니다.

각 아키텍처에 대응하는 시스템구성을 하기엔 번거로웠기 때문에, Dockerfile 을 작성하였습니다.

Docker 이미지를 빌드하여 CLI, Web API를 제공하는 컨테이너를 실행할 수 있습니다.

## Usage

### Docker

로컬 개발환경에서 Docker 컨테이너를 관리하기위한 커맨드를 제공합니다.

```bash
# Docker 이미지 빌드
make build

# Docker 컨테이너 시작 (웹)
make up service=web

# Docker 컨테이너 시작 (CLI)
make up service=cli

# Docker 컨테이너 상태 확인
make ps

# Docker 컨테이너 로그 확인
make logs service=web

# Docker 컨테이너에서 bash 쉘 실행
make rib service=web

# Docker 컨테이너에서 sh 쉘 실행
make ris service=web

# Docker 컨테이너 실행중단
make stop service=web

# Docker 컨테이너 실행중단 및 삭제
make down service=web

# 모든 리소스 정리
make purge
```

### CLI

CLI를 통해 PPT(PPTX) 파일을 PNG 파일로 변환할 수 있습니다.

**로컬스토리지의 pdf, ppt, png 디렉터리를 볼륨으로 연동하여 사용하도록 작성했습니다.**

**프로젝트 내부의 `ppt` 디렉터리에 파일을 넣고 실행하면 됩니다.**

```bash
make build && make up service=cli
make rib service=cli

> make pdf2png # PDF -> PNG 변환
> make ppt2pdf # PPT(PPTX) -> PDF 변환
```

### Web API

```bash
make build && make up service=web
```

#### 이미지 변환요청

컨테이너 실행 후, `http://localhost:38080/docs` 에 접속하면 Swagger UI를 통해 API를 확인할 수 있습니다.

`POST /preprocess/ppt` 엔드포인트를 통해 PPT(PPTX) 파일을 업로드하여 PNG 파일로 변환할 수 있습니다.

웹 애플리케이션 서버에서 백그라운드 방식으로 작업이 수행되며, task ID가 반환됩니다.

#### 작업 실행상태 확인

실행상태는 요청시 응답으로 받은 `task_id`를 `GET /preprocess/ppt/status?{task_id}` 경로에 전달하여 확인할 수 있습니다.

#### 작업 결과 확인

작업이 완료되면 디렉터리에 png 파일이 생성됩니다.

### Available `Makefile` Commands

```bash
> make help
Available targets:
bomb    -  request bombing
build   -  Docker 이미지 빌드
down    -  Docker 컨테이너 중지 및 삭제
help    -  도움말 출력
logs    -  Docker 컨테이너 로그 확인
pdf2png -  PDF -> PNG 변환
ppt2pdf -  PPT(PPTX) -> PDF 변환
ps      -  Docker 컨테이너 상태 확인
purge   -  이 프로젝트의 모든 Docker 관련 데이터 삭제
rib     -  bash 쉘 실행
ris     -  sh 쉘 실행
stop    -  Docker 컨테이너 중지
up      -  Docker 컨테이너 시작

Usage: make <target> [service=<service_name>]
```
