/*
	DBPF parsing library
	require('dbpf')(buf) returns a Buffer object
	that has fields corresponding to different parts of the buffer
	including an array of Buffers containing the files in the DBPF
*/

function A(to, name, get, set, props){
var p = props || {}
	p['get'] = get; p['set'] = set
	delete p['value']; delete p['writable'];
	Object.defineProperty(to, name, p)
}

function V(M, m) { return Number(M + '.' + m) }
V.M = function(v){ return Number(String(v).split('.')[0] || 0) }
V.m = function(v){ return Number(String(v).split('.')[1] || 0) }

var word = {
	R: function(i, o){ return this.readUInt32LE(Number(i)*4+(o||0)) },
	W: function(i, v, o){ this.writeUInt32LE(v, Number(i)*4+(o||0)) },
}

function gs_W(on, With, name, i, o){ o = o||0
	A(on, name,
		function(){
			return word.R.call(With, i, o)
		},
		function(v){
			word.W.call(With, i, v, o)
		})
}
function gs_V(on, With, name, M, m){
	A(on, name,
		function(){
			return V(word.R.call(With, M), word.R.call(With, m))
		},
		function(v){
			word.W.call(With, M, V.M(v))
			word.W.call(With, m, V.m(v))
		})
}
function get_Index(){
var R = word.R.bind(this), W = word.W.bind(this)	// utilities
var I = Array(R(9))	// the Index object
	gs_V(I, this, 'Version', 8, 15)
	gs_W(I, this, 'Count', 9)
	function _O(){ return (R(15) == 3)?16:10 }
	A(I, 'Offset', function(){ return R(_O()) }, function(v){ W(_O(), v) })
	gs_W(I, this, 'Size', 11)
	return I
}

function get_File(r){
var I = this.Index, R = word.R.bind(this), W = word.W.bind(this)
var F = {}
function gs(name, i){
var o = I.Offset + (I.Size/I.Count) * r
	A(F, name, function(){ return R(i, o) }, function(v){ W(i, v, o) })
}
	gs('Type', 0); gs('Group', 1); gs('Instance', 2)
	gs('Offset', 3); gs('Size', 4)
	F = this.slice(F.Offset, F.Offset + F.Size)
	gs('Type', 0); gs('Group', 1); gs('Instance', 2)
	gs('Offset', 3); gs('Size', 4)	
//	A(F, 'TGI', function(){ return [this.Type, this.Group, this.Instance] })
	return F
}

function DBPF(){
	A(this, 'MAGIC', function(){ return this.toString('ascii',0, 4) })
	if(this.MAGIC != "DBPF")	// assert DBPF magic
		throw new TypeError("not a DBPF buffer")
	// load header into this.{Version,UserVersion,Flags,Created,Modified}
	gs_V(this, this, 'Version', 1, 2)
	gs_V(this, this, 'UserVersion', 3, 4)
	gs_W(this, this, 'Flags', 5);
	gs_W(this, this, 'Created', 6); gs_W(this, this, 'Modified', 7)
	// load index table into this.Index
	var I = this.Index = get_Index.call(this)
	for(var i = 0; i < I.Count; i++)
		I[i] = get_File.call(this, i)
}

DBPF.Make = function(){}

module.exports = function(b){ var _ = new Buffer(b); DBPF.call(_); return _ }

