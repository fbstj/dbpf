var dbpf = require('dbpf'), fs = require('fs')

function test_headers(){
console.log('#test headers')
var h = dbpf.Header(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
console.log(h)
var b = new Buffer(96)
b.fill(0)
console.log(b)
dbpf.Header.Save.call(b, h)
console.log(b)
var H = dbpf.Header.Load.call(b)
console.log(H)
}; test_headers()

function test_file(){
console.log('#test file')
// load existing DBPF
var f = fs.readFileSync('../DJEM.dat')
// load header
var h = dbpf.Header.Load.call(f)
console.log(h)
// load index
var i = dbpf.Index.Load.call(f, h)
console.log(i)
// create new DBPF
var b = new Buffer(f.length)
b.fill(0)
// save Header
dbpf.Header.Save.call(b, h)
// save Index
dbpf.Index.Save.call(b, h, i)
// save File
fs.writeFileSync('DJEM.dat', b)
console.log('#test save')
// reload file
var f = fs.readFileSync('DJEM.dat')
// load header
var h = dbpf.Header.Load.call(f)
console.log(h)
// load index
var i = dbpf.Index.Load.call(f, h)
console.log(i)
}; test_file()

