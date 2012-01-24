function V(M, m) { return Number(M + '.' + m) }
V.M = function(v){ return Number(String(v).split('.')[0] || 0) }
V.m = function(v){ return Number(String(v).split('.')[1] || 0) }

function map(cb){	// iterates over this, calling cb(key,value)
	for(var i in this)	cb(i, this[i])
}

function DBPF_Header(V, uV, F, C, A, iV, iC, iO, iS, hC, hO, hS){
	this.Version = V || 1.0
	this.UserVersion = uV || 0.0
	this.Flags = F||0; this.Ctime = C||0; this.Atime = A||0
	this.Index = { Version: iV||7.0, Count: iC||0, Offset: iO||0, Size: iS||0 }
	this.Holes = { Count: hC||0, Offset: hO||0, Size: hS||0 }
}
exports.Header = function(){ var o = {}; DBPF_Header.apply(o, arguments); return o }

// bind to a buffer
exports.Header.Load = function(){
	var _ = this
	function W(i){ return _.readUInt32BE(i*4) }
	if (_.toString('ascii',0, 4) != "DBPF")
		throw new TypeError("not a DBPF buffer")

	return new DBPF_Header( V(W(1), W(2)), V(W(3), W(4)), W(5), W(6), W(7),
							V(W(8), W(15)), W(9), W((W(15) == 3)?16:10), W(11),
							W(12), W(13), W(14) );
}
exports.Header.Save = function(h){
	var _ = this
	this.write("DBPF", 0, 4, 'ascii')
	map.bind([
		V.M(h.Version), V.m(h.Version),
		V.M(h.UserVersion), V.m(h.UserVersion), h.Flags, h.Ctime, h.Atime,
		V.M(h.Index.Version), h.Index.Count, h.Index.Offset, h.Index.Size,
		h.Holes.Count, h.Holes.Offset, h.Holes.Size,
		V.m(h.Index.Version), h.Index.Offset
	])(function(i, v){ _.writeUInt32BE(v, 4*(Number(i)+1)) })
}


