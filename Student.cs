
public class Student
{
    public string Name { get; set; }
    public string Group { get; set; }
    public int Score { get; set; }

    public Student(string name, string group, int score)
    {
        Name = name;
        Group = group;
        Score = score;
    }

    public override string ToString()
    {
        return $"{Name,-15} {Group,-10} {Score}";
    }
}
