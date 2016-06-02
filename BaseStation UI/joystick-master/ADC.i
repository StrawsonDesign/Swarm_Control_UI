/* File : ADC.i */
%module ADC

%{
//#define SWIG_FILE_WITH_INIT
/* Includes the header in the wrapper code */
#include "ADC.h"
%}

/* Parse the header file to generate wrappers */
%include "ADC.h"