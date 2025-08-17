using System;
using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class Turn
    {
        public int Number { get; set; }
        public int ActivePlayerId { get; set; }
        public string ActivePlayerName { get; set; }
        public float StartTimestamp { get; set; }
        public float EndTimestamp { get; set; }
        
        // Events that happened this turn
        public List<GameEvent> Events { get; set; } = new();
        
        // Snapshot of all players' states at this turn
        public Dictionary<int, PlayerStats> PlayerStates { get; set; } = new();
        
        public TimeSpan Duration => TimeSpan.FromMilliseconds(EndTimestamp - StartTimestamp);
    }
    
    public class GameEvent
    {
        public float Timestamp { get; set; }
        public int PlayerId { get; set; }
        public GameEventType Type { get; set; }
        public string Description { get; set; }
        public Dictionary<string, object> Data { get; set; } = new();
    }
    
    public enum GameEventType
    {
        CityFounded,
        BuildingCompleted,
        UnitBuilt,
        TechDiscovered,
        CivicChanged,
        WarDeclared,
        PeaceSigned,
        TradeAgreement,
        CityConquered,
        UnitKilled,
        WonderBuilt
    }
}