#include <stdio.h>

#define lowerc(c) lowervec[(char)(c)]

unsigned char lowervec[1000 + 1] = {};

int stringsearch(int patlen, int skip2, char *pattern)
{
  char *pat = (char *)pattern;
  int i = 0;
#pragma cgra acc
  for (i = 0; i < patlen - 1; ++i)
  {
    if (lowerc(pat[i]) == lowerc(pat[patlen - 1]))
      skip2 = patlen - i - 1;
  }
  return skip2;
}

int main()
{

  char p[20];
  // TODO: add proper arguments
  stringsearch(20, 2, p);
}