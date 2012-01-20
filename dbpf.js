
function DBPF_Header(){
	this.Version = 1.0
	this.UserVersion = 0.0
	this.Flags = 0; this.Ctime = 0; this.Atime = 0
	this.Index = { Version: 7.0, Count: 0, Offset: 0, Size: 0 }
	this.Holes = { Count: 0, Offset: 0, Size: 0 }
}

DBPF_Header.prototype = {
	serialize: function()
	{	// serializes this into a 96 byte ArrayBuffer
		var M = function(v){ return Number(String(v).split('.')[0] || 0) },
			m = function(v){ return Number(String(v).split('.')[1] || 0) }, 
			buf = new Buffer(96), i = 0,
			word = function(v){ buf.writeUInt32BE(v, 4*i++) }
		buf.write("DBPF", 0, 4*i++, 'ascii')
		word(M(this.Version)); word(m(this.Version))
		word(M(this.UserVersion)); word(m(this.UserVersion))
		word(this.Flags); word(this.Ctime); word(this.Atime)
		word(M(this.Index.Version))
		word(this.Index.Count); word(this.Index.Offset); word(this.Index.Size)
		word(this.Holes.Count); word(this.Holes.Offset); word(this.Holes.Size)
		word(m(this.Index.Version))
		word(this.Index.Offset)
		return buf
	},
	deserialize: function(buf)
	{	// deserializes an ArrayBuffer into this
		var version = function(M, m) { return Number(M + '.' + m) },
			word = function(i){ return buf.readUInt32BE(4*i) }
		if (buf.toString('ascii',0, 4) != "DBPF")
			throw new TypeError("not a DBPF buffer")
		this.Version = version(word(1),word(2))
		this.UserVersion = version(word(3), word(4))
		this.Flags = word(5); this.Ctime = word(6); this.Atime = word(7)
		this.Index.Version = version(word(8), word(15))
		this.Index.Count = word(9)
		this.Index.Offset = word((word(15) == 3)?16:10)
		this.Index.Size = word(11)
		this.Holes.Count = word(12)
		this.Holes.Offset = word(13)
		this.Holes.Size = word(14)
	},
}

var DBPF = function(fd){
function F(){
	this.Header = new DBPF_Header()
	this.Index = []
}
F.prototype = {
	_file: fd,
	loadHeader: function() {
		var fr = new FileReader(),
			ab = fr.readAsArrayBuffer(this._file)
		this.Header.deserialize(ab)
	},
	saveHeader: function(){
		var buf = this.Header.serialize()
	},
	loadIndex: function(){ },
	saveIndex: function(){ }
}
	return new F()
}
DBPF.Header = function(){ return new DBPF_Header(arguments) }
DBPF.Index = function(){ return new DBPF_Index(arguments) }

module.exports = DBPF
