# console-colors.mk

# Color definitions for highlighting console output.
# These definitions work on MacOS and Linux, zsh and bourne/dash shells.
# Adapted from https://stackoverflow.com/a/53528374
# Posted by Robert Ranjan
# Retrieved 2026-05-18, License - CC BY-SA 4.0
# TIP: Run `make show-colors` (This target is at the end of this file.)
RED=$(shell tput setaf 1)
GREEN=$(shell tput setaf 2)
ORANGE=$(shell tput setaf 3)
BLUE=$(shell tput setaf 4)
PINK=$(shell tput setaf 5)
DARK_GREEN=$(shell tput setaf 6)
LIGHT_GREY=$(shell tput setaf 7)
BLACK=$(shell tput setaf 8)
# virtually identical to RED:
RED2=$(shell tput setaf 9)
BOLD=$(shell tput smso)
OFFBOLD=$(shell tput rmso)
_END=$(shell tput sgr0; tput rmso)

# Note the definitions with labels, like "ERROR:" have a trailing white space 
# which both separate the label from the messages when used and also have the labels
# line up equally! Use "make show-colors" to see this.
ERROR        = ${BOLD}${RED}ERROR:   
WARN         = ${ORANGE}WARNING: 
WARNING      = ${ORANGE}WARNING: 
NOTE         = ${GREEN}NOTE:    
INFO         = ${DARK_GREEN}INFO:    
TIP          = ${BOLD}${PINK}TIP:     
HIGHLIGHT    = ${BOLD}${BLUE}

# "Labels" for when you just want to, e.g., "ERROR:" colored, but the rest of the line should be "normal".
# No "${_END}" has to be provided when these labels are used.
ERROR_LABEL     = ${BOLD}${RED}ERROR:${_END}   
WARN_LABEL      = ${BOLD}${ORANGE}WARNING:${_END} 
WARNING_LABEL   = ${BOLD}${ORANGE}WARNING:${_END} 
NOTE_LABEL      = ${BOLD}${GREEN}NOTE:${_END}    
INFO_LABEL      = ${BOLD}${DARK_GREEN}INFO:${_END}    
TIP_LABEL       = ${BOLD}${PINK}TIP:${_END}     

# For "special" strings in output:
CODE            = ${PINK}

.PHONY: show-colors

# Use this target to see the colors defined above.
show-colors::
	$(info This is how the color and message definition look using $$(info ...) and related output functions:)
	$(info This is <${RED}RED${_END}>)
	$(info This is <${RED2}RED2${_END}>)
	$(info This is <${GREEN}GREEN${_END}>)
	$(info This is <${ORANGE}ORANGE${_END}>)
	$(info This is <${BLUE}BLUE${_END}>)
	$(info This is <${PINK}PINK${_END}>)
	$(info This is <${DARK_GREEN}DARK_GREEN${_END}>)
	$(info This is <${LIGHT_GREY}LIGHT_GREY${_END}>)
	$(info This is <${BLACK}BLACK${_END}>)
	$(info This is <${BOLD}${BLACK}BOLD and BLACK${_END}>)
	$(info )
	$(info This is an ERROR:     ${ERROR}Oooops! ${_END})
	$(info This is a  WARN:      ${WARN}Careful! ${_END})
	$(info This is a  WARNING:   ${WARNING}Careful! ${_END})
	$(info This is a  NOTE:      ${NOTE}Of note... ${_END})
	$(info This is an INFO:      ${INFO}It's useful to know ${_END})
	$(info This is a  TIP:       ${TIP}This can help... ${_END})
	$(info This is a  HIGHLIGHT: ${HIGHLIGHT}/foo/bar/baz ${_END})
	$(info )
	$(info This is an ERROR_LABEL:     ${ERROR_LABEL}Oooops!)
	$(info This is a  WARN_LABEL:      ${WARN_LABEL}Careful!)
	$(info This is a  WARNING_LABEL:   ${WARNING_LABEL}Careful!)
	$(info This is a  NOTE_LABEL:      ${NOTE_LABEL}Of note...)
	$(info This is an INFO_LABEL:      ${INFO_LABEL}It's useful to know)
	$(info This is a  TIP_LABEL:       ${TIP_LABEL}This can help...)
	$(info "(There isn't a 'HIGHLIGHT_LABEL', because it would be empty!)")
	@echo  # using echo suppresses "nothing to be done ..." messages.
