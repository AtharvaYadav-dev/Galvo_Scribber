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
    print("Building executable with PyInstaller for PySide6 + QML Engine...")
    app_name_nospace = version.APP_NAME.replace(' ', '_')
    sep = os.pathsep

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--name={app_name_nospace}",
        f"--paths={os.path.join('gerbyx-main', 'src')}",
        f"--add-data=qml{sep}qml",
        f"--add-data=fonts{sep}fonts",
        f"--add-data=logo{sep}logo",
        f"--add-data=config{sep}config",
        f"--add-data=gerbyx-main{sep}gerbyx-main",
        "--hidden-import=PySide6.QtQuick",
        "--hidden-import=PySide6.QtQuickControls2",
        "--hidden-import=PySide6.QtQml",
        "--hidden-import=pygrabber",
        "--hidden-import=gerbyx",
        "--hidden-import=gerbyx.tokenizer",
        "--hidden-import=gerbyx.parser",
        "--hidden-import=gerbyx.processor",
        "--collect-submodules=bridges",
        "--collect-submodules=sppl_agent",
        "--collect-all=gerbyx",
        "--exclude-module=PySide6.QtWebEngineCore",
        "--exclude-module=PySide6.QtWebEngineWidgets",
        "--exclude-module=PySide6.QtWebEngineQuick",
        "--exclude-module=PySide6.QtDesigner",
        "--exclude-module=PySide6.QtTest",
        "--exclude-module=PySide6.QtPdf",
        "--exclude-module=PySide6.QtPdfWidgets",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=matplotlib",
        "--exclude-module=botocore",
        "--exclude-module=boto3",
        "--exclude-module=tkinter",
    ]

    if os.path.exists("version_info.txt"):
        cmd.append("--version-file=version_info.txt")

    icon_path = os.path.join("logo", "new_logo.ico")
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")

    if client_id or os.path.exists("sppl_config.json"):
        cmd.append(f"--add-data=sppl_config.json{sep}.")

    cmd.append("main_qml.py")

    print(f"Running PyInstaller command:\n{' '.join(cmd)}\n")
    subprocess.run(cmd, check=True)

def update_and_compile_installer(client_id=None):
    print("Updating Inno Setup script...")
    iss_path = os.path.join('installer', 'Mini_Scriber.iss')
    
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

def validate_github_token():
    import requests
    token = get_github_token()
    if not token:
        return False, "GITHUB_TOKEN environment variable not set and github_token.txt not found."
    
    repo_owner = os.environ.get('GITHUB_OWNER', 'ruthrane25')
    repo_name = os.environ.get('GITHUB_REPO', 'Mini_Scriber')
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    try:
        resp = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers)
        if resp.status_code == 200:
            return True, "Valid token with access to repository."
        elif resp.status_code == 401:
            return False, "401 Unauthorized (Bad credentials). Your GitHub Personal Access Token in github_token.txt has expired or is invalid."
        elif resp.status_code == 403:
            return False, f"403 Forbidden. Token lacks permissions: {resp.json().get('message')}"
        elif resp.status_code == 404:
            return False, f"404 Not Found. Repository {repo_owner}/{repo_name} not found or token lacks access."
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, f"Network error connecting to GitHub: {e}"

def check_github_release_exists(tag_name):
    import requests
    repo_owner = os.environ.get('GITHUB_OWNER', 'ruthrane25')
    repo_name = os.environ.get('GITHUB_REPO', 'Mini_Scriber')
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = get_github_token()
    # Only send Authorization header if token is present
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 401:
        # Fallback to unauthenticated query for public repo tag check
        resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
    return resp.status_code == 200

def get_release_notes(cli_notes=None, cli_notes_file=None):
    """Resolves release notes from CLI arguments, a notes file, or standard changelog files."""
    if cli_notes and cli_notes.strip():
        return cli_notes.strip()
    if cli_notes_file and os.path.exists(cli_notes_file):
        with open(cli_notes_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                print(f"Loaded release notes from specified file: {cli_notes_file}")
                return content
    # Auto-detect default release notes files
    for candidate in ['release_notes.txt', 'RELEASE_NOTES.md', 'CHANGELOG.md']:
        if os.path.exists(candidate):
            with open(candidate, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    print(f"Auto-detected release notes from: {candidate}")
                    return content
    return f"Automated release build for {version.APP_NAME} v{version.VERSION}."

def upload_to_github_release(installer_path, release_notes=None):
    print("Preparing GitHub Release upload...")
    import requests
    
    token = get_github_token()
    if not token:
        print("Warning: GITHUB_TOKEN environment variable not set and github_token.txt not found.")
        print("Set it using: set GITHUB_TOKEN=your_fine_grained_pat or paste it into github_token.txt")
        return
        
    repo_owner = os.environ.get('GITHUB_OWNER', 'ruthrane25')
    repo_name = os.environ.get('GITHUB_REPO', 'Mini_Scriber')
    tag_name = f"v{version.VERSION}"
    body_text = release_notes or f"Automated release build for {version.APP_NAME} {tag_name}."
    
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
        "body": body_text,
        "draft": False,
        "prerelease": False
    }
    
    resp = requests.post(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases", headers=headers, json=release_data)
    
    if resp.status_code == 422: # Release might already exist
        print(f"Release {tag_name} might already exist. Fetching it...")
        resp = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}", headers=headers)
        if resp.status_code == 200 and release_notes:
            rel_id = resp.json().get('id')
            if rel_id:
                print(f"Updating release notes for existing release {tag_name}...")
                requests.patch(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/{rel_id}", headers=headers, json={"body": body_text})
        
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
    parser = argparse.ArgumentParser(description="Build script for Mini Scriber App (PySide6 + QML)")
    parser.add_argument("--client-id", help="Build specific installer for a client", default=None)
    parser.add_argument("--project-id", help="Project ID for the client build", default=None)
    parser.add_argument("--api-url", help="API URL to bundle for the client", default="http://127.0.0.1:8000")
    parser.add_argument("--skip-upload", action="store_true", help="Build installer locally without uploading to GitHub")
    parser.add_argument("--force-rebuild", action="store_true", help="Force rebuilding even if installer exists locally")
    parser.add_argument("--notes", help="Changelog / release notes text to display to users in the update modal", default=None)
    parser.add_argument("--notes-file", help="Path to text/markdown file containing release notes (default: release_notes.txt)", default=None)
    args = parser.parse_args()

    # Resolve release notes (from CLI string, file, or default release_notes.txt)
    resolved_release_notes = get_release_notes(args.notes, args.notes_file)

    app_name_nospace = version.APP_NAME.replace(' ', '_')
    tag_name = f"v{version.VERSION}"
    
    if args.client_id:
        installer_path = os.path.join('dist', f"{app_name_nospace}_{version.VERSION}_Setup_{args.client_id}.exe")
        print(f"--- CLIENT BUILD MODE ({args.client_id}) ---")
        with open("sppl_config.json", "w") as f:
            json.dump({
                "client_id": args.client_id,
                "project_id": args.project_id or "mini_scriber_proj_001",
                "api_url": args.api_url
            }, f)
    else:
        installer_path = os.path.join('dist', f"{app_name_nospace}_{version.VERSION}_Setup.exe")
        local_exists = os.path.exists(installer_path)

        if not args.skip_upload:
            print(f"Validating GitHub credentials for release upload...")
            token_valid, token_msg = validate_github_token()
            if not token_valid:
                print(f"\n========================================================")
                print(f" ERROR: GitHub Release upload will fail!")
                print(f" {token_msg}")
                print(f" To fix this:")
                print(f"  1. Go to GitHub -> Settings -> Developer Settings -> Personal Access Tokens")
                print(f"  2. Generate a token with 'Contents: Read and write' on 'ruthrane25/Mini_Scriber'")
                print(f"  3. Paste it into 'github_token.txt' (or pass --skip-upload to build locally only)")
                print(f"========================================================\n")
                sys.exit(1)

            print(f"Checking status for {tag_name} on GitHub...")
            release_exists = check_github_release_exists(tag_name)
            
            if release_exists:
                print(f"\n========================================================")
                print(f" ERROR: Version {tag_name} already exists on GitHub!")
                print(f" Please increment VERSION in version.py and run again.")
                print(f"========================================================\n")
                sys.exit(1)
                
            if local_exists and not args.force_rebuild:
                print(f"\nSetup executable for {tag_name} already exists locally.")
                print("Skipping PyInstaller build and uploading directly to GitHub...\n")
                upload_to_github_release(installer_path, release_notes=resolved_release_notes)
                sys.exit(0)
        
    # Full Process
    print("\nStarting full build and release process for Mini Scriber 2.0 (QML)...\n")
    update_version_info_txt()
    build_executable(client_id=args.client_id)
    update_and_compile_installer(client_id=args.client_id)
    print("\n========================================================")
    print(" Release build complete! Installer is located in the 'dist' folder.")
    print(f" Target: {os.path.abspath(installer_path)}")
    print("========================================================\n")
    
    if not args.client_id and not args.skip_upload:
        if os.path.exists(installer_path):
            upload_to_github_release(installer_path, release_notes=resolved_release_notes)
        else:
            print(f"Error: Installer not found at {installer_path}")
