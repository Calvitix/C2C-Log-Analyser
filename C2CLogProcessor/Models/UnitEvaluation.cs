using System.Collections.Generic;

namespace C2CLogProcessor.Models
{
    public class UnitEvaluationTurn
    {
        public int Turn { get; set; }
        public int PlayerId { get; set; }
        public string CityName { get; set; }
        public string UnitType { get; set; }
        public string UnitAIType { get; set; }
        public int CombatValue { get; set; }
        public int Moves { get; set; }
        public int CalculatedValue { get; set; }
        public bool IsBetterUnit { get; set; }
        public int? BaseValue { get; set; }
        public int? FinalValue { get; set; }
        public string? UnitName { get; set; }
    }

    public class BestUnitAIHistory
    {
        public string UnitAIType { get; set; }
        public string UnitType { get; set; }
        public string UnitName { get; set; }
        public int FirstTurn { get; set; }
        public int FinalValue { get; set; }

        public int BaseValue { get; set; }
    }

    public class PlayerUnitEvaluation
    {
        public int PlayerId { get; set; }

        public int LastTurn { get; set; }
        public List<UnitEvaluationTurn> Evaluations { get; set; } = new();
        public Dictionary<string, List<BestUnitAIHistory> > BestUnitsByAIType { get; set; } = new();
    }
}