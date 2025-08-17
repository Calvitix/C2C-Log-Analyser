using C2CLogProcessor.Models;
using System.Collections.Generic;
using C2CLogProcessor.Enums; // Uncomment and adjust if needed

namespace C2CLogProcessor.Parsers
{
    public interface ILogParser
    {
        ParseResult ParseFile(string inputFile, string outputFile);
    }

}