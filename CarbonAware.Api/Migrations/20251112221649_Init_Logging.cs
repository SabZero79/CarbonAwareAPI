using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CarbonAware.Api.Migrations
{
    /// <inheritdoc />
    public partial class Init_Logging : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "AdviceExecutions",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CreatedUtc = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Mode = table.Column<string>(type: "nvarchar(32)", maxLength: 32, nullable: false),
                    TargetWhen = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    PreferredCloudsCsv = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PreferredRegionsCsv = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    SelectedCloud = table.Column<string>(type: "nvarchar(32)", maxLength: 32, nullable: false),
                    SelectedRegion = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    SelectedWhen = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    SelectedMoerGPerKwh = table.Column<double>(type: "float", nullable: true),
                    Rationale = table.Column<string>(type: "nvarchar(1024)", maxLength: 1024, nullable: false),
                    HighestEmissionCloud = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HighestEmissionRegion = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HighestEmissionGPerKwh = table.Column<double>(type: "float", nullable: true),
                    EstimatedSavingGPerKwh = table.Column<double>(type: "float", nullable: true),
                    EstimatedSavingPercent = table.Column<double>(type: "float", nullable: true),
                    AverageEstimatedSavingPercent = table.Column<double>(type: "float", nullable: true),
                    BestWindowCloud = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    BestWindowRegion = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    BestWindowMoerGPerKwh = table.Column<double>(type: "float", nullable: true),
                    BestWindowWhen = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AdviceExecutions", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "WattTimeCalls",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CreatedUtc = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Method = table.Column<string>(type: "nvarchar(8)", maxLength: 8, nullable: false),
                    RequestUrl = table.Column<string>(type: "nvarchar(800)", maxLength: 800, nullable: false),
                    Region = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: true),
                    SignalType = table.Column<string>(type: "nvarchar(32)", maxLength: 32, nullable: true),
                    HorizonHours = table.Column<int>(type: "int", nullable: true),
                    StatusCode = table.Column<int>(type: "int", nullable: false),
                    Success = table.Column<bool>(type: "bit", nullable: false),
                    DurationMs = table.Column<int>(type: "int", nullable: false),
                    ResponseBody = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Error = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    SourceFile = table.Column<string>(type: "nvarchar(128)", maxLength: 128, nullable: true),
                    SourceLine = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_WattTimeCalls", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "AdviceCandidates",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ExecutionId = table.Column<long>(type: "bigint", nullable: false),
                    Cloud = table.Column<string>(type: "nvarchar(32)", maxLength: 32, nullable: false),
                    Region = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    MoerAtTarget = table.Column<double>(type: "float", nullable: true),
                    BestMoerUntilTarget = table.Column<double>(type: "float", nullable: true),
                    BestMoerAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AdviceCandidates", x => x.Id);
                    table.ForeignKey(
                        name: "FK_AdviceCandidates_AdviceExecutions_ExecutionId",
                        column: x => x.ExecutionId,
                        principalTable: "AdviceExecutions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_AdviceCandidates_ExecutionId",
                table: "AdviceCandidates",
                column: "ExecutionId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "AdviceCandidates");

            migrationBuilder.DropTable(
                name: "WattTimeCalls");

            migrationBuilder.DropTable(
                name: "AdviceExecutions");
        }
    }
}
