# firm/ — Firm Mode (NOT YET IMPLEMENTED)

This subpackage is reserved for firm-mode functionality:
- Multi-user authentication
- Role / permission system
- Matter assignment across advocates
- Conflict-check engine
- Partner-billing module
- Clerk hierarchy

**Status:** Empty placeholder in v0.1. Real implementation lands in v0.3+.

Architectural decision: solo + firm modes are combined in a single codebase per country to keep the surface area small for v0.1; firm-mode code paths are scaffolded but gated until v0.3+.

When a user runs `ailawfirm-india init --mode firm` in v0.1, the CLI raises:
> "Firm mode not yet implemented in v0.1. Use --mode solo. Firm mode lands in v0.3+."
