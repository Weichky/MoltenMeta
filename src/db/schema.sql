PRAGMA foreign_keys = ON;

------------------------------------------------------------
-- Infrastructure layer
-- Configuration is treated as key–value data, not domain model
------------------------------------------------------------
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT NOT NULL,          -- Logical section, e.g. app / logging / locale
    key     TEXT NOT NULL,           -- Configuration key
    value   TEXT NOT NULL,           -- Serialized value (type resolved in upper layers)
    UNIQUE(section, key)
);

------------------------------------------------------------
-- Language layer
-- Symbols are part of the shared descriptive language,
-- not owned by properties or conditions
------------------------------------------------------------
CREATE TABLE symbols (
    id        INTEGER PRIMARY KEY,
    symbol    TEXT NOT NULL,         -- e.g. T, P, ρ, Cp
    name      TEXT,                  -- Human-readable meaning
    category  TEXT                   -- property / condition / constant / other
);

CREATE TABLE units (
    id        INTEGER PRIMARY KEY,
    symbol    TEXT NOT NULL
);

------------------------------------------------------------
-- Ontology layer: stable entities
-- These tables describe "what exists"
------------------------------------------------------------

-- Chemical elements as stable reference entities
CREATE TABLE elements (
    id            INTEGER PRIMARY KEY,
    symbol_id     INTEGER NOT NULL,  -- Reference to language-layer symbol (Fe, Al, ...)
    atomic_mass   REAL,
    atomic_radius REAL,
    melting_point REAL,
    melt_density  REAL,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT
);

-- Material systems (alloys, compounds, etc.)
-- A system is an abstract container for composition and observations
CREATE TABLE systems (
    id           INTEGER PRIMARY KEY,
    label        TEXT NOT NULL,      -- Human-facing identifier (e.g. Fe-C alloy)
    n_component  INTEGER             -- Cached component count (denormalized)
);

-- Composition as a first-class fact:
-- fraction belongs neither to system nor element alone
CREATE TABLE system_composition (
    system_id   INTEGER NOT NULL,
    element_id  INTEGER NOT NULL,
    fraction    REAL    NOT NULL,    -- Molar or atomic fraction

    PRIMARY KEY (system_id, element_id),

    FOREIGN KEY (system_id)
        REFERENCES systems(id)
        ON DELETE CASCADE,

    FOREIGN KEY (element_id)
        REFERENCES elements(id)
        ON DELETE RESTRICT
);

------------------------------------------------------------
-- Concept layer: properties, methods, conditions
-- These describe "how we talk about observations"
------------------------------------------------------------

-- Physical / thermodynamic / mechanical quantities
CREATE TABLE properties (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,  -- e.g. density, heat_capacity
    symbol_id INTEGER NOT NULL,       -- Reference to shared symbol (ρ, Cp, ...)
    unit_id   INTEGER NOT NULL,         -- Reference to shared symbol (kg/m3, J/kg/K, ...)
    category  TEXT,                  -- Optional grouping (thermal, mechanical, ...)

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);

-- Measurement or calculation methods
CREATE TABLE methods (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,           -- e.g. experiment, DFT, MD
    type     TEXT,                    -- Experimental / computational / empirical
    detail   TEXT                     -- Free-form description
);

-- Generalized conditions (independent variables)
-- Conditions are not properties, but contextual dimensions
CREATE TABLE conditions (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,   -- temperature, pressure, magnetic_field
    symbol_id INTEGER,                -- T, P, H, ...
    unit_id   INTEGER NOT NULL

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);

------------------------------------------------------------
-- Fact layer: observations / evaluations
-- These tables describe "what was observed under which context"
------------------------------------------------------------

-- Observed or computed property values
-- A property value is an event-like fact, not an intrinsic attribute
CREATE TABLE property_values (
    id           INTEGER PRIMARY KEY,

    system_id    INTEGER NOT NULL,
    property_id  INTEGER NOT NULL,
    method_id    INTEGER,

    value        REAL    NOT NULL,    -- Observed / computed value

    FOREIGN KEY (system_id)
        REFERENCES systems(id)
        ON DELETE CASCADE,

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (method_id)
        REFERENCES methods(id)
        ON DELETE SET NULL
);

-- Contextual conditions attached to a property value
-- Enables arbitrary condition dimensions beyond T/P
CREATE TABLE property_value_conditions (
    value_id     INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    value        REAL    NOT NULL,

    PRIMARY KEY (value_id, condition_id),

    FOREIGN KEY (value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE,

    FOREIGN KEY (condition_id)
        REFERENCES conditions(id)
        ON DELETE RESTRICT
);

------------------------------------------------------------
-- Provenance layer
-- Metadata orthogonal to scientific meaning
------------------------------------------------------------
CREATE TABLE meta (
    value_id     INTEGER PRIMARY KEY,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by   TEXT,
    source_file  TEXT,

    FOREIGN KEY (value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE
);

------------------------------------------------------------
-- Indexes for high-throughput querying
------------------------------------------------------------
CREATE INDEX idx_property_values_system
    ON property_values(system_id);

CREATE INDEX idx_property_values_property
    ON property_values(property_id);

CREATE INDEX idx_system_composition_element
    ON system_composition(element_id);

CREATE INDEX idx_property_value_conditions_condition
    ON property_value_conditions(condition_id);