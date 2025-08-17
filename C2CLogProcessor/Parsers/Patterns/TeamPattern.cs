using System;
using System.Linq;
using System.Text.RegularExpressions;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Parsers.Patterns
{
    /// <summary>
    /// Pattern for team/diplomacy related information
    /// </summary>
    public class TeamPattern : IPattern
    {
        private readonly Regex _teamMetPattern = new Regex(
            @"Team\s+(\d+).*has met:\s*([^;]*)", 
            RegexOptions.Compiled);
            
        private readonly Regex _atWarPattern = new Regex(
            @"at war with:\s*([^;]*)", 
            RegexOptions.Compiled);
            
        private readonly Regex _warExpensesPattern = new Regex(
            @"Team\s+(\d+).*estimating warplan financial costs.*iExtraWarExpenses:\s+(\d+)",
            RegexOptions.Compiled);

        private readonly Regex _teamStatusLine = new Regex(
            @"Team\s+(\d+)\s+has met:\s*([^;]*);\s*at war with:\s*([^;]*);\s*planning war with:\s*(.*)", 
            RegexOptions.Compiled);

        public bool Apply(string line, GameState gameState)
        {
            bool matched = false;
            if (ApplyTeamStatusLine(line, gameState)) matched = true;
            if (_teamMetPattern.IsMatch(line))
            {
                ApplyTeamMetPattern(line, gameState);
                matched = true;
            }
            if (_atWarPattern.IsMatch(line))
            {
                ApplyWarPattern(line, gameState);
                matched = true;
            }
            if (_warExpensesPattern.IsMatch(line))
            {
                ApplyWarExpensesPattern(line, gameState);
                matched = true;
            }
            return matched;
        }

        private bool ApplyTeamStatusLine(string line, GameState gameState)
        {
            var match = _teamStatusLine.Match(line);
            if (match.Success)
            {
                // Process as needed
                return true;
            }
            return false;
        }

        private void ApplyTeamMetPattern(string line, GameState gameState)
        {
            var match = _teamMetPattern.Match(line);
            if (match.Success)
            {
                var teamId = int.Parse(match.Groups[1].Value);
                var metTeamsString = match.Groups[2].Value.Trim();
                
                if (!string.IsNullOrEmpty(metTeamsString) && gameState.Players.ContainsKey(teamId))
                {
                    var player = gameState.Players[teamId];
                    var metTeams = metTeamsString
                        .Split(',')
                        .Where(s => !string.IsNullOrWhiteSpace(s))
                        .Select(s => s.Trim())
                        .Where(s => int.TryParse(s, out _))
                        .Select(int.Parse)
                        .ToList();
                    
                    foreach (var metTeam in metTeams)
                    {
                        player.MetPlayers.Add(metTeam);
                    }
                }
            }
        }

        private void ApplyWarPattern(string line, GameState gameState)
        {
            var match = _atWarPattern.Match(line);
            if (match.Success && gameState.ActivePlayerId >= 0)
            {
                var warTeamsString = match.Groups[1].Value.Trim();
                
                if (!string.IsNullOrEmpty(warTeamsString) && 
                    gameState.Players.ContainsKey(gameState.ActivePlayerId))
                {
                    var player = gameState.Players[gameState.ActivePlayerId];
                    var warTeams = warTeamsString
                        .Split(',')
                        .Where(s => !string.IsNullOrWhiteSpace(s))
                        .Select(s => s.Trim())
                        .Where(s => int.TryParse(s, out _))
                        .Select(int.Parse)
                        .ToList();
                    
                    foreach (var warTeam in warTeams)
                    {
                        player.AtWarWith.Add(warTeam);
                    }
                }
            }
        }

        private void ApplyWarExpensesPattern(string line, GameState gameState)
        {
            var match = _warExpensesPattern.Match(line);
            if (match.Success)
            {
                var teamId = int.Parse(match.Groups[1].Value);
                var warExpenses = int.Parse(match.Groups[2].Value);
                
                // Store war expenses in player's current stats if available
                if (gameState.Players.ContainsKey(teamId) && 
                    gameState.Players[teamId].CurrentStats != null)
                {
                    // You might want to add a WarExpenses property to PlayerStats
                    // For now, we'll just log it
                    Console.WriteLine($"Team {teamId} war expenses: {warExpenses}");
                }
            }
        }
    }
}