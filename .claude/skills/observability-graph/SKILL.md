---
name: observability-graph
description: Use when converting infrastructure, cloud, Kubernetes, or observability documentation into validated architecture graphs, especially when modeling containment, deployment type, telemetry flow, provider ownership, and rendering the same graph as Mermaid/LangGraph-style overview plus React Flow interactive subgraphs.
---

# Observability Graph

Use this skill when the user wants an architecture graph for Kubernetes/cloud observability, managed service internals, agents, Helm charts, node daemons, telemetry backends, or similar systems.

## Workflow

1. Read the source docs and extract a semantic graph before choosing a renderer.
2. Separate these relation types:
   - `contains`: cluster, VM, host OS, namespace, pod, backend plane.
   - `deployedAs`: Helm chart, DaemonSet, Deployment, systemd service, updater daemon, provider-managed pipeline.
   - `collects`: source signal to collector.
   - `shipsTo`: collector to ingest/backend.
   - `reportsTo`: health detector to API condition/event/alert.
   - `managedBy`: tenant, provider, automation controller, CAPI, Argo CD.
3. Render two views from the same semantic graph:
   - Mermaid/LangGraph-style overview for stable containment and low-overlap reading.
   - React Flow subgraph views for interactive inspection and dragging.
4. Do not put every relation into one React Flow canvas. Define task-focused scopes such as `worker runtime`, `telemetry egress`, `health repair`, and `provider plane`.
5. For React Flow, calculate positions before rendering with ELK or another graph layout engine. React Flow should handle interaction, not complex layout.
6. Validate rendered geometry in a real browser before claiming success.

## Rendering Policy

- Use Mermaid `subgraph`/ELK for the first screen overview.
- Use React Flow only for scoped detail views, not as the only full-system diagram.
- Keep container nodes visually separate from detail nodes.
- Show deployment type as a badge or style, not just body text.
- Reduce edge density by scope. A scope should only include edges that explain that scope.
- If React Flow edge routing still crosses nodes, prefer fewer scoped edges or custom routed edges over adding more manual node spacing.

## When More Detail Is Needed

- Read `references/graph-model.md` for the semantic graph schema.
- Read `references/rendering.md` for Mermaid/React Flow layout rules.
- Read `references/qa-checklist.md` before browser validation.

## Completion Criteria

- The graph has one source semantic model.
- Overview and detail views agree on entities and relations.
- Helm, systemd/updater daemon, hybrid Helm-to-systemd, and provider-managed pieces are visibly distinct.
- Browser QA checks node overlap, edge-node crossing, label-node crossing, console errors, and at least one React Flow drag interaction.
