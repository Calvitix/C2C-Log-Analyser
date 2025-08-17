using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Exporters
{
    public class JsonExporter : IDataExporter
    {
        public void ExportPlayer(Player player, string filename)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            using var stream = new FileStream(filename, FileMode.Create, FileAccess.Write, FileShare.None);
            JsonSerializer.Serialize(stream, player, options);
        }

        public void ExportCities(List<City> cities, string filename)
        {
            if (cities == null || cities.Count == 0)
            {
                Console.WriteLine("No cities to export.");
                return;
            }

            try
            {
                var json = JsonSerializer.Serialize(cities, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                    Converters = { new JsonStringEnumConverter() },
                    Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                });
                File.WriteAllText(filename, json, Encoding.UTF8);
                Console.WriteLine($"City data exported to {filename} ({cities.Count} cities)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting cities to JSON: {ex.Message}");
            }
        }

        public void ExportCityHistory(City city, string cityFileName)
        {
            if (city == null)
            {
                Console.WriteLine("No city history to export.");
                return;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                    Converters = { new JsonStringEnumConverter() },
                    Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };
                var json = JsonSerializer.Serialize(city, options);
                File.WriteAllText(cityFileName, json, Encoding.UTF8);
                Console.WriteLine($"City history exported to {cityFileName}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting city history to JSON: {ex.Message}");
            }
        }

        public void ExportGameDataSummary(IEnumerable<Player> players, string filename)
        {
            if (players == null)
            {
                Console.WriteLine("No player data to export.");
                return;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                    Converters = { new JsonStringEnumConverter() },
                    Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };
                var json = JsonSerializer.Serialize(players, options);
                File.WriteAllText(filename, json, Encoding.UTF8);
                Console.WriteLine($"Game data summary exported to {filename}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game data summary to JSON: {ex.Message}");
            }
        }

        public void ExportGameTurns(int turnsFound, long elapsedMilliseconds, string filename)
        {
            try
            {
                var summary = new
                {
                    TurnsFound = turnsFound,
                    ElapsedMilliseconds = elapsedMilliseconds,
                    ElapsedSeconds = elapsedMilliseconds / 1000.0
                };
                var options = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(summary, options);
                File.WriteAllText(filename, json, Encoding.UTF8);
                Console.WriteLine($"Game turns summary exported to {filename}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting game turns summary to JSON: {ex.Message}");
            }
        }

        public void ExportPlayerTurnTimings(List<PlayerTurnTiming> timings, string filename)
        {
            if (timings == null || timings.Count == 0)
            {
                Console.WriteLine("No player turn timings to export.");
                return;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
                };
                var json = JsonSerializer.Serialize(timings, options);
                File.WriteAllText(filename, json, Encoding.UTF8);
                Console.WriteLine($"Player turn timings exported to {filename}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exporting player turn timings to JSON: {ex.Message}");
            }
        }

        public void ExportAll(
            IEnumerable<Player> players,
            List<City> cities,
            List<PlayerTurnTiming> timings,
            int turnsFound,
            long elapsedMilliseconds,
            string outputDirectory,
            GameState? gameState = null // Add optional GameState parameter
        )
        {
            Directory.CreateDirectory(outputDirectory);

            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new JsonStringEnumConverter() },
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };

            // Export all players (one file per player)
            //foreach (var player in players)
            //{
            //    var playerFile = Path.Combine(outputDirectory, $"player_{player.Id}_{player.Name}_stats.json");
            //    File.WriteAllText(playerFile, JsonSerializer.Serialize(player, options), Encoding.UTF8);
            //}

            // Export all cities (one file for all, and one per city history)
            var citiesFile = Path.Combine(outputDirectory, "cities.json");
            File.WriteAllText(citiesFile, JsonSerializer.Serialize(cities, options), Encoding.UTF8);

            //foreach (var city in cities)
            //{
            //    var cityFile = Path.Combine(outputDirectory, $"city_{city.OwnerId}_{city.Name}_history.json");
            //    File.WriteAllText(cityFile, JsonSerializer.Serialize(city, options), Encoding.UTF8);
            //}

            // Export player turn timings
            var timingsFile = Path.Combine(outputDirectory, "player_turn_timings.json");
            File.WriteAllText(timingsFile, JsonSerializer.Serialize(timings, options), Encoding.UTF8);

            // Export game data summary
            var summaryFile = Path.Combine(outputDirectory, "game_data_summary.json");
            File.WriteAllText(summaryFile, JsonSerializer.Serialize(players, options), Encoding.UTF8);

            // Export game turns summary
            var turnsFile = Path.Combine(outputDirectory, "game_turns_summary.json");
            var turnsSummary = new
            {
                TurnsFound = turnsFound,
                ElapsedMilliseconds = elapsedMilliseconds,
                ElapsedSeconds = elapsedMilliseconds / 1000.0
            };
            File.WriteAllText(turnsFile, JsonSerializer.Serialize(turnsSummary, options), Encoding.UTF8);

            // Export unit evaluations if GameState is provided
            if (gameState != null)
            {
                var unitEvalFile = Path.Combine(outputDirectory, "unit_evaluations.json");
                ExportUnitEvaluations(gameState, unitEvalFile);
            }
        }

        public void ExportUnitEvaluations(GameState gameState, string outputPath)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new JsonStringEnumConverter() },
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };
            using var stream = new FileStream(outputPath, FileMode.Create, FileAccess.Write);
            JsonSerializer.Serialize(stream, gameState.Players.Values.Select(p => p.UnitEvaluation).ToList(), options);
        }
    }
}