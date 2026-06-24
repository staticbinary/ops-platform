#!/bin/bash

pass() {
    echo "[PASS] $1"
}

fail() {
    echo "[FAIL] $1"
    exit 1
}

info() {
    echo "[INFO] $1"
}