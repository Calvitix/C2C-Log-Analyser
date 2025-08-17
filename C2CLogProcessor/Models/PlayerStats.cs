using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class PlayerStats
    {
        public int Turn { get; set; } = -99;
        public int PlayerId { get; set; } = -99;
        public int Cities { get; set; } = -99;
        public int Population { get; set; } = -99;
        public int Power { get; set; } = -99;
        public int TechPercent { get; set; } = -99;
        public int GoldRate { get; set; } = -99;
        public int ScienceRate { get; set; } = -99;
        public int CultureRate { get; set; } = -99;
        public int EspionageRate { get; set; } = -99;
        public int Treasury { get; set; } = -99;
        public int TotalGoldIncomeSelf { get; set; } = -99;
        public int TotalGoldIncomeTrade { get; set; } = -99;
        public int NumUnits { get; set; } = -99;
        public int NumSelectionGroups { get; set; } = -99;
        public int UnitUpkeep { get; set; } = -99;
        public int UnitSupplyCost { get; set; } = -99;
        public int MaintenanceCost { get; set; } = -99;
        public int CivicUpkeepCost { get; set; } = -99;
        public int CorporateMaintenance { get; set; } = -99;
        public int InflationEffect { get; set; } = -99;
        public bool IsInFinancialDifficulties { get; set; }
        public int TotalScienceOutput { get; set; } = -99;
        public int TotalEspionageOutput { get; set; } = -99;
        public int TotalCulturalOutput { get; set; } = -99;
        public int TotalFoodOutput { get; set; } = -99;
        public int TotalProductionOutput { get; set; } = -99;
        public int NationalRevIndex { get; set; } = -99;
        public int NumBarbarianUnitsKilled { get; set; } = -99;
        public int NumAnimalsSubdued { get; set; } = -99;
        public int CivicSwitches { get; set; } = -99;
        public int TotalNumCivicsSwitched { get; set; } = -99;
        public int TotalTurnsInAnarchy { get; set; } = -99;
        public double AnarchyPercent { get; set; } = -99;
        public Dictionary<string, string> Civics { get; set; } = new();
        public List<string> CivicSwitchHistory { get; set; } = new();
        public object UnitsByType { get; internal set; }
        public int Score { get; internal set; } = -99;
    }
}