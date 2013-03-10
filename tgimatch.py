from dbpf import DBPF, ID

def parse(line=""):
	l,c,r = line.partition('T')
	if c != 'T':
		return None
	l,c,r = r.partition('G')
	if c != 'G':
		return None
	T = ID(l)
	l,c,r = r.partition('I')
	if c != 'I':
		return None
	G = ID(l)
	l,c,r = r.partition(';')
	I = ID(l)
	return T,G,I

def parser(fname):
	lines = open(sys.argv[2])
	for l in lines.readlines():
		tgi = parse(l)
		if tgi is None:
			continue
		yield tgi

def search(db, fname):
	if not isinstance(db, DBPF):
		raise Exception("pass a dbpf file")
	for tgi in parser(fname):
		res = db.search(*tgi)
		if len(res) == 0:
			continue
		if len(res) > 1:
			raise Exception("multiple records found")
		yield res[0]

if __name__ == '__main__':
	import sys
	db = DBPF(sys.argv[1])
	for r in search(db, sys.argv[2]):
		print "T{:08x}G{:08x}I{:08x}".format(*r[:3]), len(r[3])
