---
name: k8s-cluster-access-bootstrap
description: Safely bootstrap or repair Kubernetes cluster access and validate cluster readiness. Use when the user asks to find or merge kubeconfig entries, retrieve admin.conf through SSH or a bastion, connect to a new lab/customer cluster, compare settings against an existing cluster, install or verify an NFS/storage provisioner, run a PVC smoke test, or produce copy-paste connection instructions for a Kubernetes/OpenStack/CAPI/Kamaji/Launcher cluster.
---

# K8s Cluster Access Bootstrap

## Overview

Use this workflow to turn partial cluster access information into a working, validated local Kubernetes context without leaking credentials or leaving test resources behind.

## Inputs

Collect only what is needed:

- Target cluster/context name.
- Source of truth: Confluence page, repo docs, operator CR, existing kubeconfig, or user-provided SSH path.
- Access route: local kubeconfig path, bastion host, SSH hop, VM name, or command that can print kubeconfig.
- Reference context, when cloning behavior from another cluster.
- Desired validation: connectivity only, node readiness, storage class, provisioner install, PVC smoke test, or end-to-end UI/API flow.

Do not print kubeconfig contents, bearer tokens, client certificates, private keys, passwords, or full secret manifests. Report context names, cluster names, server URLs, and validation results only.

## Workflow

1. Inspect current access safely.

   - Read `KUBECONFIG` and default to `~/.kube/config` when unset.
   - Use `kubectl config get-contexts`, `kubectl config view --minify --raw` only when needed, and redact sensitive fields before showing output.
   - If a context exists, verify it with `kubectl --context <ctx> get nodes -o wide` before changing anything.

2. Confirm the source path.

   - Prefer project docs or company knowledge links supplied by the user.
   - If docs disagree with live infra, verify against load balancer, HAProxy, API server, or VM facts before editing local kubeconfig.
   - Note any inferred value explicitly, such as using a bastion-exposed API port instead of the in-cluster `6443`.

3. Retrieve and normalize kubeconfig.

   - Save fetched config as `~/.kube/<cluster>-admin.conf` with `0600` permissions.
   - Rename generic cluster/context/user names to stable names, for example `<cluster>`, `<cluster>-admin`.
   - Set the external API server endpoint only after confirming the routable address and port.
   - If certificate authority data does not match an external endpoint and the user accepts that tradeoff, set `insecure-skip-tls-verify` and delete stale CA fields. Call out this security tradeoff in the final answer.

4. Merge without clobbering.

   - Back up `~/.kube/config` before merging.
   - Merge with `KUBECONFIG="$HOME/.kube/config:$HOME/.kube/<cluster>-admin.conf" kubectl config view --flatten`.
   - Preserve the user's current context unless they explicitly ask to switch it.
   - After merge, verify the new context and list only non-sensitive metadata.

5. Validate cluster readiness.

   - Run node, namespace, pod, and CR checks relevant to the request.
   - For CAPI/Kamaji/OpenStack clusters, check the resource chain from user-facing CR to CAPI `Cluster`, `controlPlaneRef`, `infrastructureRef`, `MachineDeployment`, `Machine`, and provider resources when available.
   - Report blockers as concrete missing dependencies, ports, credentials, node packages, or controller status.

6. Handle storage provisioners only when requested.

   - Compare an existing reference context first: Helm release, namespace, chart, app version, storage class, default class flag, provisioner name, reclaim policy, mount path, and node package prerequisites.
   - Install or update the provisioner using the same pattern unless there is a clear incompatibility.
   - If NFS mounting fails, check node-side packages such as `nfs-common` before changing the Helm release.

7. Smoke test and clean up.

   - Create a uniquely named test namespace and PVC only when the requested validation requires it.
   - Wait for `Bound` PVC or a clear failure reason.
   - Delete test namespace/PVC/PV if the reclaim policy leaves leftovers.
   - Verify no test resources remain.

## Final Output

Finish with:

- What was changed and what was only inspected.
- Local kubeconfig file paths and backup path, without secret content.
- Context, cluster, user, API server, and current-context status.
- Validation commands run and their result.
- Storage class/provisioner status when relevant.
- Any cleanup performed.
- A copy-paste block for future connection that avoids embedding passwords or secrets.

Stop when access is verified, the requested provisioning/validation is complete, or a missing external credential/infrastructure dependency prevents safe progress.
