using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CarbonAware.Api.Migrations
{
    /// <inheritdoc />
    public partial class Add_AverageEmissionGPerKwh : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<double>(
                name: "AverageEmissionGPerKwh",
                table: "AdviceExecutions",
                type: "float",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "AverageEmissionGPerKwh",
                table: "AdviceExecutions");
        }
    }
}
