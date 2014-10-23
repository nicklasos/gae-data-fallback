all:
    dev_appserver.py .
install:
	pip install -r requirements.txt -t lib
deploy:
	pip install -r requirements.txt -t lib
