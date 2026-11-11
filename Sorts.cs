
using System;

public static class Sorts
{
    // Завдання 1: бульбашкове сортування з прапорцем
    public static void BubbleSort<T>(
        T[] a,
        Func<T, T, int> cmp,
        out long comparisons,
        out long moves)
    {
        comparisons = 0;
        moves = 0;

        for (int i = 0; i < a.Length - 1; i++)
        {
            bool swapped = false;

            for (int j = 0; j < a.Length - 1 - i; j++)
            {
                comparisons++;

                if (cmp(a[j], a[j + 1]) > 0)
                {
                    T temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;

                    moves += 2;
                    swapped = true;
                }
            }

            if (!swapped)
                break;
        }
    }

    // Сортування вставками для невеликих ділянок
    private static void InsertionSort<T>(
        T[] a,
        int left,
        int right,
        Func<T, T, int> cmp,
        ref long comparisons,
        ref long moves)
    {
        for (int i = left + 1; i <= right; i++)
        {
            T key = a[i];
            int j = i - 1;

            while (j >= left)
            {
                comparisons++;

                if (cmp(a[j], key) <= 0)
                    break;

                a[j + 1] = a[j];
                moves++;
                j--;
            }

            a[j + 1] = key;
            moves++;
        }
    }

    // Допоміжне злиття двох ділянок
    private static void Merge<T>(
        T[] a,
        T[] buffer,
        int left,
        int mid,
        int right,
        Func<T, T, int> cmp,
        ref long comparisons,
        ref long moves)
    {
        int i = left;
        int j = mid;
        int k = left;

        while (i < mid && j < right)
        {
            comparisons++;

            if (cmp(a[i], a[j]) <= 0)
                buffer[k++] = a[i++];
            else
                buffer[k++] = a[j++];

            moves++;
        }

        while (i < mid)
        {
            buffer[k++] = a[i++];
            moves++;
        }

        while (j < right)
        {
            buffer[k++] = a[j++];
            moves++;
        }

        for (int p = left; p < right; p++)
        {
            a[p] = buffer[p];
            moves++;
        }
    }

    // Завдання 2: сортування злиттям знизу вгору
    public static void MergeSort<T>(
        T[] a,
        Func<T, T, int> cmp,
        out long comparisons,
        out long moves)
    {
        comparisons = 0;
        moves = 0;

        int n = a.Length;

        if (n < 2)
            return;

        T[] buffer = new T[n];

        for (int width = 1; width < n;)
        {
            for (int left = 0; left < n; left += 2 * width)
            {
                int mid = Math.Min(left + width, n);
                int right = Math.Min(left + 2 * width, n);

                if (mid < right)
                {
                    Merge(a, buffer, left, mid, right,
                        cmp, ref comparisons, ref moves);
                }
            }

            if (width > n / 2)
                break;

            width *= 2;
        }
    }

    // Завдання 3: гібридне сортування
    public static void HybridSort<T>(
        T[] a,
        Func<T, T, int> cmp,
        int threshold,
        out long comparisons,
        out long moves)
    {
        comparisons = 0;
        moves = 0;

        int n = a.Length;

        if (n < 2)
            return;

        if (threshold < 1)
            threshold = 1;

        T[] buffer = new T[n];

        // Спочатку сортуємо невеликі ділянки вставками
        for (int left = 0; left < n; left += threshold)
        {
            int right = Math.Min(left + threshold - 1, n - 1);

            InsertionSort(
                a, left, right, cmp,
                ref comparisons, ref moves);
        }

        // Потім об'єднуємо відсортовані ділянки
        int width = threshold;

        while (width < n)
        {
            for (int left = 0; left < n; left += 2 * width)
            {
                int mid = Math.Min(left + width, n);
                int right = Math.Min(left + 2 * width, n);

                if (mid < right)
                {
                    Merge(
                        a, buffer, left, mid, right,
                        cmp, ref comparisons, ref moves);
                }
            }

            if (width > n / 2)
                break;

            width *= 2;
        }
    }
}
