using C2CLogProcessor.Models;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Numerics;
using System.Text.RegularExpressions;

namespace C2CLogProcessor.Parsers.Patterns
{
    /// <summary>
    /// Pattern for detecting turn changes and updating game state
    /// </summary>
    public class TurnPattern : IPattern
    {
        private readonly Regex _turnChangePattern = new Regex(
            @"\[(\d+\.\d+)\]\s*Player\s+(\d+)\s*\(([^)]+)\)\s*setTurnActive\s*for\s*turn\s+(\d+)",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);
            
        private readonly Regex _turnEndPattern = new Regex(
            @"\[(\d+\.\d+)\]\s*Player\s+(\d+)\s*\(([^)]+)\)\s*turn ended",
            RegexOptions.Compiled);

        private readonly Regex _playerStatsPattern = new Regex(
            @"Player\s+(\d+)\s*\(([^)]+)\)\s*has\s+(\d+)\s+cities,\s+(\d+)\s+pop,\s+(\d+)\s+power,\s+(\d+)\s+tech percent",
            RegexOptions.Compiled);

        public bool Apply(string line, GameState gameState)
        {
            var turnMatch = _turnChangePattern.Match(line);
            var matched = false;
            if (turnMatch.Success)
            {
                var timestamp = double.Parse(turnMatch.Groups[1].Value, CultureInfo.InvariantCulture);
                var playerId = int.Parse(turnMatch.Groups[2].Value);
                var playerName = turnMatch.Groups[3].Value;
                var turnNumber = int.Parse(turnMatch.Groups[4].Value);
                gameState.CurrentTurn = turnNumber;
                gameState.ActivePlayerId = playerId;
                gameState.ActivePlayerName = playerName;

                // Add or update timing entry
                var timing = gameState.PlayerTurnTimings.FirstOrDefault(
                    t => t.Turn == turnNumber && t.PlayerId == playerId);
                if (timing == null)
                {
                    timing = new PlayerTurnTiming
                    {
                        Turn = turnNumber,
                        PlayerId = playerId,
                        PlayerName = playerName,
                        BeginTimestamp = timestamp
                    };
                    gameState.PlayerTurnTimings.Add(timing);
                }
                else
                {
                    timing.BeginTimestamp = timestamp;
                }

                UpdatePlayerStats(turnMatch, gameState, true);

                matched = true;
            }

            var endMatch = _turnEndPattern.Match(line);
            if (endMatch.Success)
            {
                var timestamp = double.Parse(endMatch.Groups[1].Value, CultureInfo.InvariantCulture);
                var playerId = int.Parse(endMatch.Groups[2].Value);
                var playerName = endMatch.Groups[3].Value;

                // Find the latest timing entry for this player
                var timing = gameState.PlayerTurnTimings
                    .Where(t => t.PlayerId == playerId)
                    .OrderByDescending(t => t.Turn)
                    .FirstOrDefault();
                if (timing != null)
                {
                    timing.EndTimestamp = timestamp;
                }
                matched = true;
            }

            // Also check for player stats which often come with turn changes
            var statsMatch = _playerStatsPattern.Match(line);
            if (statsMatch.Success)
            {
                UpdatePlayerStats(statsMatch, gameState);
                matched = true;
            }

            return matched;
        }
        
void UpdatePlayerStats(Match match, GameState gameState, bool Activeturn = false)
        {
            int playerId = -1;
            string playerName = "NO_NAME";

            if (Activeturn)
            {
                playerId = int.Parse(match.Groups[2].Value);
                playerName = match.Groups[3].Value;
            }
            else
            {
                playerId = int.Parse(match.Groups[1].Value);
                playerName = match.Groups[2].Value;
            }

            // Ensure player exists
            if (!gameState.Players.ContainsKey(playerId))
            {
                gameState.Players[playerId] = new Player(playerId, playerName);
            }

            var player = gameState.Players[playerId];

            // Create stats for this turn
            var stats = new PlayerStats
            {
                Turn = gameState.CurrentTurn,
                PlayerId = playerId
            };
            if (!Activeturn)
            {
                stats.Cities = int.Parse(match.Groups[3].Value);
                stats.Population = int.Parse(match.Groups[4].Value);
                stats.Power = int.Parse(match.Groups[5].Value);
                stats.TechPercent = int.Parse(match.Groups[6].Value);
            }

            if (player.CurrentStats != null && (player.CurrentStats.Turn == gameState.CurrentTurn))
            {
                player.UpdateStats(stats, UpdateStatsMode.CompleteOnlyEmpty);
            }
            else
            {
                player.UpdateStats(stats, UpdateStatsMode.ResetAndAdd);
            }
        }

        public static void FillEndTimestamps(PlayerTurnTiming LastTiming, double lastTimestamp)
        {
                if (LastTiming.EndTimestamp == 0)
                {
                    LastTiming.EndTimestamp = lastTimestamp; // Use last timestamp in log
                }

        }

    }
}