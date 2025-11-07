
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# map.apps Framework - Allgemeine Entwicklungsdokumentation

## Inhaltsverzeichnis


1. [Technologie-Stack & Architektur](#technologie-stack--architektur)
2. [Bundle-System & Runtime-Verhalten](#bundle-system--runtime-verhalten)
3. [Component System & Dependency Injection](#component-system--dependency-injection)
4. [MapWidgetModel - Zentrale Map-API](#mapwidgetmodel---zentrale-map-api)
5. [Event System & Tool Integration](#event-system--tool-integration)
6. [UI-System: Vue.js & Window Management](#ui-system-vuejs--window-management)
7. [Store API & Daten-Management](#store-api--daten-management)
8. [Best Practices & Patterns](#best-practices--patterns)
9. [Häufige Fehler & Lösungen](#häufige-fehler--lösungen)
10. [Praktische Bundle-Beispiele](#praktische-bundle-beispiele)

---

## Technologie-Stack & Architektur

### Technologien
- **Frontend**: TypeScript, Vue.js 2.7, Vuetify, ArcGIS JavaScript API 4.31
- **Build-System**: Maven + Gulp/npm
- **Bundle-System**: OSGi-inspirierte Microkernel-Architektur
- **Testing**: Mocha (Unit Tests), Playwright (E2E Tests)

### Architektur-Prinzipien

```
┌─────────────────────────────────────┐
│    Anwendungs-Bundles (dein Code)  │
├─────────────────────────────────────┤
│    Framework-Bundles (system, etc.) │
├─────────────────────────────────────┤
│    Core-Bundles (apprt, apprt-core) │
├─────────────────────────────────────┤
│    JavaScript Runtime (Dojo)        │
└─────────────────────────────────────┘
```

**Kern-Konzepte:**
1. **Bundles** - Modulare Einheiten mit eigenem Lifecycle
2. **Components** - Services innerhalb von Bundles (deklarativ definiert)
3. **Service Registry** - Zentrale Verwaltung aller Services
4. **Dependency Injection** - Automatische Auflösung von Abhängigkeiten
5. **Event Bus** - Lose gekoppelte Kommunikation zwischen Bundles

---

## Bundle-System & Runtime-Verhalten

### Bundle-Struktur

```
my-bundle/
├── manifest.json       # Bundle-Definition & Component-Konfiguration
├── module.ts          # Export der Component-Implementierungen
├── MyService.ts       # Service-Implementierung
├── MyWidget.vue       # Vue UI-Komponente
├── MyController.ts    # Business-Logik
├── api.ts            # Public Interfaces (TypeScript)
├── nls/              # Internationalisierung
│   ├── bundle.js     # Default Sprache (meist Englisch)
│   └── de/bundle.js  # Deutsche Übersetzungen
└── tests/            # Unit-Tests
    └── MyTest.ts
```

### manifest.json - Bundle-Definition

Die `manifest.json` ist das Herzstück jedes Bundles. Sie definiert:
- Bundle-Metadaten (Name, Version, Dependencies)
- Components (Services) und deren Konfiguration
- UI-Widget-Platzierung
- Internationalisierung

```json
{
    "name": "my-bundle",
    "version": "1.0.0",
    "title": "${bundleName}",          // i18n reference
    "description": "${bundleDescription}",
    "vendor": "My Company",
    "productName": "map.apps",
    "layer": "module",
    "i18n": ["bundle"],                // Lädt nls/bundle.js

    "dependencies": {
        "apprt-vue": "~4.19.2",        // Vue.js Integration
        "apprt-binding": "~4.19.2",    // Data Binding
        "map-widget": "~4.19.2"        // Map API
    },

    "components": [
        // Components werden hier definiert (siehe nächster Abschnitt)
    ],

    "layout-widgets": [
        // Widget-Platzierung (siehe UI-System)
    ]
}
```

### module.ts - Component-Exports

Die `module.ts` exportiert die Implementierungen, die in der manifest.json referenziert werden:

```typescript
// Einfache Exports
export { default as MyService } from "./MyService";
export { default as MyController } from "./MyController";
export { default as MyWidgetFactory } from "./MyWidgetFactory";
```

### Runtime-Verhalten: Wie map.apps Bundles lädt

**Wichtig zu verstehen:**

1. **Bundle-Loading**: Bundles werden basierend auf `startLevel` und Dependencies geladen
2. **Component-Instantiierung**: Components werden erstellt basierend auf:
    - `immediate: true` → Sofort beim Bundle-Start
    - `immediate: false` (default) → Lazy, wenn Service das erste Mal angefordert wird
3. **Dependency Injection**: map.apps injiziert automatisch:
    - Services via `references`
    - Properties via `_properties`
    - i18n via `_i18n`
    - ComponentContext via `_componentContext`

**Lifecycle-Reihenfolge:**
```
1. Bundle wird geladen
2. module.ts wird ausgewertet
3. Components werden registriert (aber noch nicht instanziiert)
4. Bei Bedarf oder wenn immediate:true:
   a. Component-Instanz wird erstellt
   b. Properties werden injiziert
   c. References werden aufgelöst und injiziert
   d. activate() wird aufgerufen
```

---

## Component System & Dependency Injection

### Component-Definition in manifest.json

Components sind die zentralen Bausteine. Hier die wichtigsten Konfigurationsoptionen:

```json
{
    "name": "MyService",                    // Component-Name
    "impl": "MyServiceImpl",                // Implementierungs-Klasse (aus module.ts)
    "provides": [                           // Service-Interfaces
        "my.Service",
        "ct.api.event.EventHandler"
    ],

    // Lifecycle & Factory-Optionen
    "immediate": true,                      // Sofort instanziieren?
    "serviceFactory": false,                // Pro Bundle eine Instanz?
    "componentFactory": false,              // Als Factory verfügbar machen?
    "instanceFactory": false,               // createInstance/destroyInstance Pattern?
    "propertiesConstructor": true,          // Properties im Constructor?
    "enabled": true,                        // Component aktiviert?

    // Konfiguration
    "properties": {
        "apiUrl": "https://api.example.com",
        "timeout": 5000,
        "-privateProperty": "internal"      // Prefix "-" = private
    },

    // Abhängigkeiten
    "references": [
        {
            "name": "_mapWidgetModel",      // Property-Name in der Klasse
            "providing": "map-widget.MapWidgetModel",  // Service-Interface
            "cardinality": "1..1",          // Pflicht
            "policy": "static"              // static oder dynamic
        },
        {
            "name": "_logger",
            "providing": "ct.framework.api.LogService",
            "cardinality": "0..1",          // Optional
            "policy": "dynamic",
            "filter": "(Bundle-SymbolicName=system)"  // LDAP Filter
        },
        {
            "name": "_validators",
            "providing": "data.Validator",
            "cardinality": "0..n",          // Array von Services
            "bind": "addValidator",         // Method bei Service-Registrierung
            "unbind": "removeValidator"     // Method bei Service-Deregistrierung
        }
    ]
}
```

#### Wichtige Optionen erklärt:

**Factory-Typen:**
- `instanceFactory: true` - Standard für Widgets, implementiert `createInstance()` / `destroyInstance()`
- `componentFactory: true` - Macht Component als Factory verfügbar via `newInstance(props)`
- `serviceFactory: true` - Jedes Bundle bekommt eigene Service-Instanz

**Cardinality:**
- `1..1` - Genau ein Service (Pflicht, wirft Error wenn fehlt)
- `0..1` - Optional, max. ein Service
- `0..n` - Array von Services (kann leer sein)
- `1..n` - Array von Services (min. einer muss vorhanden sein)

**Policy:**
- `static` - Reference wird bei Component-Aktivierung aufgelöst, bleibt fix
- `dynamic` - Reference kann sich zur Laufzeit ändern (bind/unbind Methods werden aufgerufen)

### Component-Implementierung

**WICHTIG - Automatische Injections:**
Die folgenden Properties werden von map.apps **AUTOMATISCH** injiziert und brauchen **KEINE** Reference in der manifest.json:
- `_i18n` - Internationalisierung
- `_properties` - Component Properties aus manifest.json
- `_componentContext` - Component Context

```typescript
import type { InjectedReference } from "apprt-core/InjectedReference";
import { Observers } from "apprt-core/Observers";

interface ServiceProperties {
    apiUrl: string;
    timeout: number;
}

export default class MyService {
    // Automatisch injiziert durch manifest.json references
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;
    private _logger?: InjectedReference<LogService>;  // Optional (0..1)

    // ⚠️ AUTOMATISCHE Injections (KEINE manifest.json Reference nötig!)
    private _properties!: ServiceProperties;
    private _i18n!: InjectedReference<I18N>;
    private _componentContext!: ComponentContext;

    // Resource Management
    private _observers = Observers();

    // 1. Constructor (nur wenn propertiesConstructor: true)
    constructor(properties: ServiceProperties) {
        this._properties = properties;
    }

    // 2. Aktivierung (async möglich!)
    async activate(): Promise<void> {
        this._logger?.info("Service wird aktiviert");

        // Async Initialisierung erlaubt
        await this.loadConfiguration();

        // Event-Listener registrieren
        this._observers.add(
            this._mapWidgetModel.watch("extent", this.onExtentChange.bind(this))
        );
    }

    // 3. Konfigurations-Update (optional)
    modified(): boolean {
        // true = Component wird neu gestartet
        // false = weiter laufen
        return false;
    }

    // 4. Deaktivierung - KRITISCH: Cleanup!
    deactivate(): void {
        this._observers.destroy();  // Alle Observer aufräumen
        this._logger?.info("Service wird deaktiviert");
    }

    // 5. Zerstörung (optional)
    destroy(): void {
        // Finale Cleanup-Operationen
    }

    // Methods für dynamic references (cardinality: 0..n)
    private validators = new Set<Validator>();

    addValidator(validator: Validator, serviceProps: ServiceProperties): void {
        this.validators.add(validator);
        this._logger?.debug("Validator hinzugefügt:", serviceProps["service.id"]);
    }

    removeValidator(validator: Validator): void {
        this.validators.delete(validator);
    }
}
```

### Factory Patterns

#### 1. Instance Factory (Standard für Widgets)

```typescript
// manifest.json
{
    "name": "MyWidgetFactory",
    "provides": ["dijit.Widget"],
    "instanceFactory": true,
    "properties": {
        "widgetRole": "myWidget"
    },
    "references": [{
        "name": "_controller",
        "providing": "my.Controller"
    }]
}

// Implementation
import Vue from "apprt-vue/Vue";
import VueDijit from "apprt-vue/VueDijit";
import MyWidget from "./MyWidget.vue";

export default class MyWidgetFactory {
    private _controller!: Controller;
    private _i18n!: InjectedReference<I18N>;

    // Wird von map.apps aufgerufen um Widget zu erstellen
    createInstance(): any {
        const vm = new Vue(MyWidget);
        vm.controller = this._controller;
        vm.i18n = this._i18n.get();

        // Events behandeln
        vm.$on("close", () => {
            console.log("Widget geschlossen");
        });

        return VueDijit(vm);  // Vue Component als Dijit Widget wrappen
    }

    // Optional: Cleanup wenn Widget zerstört wird
    destroyInstance(instance: any): void {
        instance.$destroy();
    }
}
```

#### 2. Component Factory

```typescript
// manifest.json
{
    "name": "StoreFactory",
    "componentFactory": true
}

// Verwendung in anderem Component
const factory = this._componentContext.locateService<ComponentFactory>("StoreFactory");
const storeInstance = factory.newInstance({
    url: "https://api.example.com",
    timeout: 5000
});
```

---

## MapWidgetModel - Zentrale Map-API

Das `MapWidgetModel` ist der zentrale Service für alle Map-Operationen. Es wrapped die ArcGIS JavaScript API View und Map.

### Zugriff auf MapWidgetModel

```typescript
// In manifest.json
{
    "references": [{
        "name": "_mapWidgetModel",
        "providing": "map-widget.MapWidgetModel"
    }]
}

// In der Component
export default class MyComponent {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;

    activate(): void {
        const view = this._mapWidgetModel.view;    // SceneView oder MapView
        const map = this._mapWidgetModel.map;      // Map Objekt
    }
}
```

### View & Map Zugriff

```typescript
import type MapView from "esri/views/MapView";
import type SceneView from "esri/views/SceneView";
import type Map from "esri/Map";

class MapInteractionService {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;

    activate(): void {
        const view = this._mapWidgetModel.view;  // MapView | SceneView
        const map = this._mapWidgetModel.map;    // Map

        // Type-Check für 2D/3D
        if (view.type === "2d") {
            const mapView = view as MapView;
            console.log("2D Map");
        } else {
            const sceneView = view as SceneView;
            console.log("3D Scene");
        }
    }
}
```

### Extent & Navigation

```typescript
class NavigationService {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;

    // Extent ändern
    async zoomToExtent(extent: __esri.Extent): Promise<void> {
        await this._mapWidgetModel.view.goTo(extent);
    }

    // Zu Koordinaten navigieren
    async goToLocation(longitude: number, latitude: number, zoom: number = 12): Promise<void> {
        await this._mapWidgetModel.view.goTo({
            center: [longitude, latitude],
            zoom: zoom
        });
    }

    // Mit Animation
    async panTo(point: __esri.Point): Promise<void> {
        await this._mapWidgetModel.view.goTo(point, {
            duration: 1000,  // ms
            easing: "ease-in-out"
        });
    }

    // 3D: Kamera-Position
    async setCameraPosition(camera: __esri.Camera): Promise<void> {
        const view = this._mapWidgetModel.view;
        if (view.type === "3d") {
            await view.goTo({
                position: camera.position,
                heading: camera.heading,
                tilt: camera.tilt
            });
        }
    }

    // Extent beobachten
    watchExtent(): void {
        this._observers.add(
            this._mapWidgetModel.watch("extent", (newExtent) => {
                console.log("Extent geändert:", newExtent);
                this.onExtentChange(newExtent);
            })
        );
    }
}
```

### Layer Management

```typescript
import FeatureLayer from "esri/layers/FeatureLayer";
import GraphicsLayer from "esri/layers/GraphicsLayer";
import Graphic from "esri/Graphic";

class LayerService {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;

    // Layer hinzufügen
    addFeatureLayer(url: string, title: string): FeatureLayer {
        const layer = new FeatureLayer({
            url: url,
            title: title,
            visible: true
        });

        this._mapWidgetModel.map.add(layer);
        return layer;
    }

    // Graphics Layer für temporäre Geometrien
    createGraphicsLayer(id: string): GraphicsLayer {
        // Prüfen ob schon existiert
        const existing = this._mapWidgetModel.map.findLayerById(id);
        if (existing) return existing as GraphicsLayer;

        const layer = new GraphicsLayer({
            id: id,
            listMode: "hide"  // Nicht in TOC anzeigen
        });

        this._mapWidgetModel.map.add(layer);
        return layer;
    }

    // Graphic zu Layer hinzufügen
    addGraphic(layerId: string, geometry: __esri.Geometry, symbol: __esri.Symbol): void {
        const layer = this._mapWidgetModel.map.findLayerById(layerId) as GraphicsLayer;
        if (!layer) return;

        const graphic = new Graphic({
            geometry: geometry,
            symbol: symbol
        });

        layer.add(graphic);
    }

    // Layer Visibility
    toggleLayer(layerId: string, visible: boolean): void {
        const layer = this._mapWidgetModel.map.findLayerById(layerId);
        if (layer) {
            layer.visible = visible;
        }
    }

    // Alle Layer durchlaufen
    forEachLayer(callback: (layer: __esri.Layer) => void): void {
        this._mapWidgetModel.map.allLayers.forEach(callback);
    }
}
```

### View Events & Interactions

```typescript
class InteractionService {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;
    private _observers = Observers();

    activate(): void {
        // Click Events
        this._observers.add(
            this._mapWidgetModel.view.on("click", (event) => {
                console.log("Map geklickt:", event.mapPoint);
                this.onMapClick(event);
            })
        );

        // Pointer Move
        this._observers.add(
            this._mapWidgetModel.view.on("pointer-move", (event) => {
                this.onPointerMove(event);
            })
        );

        // Drag Events
        this._observers.add(
            this._mapWidgetModel.view.on("drag", (event) => {
                event.stopPropagation();  // Default-Verhalten verhindern
                this.onDrag(event);
            })
        );

        // Stationary (View hat aufgehört sich zu bewegen)
        this._observers.add(
            this._mapWidgetModel.view.watch("stationary", (stationary) => {
                if (stationary) {
                    console.log("View ist stationär");
                }
            })
        );
    }

    deactivate(): void {
        this._observers.destroy();
    }

    // HitTest - Was ist unter dem Cursor?
    async hitTest(screenPoint: __esri.ScreenPoint): Promise<__esri.HitTestResult> {
        return await this._mapWidgetModel.view.hitTest(screenPoint);
    }

    // Screen zu Map Koordinaten
    toMap(screenPoint: __esri.ScreenPoint): __esri.Point {
        return this._mapWidgetModel.view.toMap(screenPoint);
    }

    // Map zu Screen Koordinaten
    toScreen(mapPoint: __esri.Point): __esri.ScreenPoint {
        return this._mapWidgetModel.view.toScreen(mapPoint);
    }
}
```

### Sketching & Drawing

```typescript
import Sketch from "esri/widgets/Sketch";
import GraphicsLayer from "esri/layers/GraphicsLayer";

class SketchService {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;
    private _sketch?: Sketch;
    private _observers = Observers();

    startSketching(layer: GraphicsLayer): void {
        this._sketch = new Sketch({
            view: this._mapWidgetModel.view,
            layer: layer,
            creationMode: "single"  // "single" oder "continuous"
        });

        // Events
        this._observers.add(
            this._sketch.on("create", (event) => {
                if (event.state === "complete") {
                    console.log("Geometrie erstellt:", event.graphic.geometry);
                    this.onGeometryCreated(event.graphic);
                }
            })
        );

        this._observers.add(
            this._sketch.on("update", (event) => {
                if (event.state === "complete") {
                    console.log("Geometrie bearbeitet:", event.graphics);
                }
            })
        );
    }

    // Zeichnen starten
    createPoint(): void {
        this._sketch?.create("point");
    }

    createPolyline(): void {
        this._sketch?.create("polyline");
    }

    createPolygon(): void {
        this._sketch?.create("polygon");
    }

    // Bearbeiten
    update(graphics: Graphic[]): void {
        this._sketch?.update(graphics);
    }

    // Zeichnen beenden
    cancel(): void {
        this._sketch?.cancel();
    }

    destroy(): void {
        this._sketch?.destroy();
        this._observers.destroy();
    }
}
```

---

## Event System & Tool Integration

### EventService - Event Bus

Der EventService ermöglicht lose gekoppelte Kommunikation zwischen Bundles.

#### Events empfangen

```typescript
// manifest.json
{
    "name": "MyEventHandler",
    "provides": ["ct.framework.api.EventHandler"],
    "immediate": true,
    "properties": {
        "Event-Topics": [
            "ct/tool/ACTIVATED",
            "ct/tool/DEACTIVATED",
            "map-widget/EXTENT_CHANGE",
            "my/custom/event",
            "my/custom/*"              // Wildcard
        ]
    }
}

// Implementation
import type { TopicEvent } from "apprt/api";

export default class MyEventHandler {
    handleEvent(event: TopicEvent): void {
        const topic = event.getTopic();
        const properties = event.getProperties();

        switch (topic) {
            case "ct/tool/ACTIVATED":
                this.onToolActivated(properties.tool);
                break;
            case "ct/tool/DEACTIVATED":
                this.onToolDeactivated(properties.tool);
                break;
            case "map-widget/EXTENT_CHANGE":
                this.onExtentChanged(properties.extent);
                break;
            default:
                if (topic.startsWith("my/custom/")) {
                    this.onCustomEvent(topic, properties);
                }
        }
    }
}
```

#### Events senden

```typescript
class MyService {
    private _eventService!: InjectedReference<EventService>;

    notifyStateChange(newState: string): void {
        this._eventService.postEvent("my/service/STATE_CHANGED", {
            state: newState,
            timestamp: Date.now()
        });
    }

    // Mit Error Handling
    notifyWithErrorHandling(topic: string, data: any): void {
        try {
            this._eventService.postEvent(topic, data);
        } catch (error) {
            this._logger?.error("Failed to post event:", error);
        }
    }
}
```

### Tool System

Tools sind UI-Aktionen (Buttons) mit eigenem Lifecycle. Sie sind zentral für die Interaktion.

#### Tool-Definition

```typescript
// manifest.json
{
    "name": "MyTool",
    "impl": "ct/tools/Tool",              // Direkte Tool-Klasse nutzen
    "provides": ["ct.tools.Tool"],
    "propertiesConstructor": true,
    "properties": {
        "id": "myTool",                   // Eindeutige ID
        "title": "${i18n.toolTitle}",     // Anzeige-Name
        "tooltip": "${i18n.toolTooltip}",
        "iconClass": "icon-custom",       // CSS Icon-Klasse
        "togglable": true,                // Toggle-Verhalten?
        "toolRole": "toolset",            // Gruppierung
        "priority": 100,                  // Sortierung
        "enabledOnActivate": true,

        // Handler Methods (in handlerScope Component)
        "clickHandler": "onToolClick",         // Bei Click (wenn nicht togglable)
        "activateHandler": "onToolActivated",  // Bei Aktivierung
        "deactivateHandler": "onToolDeactivated"  // Bei Deaktivierung
    },
    "references": [{
        "name": "handlerScope",           // Component mit Handler-Methods
        "providing": "my.Controller"
    }]
}
```

#### Tool Handler Implementation

```typescript
import { Observers } from "apprt-core/Observers";

export default class MyController {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;
    private _observers = Observers();

    // Wird aufgerufen wenn Tool aktiviert wird
    onToolActivated(): void {
        console.log("Tool aktiviert");

        // View Interaction aktivieren
        this._observers.add(
            this._mapWidgetModel.view.on("click", (event) => {
                this.handleMapClick(event);
            })
        );

        // Cursor ändern
        this._mapWidgetModel.view.container.style.cursor = "crosshair";
    }

    // Wird aufgerufen wenn Tool deaktiviert wird
    onToolDeactivated(): void {
        console.log("Tool deaktiviert");

        // Cleanup - sehr wichtig!
        this._observers.clean();

        // Cursor zurücksetzen
        this._mapWidgetModel.view.container.style.cursor = "default";
    }

    // Für nicht-togglable Tools
    onToolClick(): void {
        console.log("Tool geklickt");
        this.performAction();
    }

    private handleMapClick(event: any): void {
        const mapPoint = event.mapPoint;
        console.log("Map geklickt bei:", mapPoint);
        // Tool-spezifische Logik
    }
}
```

#### Tool-Widget Verknüpfung

Tools können mit Widgets verknüpft werden (dockTool):

```json
{
    "layout-widgets": [{
        "widgetRole": "myWidget",
        "window": {
            "dockTool": "myTool",    // Tool ID
            "dockable": true,
            "closable": true
        }
    }]
}
```

Wenn das Tool aktiviert wird, öffnet sich automatisch das Widget.

---

## UI-System: Vue.js & Window Management

### Vue.js Widget Integration

#### Widget Factory

```typescript
// manifest.json
{
    "name": "SearchWidgetFactory",
    "provides": ["dijit.Widget"],
    "instanceFactory": true,
    "properties": {
        "widgetRole": "searchWidget"
    },
    "references": [{
        "name": "_controller",
        "providing": "search.Controller"
    }]
}

// SearchWidgetFactory.ts
import Vue from "apprt-vue/Vue";
import VueDijit from "apprt-vue/VueDijit";
import SearchWidget from "./SearchWidget.vue";

export default class SearchWidgetFactory {
    private _controller!: SearchController;
    private _i18n!: InjectedReference<I18N>;

    createInstance(): any {
        const vm = new Vue(SearchWidget);

        // Props setzen
        vm.controller = this._controller;
        vm.i18n = this._i18n.get();

        // Events behandeln
        vm.$on("search", (query: string) => {
            this._controller.search(query);
        });

        vm.$on("close", () => {
            console.log("Widget geschlossen");
        });

        return VueDijit(vm);
    }
}
```

#### Vue Component

```vue
<template>
    <v-container fluid class="pa-2">
        <v-card>
            <v-toolbar color="primary" dark dense>
                <v-toolbar-title>{{ i18n.title }}</v-toolbar-title>
                <v-spacer />
                <v-btn icon @click="$emit('close')">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-toolbar>

            <v-card-text>
                <v-text-field
                    v-model="searchText"
                    :label="i18n.searchLabel"
                    append-icon="mdi-magnify"
                    @click:append="search"
                    @keyup.enter="search"
                    clearable
                />

                <v-progress-linear v-if="loading" indeterminate />

                <v-list v-if="results.length > 0">
                    <v-list-item
                        v-for="item in results"
                        :key="item.id"
                        @click="selectItem(item)"
                    >
                        <v-list-item-content>
                            <v-list-item-title>{{ item.title }}</v-list-item-title>
                            <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
                        </v-list-item-content>
                    </v-list-item>
                </v-list>

                <v-alert v-else-if="searched && !loading" type="info">
                    {{ i18n.noResults }}
                </v-alert>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
export default {
    name: "SearchWidget",

    props: {
        controller: { type: Object, required: true },
        i18n: { type: Object, required: true }
    },

    data() {
        return {
            searchText: "",
            results: [],
            loading: false,
            searched: false
        };
    },

    created() {
        // Controller Events abonnieren
        this.controller.on("search-started", () => {
            this.loading = true;
        });

        this.controller.on("search-completed", () => {
            this.loading = false;
        });

        this.controller.on("results-updated", (results) => {
            this.results = results;
        });
    },

    methods: {
        async search() {
            if (!this.searchText.trim()) return;
            this.searched = true;
            this.$emit("search", this.searchText);
        },

        selectItem(item) {
            this.$emit("item-selected", item);
        }
    }
};
</script>

<style scoped>
.v-list {
    max-height: 400px;
    overflow-y: auto;
}
</style>
```

### Window Management

Windows steuern wie Widgets angezeigt werden (floating, docked, modal, etc.).

#### Window-Konfiguration in manifest.json

```json
{
    "layout-widgets": [
        {
            "widgetRole": "myWidget",
            "attachTo": "left",              // Region: map, left, right, top, bottom
            "priority": 100,                 // Sortierung
            "sublayout": ["desktop", "tablet"],  // Responsive

            "window": {
                "title": "${i18n.windowTitle}",
                "dockable": true,            // Kann gedockt werden?
                "dockingBar": "dockingBarLeft",  // Docking-Bar ID
                "dockTool": "myTool",        // Verknüpftes Tool

                "closable": true,            // Schließen-Button?
                "minimizable": true,         // Minimieren-Button?
                "maximizable": true,         // Maximieren-Button?
                "resizable": true,           // Größe änderbar?
                "draggable": true,           // Verschiebbar?
                "modal": false,              // Modal-Dialog?

                "marginBox": {               // Initiale Größe & Position
                    "w": 400,                // Breite in px oder "%"
                    "h": 600,                // Höhe
                    "l": 20,                 // Links-Position
                    "t": 60                  // Top-Position
                },

                "minSize": {                 // Mindestgröße
                    "w": 300,
                    "h": 200
                },

                "maxSize": {                 // Maximalgröße
                    "w": 800,
                    "h": 800
                },

                "windowClass": "myCustomWindow",  // CSS-Klasse
                "minimizeOnClose": true,     // Bei Close minimieren statt schließen
                "hideOnClose": false         // Bei Close verstecken
            }
        },

        // Responsive: Unterschiedliche Configs für Devices
        {
            "widgetRole": "myWidget",
            "sublayout": ["mobile_landscape", "mobile_portrait"],
            "window": {
                "resizable": false,
                "maximizable": false,
                "marginBox": {
                    "w": "100%",
                    "h": "100%",
                    "l": 0,
                    "b": 40
                }
            }
        }
    ]
}
```

#### Window-Typen

```json
// Floating Window (default)
{
    "window": {
        "dockable": false
    }
}

// Docked Window
{
    "window": {
        "dockable": true,
        "dockingBar": "dockingBarRight"
    }
}

// Modal Dialog
{
    "window": {
        "modal": true,
        "draggable": false,
        "resizable": false,
        "marginBox": { "w": 500, "h": 300 }
    }
}

// Fullscreen Mobile
{
    "sublayout": ["mobile_portrait", "mobile_landscape"],
    "window": {
        "marginBox": { "w": "100%", "h": "100%", "l": 0, "t": 0 }
    }
}
```

### Binding API - Reaktive Datenbindung

Die Binding API synchronisiert Daten zwischen Model und View:

```typescript
import { Binding } from "apprt-binding/Binding";

class MyController {
    private _model: Model;
    private _tool: Tool;
    private _binding?: Binding;

    activate(): void {
        // Einfaches Binding (bidirektional)
        this._binding = Binding.for(this._model, this._tool)
            .sync("enabled")
            .sync("active")
            .enable();

        // Mit Transformation (einseitig)
        this._binding = Binding.for(this._model, this._tool)
            .syncToRight("state", ["title", "iconClass"], (state) => {
                return [
                    state === "active" ? "Deaktivieren" : "Aktivieren",
                    state === "active" ? "icon-on" : "icon-off"
                ];
            })
            .enable()
            .syncToRightNow();  // Sofort synchronisieren
    }

    deactivate(): void {
        this._binding?.unbind();
    }
}
```

---

## Store API & Daten-Management

Stores verwalten Daten nach dem Dojo Store Pattern.

### Memory Store

```typescript
import Memory from "apprt-core/store/Memory";

// Store erstellen
const store = new Memory({
    data: [
        { id: 1, name: "Item 1", category: "A", price: 10 },
        { id: 2, name: "Item 2", category: "B", price: 20 },
        { id: 3, name: "Item 3", category: "A", price: 15 }
    ],
    idProperty: "id"
});

// Query - Simple
const results = await store.query({ category: "A" });

// Query - Complex
const filtered = await store.query({
    $and: [
        { category: "A" },
        { price: { $lt: 20 } },
        { name: { $like: "Item*" } }
    ]
});

// Get by ID
const item = await store.get(1);

// Add
const newItem = await store.add({ id: 4, name: "Item 4", category: "C" });

// Update
await store.put({ id: 1, name: "Updated Item 1", category: "A" });

// Remove
await store.remove(1);
```

### Store Decorators

```typescript
import { Filter } from "ct/store/Filter";
import { Lookup } from "ct/store/Lookup";

// Vorfilterung
const filteredStore = Filter(store, { category: "A" });

// ID-Lookup
const lookupStore = Lookup(store, { idProperty: "id" });
const item = lookupStore.get(1);  // Synchron!

// Kombiniert
let enhancedStore = new Memory({ data });
enhancedStore = Filter(enhancedStore, { active: true });
enhancedStore = Lookup(enhancedStore, { idProperty: "id" });
```

### Async/Remote Store

```typescript
export default class RemoteStoreFactory {
    createStore(): Store {
        return {
            query: async (query: any, options?: any) => {
                const response = await fetch(`/api/items?${this.buildQuery(query)}`);
                const data = await response.json();
                return data.items;
            },

            get: async (id: string) => {
                const response = await fetch(`/api/items/${id}`);
                return await response.json();
            },

            add: async (object: any) => {
                const response = await fetch('/api/items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(object)
                });
                return await response.json();
            }
        };
    }
}
```

---

## Best Practices & Patterns

### 1. Resource Management mit Observers

**KRITISCH:** Immer Observers für Cleanup nutzen!

```typescript
import { Observers } from "apprt-core/Observers";

class MyComponent {
    private _observers = Observers();

    activate(): void {
        // Alle Event-Listener/Watches automatisch verwalten
        this._observers.add(
            this._mapWidgetModel.watch("extent", this.onExtentChange)
        );

        this._observers.add(
            this._mapWidgetModel.view.on("click", this.onClick)
        );

        // Gruppierung für selektives Cleanup
        this._observers.group("tooltips").add(
            this.view.on("pointer-move", this.showTooltip)
        );
    }

    // Selektives Cleanup
    disableTooltips(): void {
        this._observers.clean("tooltips");
    }

    deactivate(): void {
        this._observers.destroy();  // Räumt ALLES auf
    }
}
```

### 2. Asynchrone Operationen mit AbortController

```typescript
class SearchService {
    private abortController?: AbortController;

    async search(query: string): Promise<Result[]> {
        // Vorherige Anfrage abbrechen
        this.abortController?.abort();
        this.abortController = new AbortController();

        try {
            const response = await fetch(this.buildUrl(query), {
                signal: this.abortController.signal
            });

            return await response.json();

        } catch (error) {
            if (error.name === 'AbortError') {
                this._logger?.debug("Search cancelled");
                throw new Error("Search cancelled");
            }
            this._logger?.error("Search failed:", error);
            throw error;
        }
    }

    deactivate(): void {
        this.abortController?.abort();
    }
}
```

### 3. Debouncing für teure Operationen

```typescript
class AutocompleteController {
    private lastTimeout?: number;

    onSearchTextChange(text: string): void {
        // Vorheriges Timeout abbrechen
        clearTimeout(this.lastTimeout);

        // Neues Timeout setzen
        this.lastTimeout = setTimeout(() => {
            this.performSearch(text);
        }, 500);  // 500ms Debounce
    }

    deactivate(): void {
        clearTimeout(this.lastTimeout);
    }
}
```

### 4. Controller Pattern - Trennung von Logik und UI

```typescript
// Controller - Business Logic
import { Evented } from "apprt-core/Events";

interface ControllerEvents {
    "search-started": void;
    "search-completed": void;
    "results-updated": Result[];
    "error": Error;
}

export default class SearchController extends Evented<ControllerEvents> {
    private _searchService!: SearchService;

    async search(query: string): Promise<void> {
        this.emit("search-started");

        try {
            const results = await this._searchService.search(query);
            this.emit("results-updated", results);
        } catch (error) {
            this.emit("error", error);
        } finally {
            this.emit("search-completed");
        }
    }
}

// Widget - UI Only
// SearchWidget.vue reagiert auf Controller Events
```

### 5. Error Handling mit Graceful Degradation

```typescript
class RobustService {
    private async safeOperation<T>(
        operation: () => Promise<T>,
        fallback: T,
        errorMessage: string
    ): Promise<T> {
        try {
            return await operation();
        } catch (error) {
            this._logger?.error(errorMessage, error);
            this._eventService?.postEvent("error/occurred", {
                message: errorMessage,
                error: error
            });
            return fallback;
        }
    }

    async loadData(): Promise<Data[]> {
        return this.safeOperation(
            () => this.fetchData(),
            [],  // Fallback: leeres Array
            "Failed to load data"
        );
    }
}
```

### 6. TypeScript Best Practices

```typescript
// Type Guards
function isPoint(geometry: __esri.Geometry): geometry is __esri.Point {
    return geometry.type === "point";
}

// Generics
class TypedStore<T> {
    async query(filter: Partial<T>): Promise<T[]> {
        // Implementation
    }
}

// Utility Types
type ReadonlyConfig = Readonly<Config>;
type PartialUpdate = Partial<ModelData>;

// Discriminated Unions
type State =
    | { status: "loading" }
    | { status: "success"; data: any }
    | { status: "error"; error: Error };
```

---

## Häufige Fehler & Lösungen

### 1. Memory Leaks durch fehlende Observer-Cleanup

```typescript
// ❌ FALSCH - Memory Leak!
class BadComponent {
    activate() {
        this._mapWidgetModel.watch("extent", this.onExtentChange);
        // Handler wird NIE entfernt!
    }
}

// ✅ RICHTIG
class GoodComponent {
    private _observers = Observers();

    activate() {
        this._observers.add(
            this._mapWidgetModel.watch("extent", this.onExtentChange)
        );
    }

    deactivate() {
        this._observers.destroy();
    }
}
```

### 2. Race Conditions bei Async Operations

```typescript
// ❌ FALSCH - Race Condition!
async search(query: string) {
    const results = await fetch(`/api?q=${query}`);
    this.results = results;  // Alte Anfrage kann neue überschreiben!
}

// ✅ RICHTIG - Mit Search ID
private _searchId = 0;

async search(query: string) {
    const searchId = ++this._searchId;
    const results = await fetch(`/api?q=${query}`);

    if (searchId === this._searchId) {
        this.results = results;
    }
}

// ✅ ODER: Mit AbortController
private abortController?: AbortController;

async search(query: string) {
    this.abortController?.abort();
    this.abortController = new AbortController();

    const results = await fetch(`/api?q=${query}`, {
        signal: this.abortController.signal
    });
    this.results = results;
}
```

### 3. Null-Checks bei optionalen Services

```typescript
// ❌ FALSCH
this._logger.info("Message");  // Kann crashen wenn logger optional!

// ✅ RICHTIG
this._logger?.info("Message");

// ✅ ODER: Mit Fallback
const logger = this._logger ?? console;
logger.info("Message");
```

### 4. Fehlende Service-Reference

```json
// ❌ FALSCH
{
    "references": [{
        "name": "_mapModel",
        "providing": "MapModel"  // Falscher Interface-Name!
    }]
}

// ✅ RICHTIG
{
    "references": [{
        "name": "_mapWidgetModel",
        "providing": "map-widget.MapWidgetModel"
    }]
}
```

### 5. Vue Reaktivität

```javascript
// ❌ FALSCH - Nicht reaktiv!
this.items[index] = newItem;
this.object.newProperty = value;

// ✅ RICHTIG
this.$set(this.items, index, newItem);
this.$set(this.object, 'newProperty', value);

// ✅ ODER: Array ersetzen
this.items = [...this.items.slice(0, index), newItem, ...this.items.slice(index + 1)];

// ✅ ODER: Object spread
this.object = { ...this.object, newProperty: value };
```

---

## Praktische Bundle-Beispiele

### Minimales Tool Bundle

```typescript
// manifest.json
{
    "name": "my-tool",
    "version": "1.0.0",
    "i18n": ["bundle"],
    "dependencies": {
        "map-widget": "~4.19.2"
    },
    "components": [
        {
            "name": "MyTool",
            "impl": "ct/tools/Tool",
            "provides": ["ct.tools.Tool"],
            "propertiesConstructor": true,
            "properties": {
                "id": "myTool",
                "title": "${i18n.title}",
                "togglable": true,
                "activateHandler": "onActivated",
                "deactivateHandler": "onDeactivated"
            },
            "references": [{
                "name": "handlerScope",
                "providing": "my.Controller"
            }]
        },
        {
            "name": "MyController",
            "provides": ["my.Controller"],
            "immediate": true,
            "references": [{
                "name": "_mapWidgetModel",
                "providing": "map-widget.MapWidgetModel"
            }]
        }
    ]
}

// MyController.ts
import { Observers } from "apprt-core/Observers";

export default class MyController {
    private _mapWidgetModel!: InjectedReference<MapWidgetModel>;
    private observers = Observers();

    onActivated(): void {
        console.log("Tool aktiviert");

        this.observers.add(
            this._mapWidgetModel.view.on("click", this.onClick.bind(this))
        );
    }

    onDeactivated(): void {
        console.log("Tool deaktiviert");
        this.observers.clean();
    }

    private onClick(event: any): void {
        console.log("Map geklickt bei:", event.mapPoint);
    }
}

// module.ts
export { default as MyController } from "./MyController";
```

### Widget mit Controller und Service

```typescript
// manifest.json
{
    "name": "search-bundle",
    "dependencies": {
        "apprt-vue": "~4.19.2",
        "apprt-core": "~4.19.2"
    },
    "components": [
        {
            "name": "SearchService",
            "provides": ["search.Service"],
            "properties": {
                "apiUrl": "https://api.example.com/search"
            }
        },
        {
            "name": "SearchController",
            "provides": ["search.Controller"],
            "references": [{
                "name": "_searchService",
                "providing": "search.Service"
            }]
        },
        {
            "name": "SearchWidgetFactory",
            "provides": ["dijit.Widget"],
            "instanceFactory": true,
            "properties": {
                "widgetRole": "searchWidget"
            },
            "references": [{
                "name": "_controller",
                "providing": "search.Controller"
            }]
        }
    ],
    "layout-widgets": [{
        "widgetRole": "searchWidget",
        "window": {
            "title": "${i18n.title}",
            "dockable": true,
            "closable": true,
            "marginBox": { "w": 400, "h": 600 }
        }
    }]
}

// SearchService.ts
export default class SearchService {
    private _properties!: { apiUrl: string };
    private abortController?: AbortController;

    async search(query: string): Promise<Result[]> {
        this.abortController?.abort();
        this.abortController = new AbortController();

        const response = await fetch(
            `${this._properties.apiUrl}?q=${query}`,
            { signal: this.abortController.signal }
        );

        return await response.json();
    }
}

// SearchController.ts
import { Evented } from "apprt-core/Events";

export default class SearchController extends Evented {
    private _searchService!: SearchService;

    async search(query: string): Promise<void> {
        this.emit("search-started");
        try {
            const results = await this._searchService.search(query);
            this.emit("results-updated", results);
        } finally {
            this.emit("search-completed");
        }
    }
}

// SearchWidgetFactory.ts
import Vue from "apprt-vue/Vue";
import VueDijit from "apprt-vue/VueDijit";
import SearchWidget from "./SearchWidget.vue";

export default class SearchWidgetFactory {
    private _controller!: SearchController;
    private _i18n!: InjectedReference<I18N>;

    createInstance(): any {
        const vm = new Vue(SearchWidget);
        vm.controller = this._controller;
        vm.i18n = this._i18n.get();
        return VueDijit(vm);
    }
}
```

### Event Handler Bundle

```typescript
// manifest.json
{
    "name": "event-logger",
    "components": [{
        "name": "EventLogger",
        "provides": ["ct.framework.api.EventHandler"],
        "immediate": true,
        "properties": {
            "Event-Topics": [
                "ct/tool/ACTIVATED",
                "ct/tool/DEACTIVATED",
                "map-widget/EXTENT_CHANGE"
            ]
        },
        "references": [{
            "name": "_logService",
            "providing": "ct.framework.api.LogService"
        }]
    }]
}

// EventLogger.ts
export default class EventLogger {
    private _logService!: InjectedReference<LogService>;

    handleEvent(event: TopicEvent): void {
        const topic = event.getTopic();
        const props = event.getProperties();

        this._logService.info(`Event: ${topic}`, props);
    }
}
```

---

## Entwicklungskommandos

```bash
# Dev Server starten (http://localhost:9090)
mvn compile -Denv=dev

# Mit custom properties
mvn compile -Denv=dev -Dlocal.configfile=../build.properties

# TypeScript Check
npm run check-types
npm run check-types:watch

# Tests
npx gulp test
npm test


# Linting
npx gulp lint

# Build
mvn clean install
```

Hingegen unfunktional ist:

```bash
npm run check-types
```

## Zusammenfassung: Die wichtigsten Punkte

1. **Deklarative Konfiguration**: Components in manifest.json definieren
2. **Dependency Injection**: References werden automatisch injiziert
3. **Lifecycle Management**: activate/deactivate implementieren
4. **Resource Cleanup**: Immer Observers nutzen!
5. **MapWidgetModel**: Zentrale API für Map-Zugriff
6. **Event System**: Lose Kopplung zwischen Bundles
7. **Vue.js Integration**: VueDijit für Widget-Wrapping
8. **Window Management**: Flexible UI-Layouts
9. **TypeScript**: Typsicherheit nutzen
10. **Testing**: Unit Tests mit Mocha

**Die wichtigste Regel:** Immer Observers für Event-Listener und Watches nutzen, sonst Memory Leaks!
