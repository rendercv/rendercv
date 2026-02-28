#!/bin/bash
set -e

if ! command -v trivy &> /dev/null; then
    echo "trivy is not installed. Install with: brew install trivy"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "Scanning $REPO_DIR for vulnerabilities..."
trivy fs --scanners vuln "$REPO_DIR"