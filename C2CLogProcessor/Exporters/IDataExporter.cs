using System.Collections.Generic;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Exporters
{
    public interface IDataExporter
    {
        void ExportCities(List<City> cities, string filename);
        void ExportCityHistory(City city, string cityFileName);
        void ExportGameDataSummary(IEnumerable<Player> players, string v);
        void ExportGameTurns(int turnsFound, long elapsedMilliseconds, string v);
        void ExportPlayer(Player player, string filename);
        void ExportPlayerTurnTimings(List<PlayerTurnTiming> timings, string v);
        void ExportUnitEvaluations(GameState gameState, string outputPath);
        void ExportAll(
            IEnumerable<Player> players,
            List<City> cities,
            List<PlayerTurnTiming> timings,
            int turnsFound,
            long elapsedMilliseconds,
            string outputDirectory,
            GameState? gameState = null
        );
    }
}