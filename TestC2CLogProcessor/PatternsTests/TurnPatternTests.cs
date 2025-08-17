using System.Collections.Generic;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers.Patterns;
using Xunit;

namespace C2CLogProcessor.Parsers.Patterns.Tests
{
    public class TurnPatternTests
    {
        [Fact]
        public void Apply_TurnChangePattern_UpdatesGameState()
        {
            var gameState = new GameState
            {
                Players = new Dictionary<int, Player>()
            };
            var pattern = new TurnPattern();
            pattern.Apply("Player 1 (Alice) setTurnActive for turn 10", gameState);

            Assert.Equal(10, gameState.CurrentTurn);
            Assert.Equal(1, gameState.ActivePlayerId);
            Assert.Equal("Alice", gameState.ActivePlayerName);
            Assert.True(gameState.Players.ContainsKey(1));
        }

        [Fact]
        public void Apply_PlayerStatsPattern_UpdatesPlayerStats()
        {
            var gameState = new GameState
            {
                CurrentTurn = 10,
                Players = new Dictionary<int, Player>()
            };
            var pattern = new TurnPattern();
            pattern.Apply("Player 1 (Alice) has 3 cities, 10 pop, 50 power, 80 tech percent", gameState);

            Assert.True(gameState.Players.ContainsKey(1));
            var player = gameState.Players[1];
            Assert.NotNull(player.CurrentStats);
            Assert.Equal(3, player.CurrentStats.Cities);
            Assert.Equal(10, player.CurrentStats.Population);
            Assert.Equal(50, player.CurrentStats.Power);
            // Tech percent can be added to PlayerStats if needed
        }

        [Fact]
        public void Apply_IgnoresNonMatchingLines()
        {
            var gameState = new GameState
            {
                Players = new Dictionary<int, Player>()
            };
            var pattern = new TurnPattern();
            pattern.Apply("Random log line", gameState);
            // No assertion: just ensure no exceptions
        }
    }
}