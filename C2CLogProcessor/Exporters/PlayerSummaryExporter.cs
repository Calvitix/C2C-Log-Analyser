using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using C2CLogProcessor.Models;

namespace C2CLogProcessor.Exporters
{
    public class PlayerSummaryExporter
    {
        public void Export(List<Player> players, string summaryFile)
        {
            if (players == null || players.Count == 0)
                return;

            using (var writer = new StreamWriter(summaryFile, false, Encoding.UTF8))
            {
                // Write header
                writer.WriteLine("Id,Name,IsHuman,Type,Score,Population,Cities,MetPlayers,AtWarWith");

                foreach (var player in players)
                {
                    var stats = player.CurrentStats;
                    var score = stats != null ? stats.Score : 0;
                    var population = stats != null ? stats.Population : 0;
                    var cities = player.OwnedCityNames != null ? player.OwnedCityNames.Count : 0;
                    var metPlayers = player.MetPlayers != null ? player.MetPlayers.Count : 0;
                    var atWarWith = player.AtWarWith != null ? player.AtWarWith.Count : 0;

                    writer.WriteLine($"{player.Id},{player.Name},{player.IsHuman},{player.Type},{score},{population},{cities},{metPlayers},{atWarWith}");
                }
            }
        }
    }
}
