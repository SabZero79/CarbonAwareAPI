using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace CarbonAware.Providers;

public sealed class WattTimeAuthBackgroundService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly ILogger<WattTimeAuthBackgroundService> _log;

    public WattTimeAuthBackgroundService(IServiceScopeFactory scopeFactory,
                                         ILogger<WattTimeAuthBackgroundService> log)
    {
        _scopeFactory = scopeFactory;
        _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // One-time pre-warm shortly after startup
        await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);

        try
        {
            using var scope = _scopeFactory.CreateScope();
            var wt = scope.ServiceProvider.GetRequiredService<WattTimeProvider>();
            await wt.EnsureTokenAsync(stoppingToken);
            _log.LogInformation("WattTime token pre-warm done.");
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "WattTime token pre-warm failed (continuing).");
        }
    }
}
