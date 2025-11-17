HAS_GPU := `command -v nvidia-smi > /dev/null && echo "1" || echo "0"`

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
	#!/usr/bin/env bash
	mkdir -p ./models
	mkdir -p ./data
	if [ "{{HAS_GPU}}" = "1" ]; then
		echo "NVIDIA GPU detected, using docker-compose-gpu.yml"
		docker compose -f docker-compose-gpu.yml up --attach ner-gpu --attach ner-ui --build
	else
		echo "No NVIDIA GPU detected, using docker-compose.yml"
		docker compose -f docker-compose.yml up --attach ner --attach ner-ui --build
	fi

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
    sudo rm -rf /opt/microsoft
    sudo rm -rf /opt/az
    sudo rm -rf /opt/pipx
    sudo rm -rf /usr/local/.ghcup
    sudo rm -rf /usr/local/aws-cli
    sudo rm -rf /usr/local/share/vcpkg
    sudo rm -rf /usr/share/miniconda
    sudo rm -rf /home/linuxbrew
    sudo rm -rf /opt/hostedtoolcache/*
    sudo apt-get remove -y azure-cli || true
    sudo apt-get remove -y '^dotnet-.*' || true
    sudo apt-get remove -y '^aspnetcore-.*' || true
    sudo apt-get remove -y powershell || true
    sudo docker system prune --all --force --volumes
    df -h

start_detached:
	mkdir -p ./models
	mkdir -p ./data
	docker compose up --build -d

upgrade:
	. .venv/bin/activate; pip-upgrade

tag:
	#!/bin/bash
	# Get current date
	CURRENT_DATE=$(date +%Y.%-m.%-d)
	echo "Current date: $CURRENT_DATE"

	# Get the latest tag that matches today's date pattern
	LATEST_TAG=$(git tag --list "${CURRENT_DATE}.*" --sort=-version:refname | head -n1)

	if [ -z "$LATEST_TAG" ]; then
		# No tag for today, start with revision 1
		REVISION=1
	else
		# Extract revision number and increment
		REVISION=$(echo $LATEST_TAG | cut -d. -f4)
		REVISION=$((REVISION + 1))
	fi

	NEW_TAG="${CURRENT_DATE}.${REVISION}"
	echo "Creating new tag: $NEW_TAG"
	git tag $NEW_TAG
	git push --tag
