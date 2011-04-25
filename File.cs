using System;
using System.Collections.Generic;
using System.IO;

namespace fbstj.dbpf
{
    public class File
    {
        #region records
        /// <summary>An Index table record</summary>
        public struct Index
        {
            #region state
            private readonly File _f;
            private readonly uint _o;
            private readonly uint _2;

            internal Index(File file, uint offset) { _f = file; _o = offset; _2 = _f.GetU32(15); }
            #endregion

            #region TGI
            /// <summary>The Type ID</summary>
            public uint TypeID { get { return GetU32(0); } set { SetU32(0, value); } }

            /// <summary>The Groupe ID</summary>
            public uint GroupID { get { return GetU32(1); } set { SetU32(1, value); } }

            /// <summary>The Instance ID</summary>
            public uint InstanceID { get { return GetU32(2); } set { SetU32(2, value); } }

            /// <summary>The second IID (equal to the first IID in IndexV7.0)</summary>
            public uint InstanceID2 { get { return GetU32(2 + _2); } set { SetU32(2 + _2, value); } }
            #endregion

            #region properties
            /// <summary>The location of the first byte in the file</summary>
            public uint Location { get { return GetU32(3 + _2); } set { SetU32(3 + _2, value); } }

            /// <summary>The number of bytes in the file</summary>
            public uint Size { get { return GetU32(4 + _2); } set { SetU32(4 + _2, value); } }
            #endregion

            #region methods
            private uint GetU32(uint offest) { return _f.GetU32(_o + offest); }
            private void SetU32(uint offset, uint value) { _f.SetU32(_o + offset, value); }
            #endregion

        }

        /// <summary>A Hole table record</summary>
        public struct Hole
        {
            #region state
            private readonly File _f;
            private readonly uint _offset;

            internal Hole(File file, uint offset) { _f = file; _offset = offset; }
            #endregion

            #region properties
            /// <summary>The location of the first byte in the Hole</summary>
            public uint Location { get { return GetU32(0); } set { SetU32(0, value); } }

            /// <summary>The number of bytes in the Hole</summary>
            public uint Size { get { return GetU32(1); } set { SetU32(1, value); } }
            #endregion

            #region methods
            private uint GetU32(uint id) { return _f.GetU32(_offset + id); }
            private void SetU32(uint id, uint value) { _f.SetU32(_offset + id, value); }
            #endregion
        }
        #endregion

        #region state
        private readonly FileStream _file;

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
        #endregion

        #region properties
        /// <summary>The DBPF version</summary><value>SimCity 4: 1.0, Sims2: 1.x, SPORE: 2.0</value>
        public double Version { get { return GetVersion(1, 2); } set { SetVersion(1, 2, value); } }

        /// <summary>The User version</summary><value>0.0</value>
        public double User_Version { get { return GetVersion(3, 4); } set { SetVersion(3, 4, value); } }

        public uint Flags { get { return GetU32(5); } set { SetU32(5, value); } }
        public uint CTime { get { return GetU32(6); } set { SetU32(6, value); } }
        public uint ATime { get { return GetU32(7); } set { SetU32(7, value); } }

        /// <summary>The Index table version</summary><value>7.0 for </value>
        public double Index_Version { get { return GetVersion(8, 15); } set { SetVersion(8, 15, value); } }

        /// <summary>The number of Indexes in the file</summary>
        public uint Index_Count { get { return GetU32(9); } set { SetU32(9, value); } }
        /// <summary>The location of the first Index</summary>
        public uint Index_Location { get { return GetU32(10); } set { SetU32(10, value); } }
        /// <summary>The size of the Index list in bytes</summary>
        public uint Index_Size { get { return GetU32(11); } set { SetU32(11, value); } }

        /// <summary>The number of Holes in the file</summary>
        public uint Hole_Count { get { return GetU32(12); } set { SetU32(12, value); } }
        /// <summary>The location of the first Hole</summary>
        public uint Hole_Location { get { return GetU32(13); } set { SetU32(13, value); } }
        /// <summary>The size of the Hole list in bytes</summary>
        public uint Hole_Size { get { return GetU32(14); } set { SetU32(14, value); } }
        #endregion

        #region methods
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

        protected double GetVersion(uint major, uint minor)
        {
            return double.Parse(GetU32(major) + "." + GetU32(minor));
        }

        protected void SetVersion(uint major, uint minor, double version)
        {
            string[] s = version.ToString("F1").Split('.');
            SetU32(major, uint.Parse(s[0]));
            SetU32(minor, uint.Parse(s[1]));
        }
        #endregion
    }
}
