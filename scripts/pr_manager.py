import subprocess
import requests
import sys
import time

REPO = "Radhika-Thiriveedhi/share-meal-website"

def get_gh_token():
    res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
    return res.stdout.strip()

def run_git(args, check=True):
    res = subprocess.run(["git"] + args, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Git error: {res.stderr}")
        raise RuntimeError(f"Git command failed: {' '.join(args)}\n{res.stderr}")
    return res.stdout.strip()

def create_and_merge_pr(branch_name, commit_message, pr_title, pr_body, files=None):
    token = get_gh_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    print(f"\n--- Processing: {branch_name} ---")
    # 1. Switch to new branch
    run_git(["checkout", "-b", branch_name])
    
    # 2. Stage files
    if files:
        for f in files:
            run_git(["add", f])
    else:
        run_git(["add", "."])
        
    # 3. Commit
    run_git(["commit", "-m", commit_message])
    
    # 4. Push branch
    run_git(["push", "-u", "origin", branch_name])
    
    # 5. Create PR via GitHub API
    pr_data = {
        "title": pr_title,
        "head": branch_name,
        "base": "main",
        "body": pr_body
    }
    res = requests.post(f"https://api.github.com/repos/{REPO}/pulls", headers=headers, json=pr_data)
    if res.status_code != 201:
        print(f"Error creating PR: {res.status_code} - {res.text}")
        raise RuntimeError(f"Failed to create PR: {res.text}")
    pr_json = res.json()
    pr_num = pr_json["number"]
    pr_url = pr_json["html_url"]
    print(f"Created PR #{pr_num}: {pr_url}")
    
    # Allow GitHub 1 second to register mergeable state
    time.sleep(1)
    
    # 6. Merge PR via GitHub API
    merge_data = {
        "commit_title": f"Merge pull request #{pr_num} from {branch_name}",
        "commit_message": pr_title,
        "merge_method": "merge"
    }
    merge_res = requests.put(f"https://api.github.com/repos/{REPO}/pulls/{pr_num}/merge", headers=headers, json=merge_data)
    if merge_res.status_code != 200:
        print(f"Error merging PR #{pr_num}: {merge_res.status_code} - {merge_res.text}")
        raise RuntimeError(f"Failed to merge PR #{pr_num}: {merge_res.text}")
    print(f"Successfully merged PR #{pr_num}")
    
    # 7. Switch back to main and pull
    run_git(["checkout", "main"])
    run_git(["pull", "origin", "main"])
    
    # 8. Delete remote and local feature branch
    requests.delete(f"https://api.github.com/repos/{REPO}/git/refs/heads/{branch_name}", headers=headers)
    run_git(["branch", "-D", branch_name], check=False)
    print(f"Completed and cleaned up {branch_name}")
    return pr_num, pr_url

if __name__ == "__main__":
    if len(sys.argv) >= 5:
        branch = sys.argv[1]
        msg = sys.argv[2]
        title = sys.argv[3]
        body = sys.argv[4]
        files = sys.argv[5:] if len(sys.argv) > 5 else None
        create_and_merge_pr(branch, msg, title, body, files)
