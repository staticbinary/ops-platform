#!/usr/bin/env bash

set -uo pipefail

NAMESPACE="${OPS_PLATFORM_NAMESPACE:-ops-platform}"
FAILURES=0
WARNINGS=0

if [[ -t 1 ]]; then
    GREEN=$'\033[0;32m'
    YELLOW=$'\033[0;33m'
    RED=$'\033[0;31m'
    BLUE=$'\033[0;34m'
    BOLD=$'\033[1m'
    RESET=$'\033[0m'
else
    GREEN=""
    YELLOW=""
    RED=""
    BLUE=""
    BOLD=""
    RESET=""
fi

pass() {
    printf "%s✓%s %s\n" "$GREEN" "$RESET" "$1"
}

warn() {
    printf "%s!%s %s\n" "$YELLOW" "$RESET" "$1"
    WARNINGS=$((WARNINGS + 1))
}

fail() {
    printf "%s✗%s %s\n" "$RED" "$RESET" "$1"
    FAILURES=$((FAILURES + 1))
}

section() {
    printf "\n%s%s%s\n" "$BOLD" "$1" "$RESET"
    printf '%*s\n' "${#1}" '' | tr ' ' '-'
}

resource_exists() {
    kubectl get "$1" "$2" \
        -n "$NAMESPACE" \
        >/dev/null 2>&1
}

check_deployment() {
    local name="$1"
    local desired
    local available

    if ! resource_exists deployment "$name"; then
        fail "$name Deployment not found"
        return
    fi

    desired="$(
        kubectl get deployment "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.spec.replicas}' \
            2>/dev/null
    )"

    available="$(
        kubectl get deployment "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.status.availableReplicas}' \
            2>/dev/null
    )"

    desired="${desired:-0}"
    available="${available:-0}"

    if [[ "$available" == "$desired" && "$desired" -gt 0 ]]; then
        pass "$name Deployment ready ($available/$desired)"
    else
        fail "$name Deployment not ready ($available/$desired)"
    fi
}

check_daemonset() {
    local name="$1"
    local desired
    local ready

    if ! resource_exists daemonset "$name"; then
        fail "$name DaemonSet not found"
        return
    fi

    desired="$(
        kubectl get daemonset "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.status.desiredNumberScheduled}' \
            2>/dev/null
    )"

    ready="$(
        kubectl get daemonset "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.status.numberReady}' \
            2>/dev/null
    )"

    desired="${desired:-0}"
    ready="${ready:-0}"

    if [[ "$ready" == "$desired" && "$desired" -gt 0 ]]; then
        pass "$name DaemonSet ready ($ready/$desired)"
    else
        fail "$name DaemonSet not ready ($ready/$desired)"
    fi
}

check_statefulset() {
    local name="$1"
    local desired
    local ready

    if ! resource_exists statefulset "$name"; then
        fail "$name StatefulSet not found"
        return
    fi

    desired="$(
        kubectl get statefulset "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.spec.replicas}' \
            2>/dev/null
    )"

    ready="$(
        kubectl get statefulset "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.status.readyReplicas}' \
            2>/dev/null
    )"

    desired="${desired:-0}"
    ready="${ready:-0}"

    if [[ "$ready" == "$desired" && "$desired" -gt 0 ]]; then
        pass "$name StatefulSet ready ($ready/$desired)"
    else
        fail "$name StatefulSet not ready ($ready/$desired)"
    fi
}

check_service_endpoints() {
    local name="$1"
    local endpoints

    if ! resource_exists service "$name"; then
        fail "$name Service not found"
        return
    fi

    endpoints="$(
        kubectl get endpointslice \
            -n "$NAMESPACE" \
            -l "kubernetes.io/service-name=$name" \
            -o jsonpath='{.items[*].endpoints[*].addresses[*]}' \
            2>/dev/null
    )"

    if [[ -n "${endpoints//[[:space:]]/}" ]]; then
        pass "$name Service has endpoint(s): $endpoints"
    else
        fail "$name Service has no active endpoints"
    fi
}

check_pvc() {
    local name="$1"
    local phase

    if ! resource_exists pvc "$name"; then
        fail "$name PVC not found"
        return
    fi

    phase="$(
        kubectl get pvc "$name" \
            -n "$NAMESPACE" \
            -o jsonpath='{.status.phase}' \
            2>/dev/null
    )"

    if [[ "$phase" == "Bound" ]]; then
        pass "$name PVC is Bound"
    else
        fail "$name PVC status is ${phase:-Unknown}"
    fi
}

prometheus_query() {
    local encoded_query="$1"

    kubectl get --raw \
        "/api/v1/namespaces/${NAMESPACE}/services/http:prometheus:9090/proxy/api/v1/query?query=${encoded_query}" \
        2>/dev/null
}

check_prometheus_query_one() {
    local description="$1"
    local encoded_query="$2"
    local response

    response="$(prometheus_query "$encoded_query" || true)"

    if [[ -z "$response" ]]; then
        fail "$description query failed"
        return
    fi

    if grep -Eq '"value":\[[^]]*,"1"\]' <<<"$response"; then
        pass "$description"
    else
        fail "$description returned no healthy result"
    fi
}

printf "\n%sOps Platform Kubernetes Status%s\n" "$BOLD" "$RESET"
printf "Namespace: %s\n" "$NAMESPACE"
printf "Checked:   %s\n" "$(date '+%Y-%m-%d %H:%M:%S')"

section "Cluster"

if ! command -v kubectl >/dev/null 2>&1; then
    fail "kubectl is not installed or not available in PATH"
    exit 1
fi

if ! kubectl cluster-info >/dev/null 2>&1; then
    fail "Kubernetes cluster is unreachable"
    exit 1
fi

pass "Kubernetes cluster reachable"

CONTEXT="$(kubectl config current-context 2>/dev/null || true)"
printf "  Context: %s\n" "${CONTEXT:-unknown}"

if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    pass "Namespace $NAMESPACE exists"
else
    fail "Namespace $NAMESPACE does not exist"
    exit 1
fi

NOT_READY_NODES="$(
    kubectl get nodes \
        --no-headers \
        2>/dev/null |
        awk '$2 !~ /^Ready/ {print $1}'
)"

if [[ -z "$NOT_READY_NODES" ]]; then
    pass "All Kubernetes nodes are Ready"
else
    fail "Non-ready node(s): $NOT_READY_NODES"
fi

section "Applications"

check_deployment asset-service
check_deployment auth-service

section "Data"

check_statefulset postgres
check_pvc postgres-data

section "Observability"

check_deployment prometheus
check_deployment grafana
check_pvc grafana-data

check_deployment tempo
check_deployment loki
check_deployment alloy

check_deployment postgres-exporter
check_daemonset node-exporter
check_deployment blackbox-exporter

check_deployment alertmanager
check_pvc alertmanager-data

section "Service Discovery"

check_service_endpoints asset-service
check_service_endpoints auth-service
check_service_endpoints postgres

check_service_endpoints prometheus
check_service_endpoints grafana
check_service_endpoints tempo
check_service_endpoints loki
check_service_endpoints alloy

check_service_endpoints postgres-exporter
check_service_endpoints node-exporter
check_service_endpoints blackbox-exporter
check_service_endpoints alertmanager

section "Prometheus Targets"

check_prometheus_query_one \
    "Prometheus target is up" \
    'up%7Bjob%3D%22prometheus%22%7D'

check_prometheus_query_one \
    "Asset Service target is up" \
    'up%7Bjob%3D%22asset-service%22%7D'

check_prometheus_query_one \
    "Auth Service target is up" \
    'up%7Bjob%3D%22auth-service%22%7D'

check_prometheus_query_one \
    "PostgreSQL Exporter target is up" \
    'up%7Bjob%3D%22postgres-exporter%22%7D'

check_prometheus_query_one \
    "Node Exporter target is up" \
    'up%7Bjob%3D%22node-exporter%22%7D'

check_prometheus_query_one \
    "Kubelet cAdvisor target is up" \
    'up%7Bjob%3D%22cadvisor%22%7D'

check_prometheus_query_one \
    "All Blackbox HTTP probes are successful" \
    'min%28probe_success%7Bjob%3D%22blackbox-http%22%7D%29'

section "Prometheus Access"

PROMETHEUS_SERVICE_ACCOUNT="$(
    kubectl get deployment prometheus \
        -n "$NAMESPACE" \
        -o jsonpath='{.spec.template.spec.serviceAccountName}' \
        2>/dev/null
)"

if [[ "$PROMETHEUS_SERVICE_ACCOUNT" == "prometheus" ]]; then
    pass "Prometheus uses the dedicated prometheus ServiceAccount"
else
    fail "Prometheus is using ServiceAccount ${PROMETHEUS_SERVICE_ACCOUNT:-default}"
fi

if kubectl auth can-i get nodes \
    --subresource=metrics \
    --as="system:serviceaccount:${NAMESPACE}:prometheus" \
    >/dev/null 2>&1; then
    pass "Prometheus ServiceAccount can read node metrics"
else
    fail "Prometheus ServiceAccount cannot read node metrics"
fi

if kubectl auth can-i get nodes \
    --subresource=proxy \
    --as="system:serviceaccount:${NAMESPACE}:prometheus" \
    >/dev/null 2>&1; then
    pass "Prometheus ServiceAccount can access the node proxy"
else
    fail "Prometheus ServiceAccount cannot access the node proxy"
fi

section "Networking"

INGRESS_COUNT="$(
    kubectl get ingress \
        -n "$NAMESPACE" \
        --no-headers \
        2>/dev/null |
        wc -l |
        tr -d ' '
)"

if [[ "$INGRESS_COUNT" -gt 0 ]]; then
    pass "$INGRESS_COUNT Ingress resource(s) configured"

    kubectl get ingress \
        -n "$NAMESPACE" \
        --no-headers \
        -o custom-columns='NAME:.metadata.name,CLASS:.spec.ingressClassName,ADDRESS:.status.loadBalancer.ingress[0].ip,PATHS:.spec.rules[0].http.paths[*].path' \
        2>/dev/null |
        sed 's/^/  /'
else
    fail "No Ingress resources found"
fi

section "Scaling"

HPA_COUNT="$(
    kubectl get hpa \
        -n "$NAMESPACE" \
        --no-headers \
        2>/dev/null |
        wc -l |
        tr -d ' '
)"

if [[ "$HPA_COUNT" -gt 0 ]]; then
    pass "$HPA_COUNT HorizontalPodAutoscaler resource(s) configured"

    kubectl get hpa \
        -n "$NAMESPACE" \
        --no-headers \
        -o custom-columns='NAME:.metadata.name,MIN:.spec.minReplicas,MAX:.spec.maxReplicas,CURRENT:.status.currentReplicas,DESIRED:.status.desiredReplicas' \
        2>/dev/null |
        sed 's/^/  /'
else
    warn "No HorizontalPodAutoscaler resources found"
fi

if kubectl top nodes >/dev/null 2>&1; then
    pass "Metrics Server is responding"
else
    fail "Metrics Server is not responding"
fi

section "Pod Health"

UNHEALTHY_PODS="$(
    kubectl get pods \
        -n "$NAMESPACE" \
        --no-headers \
        2>/dev/null |
        awk '$3 != "Running" && $3 != "Completed" {
            print $1 " (" $3 ")"
        }'
)"

NOT_READY_PODS="$(
    kubectl get pods \
        -n "$NAMESPACE" \
        --no-headers \
        2>/dev/null |
        awk '
            $3 == "Running" {
                split($2, ready, "/")
                if (ready[1] != ready[2]) {
                    print $1 " (" $2 " ready)"
                }
            }
        '
)"

if [[ -z "$UNHEALTHY_PODS" && -z "$NOT_READY_PODS" ]]; then
    POD_COUNT="$(
        kubectl get pods \
            -n "$NAMESPACE" \
            --no-headers \
            2>/dev/null |
            wc -l |
            tr -d ' '
    )"

    pass "All $POD_COUNT Pod(s) are healthy"
else
    if [[ -n "$UNHEALTHY_PODS" ]]; then
        fail "Pod(s) in unhealthy state:"
        printf '%s\n' "$UNHEALTHY_PODS" | sed 's/^/    /'
    fi

    if [[ -n "$NOT_READY_PODS" ]]; then
        fail "Running Pod(s) not fully Ready:"
        printf '%s\n' "$NOT_READY_PODS" | sed 's/^/    /'
    fi
fi

section "Overall Status"

if [[ "$FAILURES" -eq 0 ]]; then
    if [[ "$WARNINGS" -eq 0 ]]; then
        printf "%s%sHEALTHY%s — all checks passed\n\n" \
            "$BOLD" "$GREEN" "$RESET"
    else
        printf "%s%sHEALTHY WITH %d EXPECTED WARNING(S)%s\n\n" \
            "$BOLD" "$YELLOW" "$WARNINGS" "$RESET"
    fi

    exit 0
else
    printf "%s%sUNHEALTHY%s — %d failed check(s), %d warning(s)\n\n" \
        "$BOLD" "$RED" "$RESET" "$FAILURES" "$WARNINGS"

    exit 1
fi