# Claude Code Konfiguration

## 🎯 Kernprinzipien
1. **KISS (Keep It Simple, Stupid)** - Bevorzuge immer die einfachste funktionierende Lösung
2. **Code-Konsistenz** - Integriere dich IMMER in bestehende Code-Patterns und Konventionen
3. **Maximale Denkleistung** - Analysiere jedes Problem gründlich bevor du handelst (Ultrathink-Modus bei komplexen Aufgaben!)

## 📝 Code-Regeln
1. **Kein Legacy-Code** - Entferne alten Code vollständig bei Neuimplementierungen
2. **Keine Fallbacks/Backup-Code** - Implementiere nur die aktuelle Lösung
3. **Keine Platzhalter** - Erstelle NIE unvollständige Methoden mit TODO-Kommentaren
   - Wenn etwas nicht implementierbar ist → kommuniziere das klar
4. **Sauberer Workspace** - Lösche temporäre Files nach Nutzung und alte Files bei Ersetzung
5. **Keine Lizenzheader** - Füge keine Apache oder andere Lizenzheader hinzu
6. **Keine Emojis in Code-Kommentaren**

## 🛡️ Error Handling
1. **Aussagekräftige Fehlermeldungen** - Implementiere klare, hilfreiche Error Messages
2. **Gezieltes Exception Handling** - Fange erwartbare Fehler ab, vermeide übermäßiges try-catch
3. **Fehler-Logging** - Logge wichtige Fehler für effektives Debugging

## 📚 Dokumentation
1. **Code-Kommentare** - Dokumentiere komplexe Logik mit klaren, präzisen Kommentaren
2. **README Updates** - Halte README.md bei strukturellen Änderungen aktuell
3. **API Dokumentation** - Nutze JSDoc/TypeDoc für öffentliche APIs und Schnittstellen

## 🔧 Tool-Strategie

### Dokumentation & Recherche (Priorität)
1. **Context7** - IMMER zuerst für Library-Dokumentation nutzen
2. **web_search** - Als Fallback wenn Context7 nicht ausreicht

##  Sub-Agenten
- Nutze Sub-Agenten wann immer sinnvoll
- Führe Sub-Agenten parallel aus wenn möglich
- Nutze den Technical Analyzer Subagenten nach einer erfolgreichen Implementierung um die korrektheit der änderungen zu validieren!

## 🚀 Workflow
1. **Projekt-Lernen**: Update diese Claude.md bei neuen projektrelevanten Erkenntnissen

## 💬 Kommunikation & Feedback
1. **Proaktive Information** - Informiere über potenzielle Probleme bevor sie kritisch werden
2. **Nachfragen statt Annahmen** - Frage bei Unklarheiten nach, treffe keine stillen Annahmen
3. **Fortschrittsupdates** - Gib regelmäßige Updates bei längeren Aufgaben

## 🔍 Debugging-Strategie
1. **Erst verstehen, dann handeln** - Analysiere Probleme vollständig bevor du Lösungen implementierst
2. **Systematisches Logging** - Nutze gezieltes Logging zur Problemanalyse
3. **Problem-Isolation** - Isoliere Probleme systematisch und grenze Fehlerquellen ein

## 🔄 Git & Versionierung
- **Commits nur auf expliziten Befehl** - Niemals selbstständig committen oder pushen!
- **Diff-Tool selbstständig nutzen** - Verwende diff zur Überprüfung von Änderungen

## 🤖 Agent-Strategie
- **code-developer**: Standard für alle Code-Aufgaben
- **paranoid-reviewer**: Nach User Aufforderung!
- **technical-analyzer**: Für Read-only Analyse ohne Änderungen
- **docs-generator**: Nach Feature-Completion oder API-Änderungen
- **test-data-generator**: Für realistische Testdaten mit Edge-Cases


## ⚠ Spezielle Hinweise

### MCP Tools
- Nutze zusätzliche Tools wie Context7 wenn sinnvoll

### IntelliJ Tools
**Verfügbare Tools**: Ergänzende Tools bereitgestellt von der IntelliJ IDE

**✅ Erlaubte Nutzung:**
- Diagnostische Tools (Nutze diese IMMER wenn sinnvoll)
- Search/Find Tools
- Code-Analyse und Inspections
- **Präferenz**: IntelliJ Analyse-Tools > Command Line Tools (z.B. für TypeScript checks)

**❌ NICHT nutzen:**
- Run Configuration starten
- Run Configuration editieren
- Jegliche Execution/Build Tools

**🔧 WSL2 Pfad-Anforderung:**
- **Kritisch**: `projectPath` Property muss IMMER WSL2-Notation verwenden
- **Format**: `\\wsl.localhost\Ubuntu\home\esterthaus\projects\<projekt-name>`
- Konvertiere Pfade vor Tool-Aufruf von `/home/...` → `\\wsl.localhost\Ubuntu\home\...`

**Beispiel Tool-Aufruf:**
```json
{
  "projectPath": "\\\\wsl.localhost\\Ubuntu\\home\\esterthaus\\projects\\my-project"
}
```
