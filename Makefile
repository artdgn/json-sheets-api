REPO_NAME=json-sheets-api
VENV_ACTIVATE=. .venv/bin/activate
PYTHON=.venv/bin/python
DOCKER_TAG=artdgn/$(REPO_NAME)
PORT=9000

.venv:
	python3 -m venv .venv

requirements: .venv
	$(VENV_ACTIVATE); \
	python -m pip install -U pip; \
	python -m pip install -U pip-tools; \
	pip-compile requirements.in; \
	pip-compile requirements[dev].in

install: .venv
	$(VENV_ACTIVATE); \
	python -m pip install -U pip; \
	python -m pip install -r requirements.txt
	python -m pip install -r requirements[dev].txt

kill-server:
	kill -9 `netstat -tulpn | grep $(PORT) | grep -oP "(?<=)\d+(?=\/)"`

server:
	$(VENV_ACTIVATE); \
	UVICORN_PORT=$(PORT) python server.py

build-docker:
	docker build -t $(DOCKER_TAG) .

docker-server: build-docker
	docker rm -f $(REPO_NAME) || sleep 1
	docker run -it --rm \
	--name $(REPO_NAME) \
	-p $(PORT):$(PORT) \
	-e UVICORN_PORT=$(PORT) \
	$(DOCKER_TAG)

docker-server-persist: build-docker
	docker run -dit \
	--name $(REPO_NAME) \
	-p $(PORT):$(PORT) \
	--restart unless-stopped \
	$(DOCKER_TAG)

docker-update-server:
	docker rm -f $(REPO_NAME) || sleep 1
	$(MAKE) docker-server-persist

docker-logs:
	docker logs $(REPO_NAME) -f

tests:
	pytest

ngrok:
	$(HOME)/ngrok/ngrok http $(PORT)
