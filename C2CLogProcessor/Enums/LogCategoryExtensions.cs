using System;

namespace C2CLogProcessor.Enums
{
    /// <summary>
    /// Extension methods for LogCategory enum
    /// </summary>
    public static class LogCategoryExtensions
    {
        /// <summary>
        /// Get a display-friendly name for the category
        /// </summary>
        public static string GetDisplayName(this LogCategory category)
        {
            return category switch
            {
                LogCategory.Empire => "Empire Statistics",
                LogCategory.Team => "Team & Diplomacy",
                LogCategory.City => "City Management",
                LogCategory.Unit => "Unit Information",
                LogCategory.Tech => "Technology Research",
                LogCategory.EvalTech => "Tech Evaluation",
                LogCategory.EvalUnit => "Unit Evaluation",
                LogCategory.EvalCityPlot => "City Site Evaluation",
                LogCategory.Unknown => "Unknown/Other",
                LogCategory.EmptyLineOrIgnored => "Empty/Ignore",
                _ => category.ToString()
            };
        }
        
        /// <summary>
        /// Get a short code for the category (for compact output)
        /// </summary>
        public static string GetShortCode(this LogCategory category)
        {
            return category switch
            {
                LogCategory.Empire => "EMP",
                LogCategory.Team => "TEAM",
                LogCategory.City => "CITY",
                LogCategory.Unit => "UNIT",
                LogCategory.Tech => "TECH",
                LogCategory.EvalTech => "E-TCH",
                LogCategory.EvalUnit => "E-UNT",
                LogCategory.EvalCityPlot => "E-PLT",
                LogCategory.Unknown => "UNK",
                _ => "???"
            };
        }
        
        /// <summary>
        /// Determine if this is an evaluation category
        /// </summary>
        public static bool IsEvaluation(this LogCategory category)
        {
            return category == LogCategory.EvalTech || 
                   category == LogCategory.EvalUnit || 
                   category == LogCategory.EvalCityPlot;
        }
        
        /// <summary>
        /// Parse a string to LogCategory
        /// </summary>
        public static LogCategory Parse(string value)
        {
            if (Enum.TryParse<LogCategory>(value, true, out var result))
                return result;
            
            // Try short codes
            return value?.ToUpperInvariant() switch
            {
                "EMP" => LogCategory.Empire,
                "TEAM" => LogCategory.Team,
                "CITY" => LogCategory.City,
                "UNIT" => LogCategory.Unit,
                "TECH" => LogCategory.Tech,
                "E-TCH" => LogCategory.EvalTech,
                "E-UNT" => LogCategory.EvalUnit,
                "E-PLT" => LogCategory.EvalCityPlot,
                "UNK" => LogCategory.Unknown,
                _ => LogCategory.Unknown
            };
        }
    }
}