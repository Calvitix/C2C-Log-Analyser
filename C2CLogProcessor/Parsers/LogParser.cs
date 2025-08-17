using C2CLogProcessor.Enums;
using C2CLogProcessor.Models;
using C2CLogProcessor.Parsers.Categorizers;
using C2CLogProcessor.Parsers.Patterns;
using C2CLogProcessor.Services;
using C2CLogProcessor.Services.Interfaces;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;


namespace C2CLogProcessor.Parsers
{
    public class LogParser : ILogParser
    {
        private readonly IFileService _fileService;
        private readonly IEncodingDetector _encodingDetector;
        private readonly ILogCategorizer _categorizer;
        private readonly List<IPattern> _patterns;
        private readonly GameState _gameState;

        public LogParser(
            IFileService fileService, 
            IEncodingDetector encodingDetector,
            ILogCategorizer categorizer)
        {
            _fileService = fileService;
            _encodingDetector = encodingDetector;
            _categorizer = categorizer;
            _gameState = new GameState();
            
            // Only patterns relevant for BBAI.log
            _patterns = new List<IPattern>
            {
                new TurnPattern(),
                new CityPattern(),
                new PlayerPattern()
                // Do NOT add AiEvaluationPattern here
            };
        }

        public GameState Get_gameState()
        {
            return _gameState;
        }

        public ParseResult ParseFile(string inputFile, string outputFile)
        {
            var result = new ParseResult();
            result.CategoryCounts = new Dictionary<LogCategory, int>();
            var stopwatch = Stopwatch.StartNew();

            var encoding = _encodingDetector.DetectEncoding(inputFile);
            Console.WriteLine($"Detected encoding: {encoding.EncodingName}");

            using (var reader = _fileService.OpenReader(inputFile, encoding))
            using (var writer = _fileService.OpenWriter(outputFile))
            {
                string? line;
                while ((line = reader.ReadLine()) != null)
                {
                    result.TotalLines++;

                    if (string.IsNullOrWhiteSpace(line))
                        continue;

                    var processedLine = ProcessLine(line);
                    if (processedLine != null)
                    {
                        writer.WriteLine(processedLine);
                        result.ProcessedLines++;
                        UpdateStatistics(processedLine, result);
                    }

                    if (result.TotalLines % 10000 == 0)
                        Console.WriteLine($"Processed {result.TotalLines} lines...");
                }
            }

            // Integrate parsing of AiEvaluation.log after BBAI.log, using the same _gameState
            string aiEvalPath = Path.Combine(Path.GetDirectoryName(inputFile) ?? "", "AiEvaluation.log");
            if (File.Exists(aiEvalPath))
            {
                Console.WriteLine($"Processing {aiEvalPath}...");
                var aiEvalPatterns = new List<IPattern> { new AiEvaluationPattern() };
                var encodingAi = _encodingDetector.DetectEncoding(aiEvalPath);
                using (var reader = _fileService.OpenReader(aiEvalPath, encodingAi))
                using (var writer = _fileService.OpenWriter(Path.Combine(Path.GetDirectoryName(outputFile) ?? "", "AiEvaluation_output.txt")))
                {
                    string? line;
                    while ((line = reader.ReadLine()) != null)
                    {
                        _gameState.LastTimestamp = GetTimestampfromLine(line);
                        var cleanedLine = ExtractTimestamp(line);
                        foreach (var pattern in aiEvalPatterns)
                        {
                            pattern.Apply(cleanedLine, _gameState);
                        }
                        writer.WriteLine(line);
                    }
                }
            }

            stopwatch.Stop();
            result.ElapsedMilliseconds = stopwatch.ElapsedMilliseconds;
            result.Cities = new List<City>(_gameState.Cities.Values);
            result.TurnsFound = _gameState.CurrentTurn + 1;
            result.Players = new List<Player>(_gameState.Players.Values);
            result.PlayerTurnTimings = _gameState.PlayerTurnTimings;

            return result;
        }

        private string ProcessLine(string line)
        {
            var cleanedLine = ExtractTimestamp(line);
            var Timestamp = GetTimestampfromLine(line);

            // Fill LastTimestamp for every line
            _gameState.LastTimestamp = Timestamp;

            // Apply all patterns, but TurnPattern gets the original line
            bool anyPatternMatched = false;
            foreach (var pattern in _patterns)
            {
                bool matched = (pattern is TurnPattern)
                    ? pattern.Apply(line, _gameState)
                    : pattern.Apply(cleanedLine, _gameState);
                if (matched) anyPatternMatched = true;
            }

            var playerId = GetPlayerFromLine(cleanedLine);
            var category = _categorizer.Categorize(cleanedLine);
            _gameState.FillEndTimestamp(Timestamp);
            Boolean Debug = false;
            if (category == LogCategory.Unknown && Debug)
            {
                Console.WriteLine($"Unknown category for line: {cleanedLine}");
            }

            if (!anyPatternMatched && category != LogCategory.EmptyLineOrIgnored && Debug)
            {
                cleanedLine = "NOMATCH" + cleanedLine.Trim();
            }

            return $"[{_gameState.CurrentTurn}|{playerId}|{category}] {cleanedLine}";
        }

        private double GetTimestampfromLine(string line)
        {
            // Try to extract timestamp for lastTimestamp
            var match = System.Text.RegularExpressions.Regex.Match(line, @"^\[(\d+\.\d+)\]");
            if (match.Success)
            {
                double ts = double.Parse(match.Groups[1].Value, CultureInfo.InvariantCulture);
                return ts;
            }
            return -99.0;
        }

        private string ExtractTimestamp(string line)
        {
            // Timestamp extraction logic
            var match = System.Text.RegularExpressions.Regex.Match(line, @"^\[(\d+\.\d+)\]\s*(.*)");
            return match.Success ? match.Groups[2].Value : line;
        }




        private int GetPlayerFromLine(string line)
        {
            // Player extraction logic
            return _gameState.ActivePlayerId;
        }

        private void UpdateStatistics(string processedLine, ParseResult result)
        {
            foreach (LogCategory category in Enum.GetValues(typeof(LogCategory)))
            {
                if (processedLine.Contains($"|{category}]"))
                {
                    if (!result.CategoryCounts.ContainsKey(category))
                        result.CategoryCounts[category] = 0;
                    
                    result.CategoryCounts[category]++;
                    break;
                }
            }
        }
    }
}