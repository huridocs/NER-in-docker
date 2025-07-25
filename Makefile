HAS_GPU := $(shell command -v nvidia-smi > /dev/null && echo 1 || echo 0)

install:
	. .venv/bin/activate; pip install -Ur requirements.txt

activate:
	. .venv/bin/activate

install_venv:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r dev-requirements.txt

formatter:
	. .venv/bin/activate; command black --line-length 125 .

check_format:
	. .venv/bin/activate; command black --line-length 125 . --check

remove_docker_containers:
	docker compose ps -q | xargs docker rm

remove_docker_images:
	docker compose config --images | xargs docker rmi

download_models:
	. .venv/bin/activate; command python src/download_models.py

start:
ifeq ($(OS), Windows_NT)
	if not exist models mkdir models
	if not exist data mkdir data
else
	mkdir -p ./models
	mkdir -p ./data
endif
ifeq ($(HAS_GPU), 1)
	@echo "NVIDIA GPU detected, using docker-compose-gpu.yml"
	docker compose -f docker-compose-gpu.yml up --build --attach ner-gpu
else
	@echo "No NVIDIA GPU detected, using docker-compose.yml"
	docker compose -f docker-compose.yml up --build --attach ner
endif

start_no_gpu:
	mkdir -p ./data
	mkdir -p ./models
	docker compose up --build

stop:
	docker compose stop ; docker compose -f docker-compose-gpu.yml stop

test:
	. .venv/bin/activate; command cd src; command python -m pytest

free_up_space:
	df -h
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /opt/ghc
	sudo rm -rf "/usr/local/share/boost"
	sudo rm -rf "$AGENT_TOOLSDIRECTORY"
	sudo apt-get remove -y '^llvm-.*' || true
	sudo apt-get remove -y 'php.*' || true
	sudo apt-get remove -y google-cloud-sdk hhvm google-chrome-stable firefox mono-devel || true
	sudo apt-get autoremove -y
	sudo apt-get clean
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /usr/local/lib/android
	sudo rm -rf /opt/hostedtoolcache/CodeQL
	sudo rm -rf /usr/local/share/chromium
	sudo rm -rf /usr/local/share/powershell
	sudo rm -rf /usr/share/swift
	sudo rm -rf /usr/local/julia*
	sudo docker system prune --all --force
	df -h

start_detached:
	mkdir -p ./models
	mkdir -p ./data
	docker compose up --build -d

upgrade:
	. .venv/bin/activate; pip-upgrade
