using System;
using C2CLogProcessor.Models;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq; 

namespace C2CLogProcessor.Parsers.Patterns
{
    public class AiEvaluationPattern : IPattern
    {
        private readonly Regex _beginCitySitesPattern = new Regex(@"Player (\d+) \(([^)]+)\) begin Update City Sites", RegexOptions.Compiled);
        private readonly Regex _endCitySitesPattern = new Regex(@"Player (\d+) \(([^)]+)\) end Update City Sites", RegexOptions.Compiled);
        private readonly Regex _potentialSitePattern = new Regex(@"Potential best city site \((\d+), (\d+)\) found value is (\d+) \(player modified value to (\d+)\)", RegexOptions.Compiled);
        private readonly Regex _foundSitePattern = new Regex(@"Found City Site at \((\d+), (\d+)\)", RegexOptions.Compiled);

        private readonly Regex _unitEvalPattern = new Regex(@"AI Player (\d+) evaluate Value for unit (\S+) as type (\S+), combat value (\d+), moves (\d+), Calculated value (\d+)", RegexOptions.Compiled);
        private readonly Regex _betterUnitPattern = new Regex(@"Better AI Unit found for (\S+), type (\S+), ([^,]+), base value (\-?\d+), final value (\-?\d+)", RegexOptions.Compiled);
        private readonly Regex _notChosenUnitPattern = new Regex(@"AI Unit not chosen \(not better\), type (\S+), ([^,]+), base value (\-?\d+), final value (\-?\d+)", RegexOptions.Compiled);
        private readonly Regex _citySearchPattern = new Regex(@"City ([^,]+), AI_bestUnitAI searching for (\S+)", RegexOptions.Compiled);

        private bool _inCitySitesSection = false;
        private int _currentPlayerId = -1;
        private string _currentPlayerName = "";
        private string _currentCityName = "";
        private string _currentUnitAIType = "";

        private int _lineCount = 0;

        public bool Apply(string line, GameState gameState)
        {
            _lineCount++;
            if (_lineCount % 10000 == 0)
            {
                PrintOverview(gameState);
            }

            // City Sites Section
            var beginMatch = _beginCitySitesPattern.Match(line);
            if (beginMatch.Success)
            {
                _inCitySitesSection = true;
                _currentPlayerId = int.Parse(beginMatch.Groups[1].Value);
                _currentPlayerName = beginMatch.Groups[2].Value;
                return true;
            }

            var endMatch = _endCitySitesPattern.Match(line);
            if (endMatch.Success)
            {
                _inCitySitesSection = false;
                _currentPlayerId = -1;
                _currentPlayerName = "";
                return true;
            }

            if (_inCitySitesSection)
            {
                var potentialMatch = _potentialSitePattern.Match(line);
                if (potentialMatch.Success)
                {
                    // You can fill city site evaluation here if needed
                    return true;
                }
                var foundMatch = _foundSitePattern.Match(line);
                if (foundMatch.Success)
                {
                    // You can fill found city site here if needed
                    return true;
                }
            }

            // Track current city and AI type for unit evaluation
            var citySearchMatch = _citySearchPattern.Match(line);
            if (citySearchMatch.Success)
            {
                _currentCityName = citySearchMatch.Groups[1].Value.Trim();
                _currentUnitAIType = citySearchMatch.Groups[2].Value.Trim();
                return true;
            }

            // Unit Evaluation Section
            var unitEvalMatch = _unitEvalPattern.Match(line);
            if (unitEvalMatch.Success)
            {
                int playerId = int.Parse(unitEvalMatch.Groups[1].Value);
                string unitType = unitEvalMatch.Groups[2].Value;
                string unitAIType = unitEvalMatch.Groups[3].Value;
                int combatValue = int.Parse(unitEvalMatch.Groups[4].Value);
                int moves = int.Parse(unitEvalMatch.Groups[5].Value);
                int calcValue = int.Parse(unitEvalMatch.Groups[6].Value);

                int turn = gameState.GetTurnFromTimestamp(gameState.LastTimestamp);

                // Get or create the player
                if (!gameState.Players.TryGetValue(playerId, out var player))
                {
                    player = new Player(playerId, _currentPlayerName);
                    gameState.Players[playerId] = player;
                }

                var eval = player.UnitEvaluation;
                eval.PlayerId = playerId;

                // For normal evaluation
                var newEval = new UnitEvaluationTurn
                {
                    Turn = turn,
                    PlayerId = playerId,
                    CityName = "NO_CITY",
                    UnitType = unitType,
                    UnitAIType = unitAIType,
                    CombatValue = combatValue,
                    Moves = moves,
                    CalculatedValue = calcValue,
                    IsBetterUnit = false
                };

                if (eval.LastTurn == turn)
                {
                    // If we have a current city, set it
                    if (!eval.Evaluations.Exists(e =>
                        e.PlayerId == newEval.PlayerId &&
                        e.CityName == newEval.CityName &&
                        e.UnitType == newEval.UnitType &&
                        e.UnitAIType == newEval.UnitAIType &&
                        e.CalculatedValue == newEval.CalculatedValue &&
                        e.IsBetterUnit == newEval.IsBetterUnit))
                    {
                        eval.Evaluations.Add(newEval);
                        eval.LastTurn = newEval.Turn;
                    }
                }
                else
                {
                    // If we have a new turn, add it without double check (to improve performance)
                    eval.Evaluations.Add(newEval);
                    eval.LastTurn = turn;
                }

                return true;
            }

            var betterUnitMatch = _betterUnitPattern.Match(line);
            if (betterUnitMatch.Success)
            {
                string unitAIType = betterUnitMatch.Groups[1].Value;
                string unitType = betterUnitMatch.Groups[2].Value;
                string unitName = betterUnitMatch.Groups[3].Value.Trim();
                int baseValue = int.Parse(betterUnitMatch.Groups[4].Value);
                int finalValue = int.Parse(betterUnitMatch.Groups[5].Value);

                int turn = gameState.GetTurnFromTimestamp(gameState.LastTimestamp);

                int playerId = -1;
                // find playerID with current city name
                if (string.IsNullOrEmpty(_currentCityName))
                {
                    _currentCityName = "NO_CITY"; // Default if no city is set
                }
                else
                {
                    //Get the list of cities for this player
                    foreach (var city in gameState.Cities.Values)
                    {
                        if (city.Name == _currentCityName)
                        {
                            playerId = gameState.CityToPlayerMap[city.Name];
                            break;
                        }
                    }


                }

                if (playerId == -1)
                {
                    // If we can't find the player, we can't evaluate this unit
                    Console.WriteLine($"[AiEvaluationPattern] Warning: No player found for city {_currentCityName} in turn {turn}");
                    return false;
                }
                else
                {
                    // Ensure the player exists in the game state
                    if (!gameState.Players.TryGetValue(playerId, out var player))
                    {
                        player = new Player(playerId, _currentPlayerName);
                        gameState.Players[playerId] = player;
                    }

                    PlayerUnitEvaluation eval = player.UnitEvaluation;

                    // For better unit
                    var betterEval = new UnitEvaluationTurn
                    {
                        Turn = turn,
                        PlayerId = playerId,
                        CityName = _currentCityName,
                        UnitType = unitType,
                        UnitAIType = unitAIType,
                        BaseValue = baseValue,
                        FinalValue = finalValue,
                        UnitName = unitName,
                        IsBetterUnit = true,
                        CalculatedValue = finalValue
                    };

                    if (eval.LastTurn == turn)
                    {
                        if (!eval.Evaluations.Exists(e =>
                        e.Turn == betterEval.Turn &&
                        e.PlayerId == betterEval.PlayerId &&
                        e.CityName == betterEval.CityName &&
                        e.UnitType == betterEval.UnitType &&
                        e.UnitAIType == betterEval.UnitAIType &&
                        e.CalculatedValue == betterEval.CalculatedValue &&
                        e.IsBetterUnit == betterEval.IsBetterUnit))
                        {
                            eval.Evaluations.Add(betterEval);
                            eval.LastTurn = turn;
                        }
                    }
                    else
                    {
                        eval.Evaluations.Add(betterEval);
                        eval.LastTurn = turn;
                    }

                    // Track best unit for this AI type
                    if (!eval.BestUnitsByAIType.ContainsKey(unitAIType))
                    {
                        eval.BestUnitsByAIType[unitAIType] = new List<BestUnitAIHistory>();
                    }
                    var bestUnitsList = eval.BestUnitsByAIType[unitAIType];
                    // Only add BestUnitAIHistory if its FinalValue is less than all others in the list
                    bool isStrictlyLower = bestUnitsList.Count == 0 || bestUnitsList.All(b => finalValue < b.FinalValue);
                    if (isStrictlyLower)
                    {
                        bestUnitsList.Add(new BestUnitAIHistory
                        {
                            UnitAIType = unitAIType,
                            UnitType = unitType,
                            UnitName = unitName,
                            FirstTurn = turn,
                            FinalValue = finalValue,
                            BaseValue = baseValue
                        });
                    }
                }
                return true;
            }

            var notChosenUnitMatch = _notChosenUnitPattern.Match(line);
            if (notChosenUnitMatch.Success)
            {
                // Optionally store not-chosen units if needed
                return true;
            }

            return false;
        }

        private void PrintOverview(GameState gameState)
        {
            Console.WriteLine($"[AiEvaluationPattern] Processed {_lineCount} lines.");
            foreach (var player in gameState.Players.Values)
            {
                var eval = player.UnitEvaluation;
                if (eval.Evaluations.Count == 0) continue;
                Console.WriteLine($"  Player {player.Id} ({player.Name}): {eval.Evaluations.Count} unit evaluations.");
                //foreach (var aiType in eval.BestUnitsByAIType.Keys)
                //{
                //    var best = eval.BestUnitsByAIType[aiType];
                //    Console.WriteLine($"    Best {aiType}: {best.UnitType} ({best.UnitName}), value={best.CalculatedValue}, firstTurn={best.FirstTurn}");
                //}
            }
        }
    }
}