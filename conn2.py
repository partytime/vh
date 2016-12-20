import socket
import sys
import time
import argparse
import collections
###
#settings
###

protocol_version = "?"     # Protocol Preamble
device_present = False
model_name = "?"
friendly_name = "?"
unique_id = "?"
video_inputs = 0
video_processing_units = 0
video_outputs = 0
video_monitoring_outputs = 0
serial_ports = 0
input_labels = {}
output_labels = {}
video_output_locks = {}
video_output_routing = {}
READ_BUFF_SIZE = 65535

###
#socket
###

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('videohub', 9990)
message = ""
sock.connect(server_address)
time.sleep(5)
data = sock.recv(READ_BUFF_SIZE)
message += data
#if (len(str) < READ_BUFF_SIZE):
#   break
#print message
line_array = message.split('\n')
#print line_array
while(len(line_array) > 0):
    first_line = line_array.pop(0)
    #print first_line
    #print "This is a ", first_line, " message"
    if first_line == "PROTOCOL PREAMBLE:":
        if len(line_array) == 0:
            break
        current_line = line_array.pop(0)
    #print 'current line is', current_line
    if current_line.startswith("Version:"):
      protocol_version =  current_line.split(': ')[1]
      #print "Protocol =", protocol_version

    if first_line == "VIDEOHUB DEVICE:":
        current_line = first_line
        while (len(line_array) > 0) and current_line != "":
            current_line = line_array.pop(0)
            if current_line.startswith("Device present: true"):
            	device_present = True
            	print "Device Present =", 	device_present
            if current_line.startswith("Device present: false"):
            	device_present = False
            	print "Device Present =", 	device_present
            if current_line.startswith("Model name:"):
            	model_name =  current_line.split(': ')[1]
            	print "Model name =", 	model_name
            if current_line.startswith("Friendly name:"):
            	friendly_name =  current_line.split(': ')[1]
            	print "Friendly name =", 	friendly_name
            if current_line.startswith("Unique ID:"):
            	unique_id =  current_line.split(': ')[1]
            	print "Unique ID =", 	unique_id
            if current_line.startswith("Video inputs:"):
            	video_inputs =  current_line.split(': ')[1]
            	print "Video inputs =", 	video_inputs
            if current_line.startswith("Video processing units:"):
            	video_processing_units =  current_line.split(': ')[1]
            	print "Video processing units =", 	video_processing_units
            if current_line.startswith("Video outputs:"):
            	video_outputs =  current_line.split(': ')[1]
            	print "Video outputs =", 	video_outputs
            if current_line.startswith("Video monitoring outputs:"):
            	video_monitoring_outputs =  current_line.split(': ')[1]
            	print "Video monitoring outputs =", 	video_monitoring_outputs
            if current_line.startswith("Serial ports:"):
            	serial_ports =  current_line.split(': ')[1]
            	print "Serial ports =", 	serial_ports

        ######
    if first_line == "INPUT LABELS:":
        current_line = first_line
        while (len(line_array) > 0) and current_line != "":
             current_line = line_array.pop(0)
             input_line = current_line.split(' ',1)
             if len(input_line) == 2:
                input_labels[ input_line[0]] = input_line[1]
        #print "Input labels =\n", input_labels

    if first_line == "OUTPUT LABELS:":
        current_line = first_line
        while (len(line_array) > 0) and current_line != "":
            current_line = line_array.pop(0)
            input_line = current_line.split(' ',1)
            if len(input_line) == 2:
                output_labels[ input_line[0]] = input_line[1]
        #print "Output labels =\n", output_labels

    if first_line == "VIDEO OUTPUT LOCKS:":
        current_line = first_line
        while (len(line_array) > 0) and current_line != "":
            current_line = line_array.pop(0)
            input_line = current_line.split(' ',1)
            if len(input_line) == 2:
                video_output_locks[ input_line[0]] = input_line[1]
        #print "Video output locks =\n", video_output_locks

    if first_line == "VIDEO OUTPUT ROUTING:":
        current_line = first_line
        while (len(line_array) > 0) and current_line != "":
            current_line = line_array.pop(0)
            input_line = current_line.split(' ',1)
            if len(input_line) == 2:
                video_output_routing[ input_line[0]] = input_line[1]
        #print "video output routing =\n", video_output_routing

def print_routing():
    print "Routing:"
    key = lambda x: int(x[0])
    routing_ordered = collections.OrderedDict(sorted(video_output_routing.items(), key=key))
    for key in routing_ordered:
        try:
            item = video_output_routing[key]
            print "%3d:%-32.32s>%32.32s:%3d" % ( int(item), input_labels[item], output_labels[key], int(key) )
        except KeyError, e:
            print 'got a key error %s' %str(e)
            pass

def print_inputs():
    print "Inputs:"
    key = lambda x: int(x[0])
    inputs_ordered = collections.OrderedDict(sorted(input_labels.items(), key=key))
    for key in inputs_ordered:
        print "%3d:%-32.32s" % ( int(key), input_labels[key])

def print_outputs():
    print "Outputs:"
    key = lambda x: int(x[0])
    outputs_ordered = collections.OrderedDict(sorted(output_labels.items(), key=key))
    for key in outputs_ordered:
        print "%3d:%-32.32s" % ( int(key), output_labels[key])

def add_route(route_in, route_out):
    route_in = str(route_in)
    route_out = str(route_out)
    #TODO: check that in and out exist
    #if route_in not in input_labels:
    #    print "There is no input:%s" % route_in
    #    return False
    #if route_out not in output_labels:
    #    print "There is no output:%s" % route_out
    #    return False
    print "routing %s to %s" %(route_in, route_out)
    print "in is", route_in
    print "out is", route_out
    print type(route_in)
    for key in input_labels:
        if input_labels[key] == route_in:
            route_in = key
            print "in key is", route_in
            break
    for key in output_labels:
        if output_labels[key] == route_out:
            route_out = key
            print "out key is", route_out
            break
    cmd = "VIDEO OUTPUT ROUTING:\n%s %s \n\n" % (str(route_out), str(route_in))
    sock.sendall(cmd)
print_routing()
#print_outputs()

add_route("Direct TV", "Tech Ops QC 1.1")

