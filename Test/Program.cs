using System;
using FileMode = System.IO.FileMode;
using FileStream = System.IO.FileStream;
using fbstj.dbpf;

namespace fbstj.dbpf.tests
{
    class Program
    {
        const string TEST_FILE = "../../NetworkAddonMod_IndividualNetworkRULs.dat";
        static void Main(string[] args)
        {
            FileStream fs = System.IO.File.Open(TEST_FILE, FileMode.Open);
            File f= new File(fs);
            Console.WriteLine(f.MajorVersion + "." + f.MinorVersion);
            while (true) ;//keep open
        }
    }
}
