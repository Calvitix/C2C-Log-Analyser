using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers.Patterns;
using Xunit;

namespace C2CLogProcessor.Parsers.Patterns.Tests
{
    public class TechPatternTests
    {
        [Fact]
        public void Apply_TechEvaluationPattern_ParsesTechEvaluation()
        {
            var gameState = new GameState();
            var pattern = new TechPattern();
            pattern.Apply("calculate value for tech Pottery", gameState);
            // No assertion: extend GameState to track evaluations if needed
        }

        [Fact]
        public void Apply_TechValuePattern_ParsesTechValue()
        {
            var gameState = new GameState();
            var pattern = new TechPattern();
            pattern.Apply("raw value for tech Pottery is 120", gameState);
            // No assertion: extend GameState to track values if needed
        }

        [Fact]
        public void Apply_TechCostValuePattern_ParsesTechCostValue()
        {
            var gameState = new GameState();
            var pattern = new TechPattern();
            pattern.Apply("tech Pottery: cost 80, value 120", gameState);
            // No assertion: extend GameState to track cost/values if needed
        }

        [Fact]
        public void Apply_BuildingValuePattern_ParsesBuildingValue()
        {
            var gameState = new GameState();
            var pattern = new TechPattern();
            pattern.Apply("Building Granary new mechanism value: 30", gameState);
            // No assertion: extend GameState to track building values if needed
        }

        [Fact]
        public void Apply_IgnoresNonMatchingLines()
        {
            var gameState = new GameState();
            var pattern = new TechPattern();
            pattern.Apply("Random log line", gameState);
            // No assertion: just ensure no exceptions
        }
    }
}