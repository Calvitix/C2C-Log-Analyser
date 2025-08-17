using C2CLogProcessor.Models;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace C2CLogProcessor.Parsers.Patterns
{
    /// <summary>
    /// Pattern for unit-related information
    /// </summary>
    public class UnitPattern : IPattern
    {
        private bool _inUnitsSection = false;
        private readonly Regex _unitLinePattern = new Regex(@"^\s*(.+?)\s+\((.+?)\):\s*(\d+)", RegexOptions.Compiled);
        private readonly Regex _unitsSectionStartPattern = new Regex(@"^\s*Units:", RegexOptions.Compiled);
        private readonly Regex _unitsSectionEndPattern = new Regex(@"calculates upgrade", RegexOptions.Compiled);

        private UnitInventory? _currentInventory;

        public bool Apply(string line, GameState gameState)
        {
            if (_unitsSectionStartPattern.IsMatch(line))
            {
                _inUnitsSection = true;
                _currentInventory = new UnitInventory
                {
                    PlayerId = gameState.ActivePlayerId,
                    Turn = gameState.CurrentTurn
                };
                return true;
            }

            if (_inUnitsSection && _unitsSectionEndPattern.IsMatch(line))
            {
                _inUnitsSection = false;
                if (gameState.ActivePlayerId >= 0 && gameState.Players.TryGetValue(gameState.ActivePlayerId, out var player))
                {
                    if (player.UnitInventories == null)
                        player.UnitInventories = new List<UnitInventory>();
                    player.UnitInventories.Add(_currentInventory!);
                }
                _currentInventory = null;
                return true;
            }

            if (_inUnitsSection && _currentInventory != null)
            {
                var match = _unitLinePattern.Match(line);
                if (match.Success)
                {
                    var unitType = match.Groups[1].Value.Trim();
                    var unitAIType = match.Groups[2].Value.Trim();
                    var count = int.Parse(match.Groups[3].Value);

                    _currentInventory.UnitsByType[unitType + "|" + unitAIType] = new UnitTypeInfo
                    {
                        UnitType = unitType,
                        UnitAIType = unitAIType,
                        Count = count
                    };
                    return true;
                }
            }

            return false;
        }
    }
}