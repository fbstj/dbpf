#include "dbpf.h"

int main(int argc, char *args[])
{
FILE * fp = fopen( args[1], "r" );
struct dbpf_header head;
size_t ind_width;
struct dbpf_index_v70 *index;
	if(!fp)
	{
		puts ("cannot open file");
		return -1;
	}
	if (DBPF_header(fp, &head) != 1)
	{
		puts ("header read failed");
		return -1;
	}
	ind_width = DBPF_index(fp, &head, (uint32_t **)&(index));
	if (ind_width < 1)
	{
		puts ("index read failed");
		return -1;
	}
	{
	int i;
	for (i = 0; i < head.index_count; i++)
	{
		printf("T%08xG%08xI%08x %i %i\n",
				index[i].tid, index[i].gid, index[i].iid,
				index[i].offset, index[i].size);
	}
	}
	
	free(index);

	return 0;
}

