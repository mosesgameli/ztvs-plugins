VERSION ?= dev
BIN_EXT ?=
LDFLAGS = -s -w

.PHONY: build clean

PLUGINS = plugin-os plugin-axios-mitigation

build: $(PLUGINS)

$(PLUGINS):
	go build -C $@ -ldflags="$(LDFLAGS)" -o $@$(BIN_EXT) .

clean:
	for p in $(PLUGINS); do rm -f $$p/$$p; done
