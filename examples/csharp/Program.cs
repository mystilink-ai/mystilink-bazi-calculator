using System;
using MystiLink.Bazi;

class Program
{
    static void Main()
    {
        string json = BaziCalculator.Calculate("1990-05-15", hour: 12, minute: 0);
        Console.WriteLine(json);
    }
}
