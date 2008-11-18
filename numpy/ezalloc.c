#include <stdio.h>
#include "ezalloc.h"

void alloc(int ni, int** veco, int *n)
{
    int *temp;
    temp = (int *)malloc(ni*sizeof(int));

    if (temp == NULL)
    {
        *n = 0;
    }
    else
    {
        *n = ni;
    }

    *veco = temp;
}

