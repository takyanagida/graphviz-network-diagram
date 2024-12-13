# disable all builtin rules
MAKEFLAGS += --no-builin-rules
.SUFFIXES:

all: bldg1-auto.svg

clean:
	rm bldg1-auto.svg

bldg1-auto.svg: bldg1.gv bldg1-label.json
	neato -Tsvg bldg1.gv > tmp.svg
	../svg_postprocess.py tmp.svg -l bldg1-label.json -a bldg1-background.svg > bldg1-auto.svg
