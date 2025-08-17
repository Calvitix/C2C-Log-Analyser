using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class UnitInventory
    {
        public int PlayerId { get; set; }
        public int Turn { get; set; }
        public Dictionary<string, UnitTypeInfo> UnitsByType { get; set; } = new();
        public int TotalUnits => CalculateTotalUnits();
        
        private int CalculateTotalUnits()
        {
            int total = 0;
            foreach (var unitType in UnitsByType.Values)
            {
                total += unitType.Count;
            }
            return total;
        }
    }
    
    public class UnitTypeInfo
    {
        public string UnitType { get; set; }
        public string UnitAIType { get; set; }
        public int Count { get; set; }
        public int CombatValue { get; set; }
        public int Movement { get; set; }
        public List<string> Promotions { get; set; } = new();
    }
}