using System;
using System.Collections.Generic;
using C2CLogProcessor.Enums;

namespace C2CLogProcessor.Parsers.Categorizers
{
    public class LogCategorizer : ILogCategorizer
    {
        private readonly Dictionary<LogCategory, string[]> _categoryKeywords;

        public LogCategorizer()
        {
            _categoryKeywords = new Dictionary<LogCategory, string[]>
            {
                { 
                    LogCategory.Empire, 
                    new[] { 
                        "has ", " cities", "gold rate:", "Gold rate:", "Treasury:", 
                        "tech percent", "Empire", "stats for turn", "Current civics:", 
                        "Num units:", "upgrade budget", "Total turns in anarchy", 
                        "Civic switches", "Science rate:", "Culture rate:", 
                        "Espionage rate:", "Total population:", "National rev index:",
                        "calculates upgrade budget","Workers in Area","iNumSettlers","iMaxSettlers",
                        "setTurnActive for", "trade calc", "Total gold income", "Num selection groups",
                        "(pre inflation)", "Inflation ef", "financial difficulties",
                        "Total espionage output", "Total science output", "Total cultural output",
                        "Total food output", "Total production output", " units killed", "mals subdued",
                        "Gouvernement:", "Règles:" ,"Pouvoir:","Militaire:","Religion:","Société: ",
                        "Economie: ","Bien-être:","Monnaie:","Travail: ","Education: ","Langue: ","Immigration: ",
                        "Agriculture: ","Traitement des déchets: ","ennemi a été repéré",
                        "pour population (","pour territoire (","pour technologies (","pour Merveilles (",
                        "Score total =","Score si victoire à ce tour","Economy avg",
                        "découvert une source","Naissance de ","L'âge d'or de "
                    }
                },
                { 
                    LogCategory.Team, 
                    new[] { 
                        "Team ", "at war with", "has met:", "Enemy power", 
                        "estimating warplan", "financial costs", "planning war with"
                    }
                },
                { 
                    LogCategory.City, 
                    new[] { 
                        "City ", "founds new city", "population:", "threat level", 
                        "production:", "Net happyness", "Net health", "Properties:",
                        "pushes production", "requests", "floating defender",
                        "workers have:", "workers needed:", "Considering new production",
                        "CalculateAllBuildingValues", "base value for", "final value",
                        "fondation de","Food surplus:","Local rev index","Maintenance: ",
                        "Income: ","Science: ","Espionage: ","Culture: "," trade yield:",
                        "Criminalité: value","Maladie: value","Pollution de L'eau: value",
                        "Pollution de l'air: value","PropertyBuildings:"," (pop ","Maladie: ",
                        " par les citoyens de ","Criminalité: ","ne peut pas gérer l'excédent",
                        "Risque d'incendie:","is modified.  We have",
                        " s'est développée et est désormais considérée"
                    }
                },
                {
                    LogCategory.EvalCity,
                    new[] {
                        "base value for", "final value",
                        "Calc value for","Gain from immediate", "Estimated number of turns t",
                        "enables "
                    }
                },
                { 
                    LogCategory.Unit, 
                    new[] { 
                        "Units:", "UNITAI_", "unit strength", "military units",
                        "worker units", "num units","Exp for promotion present",
                        "a tué l'animal ","une embuscade à","et gagné la promotion",
                        "des dommages collatéraux","apprivoisé l'animal"
                    }
                },
                { 
                    LogCategory.Tech, 
                    new[] { 
                        "calculate value for tech", "raw value for tech", 
                        "Civic", "Building value:", "tech path value",
                        "Evaluate tech path", "Misc value:", "Corporation value:",
                        "Promotion value:", "Tile improvement value:", "Build value:",
                        "Bonus reveal value:", "Unit value:", "enabled civic"
                    }
                },
                { 
                    LogCategory.EvalCityPlot, 
                    new[] { 
                        "Update City Sites", "city site", "Found City Site",
                        "Potential best city site", "begin Update City Sites",
                        "end Update City Sites", "player modified value"
                    }
                },
                { 
                    LogCategory.EvalUnit, 
                    new[] { 
                        "evaluate Value for unit", "Better AI Unit", 
                        "combat value", "AI_bestUnitAI", "Calculated value",
                        "AI Unit not chosen", "Taking Better AI Unit",
                        "searching for UNITAI_","Retrain available"
                    }
                },
                { 
                    LogCategory.EvalTech, 
                    new[] { 
                        "evaluate TechBuilding", "mechanism value:",
                        "Building.*new mechanism value", "evaluating buildings for tech",
                        "tech evaluation", "tech ","discovery","enables "
                    }
                },
                {
                    LogCategory.EmptyLineOrIgnored,
                    new[] {
                        "No switches made","Ignore","dans un pays lointain !", "------------------------",
                        "a adopté la doctrine ", "\t\tTurn "," -> "
                    }
                }



                
            };
        }

        public LogCategory Categorize(string line)
        {
            if (string.IsNullOrWhiteSpace(line))
                return LogCategory.EmptyLineOrIgnored;

            // Check each category's keywords
            foreach (var kvp in _categoryKeywords)
            {
                foreach (var keyword in kvp.Value)
                {
                    if (line.Contains(keyword, StringComparison.OrdinalIgnoreCase))
                    {
                        return kvp.Key;
                    }
                }
            }
            
            return LogCategory.Unknown;
        }
    }
}