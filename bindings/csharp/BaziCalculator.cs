using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;

namespace Mystilink.Bazi
{
    /// <summary>
    /// Invokes the mystilink-bazi CLI and returns JSON stdout.
    /// </summary>
    public static class BaziCalculator
    {
        public static string ResolveCli()
        {
            var env = Environment.GetEnvironmentVariable("MYSTILINK_BAZI_CLI");
            return string.IsNullOrWhiteSpace(env) ? "bazi" : env;
        }

        public static string Run(params string[] args)
        {
            var psi = new ProcessStartInfo
            {
                FileName = ResolveCli(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
            };
            foreach (var a in args)
            {
                psi.ArgumentList.Add(a);
            }

            using var proc = Process.Start(psi)
                ?? throw new InvalidOperationException("Failed to start bazi");
            string stdout = proc.StandardOutput.ReadToEnd();
            string stderr = proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            if (proc.ExitCode != 0)
            {
                var msg = string.IsNullOrWhiteSpace(stderr) ? stdout : stderr;
                throw new InvalidOperationException(
                    string.IsNullOrWhiteSpace(msg)
                        ? $"bazi exited with code {proc.ExitCode}"
                        : msg.Trim());
            }
            return stdout;
        }

        public static string Calculate(string date, int? hour = null, int minute = 0,
            string? timezone = null, double? longitude = null)
        {
            var args = new List<string> { "calculate", "--date", date };
            if (hour.HasValue)
            {
                args.Add("--hour");
                args.Add(hour.Value.ToString());
            }
            args.Add("--minute");
            args.Add(minute.ToString());
            if (!string.IsNullOrEmpty(timezone) && longitude.HasValue)
            {
                args.Add("--timezone");
                args.Add(timezone);
                args.Add("--longitude");
                args.Add(longitude.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
            }
            return Run(args.ToArray());
        }

        public static string Dayun(string date, string gender, int count = 8)
        {
            return Run("dayun", "--date", date, "--gender", gender, "--count", count.ToString());
        }

        public static string Liunian(int year, string? dayStem = null, string? pillarsJson = null)
        {
            var args = new List<string> { "liunian", "--year", year.ToString() };
            if (!string.IsNullOrEmpty(dayStem))
            {
                args.Add("--day-stem");
                args.Add(dayStem);
            }
            if (!string.IsNullOrEmpty(pillarsJson))
            {
                args.Add("--pillars-json");
                args.Add(pillarsJson);
            }
            return Run(args.ToArray());
        }

        public static string Version()
        {
            return Run("version");
        }
    }
}
