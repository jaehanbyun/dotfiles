# Semantic Graph Model

Model the system before creating renderer-specific `nodes` and `edges`.

## Containers

Containers represent real containment or ownership boundaries:

```json
{
  "id": "worker-vm",
  "kind": "vm",
  "parentId": "tenant-cluster",
  "title": "Worker Node VM",
  "description": "OpenStack Nova VM / CAPI Machine / Kubernetes Node"
}
```

Common container kinds:

- `tenant-cluster`
- `worker-vm`
- `host-os`
- `kubernetes-runtime`
- `kubernetes-api`
- `provider-plane`
- `observability-backend`

## Entities

Entities are concrete operational components:

```json
{
  "id": "monitoring-agent",
  "parentId": "host-os",
  "title": "Monitoring Agent",
  "telemetryKind": "metric",
  "deployedAs": "systemd",
  "inputs": ["hostmetrics", "journald", "node exporter"],
  "outputs": ["OTLP metrics", "host logs"],
  "evidence": ["observed systemd unit", "vendor docs"]
}
```

Use `deployedAs` values consistently:

- `helm`
- `daemonset`
- `deployment`
- `systemd`
- `updater-daemon`
- `hybrid-helm-systemd`
- `provider-managed`
- `backend`
- `user-workload`
- `pipeline`

## Relationships

Use explicit relation names instead of one generic edge type:

```json
{
  "id": "host-agent-egress",
  "source": "monitoring-agent",
  "target": "telemetry-ingest",
  "relation": "shipsTo",
  "signal": "host metrics/logs"
}
```

Recommended relation names:

- `contains`
- `deployedAs`
- `collects`
- `shipsTo`
- `enrichesWith`
- `reportsTo`
- `triggers`
- `managedBy`
- `queries`

## Scopes

Define scopes for interactive views. Each scope should list node ids and edge ids.

```json
{
  "id": "worker-runtime",
  "label": "Worker VM Runtime",
  "nodeIds": ["monitoring-agent", "node-problem-detector", "runtime-monitor"],
  "edgeIds": ["agent-update", "runtime-monitor-install"]
}
```

Scopes prevent React Flow from becoming an unreadable full-system canvas.
