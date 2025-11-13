APP_IMAGE ?= hexletprojects/qa_auto_python_testing_kanban_board_project_ru_app
APP_CONTAINER ?= kanban-app
APP_PORT ?= 5173

.PHONY: start stop restart test

start:
	docker run --rm -d --name $(APP_CONTAINER) -p $(APP_PORT):5173 $(APP_IMAGE)

stop:
	- docker stop $(APP_CONTAINER)

restart: stop start

test:
	uv run pytest
