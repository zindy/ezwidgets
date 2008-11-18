%module ezalloc
%{
#define SWIG_FILE_WITH_INIT
#include "ezalloc.h"
%}

%include "numpy.i"

%init %{
    import_array();

    /* initialize the new Python type for memory deallocation */
    _MyDeallocType.tp_new = PyType_GenericNew; 
    if (PyType_Ready(&_MyDeallocType) < 0) 
        return;  
%}


%apply (int** ARGOUTVIEWM_ARRAY1, int *DIM1) {(int** veco1, int* n1)}
%apply (int** ARGOUTVIEW_ARRAY1, int *DIM1) {(int** veco2, int* n2)}

%include "ezalloc.h"

%exception my_alloc1 {
  $action
  /* arg1,arg2,arg3 as in the wrapper (hack alert?) */
  if (*arg3 != arg1)
  {
     PyErr_SetString(PyExc_MemoryError,"Not enough memory");
     return NULL;
  }
}

%exception my_alloc2 {
  $action
  /* arg1,arg2,arg3 as in the wrapper (hack alert?) */
  if (*arg3 != arg1)
  {
     PyErr_SetString(PyExc_MemoryError,"Not enough memory");
     return NULL;
  }
}


%rename (alloc_managed) my_alloc1;

%rename (alloc_leaking) my_alloc2;

%inline %{

void my_alloc1(int ni, int** veco1, int *n1)
{
    /* The function... */
    alloc(ni, veco1, n1);
}

void my_alloc2(int ni, int** veco2, int *n2)
{
    /* The function... */
    alloc(ni, veco2, n2);
}

%}


