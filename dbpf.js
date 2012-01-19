require('DataView.extensions')

function DBPF_Header(){
	this.Version = 1.0
	this.UserVersion = 0.0
	this.Flags = 0; this.Ctime = 0; this.Atime = 0
	this.Index = { Version: 7.0, Count: 0, Offest: 0, Size: 0 }
	this.Holes = { Count: 0, Offest: 0, Size: 0 }
}
DBPF_Header.prototype = {
	serialize: function()
	{	// serializes this into a 96 byte ArrayBuffer
		var M = function(v){ return v.toString().split('.')[0] },
			m = function(v){ return v.toString().split('.')[1] }, 
			buf = new ArrayBuffer(96), dv = new DataView(buf)
		dv.setString(0, "DBPF")
		dv._splice('u32', 1, [
			M(this.Version), m(this.Version),
			M(this.UserVersion), m(this.UserVersion),
			this.Flags, this.Ctime, this.Atime,
			M(this.Index.Version),
			this.Index.Count, this.Index.Offset, this.Index.Size,
			this.Holes.Count, this.Holes.Offset, this.Holes.Size,
			m(this.Index.Version),
			this.Index.Offset
		])
		return buf
	},
	deserialize: function(buf)
	{	// deserializes an ArrayBuffer into this
		var version = function(M, m) { return Number(M + '.' + m) },
			dv = new DataView(buf)
			words = dv._slice('u32', 0, 16)
		if(dv.getString(0, 4) != "DBPF")
			throw new TypeError("not a DBPF buffer")
		this.Version = version(words[1],words[2])
		this.UserVersion = version(words[3], words[4])
		this.Flags = words[5]; this.Ctime = words[6]; this.Atime =words[7]
		this.Index.Version = version(words[8], words[15])
		this.Index.Count = words[9]
		this.Index.Offset = words[(words[15] == 3)?16:10]
		this.Index.Size = words[11]
		this.Holes.Count = words[12]
		this.Holes.Offset = words[13]
		this.Holes.Size = words[14]
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
