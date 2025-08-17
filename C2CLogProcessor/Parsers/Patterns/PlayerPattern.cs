using C2CLogProcessor.Models;
using System;
using System.Collections.Generic;
using System.Numerics;
using System.Text.RegularExpressions;

namespace C2CLogProcessor.Parsers.Patterns
{
    public class PlayerPattern : IPattern
    {
        private readonly Regex _statsPattern = new Regex(
            @"Player\s+(\d+)\s*\(([^)]+)\)\s*has\s+(\d+)\s+cities,\s+(\d+)\s+pop,\s+(\d+)\s+power,\s+(\d+)\s+tech percent",
            RegexOptions.Compiled);

        private readonly Regex _simpleIntPattern = new Regex(@"^(.*?)\s*:\s*(-?\d+)", RegexOptions.Compiled);
        private readonly Regex _ratePattern = new Regex(@"^(Gold|Science|Culture|Espionage) rate:\s*(-?\d+)", RegexOptions.Compiled);
        private readonly Regex _treasuryPattern = new Regex(@"^Treasury:\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _boolPattern = new Regex(@"^Is in financial difficulties:\s*(yes|no)", RegexOptions.Compiled | RegexOptions.IgnoreCase);
        private readonly Regex _anarchyPattern = new Regex(@"^Total turns in anarchy:\s*(\d+)\s*\(([\d.]+)%\)", RegexOptions.Compiled);
        private readonly Regex _civicHeaderPattern = new Regex(@"^Current civics:", RegexOptions.Compiled);
        private readonly Regex _civicLinePattern = new Regex(@"^\s+(.+?):\s+(.+)", RegexOptions.Compiled);
        private readonly Regex _civicSwitchHeaderPattern = new Regex(@"^Civic switch history:", RegexOptions.Compiled);
        private readonly Regex _civicSwitchLinePattern = new Regex(@"^\s+(.+)", RegexOptions.Compiled);

        // Add this regex to match get message lines
        private readonly Regex _playerGetMessagePattern = new Regex(
            @"Player\s+(\d+)\s*\([^)]+\)\s*get message\s*:\s*(.*)", RegexOptions.Compiled);

        // Add regexes for score elements and totals
        private readonly Regex _scorePopulationPattern = new Regex(@"(\d+)\s+pour population", RegexOptions.Compiled);
        private readonly Regex _scoreTerritoryPattern = new Regex(@"(\d+)\s+pour territoire", RegexOptions.Compiled);
        private readonly Regex _scoreTechPattern = new Regex(@"(\d+)\s+pour technologies", RegexOptions.Compiled);
        private readonly Regex _scoreWondersPattern = new Regex(@"(\d+)\s+pour Merveilles", RegexOptions.Compiled);
        private readonly Regex _scoreTotalPattern = new Regex(@"Score total\s*=\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _scoreVictoryPattern = new Regex(@"Score si victoire à ce tour\s*=\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _scoreSummaryPattern = new Regex(@"Total Score:\s*(\d+), Population Score:\s*(\d+).*Land Score:\s*(\d+), Tech Score:\s*(\d+), Wonder Score:\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _scoreSectionEndPattern = new Regex(@"has met:", RegexOptions.Compiled);

        // Add this regex for averages (Economy, Industry, Agriculture)
        private readonly Regex _scoreAveragesPattern = new Regex(
            @"Economy avg:\s*(\d+),\s*Industry avg:\s*(\d+),\s*Agriculture avg:\s*(\d+)", RegexOptions.Compiled);

        private bool _inCivicSection = false;
        private bool _inCivicSwitchSection = false;
        private bool _inPlayerStatsSection = false;
        private bool _inUnitsSection = false;
        private bool _inScoreSection = false;
        

        // State for score parsing
        private int? _scorePopulation = null;
        private int? _scoreTerritory = null;
        private int? _scoreTech = null;
        private int? _scoreWonders = null;
        private int? _scoreTotal = null;
        private int? _scoreVictory = null;
        private int? _scoreSummaryTotal = null;
        private int? _scoreSummaryPopulation = null;
        private int? _scoreSummaryTerritory = null;
        private int? _scoreSummaryTech = null;
        private int? _scoreSummaryWonders = null;
        private int? _scoreSectionTurn = null;

        // Add state for averages
        private int? _scoreEconomyAvg = null;
        private int? _scoreIndustryAvg = null;
        private int? _scoreAgricultureAvg = null;

        // Add these fields to your PlayerPattern class:
        private UnitInventory? _currentUnitInventory;
        private readonly Regex _unitLinePattern = new Regex(@"^\s*(.+?)\s+\((.+?)\):\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _unitsSectionEndPattern = new Regex(@"calculates upgrade", RegexOptions.Compiled);

        // Add this regex at the top of your class
        private readonly Regex _setTurnActivePattern = new Regex(@"setTurnActive for", RegexOptions.Compiled);

        public bool Apply(string line, GameState gameState)
        {
            if (string.IsNullOrWhiteSpace(line)) return false;

            if (_setTurnActivePattern.IsMatch(line))
                _inScoreSection = true;

            // Detect start of player stats section
            if (line.Contains("stats for turn", StringComparison.OrdinalIgnoreCase))
            {
                _inPlayerStatsSection = true;
                _inCivicSwitchSection = false;
                _inCivicSection = false;
                return true;
            }
            // Detect end of player stats section
            if (_civicSwitchHeaderPattern.IsMatch(line))
            {
                _inPlayerStatsSection = false;
                if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player) && player.CurrentStats != null)
                {
                    player.UpdateStats(player.CurrentStats, UpdateStatsMode.CompleteOnlyEmpty);
                }    
                _inCivicSection = false;
                _inCivicSwitchSection = true;
                return true;
            }

            // --- Close player section on "Units" line ---
            if ((_inPlayerStatsSection|| _inCivicSwitchSection || _inCivicSection) && line.Trim() == "Units:")
            {
                _inPlayerStatsSection = false;
                _inCivicSwitchSection = false;
                _inUnitsSection = true;
                if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player) && player.CurrentStats != null)
                {
                    player.UpdateStats(player.CurrentStats, UpdateStatsMode.Finalize);
                }
                return true;
            }
            // --------------------------------------------

            if (_civicHeaderPattern.IsMatch(line))
            {
                if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player) && player.CurrentStats != null)
                {
                    player.UpdateStats(player.CurrentStats, UpdateStatsMode.Finalize);
                }
                _inCivicSection = true;
                _inCivicSwitchSection = false;
                return true;
            }
            if (_civicSwitchHeaderPattern.IsMatch(line))
            {
                _inCivicSection = false;
                _inCivicSwitchSection = true;
                return true;
            }
            if (_inCivicSection)
            {
                var match = _civicLinePattern.Match(line);
                if (match.Success && gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var civicPlayer) && civicPlayer.CurrentStats != null)
                {
                    civicPlayer.CurrentStats.Civics[match.Groups[1].Value.Trim()] = match.Groups[2].Value.Trim();
                    return true;
                }
                else if (string.IsNullOrWhiteSpace(line))
                {
                    _inCivicSection = false;
                }
                return false;
            }
            if (_inCivicSwitchSection)
            {
                var switchMatch = _civicSwitchLinePattern.Match(line);
                if (switchMatch.Success && gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var switchPlayer) && switchPlayer.CurrentStats != null)
                {
                    switchPlayer.CurrentStats.CivicSwitchHistory.Add(switchMatch.Groups[1].Value.Trim());
                    return true;
                }
                else if (string.IsNullOrWhiteSpace(line))
                {
                    _inCivicSwitchSection = false;
                }
                return false;
            }

            // Only process player stats if in the section
            if (_inPlayerStatsSection)
            {
                // Try to match stats pattern
                var statsMatch = _statsPattern.Match(line);
                if (statsMatch.Success)
                {
                    ApplyStatsPattern(line, gameState);
                    return true;
                }

                // Try to match all other patterns that fill PlayerStats
                if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player) && player.CurrentStats != null)
                {
                    // Try all known patterns that fill PlayerStats
                    // --- Move the simpleIntMatch logic here ---
                    var simpleIntMatch = _simpleIntPattern.Match(line);
                    if (simpleIntMatch.Success)
                    {
                        var key = simpleIntMatch.Groups[1].Value.Trim();
                        var value = int.Parse(simpleIntMatch.Groups[2].Value);
                        switch (key)
                        {
                            case "Total gold income from self": player.CurrentStats.TotalGoldIncomeSelf = value; break;
                            case "Total gold income from trade agreements": player.CurrentStats.TotalGoldIncomeTrade = value; break;
                            case "Num units": player.CurrentStats.NumUnits = value; break;
                            case "Num selection groups": player.CurrentStats.NumSelectionGroups = value; break;
                            case "Unit Upkeep (pre inflation)": player.CurrentStats.UnitUpkeep = value; break;
                            case "Unit supply cost (pre inflation)": player.CurrentStats.UnitSupplyCost = value; break;
                            case "Maintenance cost (pre inflation)": player.CurrentStats.MaintenanceCost = value; break;
                            case "Civic upkeep cost (pre inflation)": player.CurrentStats.CivicUpkeepCost = value; break;
                            case "Corporate maintenance (pre inflation)": player.CurrentStats.CorporateMaintenance = value; break;
                            case "Inflation effect": player.CurrentStats.InflationEffect = value; break;
                            case "Total science output": player.CurrentStats.TotalScienceOutput = value; break;
                            case "Total espionage output": player.CurrentStats.TotalEspionageOutput = value; break;
                            case "Total cultural output": player.CurrentStats.TotalCulturalOutput = value; break;
                            case "Total population": player.CurrentStats.Population = value; break;
                            case "Total food output": player.CurrentStats.TotalFoodOutput = value; break;
                            case "Total production output": player.CurrentStats.TotalProductionOutput = value; break;
                            case "Num cities": player.CurrentStats.Cities = value; break;
                            case "National rev index": player.CurrentStats.NationalRevIndex = value; break;
                            case "Number of barbarian units killed": player.CurrentStats.NumBarbarianUnitsKilled = value; break;
                            case "Number of animals subdued": player.CurrentStats.NumAnimalsSubdued = value; break;
                            case "Civic switches": player.CurrentStats.CivicSwitches = value; break;
                            case "Total num civics switched": player.CurrentStats.TotalNumCivicsSwitched = value; break;
                            case "Gold rate": player.CurrentStats.GoldRate = value; break;
                            case "Science rate": player.CurrentStats.ScienceRate = value; break;
                            case "Espionage rate": player.CurrentStats.EspionageRate = value; break;
                            case "Culture rate": player.CurrentStats.CultureRate = value; break;
                            case "Treasury": player.CurrentStats.Treasury = value; break;
                            case "Total turns in anarchy": player.CurrentStats.TotalTurnsInAnarchy = value; break;

                            default:
                                Console.WriteLine($"{key}: not found in playerstat in line {line}");
                                return false;
                                break;
                        }
                        // After processing, update stats and return
                        //player.UpdateStats(player.CurrentStats, UpdateStatsMode.CompleteOnlyEmpty);
                        return true;
                    }
                    // --- End move ---

                    ApplyOtherPatterns(line, gameState);
                    // After each line, update stats to fill missing values
                    //player.UpdateStats(player.CurrentStats, UpdateStatsMode.CompleteOnlyEmpty);
                    return true;
                }
            }

            //if (ApplyPlayerGetMessage(line, gameState)) matched = true; Good if the message is matched by other patterns

            bool statsMatched = false; // Declare and initialize the variable
            bool otherMatched = false; // You may need this if referenced later
            if (_inScoreSection)
            {
                if (ApplyScorePopulation(line)) statsMatched = true;
                if (ApplyScoreTerritory(line)) statsMatched = true;
                if (ApplyScoreTech(line)) statsMatched = true;
                if (ApplyScoreWonders(line)) statsMatched = true;
                if (ApplyScoreTotal(line)) statsMatched = true;
                if (ApplyScoreVictory(line)) statsMatched = true;
                if (ApplyScoreSummary(line)) statsMatched = true;
                if (ApplyScoreAverages(line)) statsMatched = true;
                if (ApplyScoreSectionEnd(line, gameState)) statsMatched = true;
            }

            if (_inUnitsSection)
            {
                // End of units section
                if (_unitsSectionEndPattern.IsMatch(line))
                {
                    _inUnitsSection = false;
                    if (_currentUnitInventory != null && gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player))
                    {
                        player.UnitInventories ??= new List<UnitInventory>();
                        player.UnitInventories.Add(_currentUnitInventory);
                    }
                    _currentUnitInventory = null;
                    return true;
                }

                // Parse unit lines
                var match = _unitLinePattern.Match(line);
                if (match.Success && gameState.ActivePlayerId >= 0)
                {
                    if (_currentUnitInventory == null)
                    {
                        _currentUnitInventory = new UnitInventory
                        {
                            PlayerId = gameState.ActivePlayerId,
                            Turn = gameState.CurrentTurn
                        };
                    }
                    var unitType = match.Groups[1].Value.Trim();
                    var unitAIType = match.Groups[2].Value.Trim();
                    var count = int.Parse(match.Groups[3].Value);

                    _currentUnitInventory.UnitsByType[unitType + "|" + unitAIType] = new UnitTypeInfo
                    {
                        UnitType = unitType,
                        UnitAIType = unitAIType,
                        Count = count
                    };
                    return true;
                }
            }

            otherMatched = otherMatched || ApplyPlayerGetMessage(line, gameState);

            return statsMatched || otherMatched;
        }

        private void ApplyStatsPattern(string line, GameState gameState)
        {
            var match = _statsPattern.Match(line);
            if (match.Success)
            {
                var playerId = int.Parse(match.Groups[1].Value);
                var playerName = match.Groups[2].Value;

                if (!gameState.Players.TryGetValue(playerId, out var player))
                {
                    player = new Player(playerId, playerName);
                    gameState.Players[playerId] = player;
                }

                var stats = new PlayerStats
                {
                    Turn = gameState.CurrentTurn,
                    PlayerId = playerId,
                    Cities = int.Parse(match.Groups[3].Value),
                    Population = int.Parse(match.Groups[4].Value),
                    Power = int.Parse(match.Groups[5].Value),
                    TechPercent = int.Parse(match.Groups[6].Value)
                };
                //player.CurrentStats = stats;
                player.UpdateStats(stats, UpdateStatsMode.CompleteOnlyEmpty);

            }
        }

        private void ApplyOtherPatterns(string line, GameState gameState)
        {
            if (gameState.ActivePlayerId < 0 || !gameState.Players.ContainsKey(gameState.ActivePlayerId))
                return;

            var player = gameState.Players[gameState.ActivePlayerId];
            if (player.CurrentStats == null)
                return;

            var rateMatch = _ratePattern.Match(line);
            if (rateMatch.Success)
            {
                var rateType = rateMatch.Groups[1].Value.ToLowerInvariant();
                var value = int.Parse(rateMatch.Groups[2].Value);
                switch (rateType)
                {
                    case "gold": player.CurrentStats.GoldRate = value; break;
                    case "science": player.CurrentStats.ScienceRate = value; break;
                    case "culture": player.CurrentStats.CultureRate = value; break;
                    case "espionage": player.CurrentStats.EspionageRate = value; break;
                }
                return;
            }

            var treasuryMatch = _treasuryPattern.Match(line);
            if (treasuryMatch.Success)
            {
                player.CurrentStats.Treasury = int.Parse(treasuryMatch.Groups[1].Value);
                return;
            }

            var boolMatch = _boolPattern.Match(line);
            if (boolMatch.Success)
            {
                player.CurrentStats.IsInFinancialDifficulties = boolMatch.Groups[1].Value.Equals("yes", StringComparison.OrdinalIgnoreCase);
                return;
            }

            var anarchyMatch = _anarchyPattern.Match(line);
            if (anarchyMatch.Success)
            {
                player.CurrentStats.TotalTurnsInAnarchy = int.Parse(anarchyMatch.Groups[1].Value);
                player.CurrentStats.AnarchyPercent = double.Parse(anarchyMatch.Groups[2].Value);
                return;
            }

            var simpleIntMatch = _simpleIntPattern.Match(line);
            if (simpleIntMatch.Success)
            {
                var key = simpleIntMatch.Groups[1].Value.Trim();
                var value = int.Parse(simpleIntMatch.Groups[2].Value);
                switch (key)
                {
                    case "Total gold income from self": player.CurrentStats.TotalGoldIncomeSelf = value; break;
                    case "Total gold income from trade agreements": player.CurrentStats.TotalGoldIncomeTrade = value; break;
                    case "Num units": player.CurrentStats.NumUnits = value; break;
                    case "Num selection groups": player.CurrentStats.NumSelectionGroups = value; break;
                    case "Unit Upkeep (pre inflation)": player.CurrentStats.UnitUpkeep = value; break;
                    case "Unit supply cost (pre inflation)": player.CurrentStats.UnitSupplyCost = value; break;
                    case "Maintenance cost (pre inflation)": player.CurrentStats.MaintenanceCost = value; break;
                    case "Civic upkeep cost (pre inflation)": player.CurrentStats.CivicUpkeepCost = value; break;
                    case "Corporate maintenance (pre inflation)": player.CurrentStats.CorporateMaintenance = value; break;
                    case "Inflation effect": player.CurrentStats.InflationEffect = value; break;
                    case "Total science output": player.CurrentStats.TotalScienceOutput = value; break;
                    case "Total espionage output": player.CurrentStats.TotalEspionageOutput = value; break;
                    case "Total cultural output": player.CurrentStats.TotalCulturalOutput = value; break;
                    case "Total population": player.CurrentStats.Population = value; break;
                    case "Total food output": player.CurrentStats.TotalFoodOutput = value; break;
                    case "Total production output": player.CurrentStats.TotalProductionOutput = value; break;
                    case "Num cities": player.CurrentStats.Cities = value; break;
                    case "National rev index": player.CurrentStats.NationalRevIndex = value; break;
                    case "Number of barbarian units killed": player.CurrentStats.NumBarbarianUnitsKilled = value; break;
                    case "Number of animals subdued": player.CurrentStats.NumAnimalsSubdued = value; break;
                    case "Civic switches": player.CurrentStats.CivicSwitches = value; break;
                    case "Total num civics switched": player.CurrentStats.TotalNumCivicsSwitched = value; break;
                }
            }
        }

        private bool ApplyPlayerGetMessage(string line, GameState gameState)
        {
            var match = _playerGetMessagePattern.Match(line);
            if (match.Success)
            {
                var playerId = int.Parse(match.Groups[1].Value);
                var message = match.Groups[2].Value.Trim();

                // Clean font and color tags
                message = Regex.Replace(message, @"<font=\d+>", "");
                message = Regex.Replace(message, @"<color=[^>]+>", "");
                message = Regex.Replace(message, @"</color>", "");
                message = message.Trim();

                if (!gameState.Players.TryGetValue(playerId, out var player))
                    return false;

                player.Messages ??= new List<string>();
                player.Messages.Add(message);
                return true;
            }
            return false;
        }

        private bool ApplyScorePopulation(string line)
        {
            var match = _scorePopulationPattern.Match(line);
            if (match.Success)
            {
                _scorePopulation = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Population: {_scorePopulation} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreTerritory(string line)
        {
            var match = _scoreTerritoryPattern.Match(line);
            if (match.Success)
            {
                _scoreTerritory = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Territory: {_scoreTerritory} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreTech(string line)
        {
            var match = _scoreTechPattern.Match(line);
            if (match.Success)
            {
                _scoreTech = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Tech: {_scoreTech} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreWonders(string line)
        {
            var match = _scoreWondersPattern.Match(line);
            if (match.Success)
            {
                _scoreWonders = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Wonders: {_scoreWonders} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreTotal(string line)
        {
            var match = _scoreTotalPattern.Match(line);
            if (match.Success)
            {
                _scoreTotal = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Total: {_scoreTotal} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreVictory(string line)
        {
            var match = _scoreVictoryPattern.Match(line);
            if (match.Success)
            {
                _scoreVictory = int.Parse(match.Groups[1].Value);
                //Console.WriteLine($"[DEBUG] Matched Victory: {_scoreVictory} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreSummary(string line)
        {
            var match = _scoreSummaryPattern.Match(line);
            if (match.Success)
            {
                _scoreSummaryTotal = int.Parse(match.Groups[1].Value);
                _scoreSummaryPopulation = int.Parse(match.Groups[2].Value);
                _scoreSummaryTerritory = int.Parse(match.Groups[3].Value);
                _scoreSummaryTech = int.Parse(match.Groups[4].Value);
                _scoreSummaryWonders = int.Parse(match.Groups[5].Value);
                //Console.WriteLine($"[DEBUG] Matched ScoreSummary: Total={_scoreSummaryTotal}, Pop={_scoreSummaryPopulation}, Terr={_scoreSummaryTerritory}, Tech={_scoreSummaryTech}, Wonders={_scoreSummaryWonders} from line: {line}");
                return true;
            }
            return false;
        }
        private bool ApplyScoreAverages(string line)
        {
            var match = _scoreAveragesPattern.Match(line);
            if (match.Success)
            {
                _scoreEconomyAvg = int.Parse(match.Groups[1].Value);
                _scoreIndustryAvg = int.Parse(match.Groups[2].Value);
                _scoreAgricultureAvg = int.Parse(match.Groups[3].Value);
                return true;
            }
            return false;
        }
        private bool ApplyScoreSectionEnd(string line, GameState gameState)
        {
            if (_scoreSectionTurn == null)
                _scoreSectionTurn = gameState.CurrentTurn;

            if (_scoreSectionTurn != null && _scoreSectionEndPattern.IsMatch(line))
            {
                // If we have a score section turn, finalize the player stats, and add the score history, only if one of the score elements was matched and is not null
                if (_scorePopulation.HasValue || _scoreTerritory.HasValue || _scoreTech.HasValue || _scoreWonders.HasValue || _scoreTotal.HasValue || _scoreVictory.HasValue ||
                    _scoreSummaryTotal.HasValue || _scoreSummaryPopulation.HasValue || _scoreSummaryTerritory.HasValue || _scoreSummaryTech.HasValue || _scoreSummaryWonders.HasValue ||
                    _scoreEconomyAvg.HasValue || _scoreIndustryAvg.HasValue || _scoreAgricultureAvg.HasValue)
                {


                    if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player))
                    {
                            player.ScoreHistory ??= new List<PlayerScoreHistory>();
                        player.ScoreHistory.Add(new PlayerScoreHistory
                        {
                            Turn = _scoreSectionTurn.Value,
                            Population = _scorePopulation ?? _scoreSummaryPopulation ?? 0,
                            Territory = _scoreTerritory ?? _scoreSummaryTerritory ?? 0,
                            Technologies = _scoreTech ?? _scoreSummaryTech ?? 0,
                            Wonders = _scoreWonders ?? _scoreSummaryWonders ?? 0,
                            Total = _scoreTotal ?? _scoreSummaryTotal ?? 0,
                            VictoryScore = _scoreVictory,
                            EconomyAvg = _scoreEconomyAvg,
                            IndustryAvg = _scoreIndustryAvg,
                            AgricultureAvg = _scoreAgricultureAvg
                        });
                    }
                    // Reset all state
                    _scorePopulation = null;
                    _scoreTerritory = null;
                    _scoreTech = null;
                    _scoreWonders = null;
                    _scoreTotal = null;
                    _scoreVictory = null;
                    _scoreSummaryTotal = null;
                    _scoreSummaryPopulation = null;
                    _scoreSummaryTerritory = null;
                    _scoreSummaryTech = null;
                    _scoreSummaryWonders = null;
                    _scoreSectionTurn = null;
                    _scoreEconomyAvg = null;
                    _scoreIndustryAvg = null;
                    _scoreAgricultureAvg = null;
                }

                _inScoreSection = false;
                return true;
            }
            return false;
        }
        // Add this method to PlayerPattern
        private void Finalize(Player player, GameState gameState)
        {
            if (player?.CurrentStats != null)
            {
                // Call ApplyStatsPattern with a special "Finalize" attribute/flag
                // Since ApplyStatsPattern expects a line, but we want to finalize, 
                // you can add an overload or just call a method on PlayerStats.
                // Here, we assume PlayerStats has a Finalize method.
                //player.CurrentStats.Finalize();
                // Optionally, update stats in player
                player.UpdateStats(player.CurrentStats, UpdateStatsMode.Finalize);
            }
        }
    }
}