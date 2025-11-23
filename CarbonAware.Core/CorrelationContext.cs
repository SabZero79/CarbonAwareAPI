using System;
using System.Threading;

namespace CarbonAware.Core;

public interface ICorrelationContext
{
    Guid? Current { get; set; }
}

public sealed class CorrelationContext : ICorrelationContext
{
    private static readonly AsyncLocal<Guid?> _current = new();

    public Guid? Current
    {
        get => _current.Value;
        set => _current.Value = value;
    }
}
