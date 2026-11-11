
using System;
using System.Collections.Generic;

public static class Validators
{
    public static bool IsSorted<T>(
        T[] array,
        Func<T, T, int> cmp)
    {
        for (int i = 1; i < array.Length; i++)
        {
            if (cmp(array[i - 1], array[i]) > 0)
                return false;
        }

        return true;
    }

    public static bool IsPermutationOf<T>(
        T[] original,
        T[] sorted,
        IEqualityComparer<T>? equality = null)
    {
        if (original.Length != sorted.Length)
            return false;

        equality ??= EqualityComparer<T>.Default;

        var counts = new Dictionary<T, int>();

        foreach (T item in original)
        {
            counts.TryGetValue(item, out int count);
            counts[item] = count + 1;
        }

        foreach (T item in sorted)
        {
            if (!counts.TryGetValue(item, out int count))
                return false;

            if (count == 1)
                counts.Remove(item);
            else
                counts[item] = count - 1;
        }

        return counts.Count == 0;
    }

    public static bool IsStableByScore(
        Student[] students)
    {
        for (int i = 1; i < students.Length; i++)
        {
            if (students[i - 1].Score == students[i].Score &&
                string.Compare(
                    students[i - 1].Name,
                    students[i].Name,
                    StringComparison.Ordinal) > 0)
            {
                return false;
            }
        }

        return true;
    }
}
