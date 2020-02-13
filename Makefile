INSTALL_SCRIPTS_DIR=scripts
CHEFMOJI_SRC_DIR=src

include .env

install:
	# TODO: error out on python3 not being installed!
	pip install virtualenvwrapper
	. $(INSTALL_SCRIPTS_DIR)/environ
	./$(INSTALL_SCRIPTS_DIR)/setupvenvwrapper
	. /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv chefmoji-backend; setvirtualenvproject $$VIRTUAL_ENV $(pwd)
	./$(INSTALL_SCRIPTS_DIR)/installprotoc
	pip3 install -r src/requirements.txt
	export FLASK_APP=src/app.py


proto:
	protoc -I=$(CHEFMOJI_SRC_DIR)/proto --python_out=$(CHEFMOJI_SRC_DIR) src/proto/game_update.proto src/proto/player_action.proto

dev: proto
	export FLASK_ENV=development && python3 $(CHEFMOJI_SRC_DIR)/app.py

build-base: proto  
	docker build . -t base

ec2-login:
	ssh -i $(PEM_FILE) ec2-user@$(EC2_IP)

