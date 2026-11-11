
using System;
using System.Diagnostics;

public static class Benchmark
{
    public static double Measure(
        Action action,
        int repetitions = 3)
    {
        action(); // Прогрів

        double best = double.MaxValue;

        for (int i = 0; i < repetitions; i++)
        {
            Stopwatch stopwatch = Stopwatch.StartNew();

            action();

            stopwatch.Stop();

            double elapsed = stopwatch.Elapsed.TotalMilliseconds;

            if (elapsed < best)
                best = elapsed;
        }

        return best;
    }

    public static void Compare(
        int[] source,
        int threshold)
    {
        Func<int, int, int> cmp = (x, y) => x.CompareTo(y);

        int[] bubble = (int[])source.Clone();
        int[] merge = (int[])source.Clone();
        int[] hybrid = (int[])source.Clone();
        int[] standard = (int[])source.Clone();

        double bubbleTime = Measure(() =>
        {
            int[] copy = (int[])source.Clone();
            Sorts.BubbleSort(copy, cmp, out _, out _);
        });

        double mergeTime = Measure(() =>
        {
            int[] copy = (int[])source.Clone();
            Sorts.MergeSort(copy, cmp, out _, out _);
        });

        double hybridTime = Measure(() =>
        {
            int[] copy = (int[])source.Clone();
            Sorts.HybridSort(
                copy, cmp, threshold, out _, out _);
        });

        double standardTime = Measure(() =>
        {
            int[] copy = (int[])source.Clone();
            Array.Sort(copy);
        });

        Console.WriteLine(
            $"{source.Length,10} | " +
            $"{bubbleTime,12:F3} | " +
            $"{mergeTime,12:F3} | " +
            $"{hybridTime,12:F3} | " +
            $"{standardTime,12:F3}");
    }
}
