PROJECT_ROOT := $(shell cd ..; pwd)

all: build

build:
	git clone https://github.com/noise/snapstore.git files/snapstore
	JUJU_REPOSITORY=$(PROJECT_ROOT) charm build -l debug


clean:
	$(RM) -rf files/snapstore
	$(RM) -r $(PROJECT_ROOT)/builds/snapstore

deploy:
	juju deploy $(PROJECT_ROOT)/builds/snapstore

.PHONY: all build clean
