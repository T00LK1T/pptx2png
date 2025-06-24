.PHONY: help ppt2pdf pdf2png build up down stop rib ris ps logs rmi

help: # 도움말 출력
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*#' Makefile | sed -E 's/:.*#/\t- /' | sort
	@echo
	@echo "Usage: make <target> [service=<service_name>]"

## Local utilities

ppt2pdf: # PPT(PPTX) -> PDF 변환
	poetry run python -m pptx2pdf --input ./ppt --output ./pdf

pdf2png: # PDF -> PNG 변환
	poetry run python -m pdf2png --input ./pdf --output ./png

bomb: # request bombing
	poetry run python -m bomber --url $(url)

## r/ Docker
DC=docker compose -f docker-compose.yaml
build: # Docker 이미지 빌드
	$(DC) build $(service)

up: # Docker 컨테이너 시작
	$(DC) up $(service) -d

down: # Docker 컨테이너 중지 및 삭제
	$(DC) down --remove-orphans

stop: # Docker 컨테이너 중지
	$(DC) stop $(service)

rib: # bash 쉘 실행
	@[[ -z "$(service)" ]] && { echo "service=foo required"; exit 1; } || true
	@$(DC) exec -it $(service) bash

ris: # sh 쉘 실행
	@[[ -z "$(service)" ]] && { echo "service=foo required"; exit 1; } || true
	@$(DC) exec -it $(service) sh

ps: # Docker 컨테이너 상태 확인
	$(DC) ps

logs: # Docker 컨테이너 로그 확인
	@[[ -z "$(service)" ]] && { echo "service=foo required"; exit 1; } || true
	@$(DC) logs -f $(service)

purge: # 이 프로젝트의 모든 Docker 관련 데이터 삭제
	@echo "This will remove all Docker images, containers, and volumes related to this project."
	@read -p "Are you sure? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker compose -f docker-compose.yaml down --rmi all --volumes --remove-orphans; \
	else \
		echo "Aborted."; \
	fi
