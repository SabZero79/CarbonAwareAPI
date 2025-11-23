using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CarbonAware.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddWattTimeRequestId : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<Guid>(
                name: "RequestId",
                table: "WattTimeCalls",
                type: "uniqueidentifier",
                nullable: true);

            migrationBuilder.AlterColumn<DateTimeOffset>(
                name: "SelectedWhen",
                table: "AdviceExecutions",
                type: "datetimeoffset",
                nullable: true,
                oldClrType: typeof(DateTimeOffset),
                oldType: "datetimeoffset");

            migrationBuilder.AddColumn<Guid>(
                name: "RequestId",
                table: "AdviceExecutions",
                type: "uniqueidentifier",
                nullable: true);

            migrationBuilder.AddColumn<Guid>(
                name: "RequestId",
                table: "AdviceCandidates",
                type: "uniqueidentifier",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RequestId",
                table: "WattTimeCalls");

            migrationBuilder.DropColumn(
                name: "RequestId",
                table: "AdviceExecutions");

            migrationBuilder.DropColumn(
                name: "RequestId",
                table: "AdviceCandidates");

            migrationBuilder.AlterColumn<DateTimeOffset>(
                name: "SelectedWhen",
                table: "AdviceExecutions",
                type: "datetimeoffset",
                nullable: false,
                defaultValue: new DateTimeOffset(new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified), new TimeSpan(0, 0, 0, 0, 0)),
                oldClrType: typeof(DateTimeOffset),
                oldType: "datetimeoffset",
                oldNullable: true);
        }
    }
}
