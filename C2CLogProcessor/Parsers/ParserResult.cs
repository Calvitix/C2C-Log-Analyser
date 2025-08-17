using C2CLogProcessor.Models;
using System.Collections.Generic;
using C2CLogProcessor.Enums; // Uncomment and adjust if needed

namespace C2CLogProcessor.Parsers
{

    public class ParseResult
    {
        public int TotalLines { get; set; }
        public int ProcessedLines { get; set; }
        public int TurnsFound { get; set; }
        public List<City> Cities { get; set; } = new List<City>();
        public Dictionary<LogCategory, int> CategoryCounts { get; set; } = new Dictionary<LogCategory, int>();
        public long ElapsedMilliseconds { get; set; }
        public IEnumerable<Player> Players { get; internal set; } = new List<Player>();
        public List<PlayerTurnTiming> PlayerTurnTimings { get; internal set; } = new List<PlayerTurnTiming>();



    }

}