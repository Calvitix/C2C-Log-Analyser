namespace C2CLogProcessor.Models
{

    // Add this enum (move to a shared file if needed)
    public enum OrderType
    {
        Unit,
        Building,
        Unknown
    }

    // Add this class to represent an order to central (can be moved to a shared Models file if needed)
    public class CityOrderToCentral
    {
        public required string AIType { get; set; }
        public required int Strength { get; set; }
        public required int Priority { get; set; }
        public required int Turn { get; set; }
        public required OrderType OrderType { get; set; }
    }
}