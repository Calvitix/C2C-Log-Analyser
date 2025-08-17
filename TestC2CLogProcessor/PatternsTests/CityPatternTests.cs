using System.Collections.Generic;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers.Patterns;


namespace TestC2CLogProcessor.Parsers.Patterns.Tests
{
    public class CityPatternTests
    {
        [Fact]
        public void Apply_ThreatPattern_AddsOrUpdatesCityThreatLevels()
        {
            // Arrange
            var gameState = new GameState
            {
                ActivePlayerId = 42,
                Cities = new Dictionary<string, City>()
            };
            var pattern = new CityPattern();
            string line = "City Paris has threat level 5 (highest 7, total 12)";

            // Act
            pattern.Apply(line, gameState);

            // Assert
            Assert.True(gameState.Cities.ContainsKey("Paris"));
            var city = gameState.Cities["Paris"];
            Assert.Equal("Paris", city.Name);
            Assert.Equal(5, city.ThreatLevel);
            Assert.Equal(7, city.ThreatLevelHighest);
            Assert.Equal(12, city.ThreatLevelTotal);
            Assert.Equal(42, city.OwnerId);
        }

        [Fact]
        public void Apply_ThreatPattern_UpdatesExistingCity()
        {
            // Arrange
            var city = new City { Name = "Berlin" };
            var gameState = new GameState
            {
                ActivePlayerId = 99,
                Cities = new Dictionary<string, City> { { "Berlin", city } }
            };
            var pattern = new CityPattern();
            string line = "City Berlin has threat level 2 (highest 3, total 4)";

            // Act
            pattern.Apply(line, gameState);

            // Assert
            Assert.Equal(2, city.ThreatLevel);
            Assert.Equal(3, city.ThreatLevelHighest);
            Assert.Equal(4, city.ThreatLevelTotal);
            Assert.Equal(99, city.OwnerId);
        }

        [Fact]
        public void Apply_FoundingPattern_AddsNewCityAndMapsPlayer()
        {
            // Arrange
            var gameState = new GameState
            {
                ActivePlayerId = 7,
                ActivePlayerName = "Alice",
                CurrentTurn = 10,
                Cities = new Dictionary<string, City>(),
                CityToPlayerMap = new Dictionary<string, int>()
            };
            var pattern = new CityPattern();
            string line = "founds new city Rome at 12, 34";

            // Act
            pattern.Apply(line, gameState);

            // Assert
            Assert.True(gameState.Cities.ContainsKey("Rome"));
            var city = gameState.Cities["Rome"];
            Assert.Equal("Rome", city.Name);
            Assert.Equal(12, city.X);
            Assert.Equal(34, city.Y);
            Assert.Equal(10, city.FoundedTurn);
            Assert.Equal(7, city.OwnerId);
            Assert.Equal("Alice", city.OwnerName);
            Assert.True(gameState.CityToPlayerMap.ContainsKey("Rome"));
            Assert.Equal(7, gameState.CityToPlayerMap["Rome"]);
        }

        [Fact]
        public void Apply_FoundingPattern_UpdatesExistingCity()
        {
            // Arrange
            var city = new City { Name = "Madrid" };
            var gameState = new GameState
            {
                ActivePlayerId = 3,
                ActivePlayerName = "Bob",
                CurrentTurn = 5,
                Cities = new Dictionary<string, City> { { "Madrid", city } },
                CityToPlayerMap = new Dictionary<string, int>()
            };
            var pattern = new CityPattern();
            string line = "founds new city Madrid at 1, 2";

            // Act
            pattern.Apply(line, gameState);

            // Assert
            Assert.Equal(1, city.X);
            Assert.Equal(2, city.Y);
            Assert.Equal(5, city.FoundedTurn);
            Assert.Equal(3, city.OwnerId);
            Assert.Equal("Bob", city.OwnerName);
            Assert.True(gameState.CityToPlayerMap.ContainsKey("Madrid"));
            Assert.Equal(3, gameState.CityToPlayerMap["Madrid"]);
        }

        [Fact]
        public void Apply_IgnoresNonMatchingLines()
        {
            // Arrange
            var gameState = new GameState
            {
                ActivePlayerId = 1,
                Cities = new Dictionary<string, City>(),
                CityToPlayerMap = new Dictionary<string, int>()
            };
            var pattern = new CityPattern();
            string line = "This line does not match any pattern";

            // Act
            pattern.Apply(line, gameState);

            // Assert
            Assert.Empty(gameState.Cities);
            Assert.Empty(gameState.CityToPlayerMap);
        }
    }
}