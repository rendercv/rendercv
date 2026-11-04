# Application Runbook: Surface

Use this template only after repository evidence establishes the commands and
behavior. A heading with no verified content is a gap, not an operational
instruction.

## Scope

Name the application surface and the jobs this runbook supports.

## Prerequisites

List required runtimes, dependencies, services, credentials, and safe checks.

## Start

Record the exact command, process or project identity, ports, and writable
state. Distinguish fixed, defaulted, configurable, and observed values.

## Readiness

Name the observable condition that proves startup completed.

## Deterministic State

Explain how to create, select, or reset the scenario without touching unowned
state.

## Interface

Describe how to exercise the relevant browser, API, CLI, worker, or service.

## Runtime Evidence

Give retrieval commands for logs, traces, errors, and correlation identifiers.
Distinguish guaranteed fields from optional ones.

## Ownership And Cleanup

Explain how to identify resources created by this run and stop only those
resources. Keep missing cleanup policy under Unknowns.

## Validation

Name focused checks and the real-interface journey that prove the outcome.

## Unknowns

List missing facts or decisions that an agent must not invent.
