#!/usr/bin/env python

import sys
import re
from xml.dom import minidom
from xml.parsers.expat import ExpatError

CHECKSTYLE_VERSION = '5.0'

if __name__ == "__main__":

    # If "--verbose" or "-v" is passed, set verbose to True
    verbose = True if '--verbose' in sys.argv or '-v' in sys.argv else False

    # Get the index of "--input|-i" in argv
    input_index = [i for i, arg in enumerate(sys.argv) if re.match('--input|-i', arg)]

    if len(input_index) == 0:
        print("No input file specified")
        sys.exit(1)

    # Get the index of "--output|-o" in argv
    output_index = [i for i, arg in enumerate(sys.argv) if re.match('--output|-o', arg)]

    if len(output_index) == 0:
        print("No output file specified")
        sys.exit(1)

    input_file = sys.argv[input_index[0] + 1]
    output_file = sys.argv[output_index[0] + 1]
    if verbose:
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
    # Open the input file
    try:
        input_file = open(input_file, 'r')
        input_xml = minidom.parse(input_file)
        input_file.close()
    except IOError:
        print("Cannot open input file")
        sys.exit(1)
    except ExpatError:
        print("Invalid XML file as input")
        sys.exit(1)

    # Open the output file
    try:
        output_file = open(output_file, 'w')
    except IOError:
        print("Cannot create output file")
        sys.exit(1)

    impl = minidom.getDOMImplementation()
    output_xml = impl.createDocument(None, "checkstyle", None)
    errors = input_xml.getElementsByTagName('testcase')
    top_element = output_xml.documentElement
    top_element.setAttribute("version", "9.3")
    files = {}
    for e in errors:
        filename = e.getAttribute('classname')
        if filename in files.keys():
            element = files[filename]
        else:
            element = output_xml.createElement('file')
            element.setAttribute('name', filename)
            top_element.appendChild(element)
            files[filename] = element
        try:
            in_error = e.getElementsByTagName('failure')[0]
        except IndexError:
            continue

        f, line, column, message = in_error.getAttribute('message').split(':')
        type = in_error.getAttribute('type')
        out_error = output_xml.createElement("error")
        out_error.setAttribute('line', line)
        out_error.setAttribute('column', column)
        if type[0] == "E":  # check if there is an error or a warning
            severity = "error"
        else:
            severity = "warning"
        out_error.setAttribute('severity', severity)
        out_error.setAttribute('message', message)
        out_error.setAttribute('source', "lua.rules.%s" % type)

        element.appendChild(out_error)
    output_file.write(output_xml.toprettyxml(encoding='utf-8'))
    output_file.close()
