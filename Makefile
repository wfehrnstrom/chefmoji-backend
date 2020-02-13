INSTALL_SCRIPTS_DIR=scripts

include .env

install:
	# TODO: error out on python3 not being installed!
	pip3 install virtualenvwrapper
	./$(INSTALL_SCRIPTS_DIR)/setupvenvwrapper
	source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv chefmoji-backend; setvirtualenvproject $$VIRTUAL_ENV $(pwd)
	./$(INSTALL_SCRIPTS_DIR)/installprotoc
	pip3 install -r src/requirements.txt
	export FLASK_APP=src/app.py

dev:
	export FLASK_ENV=development && python3 -m flask run

prod:
	docker build . -t chefmoji
	docker run -p $(SERVER_PORT):$(SERVER_PORT) chefmoji

clean:
	rm -r *.pyc

ec2-login:
	ssh -i $(PEM_FILE) ec2-user@$(EC2_IP)

