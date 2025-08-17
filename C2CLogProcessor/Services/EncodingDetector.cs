using System;
using System.IO;
using System.Text;
using C2CLogProcessor.Services.Interfaces;

namespace C2CLogProcessor.Services
{
    public class EncodingDetector : IEncodingDetector
    {
        public Encoding DetectEncoding(string filePath)
        {
            // List of encodings to try
            var encodingsToTry = new[]
            {
                Encoding.GetEncoding(1252),    // Windows-1252 (ANSI)
                Encoding.UTF8,
                Encoding.GetEncoding("ISO-8859-1"),
                Encoding.Unicode,
                Encoding.BigEndianUnicode
            };

            foreach (var encoding in encodingsToTry)
            {
                try
                {
                    using (var reader = new StreamReader(filePath, encoding, true))
                    {
                        // Read a sample to test
                        var buffer = new char[4096];
                        int charsRead = reader.Read(buffer, 0, buffer.Length);
                        
                        if (charsRead == 0)
                            continue;

                        string sample = new string(buffer, 0, charsRead);
                        
                        // Check for common French characters that would indicate correct encoding
                        if (ContainsFrenchCharacters(sample) && !ContainsInvalidCharacters(sample))
                        {
                            return encoding;
                        }
                        
                        // If no French chars but no invalid chars either, it might still be valid
                        if (!ContainsInvalidCharacters(sample))
                        {
                            // Keep as candidate but continue checking
                            continue;
                        }
                    }
                }
                catch (Exception)
                {
                    // This encoding didn't work, try next
                    continue;
                }
            }

            // Default to Windows-1252 for Civ4 logs
            return Encoding.GetEncoding(1252);
        }

        private bool ContainsFrenchCharacters(string text)
        {
            // Common French characters
            var frenchChars = new[] { 'é', 'è', 'ê', 'ë', 'à', 'â', 'ç', 'ù', 'û', 'ô', 'î', 'ï' };
            
            foreach (var ch in frenchChars)
            {
                if (text.Contains(ch))
                    return true;
            }
            
            return false;
        }

        private bool ContainsInvalidCharacters(string text)
        {
            // Check for common indicators of wrong encoding
            return text.Contains('\ufffd') || // Unicode replacement character
                   text.Contains('�') ||
                   ContainsTooManyControlCharacters(text);
        }

        private bool ContainsTooManyControlCharacters(string text)
        {
            int controlChars = 0;
            foreach (char c in text)
            {
                if (char.IsControl(c) && c != '\n' && c != '\r' && c != '\t')
                {
                    controlChars++;
                }
            }
            
            // If more than 1% are control characters, probably wrong encoding
            return controlChars > text.Length * 0.01;
        }
    }
}