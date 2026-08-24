GRF     = njtransit.grf
SRC     = njtransit.pnml
SPRITES = $(wildcard sprites/*.png)

all: sprites nml $(GRF) roster

sprites: gen_sprites.py historic.py buses.py fleet.py
	python3 gen_sprites.py

nml: gen_nml.py fleet.py
	python3 gen_nml.py

$(GRF): $(SRC) lang/english.lng $(SPRITES)
	nmlc --grf $(GRF) $(SRC)

roster: make_roster.py fleet.py
	python3 make_roster.py

pages: make_pages.py fleet.py
	python3 make_pages.py

clean:
	rm -f $(GRF)

.PHONY: all sprites nml roster pages clean
