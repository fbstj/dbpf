using System;
using System.Collections.Generic;
using System.IO;

namespace fbstj.dbpf
{
    public class File
    {
        private readonly FileStream _file;
        public uint MajorVersion { get { return GetU32(1); } set { SetU32(1, value); } }
        public uint MinorVersion { get { return GetU32(2); } set { SetU32(2, value); } }

        public File(FileStream file)
        {
            byte[] tmp = new byte[4];
            if (file == null || !file.CanRead)
                throw new ArgumentException("Need to be able to read the file");
            file.Seek(0, SeekOrigin.Begin);
            file.Read(tmp, 0, 4);
            if (tmp[0] != 'D' || tmp[1] != 'B' || tmp[2] != 'P' || tmp[3] != 'F')
                throw new ArgumentException("File is not DBPF format");
            _file = file;
        }

        protected uint GetU32(uint offset)
        {
            byte[] tmp = new byte[4];
            _file.Seek(offset * 4, SeekOrigin.Begin);
            _file.Read(tmp, 0, 4);
            return BitConverter.ToUInt32(tmp, 0);
        }

        protected void SetU32(uint offset, uint value)
        {
            byte[] tmp = BitConverter.GetBytes(value);
            _file.Seek(offset * 4, SeekOrigin.Begin);
            _file.Write(tmp, 0, 4);
        }
    }
}
