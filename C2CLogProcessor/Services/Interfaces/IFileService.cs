using System.IO;
using System.Text;

namespace C2CLogProcessor.Services.Interfaces
{
    public interface IFileService
    {
        StreamReader OpenReader(string path, Encoding encoding);
        StreamWriter OpenWriter(string path);
        bool FileExists(string path);
    }

    public class FileService : IFileService
    {
        public StreamReader OpenReader(string path, Encoding encoding)
        {
            return new StreamReader(path, encoding);
        }

        public StreamWriter OpenWriter(string path)
        {
            return new StreamWriter(path, false, Encoding.UTF8);
        }

        public bool FileExists(string path)
        {
            return File.Exists(path);
        }
    }
}