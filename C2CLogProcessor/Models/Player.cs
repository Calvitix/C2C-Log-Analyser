using System;
using System.Collections.Generic;



namespace C2CLogProcessor.Models
{
    public enum UpdateStatsMode
    {
        ResetAndAdd,
        CompleteOnlyEmpty,
        Finalize
    }
    public class Player
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public bool IsHuman { get; set; } // true if Id < 40
        public PlayerType Type { get; set; }
        
        public PlayerStats? CurrentStats { get; set; }
        
        // Historical data
        public List<PlayerStats> StatsHistory { get; set; } = new();
        public List<string> OwnedCityNames { get; set; } = new();
        public List<PlayerScoreHistory> ScoreHistory { get; set; } = new();
        
        // Relationships
        public HashSet<int> MetPlayers { get; set; } = new();
        public HashSet<int> AtWarWith { get; set; } = new();
        
        public List<string> Messages { get; set; } = new();
        
        public List<UnitInventory> UnitInventories { get; set; } = new();

        // Add this property to integrate unit evaluations
        public PlayerUnitEvaluation UnitEvaluation { get; set; } = new PlayerUnitEvaluation();

        public int PlayerUnitEvaluationLastTurn         {
            get => UnitEvaluation.LastTurn;
            set => UnitEvaluation.LastTurn = value;
        }

        public Player(int id, string name)
        {
            Id = id;
            Name = name;
            IsHuman = id < 40;
            Type = DeterminePlayerType(id, name);
            UnitEvaluation.PlayerId = id;
        }
        
        private PlayerType DeterminePlayerType(int id, string name)
        {
            if (id < 40) return PlayerType.Human;
            if (name.Contains("Barbares") || name.Contains("Barbarian")) return PlayerType.Barbarian;
            if (name.Contains("Bêtes") || name.Contains("Beast")) return PlayerType.Beast;
            if (name.Contains("Prédateurs") || name.Contains("Predator")) return PlayerType.Predator;
            if (name.Contains("Créatures") || name.Contains("Creature")) return PlayerType.Creature;
            if (name.Contains("Insectoïdes") || name.Contains("Insectoid")) return PlayerType.Insectoid;
            if (name.Contains("Néanderthaliens") || name.Contains("Neanderthal")) return PlayerType.Neanderthal;
            return PlayerType.NPC;
        }
        
        public void UpdateStats(PlayerStats stats, UpdateStatsMode mode = UpdateStatsMode.ResetAndAdd)
        {
            Boolean Debug = true;
            switch (mode)
            {
                case UpdateStatsMode.ResetAndAdd:
                    var finalized = CurrentStats != null ? CloneStats(CurrentStats) : CloneStats(stats);
                    CurrentStats = stats;
                    StatsHistory.Add(finalized);
                    break;

                case UpdateStatsMode.CompleteOnlyEmpty:
                    if (CurrentStats == stats && Debug)
                    {
                        //Console.WriteLine("Same object");
                    }
                    else if (CurrentStats != null)
                    {
                        FillNoValueWith(CurrentStats, stats);
                    }
                    if (StatsHistory.Count > 0)
                    {
                        if (StatsHistory[^1] == stats)
                        {
                            Console.WriteLine("LastHistory and CurrenStats are Same object");
                        }
                        FillNoValueWith(StatsHistory[^1], stats);
                    }
                    break;

                case UpdateStatsMode.Finalize:
                    if (CurrentStats != null)
                    {
                        //FillNoValueWith(CurrentStats, 0);
                    }
                    if (StatsHistory.Count > 0)
                    {
                        //FillNoValueWith(StatsHistory[^1], 0);
                    }
                    //var finalized = CurrentStats != null ? CloneStats(CurrentStats) : stats;
                    //StatsHistory.Add(finalized);
                    break;
            }
        }

        // Helper to fill all -99 values in target with values from source
        private void FillNoValueWith(PlayerStats target, PlayerStats source)
        {
            if (target.Turn == -99) target.Turn = source.Turn;
            if (target.PlayerId == -99) target.PlayerId = source.PlayerId;
            if (target.Cities == -99) target.Cities = source.Cities;
            if (target.Population == -99) target.Population = source.Population;
            if (target.Power == -99) target.Power = source.Power;
            if (target.TechPercent == -99) target.TechPercent = source.TechPercent;
            if (target.GoldRate == -99) target.GoldRate = source.GoldRate;
            if (target.ScienceRate == -99) target.ScienceRate = source.ScienceRate;
            if (target.CultureRate == -99) target.CultureRate = source.CultureRate;
            if (target.EspionageRate == -99) target.EspionageRate = source.EspionageRate;
            if (target.Treasury == -99) target.Treasury = source.Treasury;
            if (target.TotalGoldIncomeSelf == -99) target.TotalGoldIncomeSelf = source.TotalGoldIncomeSelf;
            if (target.TotalGoldIncomeTrade == -99) target.TotalGoldIncomeTrade = source.TotalGoldIncomeTrade;
            if (target.NumUnits == -99) target.NumUnits = source.NumUnits;
            if (target.NumSelectionGroups == -99) target.NumSelectionGroups = source.NumSelectionGroups;
            if (target.UnitUpkeep == -99) target.UnitUpkeep = source.UnitUpkeep;
            if (target.UnitSupplyCost == -99) target.UnitSupplyCost = source.UnitSupplyCost;
            if (target.MaintenanceCost == -99) target.MaintenanceCost = source.MaintenanceCost;
            if (target.CivicUpkeepCost == -99) target.CivicUpkeepCost = source.CivicUpkeepCost;
            if (target.CorporateMaintenance == -99) target.CorporateMaintenance = source.CorporateMaintenance;
            if (target.InflationEffect == -99) target.InflationEffect = source.InflationEffect;
            if (target.TotalScienceOutput == -99) target.TotalScienceOutput = source.TotalScienceOutput;
            if (target.TotalEspionageOutput == -99) target.TotalEspionageOutput = source.TotalEspionageOutput;
            if (target.TotalCulturalOutput == -99) target.TotalCulturalOutput = source.TotalCulturalOutput;
            if (target.TotalFoodOutput == -99) target.TotalFoodOutput = source.TotalFoodOutput;
            if (target.TotalProductionOutput == -99) target.TotalProductionOutput = source.TotalProductionOutput;
            if (target.NationalRevIndex == -99) target.NationalRevIndex = source.NationalRevIndex;
            if (target.NumBarbarianUnitsKilled == -99) target.NumBarbarianUnitsKilled = source.NumBarbarianUnitsKilled;
            if (target.NumAnimalsSubdued == -99) target.NumAnimalsSubdued = source.NumAnimalsSubdued;
            if (target.CivicSwitches == -99) target.CivicSwitches = source.CivicSwitches;
            if (target.TotalNumCivicsSwitched == -99) target.TotalNumCivicsSwitched = source.TotalNumCivicsSwitched;
            if (target.TotalTurnsInAnarchy == -99) target.TotalTurnsInAnarchy = source.TotalTurnsInAnarchy;
            if (target.AnarchyPercent == -99) target.AnarchyPercent = source.AnarchyPercent;
            if (target.Score == -99) target.Score = source.Score;
        }

        // Helper to fill all -99 values in target with a constant value
        private void FillNoValueWith(PlayerStats target, int value)
        {
            if (target.Turn == -99) target.Turn = value;
            if (target.PlayerId == -99) target.PlayerId = value;
            if (target.Cities == -99) target.Cities = value;
            if (target.Population == -99) target.Population = value;
            if (target.Power == -99) target.Power = value;
            if (target.TechPercent == -99) target.TechPercent = value;
            if (target.GoldRate == -99) target.GoldRate = value;
            if (target.ScienceRate == -99) target.ScienceRate = value;
            if (target.CultureRate == -99) target.CultureRate = value;
            if (target.EspionageRate == -99) target.EspionageRate = value;
            if (target.Treasury == -99) target.Treasury = value;
            if (target.TotalGoldIncomeSelf == -99) target.TotalGoldIncomeSelf = value;
            if (target.TotalGoldIncomeTrade == -99) target.TotalGoldIncomeTrade = value;
            if (target.NumUnits == -99) target.NumUnits = value;
            if (target.NumSelectionGroups == -99) target.NumSelectionGroups = value;
            if (target.UnitUpkeep == -99) target.UnitUpkeep = value;
            if (target.UnitSupplyCost == -99) target.UnitSupplyCost = value;
            if (target.MaintenanceCost == -99) target.MaintenanceCost = value;
            if (target.CivicUpkeepCost == -99) target.CivicUpkeepCost = value;
            if (target.CorporateMaintenance == -99) target.CorporateMaintenance = value;
            if (target.InflationEffect == -99) target.InflationEffect = value;
            if (target.TotalScienceOutput == -99) target.TotalScienceOutput = value;
            if (target.TotalEspionageOutput == -99) target.TotalEspionageOutput = value;
            if (target.TotalCulturalOutput == -99) target.TotalCulturalOutput = value;
            if (target.TotalFoodOutput == -99) target.TotalFoodOutput = value;
            if (target.TotalProductionOutput == -99) target.TotalProductionOutput = value;
            if (target.NationalRevIndex == -99) target.NationalRevIndex = value;
            if (target.NumBarbarianUnitsKilled == -99) target.NumBarbarianUnitsKilled = value;
            if (target.NumAnimalsSubdued == -99) target.NumAnimalsSubdued = value;
            if (target.CivicSwitches == -99) target.CivicSwitches = value;
            if (target.TotalNumCivicsSwitched == -99) target.TotalNumCivicsSwitched = value;
            if (target.TotalTurnsInAnarchy == -99) target.TotalTurnsInAnarchy = value;
            if (target.AnarchyPercent == -99) target.AnarchyPercent = value;
            if (target.Score == -99) target.Score = value;
        }

        // Helper to clone PlayerStats
        private PlayerStats CloneStats(PlayerStats stats)
        {
            return new PlayerStats
            {
                Turn = stats.Turn,
                PlayerId = stats.PlayerId,
                Cities = stats.Cities,
                Population = stats.Population,
                Power = stats.Power,
                TechPercent = stats.TechPercent,
                GoldRate = stats.GoldRate,
                ScienceRate = stats.ScienceRate,
                CultureRate = stats.CultureRate,
                EspionageRate = stats.EspionageRate,
                Treasury = stats.Treasury,
                TotalGoldIncomeSelf = stats.TotalGoldIncomeSelf,
                TotalGoldIncomeTrade = stats.TotalGoldIncomeTrade,
                NumUnits = stats.NumUnits,
                NumSelectionGroups = stats.NumSelectionGroups,
                UnitUpkeep = stats.UnitUpkeep,
                UnitSupplyCost = stats.UnitSupplyCost,
                MaintenanceCost = stats.MaintenanceCost,
                CivicUpkeepCost = stats.CivicUpkeepCost,
                CorporateMaintenance = stats.CorporateMaintenance,
                InflationEffect = stats.InflationEffect,
                IsInFinancialDifficulties = stats.IsInFinancialDifficulties,
                TotalScienceOutput = stats.TotalScienceOutput,
                TotalEspionageOutput = stats.TotalEspionageOutput,
                TotalCulturalOutput = stats.TotalCulturalOutput,
                TotalFoodOutput = stats.TotalFoodOutput,
                TotalProductionOutput = stats.TotalProductionOutput,
                NationalRevIndex = stats.NationalRevIndex,
                NumBarbarianUnitsKilled = stats.NumBarbarianUnitsKilled,
                NumAnimalsSubdued = stats.NumAnimalsSubdued,
                CivicSwitches = stats.CivicSwitches,
                TotalNumCivicsSwitched = stats.TotalNumCivicsSwitched,
                TotalTurnsInAnarchy = stats.TotalTurnsInAnarchy,
                AnarchyPercent = stats.AnarchyPercent,
                Civics = new Dictionary<string, string>(stats.Civics),
                CivicSwitchHistory = new List<string>(stats.CivicSwitchHistory),
                UnitsByType = stats.UnitsByType,
                Score = stats.Score
            };
        }

        // Add this method to the Player class
        public void UpdateStats<T>(string propertyName, T value)
        {
            if (CurrentStats != null)
            {
                var prop = typeof(PlayerStats).GetProperty(propertyName);
                if (prop != null && prop.CanWrite)
                {
                    prop.SetValue(CurrentStats, value);
                }
            }
            if (StatsHistory.Count > 0)
            {
                var prop = typeof(PlayerStats).GetProperty(propertyName);
                if (prop != null && prop.CanWrite)
                {
                    prop.SetValue(StatsHistory[^1], value);
                }
            }
        }
    }
    
    public enum PlayerType
    {
        Human,
        Barbarian,
        Beast,
        Predator,
        Creature,
        Insectoid,
        Neanderthal,
        NPC
    }

    public class PlayerScoreHistory
    {
        public int Turn { get; set; }
        public int Population { get; set; }
        public int Territory { get; set; }
        public int Technologies { get; set; }
        public int Wonders { get; set; }
        public int Total { get; set; }
        public int? VictoryScore { get; set; }

        // Add these properties for averages
        public int? EconomyAvg { get; set; }
        public int? IndustryAvg { get; set; }
        public int? AgricultureAvg { get; set; }
    }
}