namespace CarbonAware.Targets.Options;

public sealed class GitHubActionsOptions
{
    public string Owner { get; set; } = "";
    public string Repo { get; set; } = "";
    public string Branch { get; set; } = "main";
    public string AzureWorkflow { get; set; } = "";
    public string GcpWorkflow { get; set; } = "";
    public string AwsWorkflow { get; set; } = "";
    public string Token { get; set; } = "";
}
