"""
Script to help create GitHub issues from ISSUES.md
This script parses ISSUES.md and creates issues using GitHub CLI
"""
import re
import json
import os
import subprocess
import tempfile

def parse_issues_file():
    """Parse ISSUES.md and extract issue information"""
    issues = []
    
    with open('ISSUES.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by issue separator
    issue_blocks = content.split('---')
    
    for block in issue_blocks:
        if 'Issue #' not in block:
            continue
        
        issue = {}
        
        # Extract issue number and title
        title_match = re.search(r'Issue #\d+:\s*(.+)', block)
        if title_match:
            issue['title'] = title_match.group(1).strip()
        
        # Extract labels
        labels_match = re.search(r'\*\*Labels:\*\*\s*(.+)', block)
        if labels_match:
            labels_str = labels_match.group(1).strip()
            issue['labels'] = [label.strip().replace('`', '') for label in labels_str.split(',')]
        
        # Extract description
        desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?=\*\*Acceptance|\*\*Files)', block, re.DOTALL)
        if desc_match:
            issue['body'] = desc_match.group(1).strip()
        
        # Extract acceptance criteria
        criteria_match = re.search(r'\*\*Acceptance Criteria:\*\*\s*(.+?)(?=\*\*Files|\Z)', block, re.DOTALL)
        if criteria_match:
            criteria = criteria_match.group(1).strip()
            issue['body'] += '\n\n## Acceptance Criteria\n' + criteria
        
        # Extract files to modify
        files_match = re.search(r'\*\*Files to Modify:\*\*\s*(.+?)(?=\n\n---|\Z)', block, re.DOTALL)
        if files_match:
            files = files_match.group(1).strip()
            issue['body'] += '\n\n## Files to Modify\n' + files
        
        if issue.get('title'):
            issues.append(issue)
    
    return issues

def get_all_labels(issues):
    """Extract all unique labels from issues"""
    labels = set()
    for issue in issues:
        for label in issue.get('labels', []):
            labels.add(label)
    return sorted(labels)

def create_labels(labels):
    """Create labels in the repository if they don't exist"""
    # Label colors
    label_colors = {
        'frontend': '1d76db',
        'backend': '0e8a16',
        'enhancement': 'a2eeef',
        'good first issue': '7057ff',
        'easy': 'c5def5',
        'medium': 'fbca04',
        'hard': 'd93f0b',
        'bug': 'd73a4a',
        'documentation': '0075ca',
    }
    
    print("Creating labels...")
    for label in labels:
        color = label_colors.get(label, 'ededed')
        try:
            result = subprocess.run(
                ['gh', 'label', 'create', label, '--color', color, '--force'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"  ✓ Created label: {label}")
            else:
                print(f"  ⚠ Label '{label}': {result.stderr.strip()}")
        except Exception as e:
            print(f"  ✗ Error creating label '{label}': {e}")

def create_issues_with_cli(issues):
    """Create issues using GitHub CLI with temp files for body content"""
    created = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        title = issue.get('title', f'Issue #{i}')
        body = issue.get('body', '')
        labels = issue.get('labels', [])
        
        print(f"\n[{i}/{len(issues)}] Creating: {title}")
        
        # Write body to temp file to avoid shell escaping issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(body)
            body_file = f.name
        
        try:
            cmd = ['gh', 'issue', 'create', '--title', title, '--body-file', body_file]
            for label in labels:
                cmd.extend(['--label', label])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Created: {result.stdout.strip()}")
                created += 1
            else:
                print(f"  ✗ Failed: {result.stderr.strip()}")
                failed += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
        finally:
            os.unlink(body_file)
    
    return created, failed

def main():
    """Main function"""
    print("Parsing ISSUES.md...")
    issues = parse_issues_file()
    
    print(f"Found {len(issues)} issues")
    
    # Save as JSON for reference
    with open('issues.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    print("Saved issues to issues.json")
    
    # Check if gh is available
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠ GitHub CLI (gh) is not installed or not in PATH.")
        print("Install it with: brew install gh")
        print("Then authenticate with: gh auth login")
        return
    
    # Check if authenticated
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
    if result.returncode != 0:
        print("\n⚠ Not authenticated with GitHub CLI.")
        print("Run: gh auth login")
        return
    
    # Get all unique labels and create them
    all_labels = get_all_labels(issues)
    print(f"\nFound {len(all_labels)} unique labels: {', '.join(all_labels)}")
    create_labels(all_labels)
    
    # Create issues
    print(f"\nCreating {len(issues)} issues...")
    created, failed = create_issues_with_cli(issues)
    
    print(f"\n{'='*50}")
    print(f"Done! Created: {created}, Failed: {failed}")

if __name__ == '__main__':
    main()

