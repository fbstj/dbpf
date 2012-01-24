function V(M, m) { return Number(M + '.' + m) }
V.M = function(v){ return Number(String(v).split('.')[0] || 0) }
V.m = function(v){ return Number(String(v).split('.')[1] || 0) }

function map(cb){	// iterates over this, calling cb(key,value)
	for(var i in this)	cb(i, this[i])
}

var word = {
	R: function(i, o){ return this.readUInt32LE(Number(i)*4+(o||0)) },
	W: function(i, v, o){ this.writeUInt32LE(v, Number(i)*4+(o||0)) },
}

function DBPF_Header(V, uV, F, C, A, iV, iC, iO, iS, hC, hO, hS){
	this.Version = V || 1.0
	this.UserVersion = uV || 0.0
	this.Flags = F||0; this.Ctime = C||0; this.Atime = A||0
	this.Index = { Version: iV||7.0, Count: iC||0, Offset: iO||0, Size: iS||0 }
	this.Holes = { Count: hC||0, Offset: hO||0, Size: hS||0 }
}
exports.Header=function(){var o={};DBPF_Header.apply(o,arguments);return o}

// bind to a buffer
exports.Header.Load = function(){
var _ = this.slice(0, 96), W = []
	if (_.toString('ascii',0, 4) != "DBPF")
		throw new TypeError("not a DBPF buffer")
	for(var i = 0; i < 17; i++)
		W.push(word.R.call(_, i))
	return new DBPF_Header( V(W[1], W[2]), V(W[3], W[4]), W[5], W[6], W[7],
							V(W[8], W[15]), W[9], W[(W[15] == 3)?16:10], W[11],
							W[12], W[13], W[14] );
}
exports.Header.Save = function(h){
var _ = this.slice(0, 96)
	_.fill(0)
	_.write("DBPF", 0, 4, 'ascii')
	map.call([
		V.M(h.Version), V.m(h.Version),
		V.M(h.UserVersion), V.m(h.UserVersion), h.Flags, h.Ctime, h.Atime,
		V.M(h.Index.Version), h.Index.Count, h.Index.Offset, h.Index.Size,
		h.Holes.Count, h.Holes.Offset, h.Holes.Size,
		V.m(h.Index.Version), h.Index.Offset
	], function(i, v){ word.W.call(_, Number(i)+1, v) })
}

exports.Index = function(){}

function I_meta(h){
	return { C: h.Index.Count, O: h.Index.Offset, S: h.Index.Size,
		get W(){ return this.S/this.C/4 },
	}
}
function I_record(){
	return { 
		Type: Number(this.shift()) || 0,
		Group: Number(this.shift()) || 0,
		Instance: Number(this.shift()) || 0,

		Size: Number(this.pop()) || 0,
		Offset: Number(this.pop()) || 0,
	}
}

exports.Index.Load = function(h){ var H = I_meta(h)
var i = [], _ = this.slice(H.O), W = word.R.bind(_)
	for(var j = 0; j < H.C; j++)
	{
		var a = []
		for(var k = 0; k < H.W; k++)
			a.push(W(j * H.W + k))
		i.push(I_record.call(a))
	}
	return i
}
exports.Index.Save = function(h, i){ var H = I_meta(h)
var _ = this.slice(H.O), W = word.W.bind(_)
	map.call(i, function(k, v){
		var j = Number(k)*H.W
		console.log((j+5)*4)
		W(j + 0, v.Type)
		W(j + 1, v.Group)
		W(j + 2, v.Instance)
		W(j + 3, v.Size)
		W(j + 4, v.Offset)
	})
}

exports.File = function(i){ return this.slice(i.Offset, i.Offset+i.Size) }
