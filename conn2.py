import socket
import sys
import time
import argparse
import collections
###
#settings
###

READ_BUFF_SIZE = 65535
#server_address = ('videohub', 9990)

class VHClient():
    def __init__(self, host, port = 9990):
        self.protocol_version = "?"     # Protocol Preamble
        self.device_present = False
        self.model_name = "?"
        self.friendly_name = "?"
        self.unique_id = "?"
        self.video_inputs = 0
        self.video_processing_units = 0
        self.video_outputs = 0
        self.video_monitoring_outputs = 0
        self.serial_ports = 0
        self.input_labels = {}
        self.output_labels = {}
        self.video_output_locks = {}
        self.video_output_routing = {}

        ###
        #socket
        ###

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print host, port
        self.sock.connect((host, port))
        time.sleep(5)
        #print self.data

    def read_info(self):
        self.data = self.sock.recv(READ_BUFF_SIZE)
        message = ""
        #data = sock.recv(READ_BUFF_SIZE)
        message += self.data
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
              self.protocol_version =  current_line.split(': ')[1]
              #print "Protocol =", protocol_version

            if first_line == "VIDEOHUB DEVICE:":
                current_line = first_line
                while (len(line_array) > 0) and current_line != "":
                    current_line = line_array.pop(0)
                    if current_line.startswith("Device present: true"):
                        self.device_present = True
                        print "Device Present =", 	self.device_present
                    if current_line.startswith("Device present: false"):
                        self.device_present = False
                        print "Device Present =", 	self.device_present
                    if current_line.startswith("Model name:"):
                        self.model_name =  current_line.split(': ')[1]
                        print "Model name =", 	self.model_name
                    if current_line.startswith("Friendly name:"):
                        self.friendly_name =  current_line.split(': ')[1]
                        print "Friendly name =", 	self.friendly_name
                    if current_line.startswith("Unique ID:"):
                        self.unique_id =  current_line.split(': ')[1]
                        print "Unique ID =", 	self.unique_id
                    if current_line.startswith("Video inputs:"):
                        self.video_inputs =  current_line.split(': ')[1]
                        print "Video inputs =", 	self.video_inputs
                    if current_line.startswith("Video processing units:"):
                        self.video_processing_units =  current_line.split(': ')[1]
                        print "Video processing units =", 	self.video_processing_units
                    if current_line.startswith("Video outputs:"):
                        self.video_outputs =  current_line.split(': ')[1]
                        print "Video outputs =", 	self.video_outputs
                    if current_line.startswith("Video monitoring outputs:"):
                        self.video_monitoring_outputs =  current_line.split(': ')[1]
                        print "Video monitoring outputs =", 	self.video_monitoring_outputs
                    if current_line.startswith("Serial ports:"):
                        self.serial_ports =  current_line.split(': ')[1]
                        print "Serial ports =", 	self.serial_ports

                ######
            if first_line == "INPUT LABELS:":
                current_line = first_line
                while (len(line_array) > 0) and current_line != "":
                     current_line = line_array.pop(0)
                     input_line = current_line.split(' ',1)
                     if len(input_line) == 2:
                        self.input_labels[ input_line[0]] = input_line[1]
                #print "Input labels =\n", input_labels

            if first_line == "OUTPUT LABELS:":
                current_line = first_line
                while (len(line_array) > 0) and current_line != "":
                    current_line = line_array.pop(0)
                    input_line = current_line.split(' ',1)
                    if len(input_line) == 2:
                        self.output_labels[ input_line[0]] = input_line[1]
                #print "Output labels =\n", output_labels

            if first_line == "VIDEO OUTPUT LOCKS:":
                current_line = first_line
                while (len(line_array) > 0) and current_line != "":
                    current_line = line_array.pop(0)
                    input_line = current_line.split(' ',1)
                    if len(input_line) == 2:
                        self.video_output_locks[ input_line[0]] = input_line[1]
                #print "Video output locks =\n", video_output_locks

            if first_line == "VIDEO OUTPUT ROUTING:":
                current_line = first_line
                while (len(line_array) > 0) and current_line != "":
                    current_line = line_array.pop(0)
                    input_line = current_line.split(' ',1)
                    if len(input_line) == 2:
                        self.video_output_routing[ input_line[0]] = input_line[1]
                #print "video output routing =\n", video_output_routing

    def get_routing(self):
        """ Prints the routing table
        ie, input_label > output_label
        returns: list of tuples
        """
        print "Routing:"
        array = []
        key = lambda x: int(x[0])
        routing_ordered = collections.OrderedDict(sorted(self.video_output_routing.items(), key=key))
        for key in routing_ordered:
            try:
                item = self.video_output_routing[key]
                array.append( ( int(item), self.input_labels[item], self.output_labels[key], int(key) ))
                #print "%3d:%-32.32s>%32.32s:%3d" % ( int(item), self.input_labels[item], self.output_labels[key], int(key) )
            except KeyError, e:
                print 'got a key error %s' %str(e)
                pass
        return array

    def pp_routing(self):
        """ Pretty prints the routing table """
        for tup in self.get_routing():
            print "%3d:%-32.32s>%32.32s:%3d" % ( tup[0], tup[1], tup[2], tup[3] )

    def get_inputs(self):
        """ Gets the inputs
        returns: list of tuples
        """
        print "Inputs:"
        array = []
        key = lambda x: int(x[0])
        inputs_ordered = collections.OrderedDict(sorted(self.input_labels.items(), key=key))
        for key in inputs_ordered:
            array.append( (int(key), self.input_labels[key]))
            #print "%3d:%-32.32s" % ( int(key), self.input_labels[key])
        return array

    def pp_inputs(self):
        """ Pretty prints the inputs """
        for tup in self.get_inputs():
            print "%3d:%-32.32s" % (tup[0], tup[1])

    def get_outputs(self):
        """ Gets the outputs
        returns: list of tuples
        """
        print "Outputs:"
        array = []
        key = lambda x: int(x[0])
        outputs_ordered = collections.OrderedDict(sorted(self.output_labels.items(), key=key))
        for key in outputs_ordered:
            array.append(  ( int(key), self.output_labels[key]))
            #print "%3d:%-32.32s" % ( int(key), self.output_labels[key])
        return array

    def pp_outputs(self):
        """ Pretty prints the inputs """
        for tup in self.get_outputs():
            print "%3d:%-32.32s" % (tup[0], tup[1])

    def add_route(self, route_in, route_out):
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
        for key in self.input_labels:
            if self.input_labels[key] == route_in:
                route_in = key
                print "in key is", route_in
                break
        for key in self.output_labels:
            if self.output_labels[key] == route_out:
                route_out = key
                print "out key is", route_out
                break
        cmd = "VIDEO OUTPUT ROUTING:\n%s %s \n\n" % (str(route_out), str(route_in))
        self.sendall(cmd)


#add_route("Direct TV", "Tech Ops QC 1.1")

#z = VHClient(host="videohub")
#z.read_info()
#print z.pp_routing()
