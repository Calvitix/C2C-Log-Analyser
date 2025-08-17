using System.Text.RegularExpressions;
using Xunit;

public class TurnPatternRegexTests
{
    [Theory]
    [InlineData("[20931.750] Player 2 (Empire grec) setTurnActive for turn 4")]
    [InlineData("[20930.125] Player 1 (Empire germanique) setTurnActive for turn 1")]
    public void TurnChangePattern_Matches_LogLine(string logLine)
    {
        var regex = new Regex(@"\[(\d+\.\d+)\]\s*Player\s+(\d+)\s*\(([^)]+)\)\s*setTurnActive\s*for\s*turn\s+(\d+)",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        var match = regex.Match(logLine);

        Assert.True(match.Success);
        Assert.Equal("20931.750", match.Groups[1].Value);
        // You can add more asserts for other groups if desired
    }
}