using System;
using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class GameState
    {
        public int CurrentTurn { get; set; }
        public int ActivePlayerId { get; set; } = -1;
        public string ActivePlayerName { get; set; } = "";
        public Dictionary<int, Player> Players { get; set; } = new();
        public Dictionary<int, Player> NPCs { get; set; } = new();
        public Dictionary<string, City> Cities { get; set; } = new();
        public Dictionary<string, int> CityToPlayerMap { get; set; } = new();
        public List<PlayerTurnTiming> PlayerTurnTimings { get; set; } = new();
        public PlayerTurnTiming? LastPlayerTurnTiming
        {
            get => PlayerTurnTimings.Count > 0 ? PlayerTurnTimings[^1] : null;
        }

        public double LastTimestamp { get; set; } = -99.0;

        internal void FillEndTimestamp(object timestamp)
        {
            // Set timestamp to the LastPlayerTurnTiming.EndTimestamp
            if (LastPlayerTurnTiming == null)
                return;

            if (timestamp is double d)
            {
                LastPlayerTurnTiming.EndTimestamp = d;
            }
            else if (timestamp is int i)
            {
                LastPlayerTurnTiming.EndTimestamp = i;
            }
            else if (timestamp is float f)
            {
                LastPlayerTurnTiming.EndTimestamp = f;
            }
            else if (timestamp is string s && double.TryParse(s, out double parsed))
            {
                LastPlayerTurnTiming.EndTimestamp = parsed;
            }
            // else: unsupported type, do nothing
        }

        public int GetTurnFromTimestamp(double timestamp)
        {
            // If no timings, fallback to current turn
            if (PlayerTurnTimings == null || PlayerTurnTimings.Count == 0)
                return CurrentTurn;

            // Find the PlayerTurnTiming whose BeginTimestamp is <= timestamp and EndTimestamp is >= timestamp
            foreach (var timing in PlayerTurnTimings)
            {
                if (timing.BeginTimestamp <= timestamp && timing.EndTimestamp >= timestamp)
                    return timing.Turn;
            }

            // If not found, fallback to closest previous turn
            PlayerTurnTiming? closest = null;
            foreach (var timing in PlayerTurnTimings)
            {
                if (timing.BeginTimestamp <= timestamp)
                {
                    if (closest == null || timing.BeginTimestamp > closest.BeginTimestamp)
                        closest = timing;
                }
            }
            if (closest != null)
                return closest.Turn;

            // Fallback to current turn if nothing matches
            return CurrentTurn;
        }
    }
}