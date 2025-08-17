using C2CLogProcessor.Enums;
using System.Collections.Generic;
using System;

namespace C2CLogProcessor.Parsers.Categorizers
{
    public interface ILogCategorizer
    {
        LogCategory Categorize(string line);
    }
}