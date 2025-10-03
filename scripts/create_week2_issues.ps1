# Create Week 2 GitHub Issues
# Run this script to create all 6 Week 2 feature branch issues

param(
    [Parameter(Mandatory=$false)]
    [string]$Token = $env:GITHUB_TOKEN
)

# GitHub repo info
$Owner = "MSD21091969"
$Repo = "my-tiny-data-collider"
$BaseUrl = "https://api.github.com/repos/$Owner/$Repo/issues"

# Check for token
if (-not $Token) {
    Write-Host "ERROR: GitHub token not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your token first:" -ForegroundColor Yellow
    Write-Host '  $env:GITHUB_TOKEN = ''your_token_here''' -ForegroundColor Green
    Write-Host "  .\scripts\create_week2_issues.ps1" -ForegroundColor Green
    exit 1
}

Write-Host ""
Write-Host "Creating Week 2 GitHub Issues..." -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

$CreatedIssues = @()

# Issue 1: Integration Test Templates
$Issue1 = @{
    title = "[Week 2] Implement Integration Test Templates"
    body = @"
## Goal
Generate integration tests for service layer policy enforcement.

## Tasks
- [ ] Create templates/integration_test_template.py.jinja2
- [ ] Extend Tool Factory to generate service-layer tests
- [ ] Test policy enforcement scenarios
- [ ] Generate integration tests for echo_tool
- [ ] Add 15+ integration test cases
- [ ] Document in docs/INTEGRATION_TESTING.md

## Acceptance Criteria
- [ ] Template generates valid pytest integration tests
- [ ] All echo_tool integration tests pass
- [ ] Coverage ≥ 90% for service layer
- [ ] Documentation complete

## Branch
feature/integration-test-templates

## Estimate
3-4 days
"@
    labels = @("enhancement")
}

# Issue 2: API Test Templates
$Issue2 = @{
    title = "[Week 2] Implement API Test Templates"
    body = @"
## Goal
Generate API tests for HTTP layer end-to-end validation.

## Tasks
- [ ] Create templates/api_test_template.py.jinja2
- [ ] Extend Tool Factory to generate HTTP-layer tests
- [ ] Test JWT authentication
- [ ] Test RequestEnvelope flow
- [ ] Mock FastAPI TestClient setup
- [ ] Generate API tests for echo_tool
- [ ] Add 12+ API test cases
- [ ] Document in docs/API_TESTING.md

## Acceptance Criteria
- [ ] Template generates valid FastAPI tests
- [ ] All echo_tool API tests pass
- [ ] Coverage ≥ 90% for HTTP layer
- [ ] Documentation complete

## Branch
feature/api-test-templates

## Estimate
3-4 days
"@
    labels = @("enhancement")
}

# Issue 3: Gmail Toolset
$Issue3 = @{
    title = "[Week 2] Implement Gmail Toolset"
    body = @"
## Goal
Implement Gmail toolset with real API integration.

## Tasks
- [ ] Create YAML definitions (list, send, search, get)
- [ ] Implement API client wrappers
- [ ] Add OAuth2 authentication flow
- [ ] Generate and test all Gmail tools
- [ ] Add integration with casefile storage
- [ ] Add 20+ test cases
- [ ] Document in docs/GMAIL_TOOLS.md

## Acceptance Criteria
- [ ] 4 Gmail tools with YAML configs
- [ ] API client implementation complete
- [ ] Unit + integration tests passing
- [ ] Coverage ≥ 90%
- [ ] Documentation complete
- [ ] OAuth2 flow working

## Branch
feature/google-workspace-gmail

## Estimate
5-6 days
"@
    labels = @("enhancement")
}

# Issue 4: Drive Toolset
$Issue4 = @{
    title = "[Week 2] Implement Drive Toolset"
    body = @"
## Goal
Implement Drive toolset with file operations.

## Tasks
- [ ] Create YAML definitions (list, upload, download, create folder, share)
- [ ] Implement API client wrappers
- [ ] Add OAuth2 authentication flow
- [ ] Handle file uploads/downloads
- [ ] Generate and test all Drive tools
- [ ] Add integration with casefile storage
- [ ] Add 25+ test cases
- [ ] Document in docs/DRIVE_TOOLS.md

## Acceptance Criteria
- [ ] 5 Drive tools with YAML configs
- [ ] API client implementation complete
- [ ] File upload/download working
- [ ] Unit + integration tests passing
- [ ] Coverage ≥ 90%
- [ ] Documentation complete

## Branch
feature/google-workspace-drive

## Estimate
5-6 days
"@
    labels = @("enhancement")
}

# Issue 5: Sheets Toolset
$Issue5 = @{
    title = "[Week 2] Implement Sheets Toolset"
    body = @"
## Goal
Implement Sheets toolset with data operations.

## Tasks
- [ ] Create YAML definitions (batch_get, batch_update, append, create)
- [ ] Implement API client wrappers
- [ ] Add OAuth2 authentication flow
- [ ] Handle data transforms
- [ ] Generate and test all Sheets tools
- [ ] Add integration with casefile storage
- [ ] Add 20+ test cases
- [ ] Document in docs/SHEETS_TOOLS.md

## Acceptance Criteria
- [ ] 4 Sheets tools with YAML configs
- [ ] API client implementation complete
- [ ] Data transforms working
- [ ] Unit + integration tests passing
- [ ] Coverage ≥ 90%
- [ ] Documentation complete

## Branch
feature/google-workspace-sheets

## Estimate
4-5 days
"@
    labels = @("enhancement")
}

# Issue 6: Tool Composition Engine
$Issue6 = @{
    title = "[Week 2] Implement Tool Composition Engine"
    body = @"
## Goal
Enable tool chaining and composition workflows.

## Tasks
- [ ] Extend MDSContext with chain management
- [ ] Implement composite tool type in templates
- [ ] Create chain execution engine
- [ ] Add conditional execution
- [ ] Implement chain state management
- [ ] Create example composite tool
- [ ] Add 30+ test cases
- [ ] Document in docs/TOOL_COMPOSITION.md

## Acceptance Criteria
- [ ] Composite tool type implemented
- [ ] Chain execution engine working
- [ ] Example composite tool functional
- [ ] Unit + integration tests passing
- [ ] Coverage ≥ 90%
- [ ] Documentation complete
- [ ] Error handling for failed chains

## Branch
feature/tool-composition

## Estimate
5-7 days
"@
    labels = @("enhancement")
}

# Collect all issues
$AllIssues = @($Issue1, $Issue2, $Issue3, $Issue4, $Issue5, $Issue6)

# Function to create issue
function CreateIssue {
    param($IssueData)
    
    Write-Host "Creating: $($IssueData.title)..." -ForegroundColor Cyan
    
    $Headers = @{
        "Authorization" = "Bearer $Token"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    
    $Body = @{
        title = $IssueData.title
        body = $IssueData.body
        labels = $IssueData.labels
    } | ConvertTo-Json -Depth 10
    
    try {
        $Response = Invoke-RestMethod -Uri $BaseUrl -Method Post -Headers $Headers -Body $Body -ContentType "application/json"
        Write-Host "SUCCESS: Created issue #$($Response.number)" -ForegroundColor Green
        Write-Host "  URL: $($Response.html_url)" -ForegroundColor Gray
        Write-Host ""
        return $Response
    }
    catch {
        Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        return $null
    }
}

# Create each issue
foreach ($Issue in $AllIssues) {
    $Result = CreateIssue -IssueData $Issue
    if ($Result) {
        $CreatedIssues += $Result
    }
    Start-Sleep -Seconds 1
}

# Summary
Write-Host ""
Write-Host "Summary" -ForegroundColor Yellow
Write-Host "=======" -ForegroundColor Yellow
Write-Host "Created: $($CreatedIssues.Count) / $($AllIssues.Count) issues" -ForegroundColor Green
Write-Host ""

if ($CreatedIssues.Count -gt 0) {
    Write-Host "View all issues at:" -ForegroundColor Cyan
    Write-Host "https://github.com/$Owner/$Repo/issues" -ForegroundColor White
    Write-Host ""
}

Write-Host "Done!" -ForegroundColor Green
