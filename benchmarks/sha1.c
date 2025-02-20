#include <stdio.h>

void sha_trans(int S[])
{
#pragma cgra acc
	for (int i = 16; i < 80; i++)
		S[i] = S[i - 3] ^ S[i - 8] ^ S[i - 14] ^ S[i - 16];
}

int main()
{
	int S[80];
	sha_trans(S);
}