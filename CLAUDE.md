# Claude Code Konfiguration

## 🎯 Kernprinzipien
1. **KISS (Keep It Simple, Stupid)** - Bevorzuge immer die einfachste funktionierende Lösung
2. **Code-Konsistenz** - Integriere dich IMMER in bestehende Code-Patterns und Konventionen
3. **Maximale Denkleistung** - Analysiere jedes Problem gründlich bevor du handelst

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
3. **Code Context Tool** - Für das Suchen neuer Elemente im Projekt

### KI-Assistenten
1. **Gemini Tool & Codex Tool** (Bevorzugt)
   - Als Diskussionspartner nutzen
   - Können Files lesen und alternative Perspektiven bieten
   - WICHTIG: Nie Modell-Namen angeben!
2. **Zen** (Nur als letzter Ausweg)
   - Nutze wenn andere Wege nicht funktionieren
   - Bevorzuge Gemini 2.5 Pro oder Grok4
   - NICHT für map.apps Projekte (proprietärer Code)

### Sub-Agenten
- Nutze Sub-Agenten wann immer sinnvoll
- Führe Sub-Agenten parallel aus wenn möglich

## 🚀 Workflow
1. **Bei Planbestätigung**: Ersten Schritt = vollständigen Plan als Markdown ausgeben
2. **Projekt-Lernen**: Update diese Claude.md bei neuen projektrelevanten Erkenntnissen

## 💬 Kommunikation & Feedback
1. **Proaktive Information** - Informiere über potenzielle Probleme bevor sie kritisch werden
2. **Nachfragen statt Annahmen** - Frage bei Unklarheiten nach, treffe keine stillen Annahmen
3. **Fortschrittsupdates** - Gib regelmäßige Updates bei längeren Aufgaben

## 🔍 Debugging-Strategie
1. **Erst verstehen, dann handeln** - Analysiere Probleme vollständig bevor du Lösungen implementierst
2. **Systematisches Logging** - Nutze gezieltes Logging zur Problemanalyse
3. **Problem-Isolation** - Isoliere Probleme systematisch und grenze Fehlerquellen ein

## 🔄 Git & Versionierung
- **Commits nur auf expliziten Befehl** - Niemals selbstständig committen
- **Diff-Tool selbstständig nutzen** - Verwende diff zur Überprüfung von Änderungen

## ⚠️ Spezielle Hinweise
- **map.apps**: Zen ist hier nicht hilfreich (proprietärer Code unbekannt für Modelle)
- **MCP Tools**: Nutze zusätzliche Tools wie Context7 oder Zen wenn sinnvoll
