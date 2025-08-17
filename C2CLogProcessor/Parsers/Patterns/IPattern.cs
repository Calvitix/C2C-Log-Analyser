using C2CLogProcessor.Models;

namespace C2CLogProcessor.Parsers.Patterns
{
    public interface IPattern
    {
        /// <summary>
        /// Applies the pattern to the line and returns true if a match was found and processed.
        /// </summary>
        bool Apply(string line, GameState gameState);
    }
}