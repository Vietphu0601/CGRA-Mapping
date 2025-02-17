#include <stdio.h>
#include <math.h>

int bit_count(long x)
{
  int n = 0;
  if (x == 0)
  {
    return 0;
  }
#pragma cgra acc
  do
  {
    n++;
  } while (0 != (x = x & (x - 1)));

  return (n);
}

int main()
{

  int a = 6789;

  int res = bit_count(a);

  printf("%d", res);
  return 0;
}
