namespace CarbonAware.Core.Auditing;

public interface IAuditSink
{
    Task LogWattTimeCallAsync(WattTimeCallRecord rec, CancellationToken ct = default);
    Task LogAdviceAsync(AdviceRecord rec, IEnumerable<AdviceCandidateRecord>? candidates = null, CancellationToken ct = default);
}

public sealed class WattTimeCallRecord
{
    public string Method { get; init; } = "GET";
    public string RequestUrl { get; init; } = default!;
    public string? Region { get; init; }
    public string? SignalType { get; init; }
    public int? HorizonHours { get; init; }
    public int StatusCode { get; init; }
    public bool Success { get; init; }
    public int DurationMs { get; init; }
    public string? ResponseBody { get; init; }
    public string? Error { get; init; }
    public string? SourceFile { get; init; }
    public int? SourceLine { get; init; }
    public DateTimeOffset CreatedUtc { get; init; } = DateTimeOffset.UtcNow;
    public Guid? RequestId { get; init; }
}

public sealed class AdviceRecord
{
    public string Mode { get; init; } = default!;               // run_now | schedule_at
    public DateTimeOffset TargetWhen { get; init; }
    public string? PreferredCloudsCsv { get; init; }
    public string? PreferredRegionsCsv { get; init; }

    public string SelectedCloud { get; init; } = default!;
    public string SelectedRegion { get; init; } = default!;
    public DateTimeOffset? SelectedWhen { get; init; }
    public double? SelectedMoerGPerKwh { get; init; }
    public string Rationale { get; init; } = default!;

    public string? HighestEmissionCloud { get; init; }
    public string? HighestEmissionRegion { get; init; }
    public double? HighestEmissionGPerKwh { get; init; }
    public double? EstimatedSavingGPerKwh { get; init; }
    public double? EstimatedSavingPercent { get; init; }
    public double? AverageEmissionGPerKwh { get; init; }
    public double? AverageEstimatedSavingPercent { get; init; }

    public string? BestWindowCloud { get; init; }
    public string? BestWindowRegion { get; init; }
    public double? BestWindowMoerGPerKwh { get; init; }
    public DateTimeOffset? BestWindowWhen { get; init; }
    public DateTimeOffset CreatedUtc { get; init; } 
    public Guid? RequestId { get; init; }
}

public sealed class AdviceCandidateRecord
{
    public string Cloud { get; init; } = default!;
    public string Region { get; init; } = default!;
    public double? MoerAtTarget { get; init; }
    public double? BestMoerUntilTarget { get; init; }
    public DateTimeOffset? BestMoerAt { get; init; }
}

public sealed class AuditOptions
{
    public bool EnableDatabaseLogging { get; set; } = true;
}
