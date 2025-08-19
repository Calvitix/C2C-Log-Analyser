using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Parsers.Patterns
{

    public class CityPattern : IPattern
    {
        private readonly Regex _threatPattern = new Regex(
            @"City\s+(\S+)\s+has threat level\s+(\d+)\s+\(highest\s+(\d+),\s+total\s+(\d+)\)",
            RegexOptions.Compiled);

        private readonly Regex _foundingPattern = new Regex(
            @"founds new city\s+(\S+)\s+at\s+(\d+),\s+(\d+)",
            RegexOptions.Compiled);

        // Regex for city block start: [timestamp]      City Babylone:
        private readonly Regex _cityBlockStart = new Regex(
            @"City\s+([^:]+):\s*$", RegexOptions.Compiled);

        // Regex for each property line: [timestamp]          Population: 6
        private readonly Regex _propertyLine = new Regex(
            @"^\s*(\w[\w\s'\-È…‡¿Ë»Í ÓŒÙ‘˚€Á«]+):\s*(-?\d+)",
            RegexOptions.Compiled);

        // Regex for city production lines
        private readonly Regex _cityProductionPattern = new Regex(
            @"City\s+(.+?)\s+pushes production of (?:building|unit|project)\s+(.+)", RegexOptions.Compiled);

        // Update regex to capture order type (unit/building)
        private readonly Regex _cityOrderToCentralPattern = new Regex(
            @"City\s+(.+?)\s+pop\s+\d+\s+puts out tenders for\s+(-?\d+)\s+(unit|building)\s+strength of AIType:\s+(\w+)\s+at priority\s+(\d+)",
            RegexOptions.Compiled);

        // Add this regex for workers info
        private readonly Regex _cityWorkersPattern = new Regex(
            @"Player\s+(\d+),\s*city:\s*(.+?),\s*workers have:\s*(\d+),\s*workers needed:\s*(\d+)",
            RegexOptions.Compiled);

        // Add this regex for city building completion messages (French example)
        private readonly Regex _cityBuildingCompletedPattern = new Regex(
            @"get message\s*:\s*<font=\d+>(?:Des\s+<color=[^>]+>(.+?)</color>\s+ont ÈtÈ construites par les citoyens de\s+(.+)|(.+?)\s+has been built by the citizens of\s+(.+))",
            RegexOptions.Compiled);

        // Add this regex for single-building completion messages (French, singular "Une ... a ÈtÈ construite ...")
        private readonly Regex _citySingleBuildingCompletedPattern = new Regex(
            @"get message\s*:\s*<font=\d+>(?:Une\s+<color=[^>]+>(.+?)</color>\s+a ÈtÈ construite par les citoyens de\s+(.+)|(.+?)\s+has been built by the citizens of\s+(.+))",
            RegexOptions.Compiled);

        // Add this regex for defender requests (unit, AI_UNKNOWN)
        private readonly Regex _cityDefenderRequestPattern = new Regex(
            @"City\s+(.+?)\s+requests\s+(-?\d+)\s+floating defender strength at priority\s+(\d+)",
            RegexOptions.Compiled);

        // Add this regex for value+change properties
        private readonly Regex _propertyValueChangeLine = new Regex(
            @"^\s*(\w[\w\s'\-È…‡¿Ë»Í ÓŒÙ‘˚€Á«]+):\s*value\((-?\d+)\)\s*change\((-?\d+)\)",
            RegexOptions.Compiled);

        public bool Apply(string line, GameState gameState)
        {
            bool matched = false;
            if (ApplyThreatPattern(line, gameState)) matched = true;
            if (ApplyFoundingPattern(line, gameState)) matched = true;
            if (ApplyCityTurnData(line, gameState)) matched = true;
            if (ApplyCityProduction(line, gameState)) matched = true;
            if (ApplyCityOrderToCentral(line, gameState)) matched = true;
            if (ApplyCityWorkers(line, gameState)) matched = true;
            if (ApplyCityBuildingCompleted(line, gameState)) matched = true;
            if (ApplyCitySingleBuildingCompleted(line, gameState)) matched = true;
            if (ApplyCityDefenderRequest(line, gameState)) matched = true; // <-- Add this
            return matched;
        }

        private bool ApplyThreatPattern(string line, GameState gameState)
        {
            var match = _threatPattern.Match(line);
            if (match.Success)
            {
                var cityName = match.Groups[1].Value;
                
                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.ThreatLevel = int.Parse(match.Groups[2].Value);
                city.ThreatLevelHighest = int.Parse(match.Groups[3].Value);
                city.ThreatLevelTotal = int.Parse(match.Groups[4].Value);
                city.OwnerId = gameState.ActivePlayerId;
                return true;
            }
            return false;
        }

        private bool ApplyFoundingPattern(string line, GameState gameState)
        {
            var match = _foundingPattern.Match(line);
            if (match.Success)
            {
                var cityName = match.Groups[1].Value;

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.X = int.Parse(match.Groups[2].Value);
                city.Y = int.Parse(match.Groups[3].Value);
                city.FoundedTurn = gameState.CurrentTurn;
                city.OwnerId = gameState.ActivePlayerId;
                city.OwnerName = gameState.ActivePlayerName;

                gameState.CityToPlayerMap[cityName] = gameState.ActivePlayerId;

                // Fill OwnedCityNames in Player
                if (gameState.Players.TryGetValue(city.OwnerId, out var player))
                {
                    if (!player.OwnedCityNames.Contains(cityName))
                        player.OwnedCityNames.Add(cityName);
                }

                // Example for ownership assignment
                if (city.OwnerId != gameState.ActivePlayerId)
                {
                    city.OwnerId = gameState.ActivePlayerId;
                    city.OwnerName = gameState.ActivePlayerName;
                    if (gameState.Players.TryGetValue(city.OwnerId, out var player2))
                    {
                        if (!player2.OwnedCityNames.Contains(city.Name))
                            player2.OwnedCityNames.Add(city.Name);
                    }
                }

                return true;
            }
            return false;
        }

        // --- New logic for per-turn city data ---

        // State for multi-line parsing
        private string? _currentCityName = null;
        private CityTurnData? _currentTurnData = null;
        private int _lastParsedTurn = -1;

        private static readonly Dictionary<string, Action<CityTurnData, int>> _propertySetters = new()
        {
            ["Population"] = (ctd, v) => ctd.Population = v,
            ["Production"] = (ctd, v) => ctd.Production = v,
            ["Food surplus"] = (ctd, v) => ctd.FoodSurplus = v,
            ["Local rev index"] = (ctd, v) => ctd.LocalRevIndex = v,
            ["Maintenance"] = (ctd, v) => ctd.Maintenance = v,
            ["Income"] = (ctd, v) => ctd.Income = v,
            ["Science"] = (ctd, v) => ctd.Science = v,
            ["Espionage"] = (ctd, v) => ctd.Espionage = v,
            ["Culture"] = (ctd, v) => ctd.Culture = v,
            ["Net happyness"] = (ctd, v) => ctd.NetHappiness = v,
            ["Net health"] = (ctd, v) => ctd.NetHealth = v,
            ["Food trade yield"] = (ctd, v) => ctd.FoodTradeYield = v,
            ["Production trade yield"] = (ctd, v) => ctd.ProductionTradeYield = v,
            ["Commerce trade yield"] = (ctd, v) => ctd.CommerceTradeYield = v,
            ["CriminalitÈ"] = (ctd, v) => ctd.Criminalite = v,
            ["Maladie"] = (ctd, v) => ctd.Maladie = v,
            ["Pollution de L'eau"] = (ctd, v) => ctd.PollutionEau = v,
            ["Pollution de L'air"] = (ctd, v) => ctd.PollutionAir = v,
            ["Education"] = (ctd, v) => ctd.Education = v,
            ["Risque d'incendie"] = (ctd, v) => ctd.RisqueIncendie = v,
            ["Tourisme"] = (ctd, v) => ctd.Tourisme = v,
            ["Crime"] = (ctd, v) => ctd.Criminalite = v,
            ["Disease"] = (ctd, v) => ctd.Maladie = v,
            ["Water Pollution"] = (ctd, v) => ctd.PollutionEau = v,
            ["Air Pollution"] = (ctd, v) => ctd.PollutionAir = v,
            ["Education"] = (ctd, v) => ctd.Education = v,
            ["Flammability"] = (ctd, v) => ctd.RisqueIncendie = v,
            ["Tourism"] = (ctd, v) => ctd.Tourisme = v,
            ["Unit value"] = (ctd, v) => ctd.Ignore = v,
            ["Build value"] = (ctd, v) => ctd.Ignore = v,
            ["Building value"] = (ctd, v) => ctd.Ignore = v,
            ["Promotion value"] = (ctd, v) => ctd.Ignore = v,
            ["Corporation value"] = (ctd, v) => ctd.Ignore = v,
            ["Misc value"] = (ctd, v) => ctd.Ignore = v,
            ["Tile improvement value"] = (ctd, v) => ctd.Ignore = v,
            ["Bonus reveal value"] = (ctd, v) => ctd.Ignore = v,
            ["Religion value"] = (ctd, v) => ctd.Ignore = v,
            ["Free on first discovery value"] = (ctd, v) => ctd.Ignore = v,

            
        };

        private static readonly Dictionary<string, Action<CityTurnData, int, int?>> _propertySettersValueChange = new()
        {
            ["CriminalitÈ"] = (ctd, v, c) => { ctd.Criminalite = v; if (c.HasValue) ctd.CriminaliteChange = c.Value; },
            ["Maladie"] = (ctd, v, c) => { ctd.Maladie = v; if (c.HasValue) ctd.MaladieChange = c.Value; },
            ["Pollution de L'eau"] = (ctd, v, c) => { ctd.PollutionEau = v; if (c.HasValue) ctd.PollutionEauChange = c.Value; },
            ["Pollution de L'air"] = (ctd, v, c) => { ctd.PollutionAir = v; if (c.HasValue) ctd.PollutionAirChange = c.Value; },
            ["Education"] = (ctd, v, c) => { ctd.Education = v; if (c.HasValue) ctd.EducationChange = c.Value; },
            ["Risque d'incendie"] = (ctd, v, c) => { ctd.RisqueIncendie = v; if (c.HasValue) ctd.RisqueIncendieChange = c.Value; },
            ["Tourisme"] = (ctd, v, c) => { ctd.Tourisme = v; if (c.HasValue) ctd.TourismeChange = c.Value; },
            ["Crime"] = (ctd, v, c) => { ctd.Criminalite = v; if (c.HasValue) ctd.CriminaliteChange = c.Value; },
            ["Disease"] = (ctd, v, c) => { ctd.Maladie = v; if (c.HasValue) ctd.MaladieChange = c.Value; },
            ["Water Pollution"] = (ctd, v, c) => { ctd.PollutionEau = v; if (c.HasValue) ctd.PollutionEauChange = c.Value; },
            ["Air Pollution"] = (ctd, v, c) => { ctd.PollutionAir = v; if (c.HasValue) ctd.PollutionAirChange = c.Value; },
            ["Education"] = (ctd, v, c) => { ctd.Education = v; if (c.HasValue) ctd.EducationChange = c.Value; },
            ["Flammability"] = (ctd, v, c) => { ctd.RisqueIncendie = v; if (c.HasValue) ctd.RisqueIncendieChange = c.Value; },
            ["Tourism"] = (ctd, v, c) => { ctd.Tourisme = v; if (c.HasValue) ctd.TourismeChange = c.Value; },

        };

        private bool ApplyCityTurnData(string line, GameState gameState)
        {
            // Detect start of a city block
            var cityBlockMatch = _cityBlockStart.Match(line);
            if (cityBlockMatch.Success)
            {
                // Save previous city turn data if any
                if (_currentCityName != null && _currentTurnData != null)
                {
                    if (gameState.Cities.TryGetValue(_currentCityName, out var prevCity))
                    {
                        prevCity.History.Add(_currentTurnData);
                        // Update the city's Population property
                        prevCity.Population = _currentTurnData.Population;
                    }
                }

                _currentCityName = cityBlockMatch.Groups[1].Value.Trim();
                _currentTurnData = new CityTurnData { Turn = gameState.CurrentTurn };
                _lastParsedTurn = gameState.CurrentTurn;

                // Ensure city exists
                if (!gameState.Cities.TryGetValue(_currentCityName, out var city))
                {
                    city = new City { Name = _currentCityName };
                    gameState.Cities[_currentCityName] = city;
                }
                return true;
            }

            // If in a city block, parse property lines
            if (_currentCityName != null && _currentTurnData != null)
            {
                // Try value+change pattern first
                var valueChangeMatch = _propertyValueChangeLine.Match(line);
                if (valueChangeMatch.Success)
                {
                    var propName = valueChangeMatch.Groups[1].Value.Trim();
                    var value = int.Parse(valueChangeMatch.Groups[2].Value);
                    var change = int.Parse(valueChangeMatch.Groups[3].Value);

                    if (_propertySettersValueChange.TryGetValue(propName, out var setter))
                    {
                        setter(_currentTurnData, value, change);
                    }
                    return false;
                }

                // Fallback to original property line
                var propMatch = _propertyLine.Match(line);
                if (propMatch.Success)
                {
                    var propName = propMatch.Groups[1].Value.Trim();
                    var value = int.Parse(propMatch.Groups[2].Value);

                    if (_propertySetters.TryGetValue(propName, out var setter))
                    {
                        setter(_currentTurnData, value);
                    }
                    else
                    {
                        Console.WriteLine($"Unknown property '{propName}' for city '{_currentCityName}' at turn {_lastParsedTurn}");
                    }
                }
                // Optionally, handle end of city block (e.g., next city or empty line)
                // If you want to finalize on empty line:
                if (string.IsNullOrWhiteSpace(line) || line.Contains("setTurnActive"))
                {
                    if (gameState.Cities.TryGetValue(_currentCityName, out var city))
                    {
                        city.History.Add(_currentTurnData);
                        city.Population = _currentTurnData.Population;
                    }
                    _currentCityName = null;
                    _currentTurnData = null;
                }
            }
            return false;
        }

        private bool ApplyCityProduction(string line, GameState gameState)
        {
            var match = _cityProductionPattern.Match(line);
            if (match.Success)
            {
                var cityName = match.Groups[1].Value.Trim();
                var productName = match.Groups[2].Value.Trim();

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                // Ensure the list exists
                city.Produced ??= new List<CityProduction>();
                city.Produced.Add(new CityProduction
                {
                    ProductName = productName,
                    Turn = gameState.CurrentTurn
                });
                return true;
            }
            return false;
        }

        // Update ApplyCityOrderToCentral
        private bool ApplyCityOrderToCentral(string line, GameState gameState)
        {
            var match = _cityOrderToCentralPattern.Match(line);
            if (match.Success)
            {
                var cityName = match.Groups[1].Value.Trim();
                var strengthStr = match.Groups[2].Value.Trim();
                var orderTypeStr = match.Groups[3].Value.Trim().ToLowerInvariant();
                var aiType = match.Groups[4].Value.Trim();
                var priorityStr = match.Groups[5].Value.Trim();

                // Defensive parsing for strength and priority
                if (!int.TryParse(strengthStr, out var strength))
                    return false;
                if (!int.TryParse(priorityStr, out var priority))
                    return false;

                OrderType orderType = orderTypeStr switch
                {
                    "unit" => OrderType.Unit,
                    "building" => OrderType.Building,
                    _ => OrderType.Unknown
                };

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.OrdersToCentral ??= new List<CityOrderToCentral>();
                city.OrdersToCentral.Add(new CityOrderToCentral
                {
                    AIType = aiType,
                    Strength = strength,
                    Priority = priority,
                    Turn = gameState.CurrentTurn,
                    OrderType = orderType
                });
                return true;
            }
            return false;
        }

        private bool ApplyCityWorkers(string line, GameState gameState)
        {
            var match = _cityWorkersPattern.Match(line);
            if (match.Success)
            {
                var playerId = int.Parse(match.Groups[1].Value);
                var cityName = match.Groups[2].Value.Trim();
                var workersHave = int.Parse(match.Groups[3].Value);
                var workersNeeded = int.Parse(match.Groups[4].Value);

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.WorkersHave = workersHave;
                city.WorkersNeeded = workersNeeded;
                gameState.CityToPlayerMap[cityName] = playerId;
                if (gameState.Players.TryGetValue(playerId, out var player))
                {
                    if (!player.OwnedCityNames.Contains(cityName))
                        player.OwnedCityNames.Add(cityName);
                }
                // If the city is not owned by the player, set ownership
                gameState.ActivePlayerId = playerId;
                return true;
            }
            return false;
        }

        private bool ApplyCityBuildingCompleted(string line, GameState gameState)
        {
            var match = _cityBuildingCompletedPattern.Match(line);
            if (match.Success)
            {
                string buildingName, cityName;
                if (!string.IsNullOrEmpty(match.Groups[1].Value) && !string.IsNullOrEmpty(match.Groups[2].Value))
                {
                    // French format
                    buildingName = match.Groups[1].Value.Trim();
                    cityName = match.Groups[2].Value.Trim();
                }
                else
                {
                    // English format
                    buildingName = match.Groups[3].Value.Trim();
                    cityName = match.Groups[4].Value.Trim();
                }

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.Produced ??= new List<CityProduction>();
                city.Produced.Add(new CityProduction
                {
                    ProductName = buildingName,
                    Turn = gameState.CurrentTurn
                });
                return true;
            }
            return false;
        }

        private bool ApplyCitySingleBuildingCompleted(string line, GameState gameState)
        {
            var match = _citySingleBuildingCompletedPattern.Match(line);
            if (match.Success)
            {
                string buildingName, cityName;
                if (!string.IsNullOrEmpty(match.Groups[1].Value) && !string.IsNullOrEmpty(match.Groups[2].Value))
                {
                    // French format
                    buildingName = match.Groups[1].Value.Trim();
                    cityName = match.Groups[2].Value.Trim();
                }
                else
                {
                    // English format
                    buildingName = match.Groups[3].Value.Trim();
                    cityName = match.Groups[4].Value.Trim();
                }

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.Produced ??= new List<CityProduction>();
                city.Produced.Add(new CityProduction
                {
                    ProductName = buildingName,
                    Turn = gameState.CurrentTurn
                });
                return true;
            }
            return false;
        }

        private bool ApplyCityDefenderRequest(string line, GameState gameState)
        {
            var match = _cityDefenderRequestPattern.Match(line);
            if (match.Success)
            {
                var cityName = match.Groups[1].Value.Trim();
                var strengthStr = match.Groups[2].Value.Trim();
                var priorityStr = match.Groups[3].Value.Trim();

                if (!int.TryParse(strengthStr, out var strength))
                    return false;
                if (!int.TryParse(priorityStr, out var priority))
                    return false;

                if (!gameState.Cities.TryGetValue(cityName, out var city))
                {
                    city = new City { Name = cityName };
                    gameState.Cities[cityName] = city;
                }

                city.OrdersToCentral ??= new List<CityOrderToCentral>();
                city.OrdersToCentral.Add(new CityOrderToCentral
                {
                    AIType = "AI_UNKNOWN",
                    Strength = strength,
                    Priority = priority,
                    Turn = gameState.CurrentTurn,
                    OrderType = OrderType.Unit
                });
                return true;
            }
            return false;
        }
    }
}