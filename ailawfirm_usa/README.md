# ailawfirm_usa/ — core package

The Python package that powers **AI Brain — USA**.

For the product overview, install guide, and the authoritative agent / MCP-tool list, see the repository [README.md](../README.md). This file documents the internal package layout for contributors.

## Layout

This package follows the standard AI Brain — USA shape: a CLI entry point, a configuration loader, a set of specialist agents under `agents/`, an MCP server exposing the tools described in the top-level README, and a forked memory/retrieval layer.

Run `ls ailawfirm_usa/` for the authoritative, current module set — the package is the source of truth, not this file.

## Credit

The memory / retrieval architecture is forked from a local memory architecture (MIT) and credited in the top-level README.
