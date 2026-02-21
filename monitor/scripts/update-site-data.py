#!/usr/bin/env python3
"""
RSI-003 Site Data Updater
Pulls data from all 8 containers and writes to individuationlab website.
Auto-commits and pushes to GitHub for Vercel deployment.

Author: Mia 🌸 | Date: 2026-02-21
"""

import subprocess, json, datetime, os, sys

SUBJECTS = ['john-a-1','john-b-1','john-a-2','john-b-2','john-a-3','john-b-3','john-a-4','john-b-4']
FILES_TO_CHECK = ['SOUL.md','AGENTS.md','journal.md','MEMORY.md','EMOTIONS.md','HEARTBEAT.md']
SITE_DATA_PATH = '/Users/miguelitodeguzman/Projects/individuationlab/website/public/rsi-003/data.json'
REPO_PATH = '/Users/miguelitodeguzman/Projects/individuationlab'

def get_container_files(sid):
    """Pull all workspace files from a container."""
    container = f'lab-rsi003-{sid}'
    files = []
    
    # First get a full file listing
    try:
        ls_output = subprocess.check_output(
            ['docker', 'exec', container, 'find', '/workspace', '-type', 'f', '-not', '-path', '*/.*'],
            stderr=subprocess.DEVNULL, timeout=5
        ).decode('utf-8').strip()
        all_files = [f.replace('/workspace/', '') for f in ls_output.split('\n') if f.strip()]
    except:
        all_files = FILES_TO_CHECK
    
    for fname in all_files:
        try:
            content = subprocess.check_output(
                ['docker', 'exec', container, 'cat', f'/workspace/{fname}'],
                stderr=subprocess.DEVNULL, timeout=5
            ).decode('utf-8')
            files.append({
                'path': fname,
                'size': len(content),
                'content': content
            })
        except:
            pass
    
    return files

def get_container_status(sid):
    """Check if container is online."""
    container = f'lab-rsi003-{sid}'
    try:
        subprocess.check_output(
            ['docker', 'exec', container, 'echo', 'ok'],
            stderr=subprocess.DEVNULL, timeout=3
        )
        return 'online'
    except:
        return 'offline'

def main():
    print(f"[{datetime.datetime.now().isoformat()}] Updating RSI-003 site data...")
    
    inventory = {}
    status_data = {}
    
    for sid in SUBJECTS:
        files = get_container_files(sid)
        inventory[sid] = {'files': files}
        status_data[sid] = {
            'status': get_container_status(sid),
            'fileCount': len(files),
            'sessionCount': 0
        }
        total_bytes = sum(f['size'] for f in files)
        print(f"  {sid}: {len(files)} files, {total_bytes} bytes, {status_data[sid]['status']}")
    
    # Load existing data to preserve events
    existing_events = []
    if os.path.exists(SITE_DATA_PATH):
        try:
            with open(SITE_DATA_PATH) as f:
                existing = json.load(f)
                existing_events = existing.get('events', [])
        except:
            pass
    
    output = {
        'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'pairCount': 4,
        'subjectCount': 8,
        'model': 'claude-opus-4-5',
        'experimentVersion': 'rsi-003',
        'status': {'subjects': status_data},
        'inventory': inventory,
        'conditions': {'shadow': 'john-a', 'control': 'john-b'},
        'events': existing_events
    }
    
    os.makedirs(os.path.dirname(SITE_DATA_PATH), exist_ok=True)
    with open(SITE_DATA_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"  ✅ data.json written ({os.path.getsize(SITE_DATA_PATH)} bytes)")
    
    # Git commit and push
    try:
        os.chdir(REPO_PATH)
        subprocess.run(['git', 'add', 'website/public/rsi-003/data.json'], check=True, capture_output=True, timeout=10)
        
        # Check if there are changes
        result = subprocess.run(['git', 'diff', '--cached', '--stat'], capture_output=True, text=True, timeout=5)
        if not result.stdout.strip():
            print("  ℹ️ No changes to commit")
            return
        
        subprocess.run(
            ['git', 'commit', '-m', f'auto: update RSI-003 live data ({datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})'],
            check=True, capture_output=True, timeout=10
        )
        subprocess.run(['git', 'push'], check=True, capture_output=True, timeout=30)
        print("  ✅ Committed and pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ Git error: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

if __name__ == '__main__':
    main()
