#!/bin/bash

# setup_github_repo.sh
# This script helps configure a GitHub repository for OSS development best practices.

echo "GitHub Repository Setup Script"
echo "--------------------------------"
echo "This script will guide you through setting up your GitHub repository with recommended configurations:"
echo "- Protect the main branch (require PR reviews, prevent force pushes, etc.)"
echo "- Enable issue and pull request templates guidance"
echo "- Enable vulnerability alerts"
echo "- Enable automated security fixes (Dependabot)"
echo ""
echo "Prerequisites:"
echo "- GitHub CLI ('gh') must be installed and authenticated."
echo "- You must have admin rights to the repository you want to configure."
echo "--------------------------------"

# Function to check if gh CLI is installed and user is logged in
check_gh_installed_and_auth() {
  if ! command -v gh &> /dev/null
  then
    echo "❌ ERROR: gh CLI not found."
    echo "   Please install gh CLI from https://cli.github.com/ and ensure it's in your PATH."
    exit 1
  fi
  echo "✓ gh CLI is installed."

  # Check gh auth status
  if ! gh auth status &> /dev/null; then
    echo "❌ ERROR: You are not logged into GitHub CLI."
    echo "   Please run 'gh auth login' to authenticate, then try running this script again."
    exit 1
  fi
  echo "✓ Authenticated with GitHub CLI."
}

# Function to get repository information
get_repo_info() {
  echo ""
  echo "Please enter the details of the GitHub repository you want to configure:"
  read -p "Enter the repository owner (e.g., your-username): " REPO_OWNER
  while [[ -z "$REPO_OWNER" ]]; do
    echo "Repository owner cannot be empty."
    read -p "Enter the repository owner (e.g., your-username): " REPO_OWNER
  done

  read -p "Enter the repository name (e.g., your-repo-name): " REPO_NAME
  while [[ -z "$REPO_NAME" ]]; do
    echo "Repository name cannot be empty."
    read -p "Enter the repository name (e.g., your-repo-name): " REPO_NAME
  done
  echo ""
}

# Function to protect the main branch
protect_main_branch() {
  echo "⏳ Attempting to protect the main branch for ${REPO_OWNER}/${REPO_NAME}..."

  gh api \
    --method PUT \
    -H "Accept: application/vnd.github.v3+json" \
    "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
    -f allow_force_pushes=false \
    -f allow_deletions=false \
    -f enforce_admins=true \
    --slurpfile required_pull_request_reviews <(echo '{
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false,
      "required_approving_review_count": 1
    }') \
    -f required_status_checks=null \
    -f restrictions=null \
    --silent

  if [ $? -eq 0 ]; then
    echo "✅ Successfully protected the main branch."
    echo "   Branch Protection Rules Applied:"
    echo "   - Require pull request reviews before merging: On"
    echo "     - Required approving reviews: 1"
    echo "     - Dismiss stale pull request approvals: On"
    echo "   - Require status checks to pass before merging: Off (currently no specific checks enforced by script)"
    echo "   - Enforce admin bypass prevention: On"
    echo "   - Prevent force pushes: On"
    echo "   - Prevent deletions: On"
  else
    echo "❌ CRITICAL: Failed to protect the 'main' branch for ${REPO_OWNER}/${REPO_NAME}."
    echo "   This is a critical step. Further repository setup might be incomplete or insecure."
    echo "   Please check the repository path, your permissions, and gh CLI authentication."
    exit 1
  fi
}

# Function to enable issue templates
enable_issue_templates() {
  echo "⏳ Configuring issue templates guidance for ${REPO_OWNER}/${REPO_NAME}..."
  gh api \
    --method PATCH \
    -H "Accept: application/vnd.github.v3+json" \
    "/repos/${REPO_OWNER}/${REPO_NAME}" \
    -f has_issues=true \
    --silent

  if [ $? -eq 0 ]; then
    echo "✅ Issue tracking has been confirmed/enabled."
    echo "   Reminder: Create detailed issue templates in '.github/ISSUE_TEMPLATE'."
  else
    echo "⚠️ WARNING: Failed to update repository settings for issue templates guidance for ${REPO_OWNER}/${REPO_NAME}."
    echo "   Please check your permissions. This is not a critical failure; script will continue."
  fi
}

# Function to enable pull request templates
enable_pr_templates() {
  echo "ℹ️ Configuring pull request templates guidance for ${REPO_OWNER}/${REPO_NAME}..."
  echo "   Pull request templates are encouraged for consistency."
  echo "   Reminder: Create templates in '.github/PULL_REQUEST_TEMPLATE/' or as '.github/PULL_REQUEST_TEMPLATE.md'."
}

# Function to enable vulnerability alerts
enable_vulnerability_alerts() {
  echo "⏳ Enabling vulnerability alerts for ${REPO_OWNER}/${REPO_NAME}..."
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github.v3+json" \
    "/repos/${REPO_OWNER}/${REPO_NAME}/vulnerability-alerts" \
    --silent

  if [ $? -eq 0 ]; then
    echo "✅ Successfully enabled vulnerability alerts for ${REPO_OWNER}/${REPO_NAME}."
  else
    echo "⚠️ WARNING: Failed to enable vulnerability alerts for ${REPO_OWNER}/${REPO_NAME}."
    echo "   This feature might require admin rights or a specific GitHub plan."
    echo "   Please check your permissions. Script will continue."
  fi
}

# Function to enable automated security fixes (Dependabot)
enable_automated_security_fixes() {
  echo "⏳ Enabling automated security fixes (Dependabot) for ${REPO_OWNER}/${REPO_NAME}..."
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github.v3+json" \
    "/repos/${REPO_OWNER}/${REPO_NAME}/automated-security-fixes" \
    --silent

  if [ $? -eq 0 ]; then
    echo "✅ Successfully enabled automated security fixes (Dependabot) for ${REPO_OWNER}/${REPO_NAME}."
  else
    echo "⚠️ WARNING: Failed to enable automated security fixes (Dependabot) for ${REPO_OWNER}/${REPO_NAME}."
    echo "   This feature might require admin rights or a specific GitHub plan (e.g., GitHub Advanced Security)."
    echo "   Please check your permissions. Script will continue."
  fi
}

# --- Main script execution ---
check_gh_installed_and_auth
get_repo_info

echo "--------------------------------"
echo "You are about to apply settings to the following repository:"
echo "Owner: ${REPO_OWNER}"
echo "Name:  ${REPO_NAME}"
echo "--------------------------------"
read -p "Do you want to proceed with applying these settings? (yes/no): " CONFIRMATION

if [[ "${CONFIRMATION,,}" != "yes" ]]; then
  echo "Configuration aborted by the user."
  exit 0
fi

echo ""
echo "Proceeding with repository configuration..."
echo "--------------------------------"

protect_main_branch
enable_issue_templates
enable_pr_templates
enable_vulnerability_alerts
enable_automated_security_fixes

echo "--------------------------------"
echo "✅ GitHub Repository Setup Script Finished!"
echo "All configured settings have been applied (or attempted) for ${REPO_OWNER}/${REPO_NAME}."
echo ""
echo "--------------------------------"
echo "Next Steps / Manual Configuration:"
echo "--------------------------------"
echo "- Consider creating detailed issue templates in the '.github/ISSUE_TEMPLATE' directory."
echo "- Consider creating pull request templates in the '.github/PULL_REQUEST_TEMPLATE' directory or as a '.github/PULL_REQUEST_TEMPLATE.md' file."
echo "- Review and configure specific required status checks for your 'main' branch protection rules if needed."
echo "  (Currently, no specific checks are enforced by this script beyond requiring PRs)."
echo "- Explore other repository settings that might be relevant to your project (e.g., Actions, Pages, webhooks, environments)."
echo "--------------------------------"

exit 0
