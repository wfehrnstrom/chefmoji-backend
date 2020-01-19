INSTALL_SCRIPTS_DIR=scripts

install:
	pip install virtualenvwrapper
	./$(INSTALL_SCRIPTS_DIR)/setupvenvwrapper
	source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv chefmoji-backend; setvirtualenvproject $$VIRTUAL_ENV $(pwd)
	./$(INSTALL_SCRIPTS_DIR)/installprotoc


