#include <stdio.h>
#include "inplace.h"

void inplace(double *invec, int n)
{
    int i;

    for (i=0; i<n; i++)
    {
        invec[i] = 2*invec[i];
    }
}


