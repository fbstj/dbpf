var DBPF = require('dbpf'), fs = require('fs')

var f = DBPF(fs.readFileSync('../DJEM.dat'))

console.log(f.MAGIC,f.Version,f.UserVersion,f.Flags,f.Created, f.Modified)

var I = f.Index
console.log(I)
console.log(I.Version, I.Count, I.Offset, I.Size)
var f2 = I[0]
console.log(f2.Type, f2.Group, f2.Instance, f2.Offset, f2.Size)
	f2 = I[1]
console.log(f2.Type, f2.Group, f2.Instance, f2.Offset, f2.Size)


