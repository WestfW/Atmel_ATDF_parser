# Atmel\_ATDF\_parser
### Python code that parses the XML from an Atmel .ATDF Device Description file, and allows you to find/print various information and relationships that are not present in the .h files.

 ----
# Problem Statement
The usual .h include files provided as part of CMSIS-Atmel do not include information about which pins, or even which ports, support which function, or which peripherals conflict with each other.  For example, the initial justification for this effort was to programmatically figure out what a given pin was doing, based on the PMUX settings.
There's an XML file that is provide in the same device support "pack" called __chipname.atdf__ that provides much more detailed information, but it's relatively unreadable.
The python code here is supposed to provide functions, tools, and examples, for extracting information from the atdf files in friendlier ways.
There are essentially two ways to use these function.  You can run the code in a Python interactive interpreter (ie "Python3 -i som_pinmux.py"), and type in function calls manually, or you can specify commands or some simplified arguments on the command line from your shell.

----
# This is a WORK IN PROGRESS.
## Subject to changes, fixes, breakage, and probably mismatches with this documentation.

----
## Functions provided
Theoretically, "get" functions return python data structures, while "show" functions actually print output.

### findPorts()
Mostly an internal function.  Finds all the Ports defined in the .atdf file.  Returns a string like "AB" if the chip has PortA and PortB.

### readATDF(fn="")
Read the file and do basic input parsing into an XML Tree structure.  (using the Python XML elementtree library, which makes this pretty easy.)  If no filename is provided, it will prompt for one.

### dumpPMUX()
Dumps C data structures that map PortPins to Functions.

~~~
/* start PMUX_D */ 
const char * pads2pmux_D[] = {
/* PA00 */ "", "SERCOM1PAD0",
/* PA01 */ "", "SERCOM1PAD1",
/* PA02 */ "",
/* PA03 */ "",
/* PA04 */ "", "SERCOM0PAD0",
/* PA05 */ "", "SERCOM0PAD1",
/* PA06 */ "", "SERCOM0PAD2",
/* PA07 */ "", "SERCOM0PAD3",
/* PA08 */ "", "SERCOM2PAD1",
/* PA09 */ "", "SERCOM2PAD0",
/* PA10 */ "", "SERCOM2PAD2",
/* PA11 */ "", "SERCOM2PAD3",
/* PA12 */ "", "SERCOM4PAD1",
/* PA13 */ "", "SERCOM4PAD0",
/* PA14 */ "", "SERCOM4PAD2",
(etc)
~~~
(Hmm.  that's not quite correct at the moment.)

### showPortPin(pp)
A "PortPin" is a name like "PB01" or "PA12", which is used all over the datasheets.  This function prints information about what functions are available on that pin.

~~~
showPortPin("PA12")
PA12
  AC: CMP0 pmux:M
  EIC: EXTINT12 pmux:A
  PCC: DEN1 pmux:K
  PORT: P12 pmux:default
  SDHC0: SDCD pmux:I
  SERCOM2: PAD0 pmux:C
  SERCOM4: PAD1 pmux:D
  TC2: WO0 pmux:E
  TCC0: WO6 pmux:F
  TCC1: WO2 pmux:G
~~~
  
### showChipPin(cp)
A "chipPin" in a chip package pin name.  Usually an integer for most packages, but could be something like "C4" for a BGA package.

~~~
showChipPin("12")
Chip Pin 12 on ATSAMD51P20A is PB05
  ADC0: X23 pmux:B
  ADC0: Y23 pmux:B
  ADC1: AIN7 pmux:B
  EIC: EXTINT5 pmux:A
  PORT: P37 pmux:default
~~~
### getAllPins()
Returns a list of all the pins on the chip variant.  (Uses the first package with numeric pin numbers.)

### showAllPins(func)
Runs the Python __func__ specified for each pin on the chip.  For example, showAllPins(print) will simply print all the pin names.

### showInstance(name)
Show information about a pin-occupying peripheral.

~~~
showInstance("DAC")
PA02 DAC VOUT0 pmuxB 
PA05 DAC VOUT1 pmuxB 
~~~
~~~
showInstance("USB")
PA23 USB SOF_1KHZ pmuxH ioset: 1
PA24 USB DM pmuxH 
PA25 USB DP pmuxH 
PB22 USB SOF_1KHZ pmuxH ioset: 2
~~~

### getModules(all=False)
Return a list of peripheral names (as used in showInstance) present on the chip.  With argument __False__, only pin-occupying peripherals are shown, but the list includes all instances of the peripheral.
With argument __True__, all peripherals are listed, but only the top-level name...

~~~
getModules()
['AC',
 'ADC0',
 'ADC1',
 'CCL',
 'DAC',
 'EIC',
 (etc)
~~~

~~~
getModules(True)
['AC',
 'ADC',
 'AES',
 'CCL',
 'CMCC',
 'DAC',
~~~

## Command Line use
Some functions are also available from the shell command line.
The first argument is the .atdf filename.
Additional arguments are interpreted as follows:

1. Argument contains parenthesis.  It will be invoked as python code using __eval()__.  This allows commands like `sam_atdf.py samd21e18a.atdf "dumpPMUX()"`
2. Argument is an integer.  We'll call __showChipPin()__  to display info about that pin.
3. Argument begins with "P".  We call __showPortPin()__.
4. Everything else.  We call __showInstance()__ with an uppercased copy of the argument.  This allows you to type commands like `sam_atdf.py samd21e18a.atdf pcc` without the code trying to look for a PortPin with that name (PortPins have to being with an upper-case "P")

So you can issue a complex command like `sam_atdf.py samd21e18a.atdf 12 15 20 PB00 PA9 sercom1 sercom2`




