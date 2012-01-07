DataView.prototype._types = {
	s8: { size: 1, signed: true,	get: 'getInt8', 	set: 'setInt8' },
	u8: { size: 1, signed: false,	get: 'getUint8',	set: 'setUint8' },
	s16: { size: 2, signed: true,	get: 'getInt16',	set: 'setInt16' },
	u16: { size: 2, signed: false,	get: 'getUint16',	set: 'setUint16' },
	s32: { size: 4, signed: true,	get: 'getInt32',	set: 'setInt32' },
	u32: { size: 4, signed: false,	get: 'getUint32',	set: 'setUint32' },
	str: { size: 1, get: 'getChar', set: 'setChar', slice: 'getString', splice: 'setString' },
}
DataView.prototype._get = function(type, offset){
	var t = this._types[type]
	return this[t.get](t.size * offset)
}
DataView.prototype._set = function(type, offset, value){
	var t = this._types[type]
	return this[t.set](t.size * offset, value)
}
DataView.prototype._slice = function(type, offset, length){
	var out = []
	for(var i = 0; i < length; i++)
		out[i] = this._get(type, offset + i)
	return out
}
DataView.prototype._splice = function(type, offset, values){
	for(var i = 0; i < values.length; i++)
		this._set(type, offset + i, values[i])
}

DataView.prototype.getChar = function(byteOffset) {
	return String.fromCharCode(this.getUint8(byteOffset))
}
DataView.prototype.setChar = function(byteOffset, value)
{
	this.setUint8(byteOffset, value.charCodeAt(0))
}

DataView.prototype.getString = function(byteOffset, length){
	return this._slice('str', byteOffset, length).join('')
}
DataView.prototype.setString = function(byteOffset, value){
	this._splice('str', byteOffset, value);
}