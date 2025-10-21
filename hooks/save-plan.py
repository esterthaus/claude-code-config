#!/usr/bin/env python3
"""
Auto-Save Approved Plans Hook
Speichert genehmigte Pläne als Markdown mit Plan-Titel als Dateinamen
"""
import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# Projekt-Verzeichnis für Plans - DIREKT in docs/
PROJECT_DIR = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
PLANS_DIR = Path(PROJECT_DIR) / 'docs'

# Log-Datei IMMER im Home-Verzeichnis (minimal logging)
HOME_DIR = Path.home()
LOG_FILE = HOME_DIR / '.claude' / 'hooks' / 'plan-hook.log'

def log(message):
    """Schreibe in zentrale Log-Datei (nur Fehler)"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')

def extract_title_from_plan(plan):
    """Extrahiere Titel aus Plan (erste Zeile, meist Markdown Header)"""
    lines = plan.strip().split('\n')
    if not lines:
        return None
    
    first_line = lines[0].strip()
    
    # Entferne Markdown Header Zeichen (# ## ### etc.)
    title = re.sub(r'^#+\s*', '', first_line)
    
    # Entferne Sonderzeichen und ersetze durch Bindestriche
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'\s+', '-', title)
    title = title.lower().strip('-')
    
    # Begrenze Länge
    if len(title) > 80:
        title = title[:80].rsplit('-', 1)[0]  # Schneide beim letzten Wort
    
    return title if title else None

def save_plan(input_data):
    try:
        # Extrahiere Tool-Informationen
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Nur für ExitPlanMode
        if tool_name != 'ExitPlanMode':
            sys.exit(0)
        
        # Plan extrahieren
        plan = tool_input.get('plan', '')
        if not plan:
            log("FEHLER: Kein Plan gefunden!")
            sys.exit(0)
        
        # Erstelle docs/ Verzeichnis
        PLANS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Extrahiere Titel für Dateinamen
        title = extract_title_from_plan(plan)
        
        if title:
            filename = f'{title}.md'
        else:
            # Fallback auf Timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'plan_{timestamp}.md'
        
        filepath = PLANS_DIR / filename
        
        # Falls Datei existiert, füge Timestamp hinzu
        if filepath.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{title}_{timestamp}.md' if title else filename
            filepath = PLANS_DIR / filename
        
        # Plan speichern
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'# Approved Plan\n')
            f.write(f'**Datum:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'**Projekt:** {PROJECT_DIR}\n\n')
            f.write('---\n\n')
            f.write(plan)
            f.write('\n\n---\n*Auto-saved by Claude Code hook*\n')
        
        # Nur Erfolg loggen
        log(f"✓ Plan gespeichert: {filepath}")
        
        # Bestätigungsnachricht (sichtbar mit Ctrl-R)
        print(f"✓ Plan gespeichert: {filepath}")
        
        sys.exit(0)
        
    except Exception as e:
        log(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(0)

if __name__ == '__main__':
    try:
        input_data = json.load(sys.stdin)
        save_plan(input_data)
    except Exception as e:
        log(f"STARTUP FEHLER: {e}")
        sys.exit(0)
