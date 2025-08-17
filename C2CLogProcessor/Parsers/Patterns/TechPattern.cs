using System.Text.RegularExpressions;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Parsers.Patterns
{
    /// <summary>
    /// Pattern for technology-related information
    /// </summary>
    public class TechPattern : IPattern
    {
        private readonly Regex _techEvaluationPattern = new Regex(
            @"calculate value for tech\s+(.+?)(?:\s*\(|$)",
            RegexOptions.Compiled);

        private readonly Regex _techValuePattern = new Regex(
            @"raw value for tech\s+(.+?)\s+is\s+(\d+)",
            RegexOptions.Compiled);

        private readonly Regex _techCostValuePattern = new Regex(
            @"tech\s+(.+?):\s*cost\s+(\d+),\s*value\s+(\d+)",
            RegexOptions.Compiled);

        private readonly Regex _buildingValuePattern = new Regex(
            @"Building\s+(.+?)\s+new mechanism value:\s*(-?\d+)",
            RegexOptions.Compiled);

        public bool Apply(string line, GameState gameState)
        {
            bool matched = false;
            matched |= ApplyTechEvaluation(line, gameState);
            matched |= ApplyTechValue(line, gameState);
            matched |= ApplyTechCostValue(line, gameState);
            matched |= ApplyBuildingValue(line, gameState);
            return matched;
        }

        private bool ApplyTechEvaluation(string line, GameState gameState)
        {
            var match = _techEvaluationPattern.Match(line);
            if (match.Success)
            {
                var techName = match.Groups[1].Value.Trim();
                // Track tech being evaluated
                // Could store in a TechEvaluation structure
                return true;
            }
            return false;
        }

        private bool ApplyTechValue(string line, GameState gameState)
        {
            var match = _techValuePattern.Match(line);
            if (match.Success)
            {
                var techName = match.Groups[1].Value.Trim();
                var value = int.Parse(match.Groups[2].Value);
                // Store tech values for analysis
                return true;
            }
            return false;
        }

        private bool ApplyTechCostValue(string line, GameState gameState)
        {
            var match = _techCostValuePattern.Match(line);
            if (match.Success)
            {
                var techName = match.Groups[1].Value.Trim();
                var cost = int.Parse(match.Groups[2].Value);
                var value = int.Parse(match.Groups[3].Value);
                // Store tech cost/value ratios
                return true;
            }
            return false;
        }

        private bool ApplyBuildingValue(string line, GameState gameState)
        {
            var match = _buildingValuePattern.Match(line);
            if (match.Success)
            {
                var buildingName = match.Groups[1].Value.Trim();
                var value = int.Parse(match.Groups[2].Value);
                // Store building evaluations
                return true;
            }
            return false;
        }
    }
}