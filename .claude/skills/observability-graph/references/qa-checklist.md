# Browser QA Checklist

Run rendered validation before saying the graph is correct.

## Required Checks

- App loads at the expected local URL.
- Page is not blank.
- No framework overlay is visible.
- Console has no relevant errors or warnings.
- Mermaid overview has no node overlap.
- Mermaid overview has no edge path crossing through non-endpoint nodes.
- Mermaid overview has no edge label overlapping nodes.
- React Flow selected scope has no detail-node overlap.
- React Flow selected scope has no edge path crossing through non-endpoint nodes.
- React Flow selected scope has no edge label overlapping nodes.
- At least one React Flow node can be dragged and the edge remains connected.
- Desktop and mobile overview screenshots are captured when the user cares about readability.

## Geometry Notes

- Ignore the source and target nodes when sampling an edge path; endpoints naturally touch their nodes.
- For React Flow, test initial layout geometry before running drag checks.
- After drag checks, verify drag delta separately. Do not treat the post-drag layout as automatic layout quality.
- Test every interactive graph scope, not just the default scope.

## Failure Response

If a geometry check fails, do not claim the diagram is correct. Fix in this order:

1. Remove out-of-scope edges from the current view.
2. Split the scope.
3. Increase layout spacing.
4. Change handles or edge type.
5. Add custom routed edges.

Keep screenshots under a temporary or ignored directory unless the user asks for committed artifacts.
