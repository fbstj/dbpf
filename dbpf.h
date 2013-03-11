/*
	DBPF functions
*/
#ifndef __DBPF_H
#define __DBPF_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct dbpf_header {
	char magic[4];
	uint32_t
		version_major, version_minor,
		user_version_major, user_version_minor,
		flags, ctime, atime,
		index_version_major,
		index_count, index_offset, index_size,
		holes_count, holes_offest, holes_size,
		index_version_minor, index_offest_v2;
	uint8_t reserved[28];
};

struct dbpf_index_v70 { uint32_t tid, gid, iid, offset, size; };
struct dbpf_index_v71 { uint32_t tid, gid, iid, eiid, offset, size; };

// 
extern int DBPF_header(FILE *, struct dbpf_header *);
// parse the index into the third parameter, return the size of allocated buffer
extern size_t DBPF_index(FILE *, struct dbpf_header *, uint32_t **);

#endif // __DBPF_H

