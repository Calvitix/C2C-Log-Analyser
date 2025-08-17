namespace C2CLogProcessor.Enums
{
    /// <summary>
    /// Categories for different types of log entries
    /// </summary>
    public enum LogCategory
    {
        /// <summary>
        /// Empire-wide statistics and information
        /// </summary>
        Empire,
        
        /// <summary>
        /// Team/diplomacy related information
        /// </summary>
        Team,
        
        /// <summary>
        /// City-specific information
        /// </summary>
        City,

        /// <summary>
        /// City-specific information for evaluation of production or needs
        /// </summary>
        EvalCity,

        /// <summary>
        /// Unit-related information
        /// </summary>
        Unit,
        
        /// <summary>
        /// Technology research and evaluation
        /// </summary>
        Tech,
        
        /// <summary>
        /// Technology building evaluations
        /// </summary>
        EvalTech,
        
        /// <summary>
        /// Unit AI evaluations
        /// </summary>
        EvalUnit,
        
        /// <summary>
        /// City plot/site evaluations
        /// </summary>
        EvalCityPlot,
        
        /// <summary>
        /// Unrecognized log entries
        /// </summary>
        Unknown,

        EmptyLineOrIgnored
    }
}