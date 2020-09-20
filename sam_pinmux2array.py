#
# sam_pinmux2array.py
# August 2020, bu Bill Westfield
#
# the per-device CMSIS-copatible .h files lack information anout
# how port pins (ie PORTA, but 1) map onto the peripherals that
# those pins support.
#
# This program generates arrays that provide that function.

import xml.etree.ElementTree as ET
from collections import OrderedDict

# Find all the ports actually present on this chip.  (Chips with fewer pins
#  have fewer ports.)  Look for pads in any pinout that are ports (begin with
#  "P", so as to exclude power, reset, etc.
def findPorts():
    portsPresent={"A":"", "B":"", "C":"", "D":""}
    pins=ATDFXML.findall(".//*/pinout/pin")
    for pin in pins:
        portname = pin.get("pad")
        if portname[0] == "P": portsPresent[portname[1]] = portname[1]
    return "".join(portsPresent.values())    

# read and parse an ATDF file.  (ATmel Device File)
#  This is XML that theoretically defines all the functions of the chip.
#  The C .h files are supposed to be derived from these.
def readATDF(fn=""):
    global ATDFXML
    if fn == "":
        fn = input("ATDF File for Device: ")
    if fn == "": fn = "samd51.atdf"
    F = open(fn)
    data = F.read()
    ATDFXML = ET.fromstring(data)
    F.close()      

# Dump PMUX arrays, indexed by PORT*32+bit
def dumpPMUX():
    # Handle all 16 possible PINMUX values.  Not all are in use.
    for pinmuxVal in "ABCDEFGHIJKLMNOP":
        # The function="x" attribute occurs as part of a "signal" down in the tree,
        # inside peripherals->module->instance->signals->signal.
        # search for the "function", and then back up to get the module instances.
        pinMuxFunc= ".//*[@function='" + pinmuxVal + "']/../.."
        instances = ATDFXML.findall(pinMuxFunc)
        if instances:
            # initialize an array declartion containing all the possible pins
            # (portA..portD, 32bits per port)
            # This is an "Ordered Dictionary", keyed by portPin (PD03)
            # the "C declaration" stuff is just inserted at appropriate places.
            portPins= OrderedDict()
            portPins["start PMUX_"+pinmuxVal] = "\nconst char * pads2pmux_" + pinmuxVal + "[] = {"

            for port in findPorts():
                for bit in range(0,32):
                    portPins["P"+port+str.zfill(str(bit),2)] = '"",'
                portPins[port+" end"] = "\n"
            
            for instance in instances:
                name=instance.get("name")
                # now, for each instance, find all the signals/pads.
                for s in instance.findall("signals/signal"):        
                    ### print (name, s.get("function"), s.get("pad"))
                    # A given module can have pins for more than one "function"
                    #  (ie SERCOM has both PINMUX=SERCOM and SERCOMALT)
                    #  Only "output" the pad info if function matches.
                    if s.get("function") == pinmuxVal:
                        padName=s.get("group")
                        # Some functions only have a single pad, so no index.
                        if s.get("index"):
                            padName += s.get("index")
                        # add to the string, in case there's more than one
                        #  thing per pinmuxVal (happens for Analog)
                        portPins[s.get("pad")] +=  ' "' + name + padName + '",'
            
            for key, value in portPins.items(): 
                print("/* " + key + " */", value)
            print("};")


#
# Funcions aimed at interactive use, one the tree is parsed.
#

#
# convert an element attribute to a string.
# This is slighly complex becase some elements have indicies (ADC03)
# and some done (DAC)
def e2s(element, attrib, label=""):
    a = element.get(attrib)
    if None == a: return ""
    if (label != ""): a = label + ": " + a
    return a
                
#
# Show all the functions available on a particular port pin (like "PA03")
#
def showPortPin(pp):
    funcs = ATDFXML.findall(".//*[@pad='" + pp + "']/../..")
    for f in funcs:
        for s in f.findall("signals/signal"):  
            if s.get("pad") == pp:
                padName=s.get("group")
                # Some functions only have a single pad, so no index.
                if s.get("index"):
                    padName += s.get("index")
                print("  " + f.get("name") + ": " + padName +
                      " pmux:" + s.get("function"))
#
# Show functions available on a particular chip pin ("position")
# (figure out what "pad" has that position, and call showPortPin on it.)
#
def showChipPin(cp):
    pp = ATDFXML.find(".//*[@position='" + cp + "']").get("pad")
    print("Chip Pin "+cp + " on " +
          ATDFXML.find("devices/device").get("name") + " is "+pp)
    showPortPin(pp)
    
#
# Dump info about ALL the pins on a chip.
# for now, look for a package with numbered pins (NOT a BGA!)
# (pass a function on what to do for each pin name.  Like "print" to just
#  show which pins exist, or "showChipPin" to print all info.)
#
def showAllPins(x):
    aPinout = ATDFXML.find(".//*/pinout/pin/[@position='1']/..")
    allpins = aPinout.findall("pin")
    for p in [x.get("position") for x in allpins]:
        x(p)
        
#
# Show the pads that implement a particular peripheral ("instance")
#
def showInstance(name):
    instance = ATDFXML.find(".//*/instance/[@name='" + name + "']")
    signals = instance.findall("signals/signal")
#    if None != instance.find(".//*[@ioset]"):
    signals = sorted(signals, key=lambda x:x.get("pad"))
    for s in signals:        
        padName=s.get("group")
        # Some functions only have a single pad, so no index.
        padName += e2s(s, "index")
        print(s.get("pad"), name, padName, "pmux" +
              s.get("function"), e2s(s, "ioset", "ioset"))
        
        
# Stuff to execute right away

readATDF()

