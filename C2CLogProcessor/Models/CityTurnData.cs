using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class CityTurnData
    {
        public int Turn { get; set; }
        public int Population { get; set; }
        public int Production { get; set; }
        public int FoodSurplus { get; set; }
        public int LocalRevIndex { get; set; }
        public int Maintenance { get; set; }
        public int Income { get; set; }
        public int Science { get; set; }
        public int Espionage { get; set; }
        public int Culture { get; set; }
        public int NetHappiness { get; set; }
        public int NetHealth { get; set; }
        public int FoodTradeYield { get; set; }
        public int ProductionTradeYield { get; set; }
        public int CommerceTradeYield { get; set; }

        // Add properties for each city property you want to track (value only)
        public int Criminalite { get; set; }
        public int Maladie { get; set; }
        public int PollutionEau { get; set; }
        public int PollutionAir { get; set; }
        public int Education { get; set; }
        public int RisqueIncendie { get; set; }
        public int Tourisme { get; set; }
        public Dictionary<string, List<string>> PropertyBuildings { get; set; } = new();
        public int CriminaliteChange { get; set; }
        public int MaladieChange { get; set; }
        public int PollutionEauChange { get; set; }
        public int PollutionAirChange { get; set; }
        public int EducationChange { get; set; }
        public int Ignore { get; internal set; }
        public int RisqueIncendieChange { get; internal set; }
        public int TourismeChange { get; internal set; }
    }
}