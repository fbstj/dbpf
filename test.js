var dbpf = require('dbpf'), fs = require('fs')

function test_headers(){
var h = dbpf.Header(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
console.log(h)
var b = new Buffer(96)
console.log(b)
dbpf.Header.Save.call(b, h)
console.log(b)
var H = dbpf.Header.Load.call(b)
console.log(H)
};// test_headers()

function test_file(){
var f = fs.readFileSync('../DJEM.dat')
var h = dbpf.Header.Load.call(f)
console.log(h)

}; test_file()

