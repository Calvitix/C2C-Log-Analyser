using C2CLogProcessor.Exporters;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers;
using C2CLogProcessor.Parsers.Categorizers;
using C2CLogProcessor.Services;
using C2CLogProcessor.Services.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;


namespace C2CLogProcessor
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Register encoding provider
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

                // Setup dependency injection
                var serviceProvider = ConfigureServices();
                
                // Get the main application service
                var app = serviceProvider.GetRequiredService<Application>();
                
                // Run the application
                app.Run(args);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
            }
            
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }

        private static ServiceProvider ConfigureServices()
        {
            var services = new ServiceCollection();

            // Register services
            services.AddSingleton<IFileService, FileService>();
            services.AddSingleton<IEncodingDetector, EncodingDetector>();
            services.AddSingleton<ILogParser, LogParser>();
            services.AddSingleton<ILogCategorizer, LogCategorizer>();
            services.AddSingleton<IDataExporter, CsvExporter>();
            services.AddSingleton<Application>();

            return services.BuildServiceProvider();
        }
    }

    public class Application
    {
        private readonly ILogParser _parser;
        private readonly IDataExporter _exporter;

        public Application(ILogParser parser, IDataExporter exporter)
        {
            _parser = parser;
            _exporter = exporter;
        }

        public static int CityHistoryInterval { get; private set; } = 1;
        public static int PlayerHistoryInterval { get; private set; } = 1;

        public static void LoadHistoryIntervalsFromConfig()
        {
            var configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "appsettings.json");
            if (!File.Exists(configPath))
            {
                var defaultConfig = "{\n  \"CityHistoryInterval\": 1,\n  \"PlayerHistoryInterval\": 1\n}\n";
                File.WriteAllText(configPath, defaultConfig);
            }
            var config = new ConfigurationBuilder()
                .SetBasePath(AppDomain.CurrentDomain.BaseDirectory)
                .AddJsonFile("appsettings.json", optional: true)
                .Build();
            CityHistoryInterval = int.TryParse(config["CityHistoryInterval"], out var cityVal) ? cityVal : 1;
            PlayerHistoryInterval = int.TryParse(config["PlayerHistoryInterval"], out var playerVal) ? playerVal : 1;
        }

        public void Run(string[] args)
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\');
            string lastDir = exeDir.Split(Path.DirectorySeparatorChar).Last().ToLowerInvariant();
            LoadHistoryIntervalsFromConfig();
            string inputFile;
            if (args.Length > 0 && !string.IsNullOrWhiteSpace(args[0]))
            {
                inputFile = args[0];
            }
            else if (lastDir != "debug" && lastDir != "release" && lastDir != "net8.0" && lastDir != "net9.0")
            {
                inputFile = @".\Data\Logs\BBAI.log";
            }
            else
            {
                inputFile = @"..\\..\\..\\..\\Data\\Logs\\BBAI.log";
            }

            string outputFile;
            if (args.Length > 1 && !string.IsNullOrWhiteSpace(args[1]))
            {
                outputFile = args[1];
            }
            else if (lastDir != "debug" && lastDir != "release" && lastDir != "net8.0" && lastDir != "net9.0")
            {
                outputFile = @".\Data\Output\civ4_game_processed.log";
            }
            else
            {
                outputFile = @"..\\..\\..\\..\\Data\\Output\\civ4_game_processed.log";
            }

            // Validate input file, check if it exists, change it to the default path only with .\\Data\\Logs\\BBAI.log
            if (string.IsNullOrWhiteSpace(inputFile) || !System.IO.File.Exists(inputFile))
            {
                Console.WriteLine($"Input file '{inputFile}' does not exist. Please provide a valid path.");
                return;
            }

            // Validate output file path
            if (string.IsNullOrWhiteSpace(outputFile))
            {
                Console.WriteLine("Output file path cannot be empty.");
                return;
            }

            if (!outputFile.EndsWith(".log", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Output file must have a .log extension.");
                return;
            }

            // Ensure input file is a valid log file
            if (!inputFile.EndsWith("BBAI.log", StringComparison.OrdinalIgnoreCase) && !inputFile.EndsWith(".log", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Input file must be a BBAI.log or a .log file.");
                return;
            }

            // If input file is a directory, append BBAI.log to it
            //Add \\BBAI.log if it isn't at end of inputfile
            if (!inputFile.EndsWith("BBAI.log", StringComparison.OrdinalIgnoreCase))
            {
                inputFile = System.IO.Path.Combine(inputFile, "BBAI.log");
            }

            // Ensure output directory exists
            string? outputDir = System.IO.Path.GetDirectoryName(outputFile) ?? string.Empty;
            if (!string.IsNullOrEmpty(outputDir) && !System.IO.Directory.Exists(outputDir))
            {
                System.IO.Directory.CreateDirectory(outputDir);
            }


            Console.WriteLine($"Processing {inputFile}...");

            var result = _parser.ParseFile(inputFile, outputFile);

            Console.WriteLine($"\nProcessing complete!");
            Console.WriteLine($"Output written to: {outputFile}");

            // Export all data to CSV
            /*
            string csvOutputDir = "..\\..\\..\\..\\Data\\Output\\csv";
            _exporter.ExportAll(
                result.Players ?? Enumerable.Empty<Player>(),
                result.Cities ?? new List<City>(),
                result.PlayerTurnTimings ?? new List<PlayerTurnTiming>(),
                result.TurnsFound,
                result.ElapsedMilliseconds,
                csvOutputDir
            );
            Console.WriteLine($"All CSV exports written to: {csvOutputDir}");
            */

            // Export all data to JSON
            var jsonExporter = new JsonExporter();
            string jsonOutputDir = outputDir + "\\json";

            //Check if the directory exists, if not create it
            if (!System.IO.Directory.Exists(jsonOutputDir))
            {
                System.IO.Directory.CreateDirectory(jsonOutputDir);
            }

            //Clean the Datas, by keeping only one every CityHistoryInterval in the City.History
            CleanCityHistory(result.Cities?.ToList() ?? new List<City>(), CityHistoryInterval);

            //The same for the Player.TurnHistory, UnitInventory, UnitEvalusation and Score History and , keep only one every PlayerHistoryInterval
            CleanPlayerHistory(result.Players?.ToList() ?? new List<Player>(), PlayerHistoryInterval);


            jsonExporter.ExportAll(
                result.Players ?? Enumerable.Empty<Player>(),
                result.Cities ?? new List<City>(),
                result.PlayerTurnTimings ?? new List<PlayerTurnTiming>(),
                result.TurnsFound,
                result.ElapsedMilliseconds,
                jsonOutputDir
            );
            Console.WriteLine($"All JSON exports written to: {jsonOutputDir}");
        }

        // Utility methods for cleaning history
        public static void CleanCityHistory(List<City> cities, int interval)
        {
            foreach (var city in cities)
            {
                if (city.History != null && city.History.Count > 0 && interval > 1)
                {
                    city.History = city.History
                        .Where(h => h.Turn % interval == 0)
                        .ToList();
                }
            }
        }

        public static void CleanPlayerHistory(IEnumerable<Player> players, int interval)
        {
            foreach (var player in players)
            {
                // StatsHistory
                if (player.StatsHistory != null && player.StatsHistory.Count > 0 && interval > 1)
                {
                    player.StatsHistory = player.StatsHistory
                        .Where(h => h.Turn % interval == 0)
                        .ToList();
                }
                // ScoreHistory
                if (player.ScoreHistory != null && player.ScoreHistory.Count > 0 && interval > 1)
                {
                    player.ScoreHistory = player.ScoreHistory
                        .Where(h => h.Turn % interval == 0)
                        .ToList();
                }
                // UnitInventories
                if (player.UnitInventories != null && player.UnitInventories.Count > 0 && interval > 1)
                {
                    player.UnitInventories = player.UnitInventories
                        .Where(h => h.Turn % interval == 0)
                        .ToList();
                }
                // UnitEvaluation
                if (player.UnitEvaluation != null && player.UnitEvaluation.Evaluations.Count > 0 && interval > 1)
                {
                    player.UnitEvaluation.Evaluations = player.UnitEvaluation.Evaluations
                        .Where(h => h.Turn % interval == 0)
                        .ToList();
                }
            }
        }
    }
}
// End of Program.cs
// This code is part of the C2CLogProcessor project, which processes Civilization IV log files