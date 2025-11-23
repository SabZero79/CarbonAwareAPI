using CarbonAware.Core.Auditing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace CarbonAware.Api.Data;

public sealed class EfAuditSink : IAuditSink
{
    private readonly AuditOptions _options;
    private readonly LoggingDbContext _db;
 
    public EfAuditSink(LoggingDbContext db, IOptions<AuditOptions> options)
    {
        _db = db;
        _options = options.Value;
    }


    public async Task LogWattTimeCallAsync(WattTimeCallRecord rec, CancellationToken ct = default)
   {
        if (!_options.EnableDatabaseLogging)
        {
            // Logging disabled: do nothing
            return;
        }
        _db.WattTimeCalls.Add(new WattTimeCallLog
        {
            CreatedUtc = rec.CreatedUtc,
            Method = rec.Method,
            RequestUrl = rec.RequestUrl,
            Region = rec.Region,
            SignalType = rec.SignalType,
            HorizonHours = rec.HorizonHours,
            StatusCode = rec.StatusCode,
            Success = rec.Success,
            DurationMs = rec.DurationMs,
            ResponseBody = rec.ResponseBody,
            Error = rec.Error,
            SourceFile = rec.SourceFile,
            SourceLine = rec.SourceLine,
            RequestId = rec.RequestId
        });
        await _db.SaveChangesAsync(ct);
    }

    public async Task LogAdviceAsync(AdviceRecord rec, IEnumerable<AdviceCandidateRecord>? candidates = null, CancellationToken ct = default)
    {
        if (!_options.EnableDatabaseLogging)
        {
            // Logging disabled: do nothing
            return;
        }
        var exec = new AdviceExecutionLog
        {
            CreatedUtc = rec.CreatedUtc,
            Mode = rec.Mode,
            TargetWhen = rec.TargetWhen,
            PreferredCloudsCsv = rec.PreferredCloudsCsv,
            PreferredRegionsCsv = rec.PreferredRegionsCsv,
            SelectedCloud = rec.SelectedCloud,
            SelectedRegion = rec.SelectedRegion,
            SelectedWhen = rec.SelectedWhen,
            SelectedMoerGPerKwh = rec.SelectedMoerGPerKwh,
            Rationale = rec.Rationale,
            HighestEmissionCloud = rec.HighestEmissionCloud,
            HighestEmissionRegion = rec.HighestEmissionRegion,
            HighestEmissionGPerKwh = rec.HighestEmissionGPerKwh,
            EstimatedSavingGPerKwh = rec.EstimatedSavingGPerKwh,
            EstimatedSavingPercent = rec.EstimatedSavingPercent,
            AverageEmissionGPerKwh = rec.AverageEmissionGPerKwh,
            AverageEstimatedSavingPercent = rec.AverageEstimatedSavingPercent,
            BestWindowCloud = rec.BestWindowCloud,
            BestWindowRegion = rec.BestWindowRegion,
            BestWindowMoerGPerKwh = rec.BestWindowMoerGPerKwh,
            BestWindowWhen = rec.BestWindowWhen,
            RequestId = rec.RequestId
        };

        if (candidates is not null)
        {
            foreach (var c in candidates)
            {
                exec.Candidates.Add(new AdviceCandidateLog
                {
                    Cloud = c.Cloud,
                    Region = c.Region,
                    MoerAtTarget = c.MoerAtTarget,
                    BestMoerUntilTarget = c.BestMoerUntilTarget,
                    BestMoerAt = c.BestMoerAt
                });
            }
        }

        _db.AdviceExecutions.Add(exec);
        await _db.SaveChangesAsync(ct);
    }
}
