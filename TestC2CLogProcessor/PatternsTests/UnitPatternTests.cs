using System.Collections.Generic;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers.Patterns;


namespace C2CLogProcessor.Parsers.Patterns.Tests
{
    public class UnitPatternTests
    {
        [Fact]
        public void Apply_UnitInventorySection_ParsesUnitCounts()
        {
            var player = new Player(1, "Alice") { CurrentStats = new PlayerStats() };
            var gameState = new GameState
            {
                ActivePlayerId = 1,
                Players = new Dictionary<int, Player> { { 1, player } }
            };
            var pattern = new UnitPattern();

            pattern.Apply("Units:", gameState);
            pattern.Apply("Warrior (UNITAI_ATTACK): 3", gameState);
            pattern.Apply("", gameState); // End of section

            Assert.Equal(3, ((Dictionary<string, int>)player.CurrentStats.UnitsByType)["Warrior (UNITAI_ATTACK)"]);
        }

        [Fact]
        public void Apply_UnitEvaluationPattern_ParsesEvaluation()
        {
            var gameState = new GameState();
            var pattern = new UnitPattern();
            pattern.Apply("evaluate Value for unit Warrior as type UNITAI_ATTACK, combat value 10, moves 2, Calculated value 15", gameState);
            // No assertion: extend GameState to track evaluations if needed
        }

        [Fact]
        public void Apply_BetterUnitPattern_ParsesBetterUnit()
        {
            var gameState = new GameState();
            var pattern = new UnitPattern();
            pattern.Apply("Better AI Unit found for UNITAI_ATTACK, type Warrior, Swordsman, base value 12, final value 18", gameState);
            // No assertion: extend GameState to track best units if needed
        }

        [Fact]
        public void Apply_IgnoresNonMatchingLines()
        {
            var gameState = new GameState();
            var pattern = new UnitPattern();
            pattern.Apply("Random log line", gameState);
            // No assertion: just ensure no exceptions
        }
    }
}