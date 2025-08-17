namespace C2CLogProcessor.Models
{
    // Add this class to represent a produced item (can be moved to a shared Models file if needed)
    public class CityProduction
    {
        public required string ProductName { get; set; }
        public required int Turn { get; set; }
    }
}