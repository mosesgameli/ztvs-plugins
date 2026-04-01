VERSION ?= dev
BIN_EXT ?=
LDFLAGS = -s -w

PLUGINS = plugin-os plugin-axios-mitigation

.PHONY: build clean $(PLUGINS)

build: $(PLUGINS)

$(PLUGINS):
	go build -C $@ -ldflags="$(LDFLAGS)" -o $@$(BIN_EXT) ./cmd

clean:
	for p in $(PLUGINS); do rm -f $$p/$$p; done
