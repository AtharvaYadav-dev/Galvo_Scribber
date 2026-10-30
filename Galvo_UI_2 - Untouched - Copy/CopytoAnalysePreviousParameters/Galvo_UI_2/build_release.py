import os
import sys
import shutil
import re
import subprocess
import hashlib
import json
import datetime
import argparse

# Load version info
import version

def update_version_info_txt():
    print("Updating version_info.txt...")
    v_tuple = tuple(version.VERSION.split('.'))
    if len(v_tuple) == 3:
        v_tuple = v_tuple + ('0',)
    
    if os.path.exists('version_info.txt'):
        with open('version_info.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex replacements
        content = re.sub(r"filevers=\(.*?\)", f"filevers=({','.join(v_tuple)})", content)
        content = re.sub(r"prodvers=\(.*?\)", f"prodvers=({','.join(v_tuple)})", content)
        content = re.sub(r"StringStruct\('FileVersion',\s*'.*?'\)", f"StringStruct('FileVersion', '{version.VERSION}')", content)
        content = re.sub(r"StringStruct\('ProductVersion',\s*'.*?'\)", f"StringStruct('ProductVersion', '{version.VERSION}')", content)
        content = re.sub(r"StringStruct\('CompanyName',\s*'.*?'\)", f"StringStruct('CompanyName', '{version.COMPANY}')", content)
        content = re.sub(r"StringStruct\('ProductName',\s*'.*?'\)", f"StringStruct('ProductName', '{version.APP_NAME}')", content)
        
        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(content)

def build_executable(client_id=None):
    print("Building executable with PyInstaller...")
    app_name_nospace = version.APP_NAME.replace(' ', '_')
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--name={app_name_nospace}",
        "--add-binary=gt5motion_GT.dll:.",
        "--add-binary=gt5motion.dll:.",
        "--add-binary=4_mcc_GT.bin:.",
        "--add-binary=5_mcc_GT.bin:.",
        "--add-data=style.json:.",
        "--add-data=config:config",
        "--add-data=Qss:Qss",
        "--add-data=newest100mm.cor:.",
        "--version-file=version_info.txt",
        "--icon=logo/new_logo.ico"
    ]
    if os.path.exists("logo/new_logo.ico"):
        cmd.insert(-1, "--icon=logo/new_logo.ico")
    if client_id:
        cmd.append("--add-data=sppl_config.json:.")
        
    cmd.append("main.py")
    subprocess.run(cmd, check=True)

def update_and_compile_installer(client_id=None):
    print("Updating Inno Setup script...")
    iss_path = os.path.join('installer', 'Galvo.iss')
    
    with open(iss_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update defines
    content = re.sub(r'#define MyAppVersion ".*?"', f'#define MyAppVersion "{version.VERSION}"', content)
    content = re.sub(r'#define MyAppName ".*?"', f'#define MyAppName "{version.APP_NAME}"', content)
    content = re.sub(r'#define MyAppPublisher ".*?"', f'#define MyAppPublisher "{version.COMPANY}"', content)
    content = re.sub(r'#define MyAppExeName ".*?"', f'#define MyAppExeName "{version.EXE_NAME}"', content)

    with open(iss_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Compiling Inno Setup script...")
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    iscc = None
    for p in iscc_paths:
        if os.path.exists(p):
            iscc = p
            break
            
    if not iscc:
        print("Warning: Inno Setup compiler (ISCC.exe) not found. Installer not compiled automatically.")
        return

    cmd = [iscc]
    if client_id:
        cmd.append(f'/F{version.APP_NAME.replace(" ", "_")}_{version.VERSION}_Setup_{client_id}')
    
    cmd.append(iss_path)
    subprocess.run(cmd, check=True)

def generate_sha256(filepath):
    print(f"Generating SHA-256 for {filepath}...")
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_github_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            with open('github_token.txt', 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            pass
    return token

def check_github_release_exists(tag_name):
    import requests
    token = get_github_token()
    repo_owner = os.environ.get('GITHUB_OWNER', 'ruthrane25')
    repo_name = os.environ.get('GITHUB_REPO', 'Galvo')
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}"
    resp = requests.get(url, headers=headers)
    return resp.status_code == 200

def upload_to_github_release(installer_path):
    print("Preparing GitHub Release upload...")
    import requests
    
    token = get_github_token()
    if not token:
        print("Warning: GITHUB_TOKEN environment variable not set and github_token.txt not found.")
        print("Set it using: set GITHUB_TOKEN=your_fine_grained_pat or paste it into github_token.txt")
        return
        
    repo_owner = os.environ.get('GITHUB_OWNER', 'ruthrane25')
    repo_name = os.environ.get('GITHUB_REPO', 'Galvo')
    tag_name = f"v{version.VERSION}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # 1. Create a Release
    print(f"Creating release {tag_name} in {repo_owner}/{repo_name}...")
    release_data = {
        "tag_name": tag_name,
        "name": f"{version.APP_NAME} {tag_name}",
        "body": f"Automated release build for {version.APP_NAME} {tag_name}.",
        "draft": False,
        "prerelease": False
    }
    
    resp = requests.post(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases", headers=headers, json=release_data)
    
    if resp.status_code == 422: # Release might already exist
        print(f"Release {tag_name} might already exist. Fetching it...")
        resp = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}", headers=headers)
        
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error communicating with GitHub: {e}")
        print(resp.text)
        return
        
    release_info = resp.json()
    upload_url = release_info['upload_url'].split('{')[0] # Clean templated URL
    
    # 2. Upload the Asset
    asset_name = os.path.basename(installer_path)
    print(f"Uploading asset {asset_name} to release...")
    
    headers['Content-Type'] = "application/octet-stream"
    with open(installer_path, 'rb') as f:
        upload_resp = requests.post(f"{upload_url}?name={asset_name}", headers=headers, data=f)
    
    try:
        upload_resp.raise_for_status()
        print("Upload complete! Release is available on GitHub.")
    except requests.exceptions.HTTPError as e:
        print(f"Error uploading asset: {e}")
        print(upload_resp.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build script for Mini Scriber App")
    parser.add_argument("--client-id", help="Build specific installer for a client", default=None)
    parser.add_argument("--project-id", help="Project ID for the client build", default=None)
    parser.add_argument("--api-url", help="API URL to bundle for the client", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    app_name_nospace = version.APP_NAME.replace(' ', '_')
    tag_name = f"v{version.VERSION}"
    
    if args.client_id:
        installer_path = os.path.join('dist', f"{app_name_nospace}_{version.VERSION}_Setup_{args.client_id}.exe")
        print(f"--- CLIENT BUILD MODE ({args.client_id}) ---")
        with open("sppl_config.json", "w") as f:
            json.dump({
                "client_id": args.client_id,
                "project_id": args.project_id or "galvo_proj_001",
                "api_url": args.api_url
            }, f)
    else:
        installer_path = os.path.join('dist', f"{app_name_nospace}_{version.VERSION}_Setup.exe")
        print(f"Checking status for {tag_name}...")
        release_exists = check_github_release_exists(tag_name)
        local_exists = os.path.exists(installer_path)
        
        if release_exists:
            print(f"\n========================================================")
            print(f" ERROR: Version {tag_name} already exists on GitHub!")
            print(f" Please increment VERSION in version.py and run again.")
            print(f"========================================================\n")
            sys.exit(1)
            
        if local_exists:
            print(f"\nSetup executable for {tag_name} already exists locally.")
            print("Skipping PyInstaller build and uploading directly to GitHub...\n")
            upload_to_github_release(installer_path)
            sys.exit(0)
        
    # Full Process
    print("\nStarting full build and release process...\n")
    update_version_info_txt()
    build_executable(client_id=args.client_id)
    update_and_compile_installer(client_id=args.client_id)
    print("Release build complete! Installer is located in the 'dist' folder.")
    
    if not args.client_id:
        if os.path.exists(installer_path):
            upload_to_github_release(installer_path)
        else:
            print(f"Error: Installer not found at {installer_path}")
