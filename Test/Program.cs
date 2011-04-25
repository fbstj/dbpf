using System;
using System.IO;

namespace fbstj.dbpf.tests
{
    class Program
    {
        const string TEST_FILE = "../../NetworkAddonMod_IndividualNetworkRULs.dat";
        static void Main(string[] args)
        {
            FileStream fs = File.Open(TEST_FILE, FileMode.Open);
            byte[] buf = new byte[4];
            fs.Seek(0, SeekOrigin.Begin);
            fs.Read(buf, 0, 4);
            foreach(byte b in buf)
                Console.Write((char)b);
            while (true) ;//keep open
        }
    }
}
