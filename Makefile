INSTALL_SCRIPTS_DIR=scripts
CHEFMOJI_SRC_DIR=src

include .env

install:
	# TODO: error out on python3 not being installed!
	pip install virtualenvwrapper
	source $(install_SCRIPTS_DIR)/environ
	./$(INSTALL_SCRIPTS_DIR)/setupvenvwrapper
	source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv chefmoji-backend; setvirtualenvproject $$VIRTUAL_ENV $(pwd)
	./$(INSTALL_SCRIPTS_DIR)/installprotoc
	pip install -r src/requirements.txt

proto:
	protoc -I=$(CHEFMOJI_SRC_DIR)/proto --python_out=$(CHEFMOJI_SRC_DIR) src/proto/game_update.proto src/proto/player_action.proto

dev:
	export FLASK_ENV=development && python3 $(CHEFMOJI_SRC_DIR)/app.py

prod:
	docker build . -t chefmoji
	docker run -p $(SERVER_PORT):$(SERVER_PORT) chefmoji

ec2-login:
	ssh -i $(PEM_FILE) ec2-user@$(EC2_IP)

