using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Exporters
{
    public class CsvExporter : IDataExporter
    {
        public void ExportCities(List<City> cities, string filename)
        {
            if (cities == null || cities.Count == 0)
            {
                Console.WriteLine("No cities to export.");
                return;
            }

            try
            {
                using (var writer = new StreamWriter(filename, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');
                    
                    // Write header
                    writer.WriteLine("Name,OwnerId,OwnerName,ThreatLevel,ThreatHighest,ThreatTotal," +
                                   "Population,X,Y,FoundedTurn,CurrentProduction,ProductionValue," +
                                   "DefendersRequested,WorkersHave,WorkersNeeded");
                    
                    // Write data sorted by owner and name
                    foreach (var city in cities.OrderBy(c => c.OwnerId).ThenBy(c => c.Name))
                    {
                        writer.WriteLine($"\"{EscapeCsvField(city.Name)}\",{city.OwnerId}," +
                                       $"\"{EscapeCsvField(city.OwnerName)}\"," +
                                       $"{city.ThreatLevel},{city.ThreatLevelHighest},{city.ThreatLevelTotal}," +
                                       $"{city.Population},{city.X},{city.Y},{city.FoundedTurn}," +
                                       $"\"{EscapeCsvField(city.CurrentProduction)}\",{city.ProductionValue}," +
                                       $"{city.DefendersRequested},{city.WorkersHave},{city.WorkersNeeded}");
                    }
                }
                
                Console.WriteLine($"City data exported to {filename} ({cities.Count} cities)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting cities: {ex.Message}");
            }
        }

        public void ExportPlayer(Player player, string filename)
        {
            try
            {
                using (var writer = new StreamWriter(filename, false, Encoding.UTF8))
                {
                    // Write BOM
                    writer.Write('\uFEFF');

                    // Write header for PlayerStats
                    writer.WriteLine(
                        "PlayerId,Name,Type,IsHuman,Turn,Cities,Population,Power,TechPercent," +
                        "GoldRate,ScienceRate,CultureRate,EspionageRate,Treasury,TotalGoldIncomeSelf,TotalGoldIncomeTrade," +
                        "NumUnits,NumSelectionGroups,UnitUpkeep,UnitSupplyCost,MaintenanceCost,CivicUpkeepCost,CorporateMaintenance,InflationEffect," +
                        "IsInFinancialDifficulties,TotalScienceOutput,TotalEspionageOutput,TotalCulturalOutput,TotalFoodOutput,TotalProductionOutput," +
                        "NationalRevIndex,NumBarbarianUnitsKilled,NumAnimalsSubdued,CivicSwitches,TotalNumCivicsSwitched,TotalTurnsInAnarchy,AnarchyPercent," +
                        "Civics,CivicSwitchHistory,MetPlayers,AtWarWith,OwnedCities"
                    );

                    // Export all stat history
                    var statsList = player.StatsHistory ?? new List<PlayerStats>();
                    if (statsList.Count == 0 && player.CurrentStats != null)
                        statsList.Add(player.CurrentStats);

                    foreach (var stats in statsList)
                    {
                        writer.WriteLine(
                            $"{player.Id},\"{EscapeCsvField(player.Name)}\"," +
                            $"{player.Type},{player.IsHuman}," +
                            $"{stats.Turn},{stats.Cities},{stats.Population},{stats.Power},{stats.TechPercent}," +
                            $"{stats.GoldRate},{stats.ScienceRate},{stats.CultureRate},{stats.EspionageRate},{stats.Treasury},{stats.TotalGoldIncomeSelf},{stats.TotalGoldIncomeTrade}," +
                            $"{stats.NumUnits},{stats.NumSelectionGroups},{stats.UnitUpkeep},{stats.UnitSupplyCost},{stats.MaintenanceCost},{stats.CivicUpkeepCost},{stats.CorporateMaintenance},{stats.InflationEffect}," +
                            $"{stats.IsInFinancialDifficulties},{stats.TotalScienceOutput},{stats.TotalEspionageOutput},{stats.TotalCulturalOutput},{stats.TotalFoodOutput},{stats.TotalProductionOutput}," +
                            $"{stats.NationalRevIndex},{stats.NumBarbarianUnitsKilled},{stats.NumAnimalsSubdued},{stats.CivicSwitches},{stats.TotalNumCivicsSwitched},{stats.TotalTurnsInAnarchy},{stats.AnarchyPercent}," +
                            $"\"{EscapeCsvField(string.Join(";", stats.Civics?.Select(kv => $"{kv.Key}:{kv.Value}") ?? Enumerable.Empty<string>()))}\"," +
                            $"\"{EscapeCsvField(string.Join(";", stats.CivicSwitchHistory ?? new List<string>()))}\"," +
                            $"\"{string.Join(';', player.MetPlayers ?? new HashSet<int>())}\"," +
                            $"\"{string.Join(';', player.AtWarWith ?? new HashSet<int>())}\"," +
                            $"\"{string.Join(';', player.OwnedCityNames ?? new List<string>())}\""
                        );
                    }

                    // Export ScoreHistory
                    writer.WriteLine();
                    writer.WriteLine("ScoreHistory: Turn,Population,Territory,Technologies,Wonders,Total,VictoryScore,EconomyAvg,IndustryAvg,AgricultureAvg");
                    foreach (var score in player.ScoreHistory ?? new List<PlayerScoreHistory>())
                    {
                        writer.WriteLine($"{score.Turn},{score.Population},{score.Territory},{score.Technologies},{score.Wonders},{score.Total},{score.VictoryScore},{score.EconomyAvg},{score.IndustryAvg},{score.AgricultureAvg}");
                    }

                    // Export Messages
                    writer.WriteLine();
                    writer.WriteLine("Messages:");
                    foreach (var msg in player.Messages ?? new List<string>())
                        writer.WriteLine(EscapeCsvField(msg));
                }

                Console.WriteLine($"Player data exported to {filename} ({player.StatsHistory?.Count ?? 0} stat records)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting players: {ex.Message}");
            }
        }

        public void ExportPlayerTurnTimings(List<PlayerTurnTiming> timings, string filename)
        {
            using (var writer = new StreamWriter(filename, false, Encoding.UTF8))
            {
                writer.WriteLine("Turn,PlayerId,PlayerName,BeginTimestamp,EndTimestamp");
                foreach (var t in timings.OrderBy(x => x.Turn).ThenBy(x => x.PlayerId))
                {

                    writer.WriteLine($"{t.Turn},{t.PlayerId},\"{EscapeCsvField(t.PlayerName)}\",{t.BeginTimestamp.ToString(CultureInfo.InvariantCulture)},{t.EndTimestamp.ToString(CultureInfo.InvariantCulture)}");
                }
            }
        }

        private string EscapeCsvField(string field)
        {
            if (string.IsNullOrEmpty(field))
                return "";
            
            // Escape quotes by doubling them
            return field.Replace("\"", "\"\"");
        }

        void IDataExporter.ExportCityHistory(City city, string cityFileName)
        {
            if (city == null)
            {
                Console.WriteLine("No city history to export.");
                return;
            }

            try
            {
                using (var writer = new StreamWriter(cityFileName, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');

                    // Write city info
                    writer.WriteLine("Name,OwnerId,OwnerName,ThreatLevel,ThreatHighest,ThreatTotal,Population,X,Y,FoundedTurn,CurrentProduction,ProductionValue,DefendersRequested,WorkersHave,WorkersNeeded");
                    writer.WriteLine($"\"{EscapeCsvField(city.Name)}\",{city.OwnerId},\"{EscapeCsvField(city.OwnerName)}\",{city.ThreatLevel},{city.ThreatLevelHighest},{city.ThreatLevelTotal},{city.Population},{city.X},{city.Y},{city.FoundedTurn},\"{EscapeCsvField(city.CurrentProduction)}\",{city.ProductionValue},{city.DefendersRequested},{city.WorkersHave},{city.WorkersNeeded}");

                    // Write per-turn history
                    writer.WriteLine();
                    writer.WriteLine("Turn,Population,Production,FoodSurplus,LocalRevIndex,Maintenance,Income,Science,Espionage,Culture,NetHappiness,NetHealth,FoodTradeYield,ProductionTradeYield,CommerceTradeYield,Criminalite,Maladie,PollutionEau,PollutionAir,Education,RisqueIncendie,Tourisme,PropertyBuildings");
                    foreach (var turnData in city.History.OrderBy(h => h.Turn))
                    {
                        string propertyBuildings = "";
                        if (turnData.PropertyBuildings != null && turnData.PropertyBuildings.Count > 0)
                        {
                            propertyBuildings = string.Join(";",
                                turnData.PropertyBuildings.Select(
                                    kv => $"{kv.Key}:{string.Join("|", kv.Value ?? new List<string>())}"
                                )
                            );
                        }

                        writer.WriteLine(
                            $"{turnData.Turn},{turnData.Population},{turnData.Production},{turnData.FoodSurplus},{turnData.LocalRevIndex},{turnData.Maintenance},{turnData.Income},{turnData.Science},{turnData.Espionage},{turnData.Culture},{turnData.NetHappiness},{turnData.NetHealth},{turnData.FoodTradeYield},{turnData.ProductionTradeYield},{turnData.CommerceTradeYield},{turnData.Criminalite},{turnData.Maladie},{turnData.PollutionEau},{turnData.PollutionAir},{turnData.Education},{turnData.RisqueIncendie},{turnData.Tourisme},\"{EscapeCsvField(propertyBuildings)}\""
                        );
                    }

                    // Write produced items
                    writer.WriteLine();
                    writer.WriteLine("Produced: Turn,ProductName");
                    foreach (var prod in city.Produced ?? new List<CityProduction>())
                        writer.WriteLine($"{prod.Turn},{EscapeCsvField(prod.ProductName)}");

                    // Write orders to central
                    writer.WriteLine();
                    writer.WriteLine("OrdersToCentral: Turn,OrderType,AIType,Strength,Priority");
                    foreach (var order in city.OrdersToCentral ?? new List<CityOrderToCentral>())
                        writer.WriteLine($"{order.Turn},{order.OrderType},{order.AIType},{order.Strength},{order.Priority}");
                }

                Console.WriteLine($"City history exported to {cityFileName}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting city history: {ex.Message}");
            }
            
        }

        void IDataExporter.ExportGameDataSummary(IEnumerable<Player> players, string filename)
        {
            if (players == null || !players.Any())
            {
                Console.WriteLine("No player data to export.");
                return;
            }

            try
            {
                using (var writer = new StreamWriter(filename, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');

                    // Write header
                    writer.WriteLine("PlayerId,Name,Type,IsHuman,TotalCities,TotalPopulation,TotalPower,TotalGold,TotalScience,TotalCulture,TotalEspionage");

                    foreach (var player in players.OrderBy(p => p.Id))
                    {
                        var stats = player.CurrentStats ?? player.StatsHistory?.LastOrDefault();
                        if (stats == null)
                            continue;

                        writer.WriteLine(
                            $"{player.Id},\"{EscapeCsvField(player.Name)}\"," +
                            $"{player.Type},{player.IsHuman}," +
                            $"{stats.Cities},{stats.Population},{stats.Power},{stats.Treasury},{stats.TotalScienceOutput},{stats.TotalCulturalOutput},{stats.TotalEspionageOutput}"
                        );
                    }
                }

                Console.WriteLine($"Game data summary exported to {filename} ({players.Count()} players)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game data summary: {ex.Message}");
            }
        }

        void IDataExporter.ExportGameTurns(int turnsFound, long elapsedMilliseconds, string filename)
        {
            try
            {
                using (var writer = new StreamWriter(filename, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');
                    // Write header
                    writer.WriteLine("TurnsFound,ElapsedMilliseconds,ElapsedSeconds");
                    // Write data
                    writer.WriteLine($"{turnsFound},{elapsedMilliseconds},{elapsedMilliseconds / 1000.0:F3}");
                }
                Console.WriteLine($"Game turns summary exported to {filename} (turns: {turnsFound}, time: {elapsedMilliseconds} ms)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game turns summary: {ex.Message}");
            }
        }

        public void ExportAll(
            IEnumerable<Player> players,
            List<City> cities,
            List<PlayerTurnTiming> timings,
            int turnsFound,
            long elapsedMilliseconds,
            string outputDirectory,
            GameState? gameState = null
        )
        {
            Directory.CreateDirectory(outputDirectory);

            // Export players, cities, timings, etc. as needed...

            // Export unit evaluations if GameState is provided
            if (gameState != null)
            {
                var unitEvalFile = Path.Combine(outputDirectory, "unit_evaluations.csv");
                ExportUnitEvaluations(gameState, unitEvalFile);
            }
        }

        private void ExportCityHistory(City city, string cityFile)
        {
            if (city == null)
            {
                Console.WriteLine("No city history to export.");
                return;
            }

            try
            {
                using (var writer = new StreamWriter(cityFile, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');

                    // Write city info
                    writer.WriteLine("Name,OwnerId,OwnerName,ThreatLevel,ThreatHighest,ThreatTotal,Population,X,Y,FoundedTurn,CurrentProduction,ProductionValue,DefendersRequested,WorkersHave,WorkersNeeded");
                    writer.WriteLine($"\"{EscapeCsvField(city.Name)}\",{city.OwnerId},\"{EscapeCsvField(city.OwnerName)}\",{city.ThreatLevel},{city.ThreatLevelHighest},{city.ThreatLevelTotal},{city.Population},{city.X},{city.Y},{city.FoundedTurn},\"{EscapeCsvField(city.CurrentProduction)}\",{city.ProductionValue},{city.DefendersRequested},{city.WorkersHave},{city.WorkersNeeded}");

                    // Write per-turn history
                    writer.WriteLine();
                    writer.WriteLine("Turn,Population,Production,FoodSurplus,LocalRevIndex,Maintenance,Income,Science,Espionage,Culture,NetHappiness,NetHealth,FoodTradeYield,ProductionTradeYield,CommerceTradeYield,Criminalite,Maladie,PollutionEau,PollutionAir,Education,RisqueIncendie,Tourisme,PropertyBuildings");
                    foreach (var turnData in city.History.OrderBy(h => h.Turn))
                    {
                        string propertyBuildings = "";
                        if (turnData.PropertyBuildings != null && turnData.PropertyBuildings.Count > 0)
                        {
                            propertyBuildings = string.Join(";",
                                turnData.PropertyBuildings.Select(
                                    kv => $"{kv.Key}:{string.Join("|", kv.Value ?? new List<string>())}"
                                )
                            );
                        }

                        writer.WriteLine(
                            $"{turnData.Turn},{turnData.Population},{turnData.Production},{turnData.FoodSurplus},{turnData.LocalRevIndex},{turnData.Maintenance},{turnData.Income},{turnData.Science},{turnData.Espionage},{turnData.Culture},{turnData.NetHappiness},{turnData.NetHealth},{turnData.FoodTradeYield},{turnData.ProductionTradeYield},{turnData.CommerceTradeYield},{turnData.Criminalite},{turnData.Maladie},{turnData.PollutionEau},{turnData.PollutionAir},{turnData.Education},{turnData.RisqueIncendie},{turnData.Tourisme},\"{EscapeCsvField(propertyBuildings)}\""
                        );
                    }

                    // Write produced items
                    writer.WriteLine();
                    writer.WriteLine("Produced: Turn,ProductName");
                    foreach (var prod in city.Produced ?? new List<CityProduction>())
                        writer.WriteLine($"{prod.Turn},{EscapeCsvField(prod.ProductName)}");

                    // Write orders to central
                    writer.WriteLine();
                    writer.WriteLine("OrdersToCentral: Turn,OrderType,AIType,Strength,Priority");
                    foreach (var order in city.OrdersToCentral ?? new List<CityOrderToCentral>())
                        writer.WriteLine($"{order.Turn},{order.OrderType},{order.AIType},{order.Strength},{order.Priority}");
                }

                Console.WriteLine($"City history exported to {cityFile}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting city history: {ex.Message}");
            }
        }

        private void ExportGameDataSummary(IEnumerable<Player> players, string summaryFile)
        {
            if (players == null || !players.Any())
            {
                Console.WriteLine("No player data to export.");
                return;
            }

            try
            {
                using (var writer = new StreamWriter(summaryFile, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');

                    // Write header
                    writer.WriteLine("PlayerId,Name,Type,IsHuman,TotalCities,TotalPopulation,TotalPower,TotalGold,TotalScience,TotalCulture,TotalEspionage");

                    foreach (var player in players.OrderBy(p => p.Id))
                    {
                        var stats = player.CurrentStats ?? player.StatsHistory?.LastOrDefault();
                        if (stats == null)
                            continue;

                        writer.WriteLine(
                            $"{player.Id},\"{EscapeCsvField(player.Name)}\"," +
                            $"{player.Type},{player.IsHuman}," +
                            $"{stats.Cities},{stats.Population},{stats.Power},{stats.Treasury},{stats.TotalScienceOutput},{stats.TotalCulturalOutput},{stats.TotalEspionageOutput}"
                        );
                    }
                }

                Console.WriteLine($"Game data summary exported to {summaryFile}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game data summary: {ex.Message}");
            }
        }

        private void ExportGameTurns(int turnsFound, long elapsedMilliseconds, string turnsFile)
        {
            try
            {
                using (var writer = new StreamWriter(turnsFile, false, Encoding.UTF8))
                {
                    // Write BOM for Excel UTF-8 recognition
                    writer.Write('\uFEFF');
                    // Write header
                    writer.WriteLine("TurnsFound,ElapsedMilliseconds,ElapsedSeconds");
                    // Write data
                    writer.WriteLine($"{turnsFound},{elapsedMilliseconds},{elapsedMilliseconds / 1000.0:F3}");
                }
                Console.WriteLine($"Game turns summary exported to {turnsFile}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game turns summary: {ex.Message}");
            }
        }

        public void ExportUnitEvaluations(GameState gameState, string outputPath)
        {
            using var writer = new StreamWriter(outputPath, false, Encoding.UTF8);
            writer.WriteLine("PlayerId,Turn,CityName,UnitType,UnitAIType,CombatValue,Moves,CalculatedValue,IsBetterUnit,BaseValue,FinalValue,UnitName");
            foreach (var eval in gameState.Players.Values.Select(p => p.UnitEvaluation).Where(e => e != null))
            {
                foreach (var e in eval.Evaluations)
                {
                    writer.WriteLine($"{eval.PlayerId},{e.Turn},{e.CityName},{e.UnitType},{e.UnitAIType},{e.CombatValue},{e.Moves},{e.CalculatedValue},{e.IsBetterUnit},{e.BaseValue},{e.FinalValue},{e.UnitName}");
                }
            }
        }
    }
}