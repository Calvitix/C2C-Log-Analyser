using C2CLogProcessor.Exporters;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers;
using C2CLogProcessor.Parsers.Categorizers;
using C2CLogProcessor.Services;
using C2CLogProcessor.Services.Interfaces;
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

        public void Run(string[] args)
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\');
            string lastDir = exeDir.Split(Path.DirectorySeparatorChar).Last().ToLowerInvariant();

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
    }
}
// End of Program.cs
// This code is part of the C2CLogProcessor project, which processes Civilization IV log files