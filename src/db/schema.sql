PRAGMA foreign_keys = ON;

CREATE TABLE elements (
    id            INTEGER PRIMARY KEY,
    symbol        TEXT    NOT NULL UNIQUE,
    atomic_mass   REAL,
    atomic_radius REAL,
    melting_point REAL,
    melt_density  REAL
);

CREATE TABLE systems (
    id           INTEGER PRIMARY KEY,
    component    TEXT    NOT NULL,
    n_component  INTEGER NOT NULL,
);

CREATE TABLE system_composition (
    system_id   INTEGER NOT NULL,
    element_id  INTEGER NOT NULL,
    fraction    REAL    NOT NULL,

    PRIMARY KEY (system_id, element_id),

    FOREIGN KEY (system_id)
        REFERENCES systems(id)
        ON DELETE CASCADE,

    FOREIGN KEY (element_id)
        REFERENCES elements(id)
        ON DELETE RESTRICT
);

CREATE TABLE properties (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    symbol    TEXT NOT NULL,
    unit      TEXT NOT NULL,
    category  TEXT
);

CREATE TABLE methods (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    type     TEXT,
    detail   TEXT
);

CREATE TABLE property_values (
    id           INTEGER PRIMARY KEY,

    system_id    INTEGER NOT NULL,
    property_id  INTEGER NOT NULL,
    method_id    INTEGER,

    value        REAL    NOT NULL,
    temperature  REAL,
    pressure     REAL,

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

CREATE TABLE meta (
    value_id     INTEGER PRIMARY KEY,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by    TEXT,
    source_file  TEXT,

    FOREIGN KEY (value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_property_values_system
    ON property_values(system_id);

CREATE INDEX idx_property_values_property
    ON property_values(property_id);

CREATE INDEX idx_property_values_tp
    ON property_values(property_id, temperature, pressure);

CREATE INDEX idx_system_composition_element
    ON system_composition(element_id);