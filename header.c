#include "dbpf.h"
#include <stdio.h>
#include <string.h>

FILE *fp;

int is_dbpf(FILE *fp);

int main(int argc, char *args[])
{
	fp = fopen( "../zz_Maxis_DJEM.dat", "r" );
	if(!fp)
	{
		puts ("cannot open file");
		return -1;
	}
	if(!is_dbpf(fp))
	{
		puts("not a DBPF file");
		return -1;
	}
	unsigned int head[17];
	fseek(fp, 4, SEEK_SET);
	fread(head, 4, 17, fp);

	return 0;
}

int is_dbpf(FILE *fp)
{
	int err;
	long tell = ftell(fp);
	char magic[5];

	err = fseek(fp, 0, SEEK_SET);
	if(err) return 0;

	err = fread(magic, 4, 1, fp);
	if(err != 1) return 0;
	magic[4] = 0;
	
	err = fseek(fp, tell, SEEK_SET);
	if(err)	return 0; //die?

	return !strcmp(magic, "DBPF");
}