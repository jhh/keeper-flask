DROP TABLE IF EXISTS trace;
DROP TABLE IF EXISTS action;
DROP TABLE IF EXISTS activity;
DROP VIEW IF EXISTS action_trace;

CREATE TABLE activity (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    timestamp timestamp without time zone NOT NULL DEFAULT now(),
    meta jsonb NOT NULL DEFAULT '{}'::jsonb,
    measures text[] NOT NULL DEFAULT '{}'::text[],
    data real[] NOT NULL DEFAULT '{}'::real[]
);

CREATE TABLE action (
    id SERIAL PRIMARY KEY,
    activity_id uuid REFERENCES activity(id),
    name text NOT NULL,
    timestamp timestamp without time zone NOT NULL DEFAULT now(),
    meta jsonb NOT NULL DEFAULT '{}'::jsonb,
    measures text[] NOT NULL DEFAULT '{}'::text[],
    data real[] NOT NULL DEFAULT '{}'::real[],
    trace_measures text[] NOT NULL DEFAULT '{}'::text[]
);

CREATE TABLE trace (
    id SERIAL PRIMARY KEY,
    action_id integer NOT NULL REFERENCES action(id) ON DELETE CASCADE,
    millis integer NOT NULL DEFAULT 0,
    data real[] NOT NULL DEFAULT '{}'::real[]
);

CREATE VIEW action_trace AS  SELECT t.action_id,
    t.millis,
    u.measure,
    u.value
   FROM action a,
    trace t,
    LATERAL UNNEST(a.trace_measures, t.data) u(measure, value)
  WHERE a.id = t.action_id;
