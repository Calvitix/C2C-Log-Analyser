using System.Collections.Generic;
using C2CLogProcessor.Models;


namespace C2CLogProcessor.Models
{
    public class City
    {
        public required string Name { get; set; }
        public int OwnerId { get; set; } = -1;
        public string OwnerName { get; set; } = "";
        
        // Threat levels
        public int ThreatLevel { get; set; }
        public int ThreatLevelHighest { get; set; }
        public int ThreatLevelTotal { get; set; }
        
        // Location
        public int X { get; set; }
        public int Y { get; set; }
        
        // Properties
        public int Population { get; set; } = 1;
        public int FoundedTurn { get; set; }
        public string? CurrentProduction { get; set; }
        public int ProductionValue { get; set; }
        public int DefendersRequested { get; set; }
        public int WorkersHave { get; set; }
        public int WorkersNeeded { get; set; }
        
        // Per-turn history
        public List<CityTurnData> History { get; set; } = new();
        public List<CityProduction> Produced { get; set; } = new();
        public List<CityOrderToCentral> OrdersToCentral { get; set; } = new();
    }
}