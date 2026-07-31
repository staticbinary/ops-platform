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
    kubectl get "$1" "$2" -n "$NAMESPACE" >/dev/null 2>&1
}

check_deployment() {
    local name="$1"
    local desired
    local available

    if ! resource_exists deployment "$name"; then
        fail "$name Deployment not found"
        return
    fi

    desired="$(kubectl get deployment "$name" -n "$NAMESPACE" \
        -o jsonpath='{.spec.replicas}' 2>/dev/null)"
    available="$(kubectl get deployment "$name" -n "$NAMESPACE" \
        -o jsonpath='{.status.availableReplicas}' 2>/dev/null)"

    desired="${desired:-0}"
    available="${available:-0}"

    if [[ "$available" == "$desired" && "$desired" -gt 0 ]]; then
        pass "$name Deployment ready ($available/$desired)"
    else
        fail "$name Deployment not ready ($available/$desired)"
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

    desired="$(kubectl get statefulset "$name" -n "$NAMESPACE" \
        -o jsonpath='{.spec.replicas}' 2>/dev/null)"
    ready="$(kubectl get statefulset "$name" -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}' 2>/dev/null)"

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
        kubectl get endpoints "$name"             -n "$NAMESPACE"             -o jsonpath='{range .subsets[*].addresses[*]}{.ip}{" "}{end}'             2>/dev/null
    )"

    if [[ -n "${endpoints// }" ]]; then
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

    phase="$(kubectl get pvc "$name" -n "$NAMESPACE" \
        -o jsonpath='{.status.phase}' 2>/dev/null)"

    if [[ "$phase" == "Bound" ]]; then
        pass "$name PVC is Bound"
    else
        fail "$name PVC status is ${phase:-Unknown}"
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
        --no-headers 2>/dev/null |
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
check_deployment tempo
check_deployment grafana
check_pvc grafana-data

if resource_exists deployment loki; then
    check_deployment loki
else
    warn "Loki has not been migrated yet"
fi

if resource_exists deployment alertmanager; then
    check_deployment alertmanager
else
    warn "Alertmanager has not been migrated yet"
fi

section "Service Discovery"

check_service_endpoints asset-service
check_service_endpoints auth-service
check_service_endpoints postgres
check_service_endpoints prometheus
check_service_endpoints tempo
check_service_endpoints grafana

section "Networking"

INGRESS_COUNT="$(
    kubectl get ingress -n "$NAMESPACE" \
        --no-headers 2>/dev/null |
        wc -l |
        tr -d ' '
)"

if [[ "$INGRESS_COUNT" -gt 0 ]]; then
    pass "$INGRESS_COUNT Ingress resource(s) configured"
    kubectl get ingress -n "$NAMESPACE" \
        --no-headers \
        -o custom-columns='NAME:.metadata.name,CLASS:.spec.ingressClassName,ADDRESS:.status.loadBalancer.ingress[0].ip,PATHS:.spec.rules[0].http.paths[*].path' \
        2>/dev/null |
        sed 's/^/  /'
else
    fail "No Ingress resources found"
fi

section "Scaling"

HPA_COUNT="$(
    kubectl get hpa -n "$NAMESPACE" \
        --no-headers 2>/dev/null |
        wc -l |
        tr -d ' '
)"

if [[ "$HPA_COUNT" -gt 0 ]]; then
    pass "$HPA_COUNT HorizontalPodAutoscaler resource(s) configured"
    kubectl get hpa -n "$NAMESPACE" \
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
    kubectl get pods -n "$NAMESPACE" \
        --no-headers 2>/dev/null |
        awk '$3 != "Running" && $3 != "Completed" {print $1 " (" $3 ")"}'
)"

NOT_READY_PODS="$(
    kubectl get pods -n "$NAMESPACE" \
        --no-headers 2>/dev/null |
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
        kubectl get pods -n "$NAMESPACE" \
            --no-headers 2>/dev/null |
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
