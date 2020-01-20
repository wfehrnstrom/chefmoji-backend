INSTALL_SCRIPTS_DIR=scripts
SERVER_PORT=5000


install:
	pip install virtualenvwrapper
	./$(INSTALL_SCRIPTS_DIR)/setupvenvwrapper
	source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv chefmoji-backend; setvirtualenvproject $$VIRTUAL_ENV $(pwd)
	./$(INSTALL_SCRIPTS_DIR)/installprotoc
	pip install -r src/requirements.txt
	export FLASK_APP=src/app.py

dev:
	export FLASK_ENV=development && python -m flask run

prod:
	docker build . -t chefmoji
	docker run -p $(SERVER_PORT):$(SERVER_PORT) chefmoji

clean:
	rm -r *.pyc