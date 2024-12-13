#!/usr/bin/env python3

from xml.dom import minidom
import json
import argparse
import sys
import logging
import datetime

label_to_enlarge = ['≈']

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('input', type=argparse.FileType(), nargs='?', default=sys.stdin)
parser.add_argument('-l', type=argparse.FileType(), dest='label_file', default=None,
                    help='label.json file to translate labels.')
parser.add_argument('-a', action='append', type=argparse.FileType(), dest='layer_svg',
                    help='layer.svg file to append (multiple -a can be specified).')
args = parser.parse_args()
input_dom = minidom.parse(args.input)
label_translation = None
layer_dom_array = None
if args.label_file:
    label_translation = json.load(args.label_file)
if args.layer_svg:
    layer_dom_array = list()
    for a_file in args.layer_svg:
        layer_dom_array.append(minidom.parse(a_file))

# label translation
for elem in input_dom.getElementsByTagName('*'):
    if elem.getAttribute('id') == 'graph0':
        graph0 = elem
        break
translated_labels_g = graph0.appendChild(input_dom.createElement('g'))
translated_labels_g.setAttribute('id', 'translated-labels')
translated_labels_g.setAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'inkscape:groupmode', 'layer')
enlarged_labels_g = graph0.appendChild(input_dom.createElement('g'))
enlarged_labels_g.setAttribute('id', 'enlarged-labels')
enlarged_labels_g.setAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'inkscape:groupmode', 'layer')
unchanged_labels_g = graph0.appendChild(input_dom.createElement('g'))
unchanged_labels_g.setAttribute('id', 'unchanged-labels')
unchanged_labels_g.setAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'inkscape:groupmode', 'layer')

def translate_labels():
    for text_elem in input_dom.getElementsByTagName('text'):
        for text_node in text_elem.childNodes:
            if text_node.data in label_translation:
                text_elem.setAttribute('id', text_node.data)
                text_node.replaceWholeText(label_translation[text_node.data])
                translated_labels_g.appendChild(text_elem)
            else:
                logging.warning('translate: ' + text_node.data)
                unchanged_labels_g.appendChild(text_elem)
            if text_node.data in label_to_enlarge:
                text_elem.setAttribute(
                    'font-size',
                    str(float(text_elem.getAttribute('font-size')) * 1.5)
                )
                enlarged_labels_g.appendChild(text_elem)

if label_translation:
    translate_labels()

# append layers
append_location = input_dom.getElementsByTagName('svg')[0]
def append_layers():
    for layer_dom in layer_dom_array:
        for svg_elem in layer_dom.getElementsByTagName('svg'):
            for direct_child_node in svg_elem.childNodes:
                if direct_child_node.nodeName == 'g':
                    node_to_be_appended = direct_child_node.cloneNode(True)
                    append_location.appendChild(node_to_be_appended)

if layer_dom_array:
    append_layers()

# append timestamp
append_location.appendChild(
    minidom.parseString(
        '<g id="timestamp"><text><tspan>Composited: {0}</tspan><tspan x="0" dy="1.2em">Edited: N/A</tspan></text></g>'.
        format(datetime.datetime.now().isoformat(sep=' ',timespec='seconds'))
    ).documentElement
)

# hide background square
for elem in input_dom.getElementsByTagName('polygon'):
    if elem.getAttribute('stroke') == 'transparent':
        elem.setAttribute('style', 'display: none')

# output
input_dom.writexml(sys.stdout)
