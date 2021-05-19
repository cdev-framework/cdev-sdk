## This module contains the code to parse functions out of python files. This will be used to parse the function handlers into individual files
## to help deploy them as individual primitives. This module will hold no state and instead simply parse what is available in a file. It will be
## dependant on other modules to monitor the state of files to determine when an update has occured. This module only provides information about
## what lines correspond to a function and does not handle the actual writing of intermediate files.
