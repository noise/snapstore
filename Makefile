ENV = env

snap: ## Snap it up
	snapcraft clean snapstore
	snapcraft snap

$(ENV):
	virtualenv $(ENV)

deps: env ## install dependencies
	$(ENV)/bin/pip install -q -r requirements.txt

lint: env ## flake8 the source
	$(ENV)/bin/flake8 store.py --max-line-length=99

clean: ## tidy up the house
	rm snapstore-example*.snap
	snapcraft clean
	rm -r $(ENV)

run: env deps
	$(ENV)/bin/python store.py

help:
	@grep -P '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: all deps lint clean snap help
