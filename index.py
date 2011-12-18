import struct
import json
from sys import argv, stdin

err = dict()

fn = argv[1]
f = open(fn, 'rb')

h = json.loads(argv[2] if len(argv) > 2 else stdin.read())
i = h['index']

oo = list()

for i in range(0, i['count']):
	print i