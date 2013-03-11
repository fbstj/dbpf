// functions for dealing with DBPF files
#include "dbpf.h"

int DBPF_header(FILE *file, struct dbpf_header *head)
{
int err;
char magic[5];
	// seek to beginning
	err = fseek(file, 0, SEEK_SET);
	if (err) return 0;
	// read header
	err = fread(head, 96, 1, file);
	if (err != 1) return 0;
	// check for magic
	strncpy(magic, head->magic, 4); magic[4] = 0;
	if (strcmp(magic, "DBPF") != 0) return 0;
	// ... more validation?
	return 1;
}

size_t DBPF_index(FILE * file, struct dbpf_header * head, uint32_t ** index)
{
size_t err;
uint32_t *data;
uint32_t width;
	// validate index is a table of words
	if ((head->index_size % sizeof(uint32_t)) != 0) return -1;
	// calculate width
	width = head->index_size / head->index_count;
	// validate width is a record of wrods
	if ((width % sizeof(uint32_t)) != 0)	return -1;
	// validate table has count records
	if ((head->index_count * width) != head->index_size) return -1;
	// allocate some space for the table
	data = (uint32_t *)malloc(head->index_size);
	if (data == NULL) return -1;
	// find the table
	err = fseek(file, head->index_offset, SEEK_SET);
	if (err) return -err;
	// read the table
	err = fread(data, width, head->index_count, file);
	if (ferror(file) != 0) return -err;
	// point the user at the table
	*index = data;
	return width / sizeof(uint32_t);
}

