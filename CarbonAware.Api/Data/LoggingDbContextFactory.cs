using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;
using System.IO;

namespace CarbonAware.Api.Data
{
    /// <summary>
    /// Used by EF Core tools to create the DbContext at design time (migrations).
    /// </summary>
    public sealed class LoggingDbContextFactory : IDesignTimeDbContextFactory<LoggingDbContext>
    {
        public LoggingDbContext CreateDbContext(string[] args)
        {
            // Build config from appsettings.json + environment variables
            var basePath = Directory.GetCurrentDirectory();
            var config = new ConfigurationBuilder()
                .SetBasePath(basePath)
                .AddJsonFile("appsettings.json", optional: true)
                .AddJsonFile("appsettings.Development.json", optional: true)
                .AddEnvironmentVariables()
                .Build();

            var cs = config.GetConnectionString("LoggingDb")
                     ?? "Server=localhost,1433;Database=CarbonAwareLogs;User Id=sa;Password=Your@Passw0rd;TrustServerCertificate=True;MultipleActiveResultSets=True;";

            var options = new DbContextOptionsBuilder<LoggingDbContext>()
                .UseSqlServer(cs, sql => sql.EnableRetryOnFailure(5, TimeSpan.FromSeconds(2), null))
                .Options;

            return new LoggingDbContext(options);
        }
    }
}
