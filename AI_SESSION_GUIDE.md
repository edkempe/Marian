# AI Session Management Guide

## Quick Start

### Initial Prompt
```markdown
Hi! Let's work on Marian. Please review the project documentation and let me know what you understand about the project and what we should focus on.
```

### Expected AI Response
1. Review key documentation
2. Summarize project understanding:
   - Core objectives
   - Key components
   - Current state
   - Critical guidelines
3. Identify potential focus areas from BACKLOG.md
4. Ask for confirmation before proceeding

### Follow-up Discussion
- Confirm or correct AI's understanding
- Agree on specific focus area
- Set any specific guidelines for the session

### Closing Prompt
```markdown
Let's close this session.
```

### Expected AI Closing Response
1. Create session log (docs/sessions/YYYY-MM-DD-HH-MM.md):
   ```markdown
   # Session YYYY-MM-DD-HH-MM

   ## Accomplished
   - [List of completed work]

   ## Decisions
   - [Key decisions made]
   - [Changes to project structure/process]
   - [Important context for future work]

   ## Follow-up Tasks
   - Added to BACKLOG.md:
     - Task A (Immediate Priority)
     - Task B (High Priority)
   ```

2. Update BACKLOG.md:
   - Add new tasks with priority
   - Include session reference
   - Add relevant context
   - Update task priorities if needed

3. Provide closing summary to user:
   - Work accomplished
   - Key decisions
   - Next priorities
   - Request confirmation

## Task Management

### BACKLOG.md Structure
```markdown
# Backlog

## Immediate Priority (Identified in last session: YYYY-MM-DD)
- [ ] Task A (From: Session YYYY-MM-DD)
  - Context: [Direct follow-up from previous work]
  - Dependencies: [Required prerequisites]

## High Priority
- [ ] Task B
  - Added: YYYY-MM-DD
  - Context: [Why this is important]

## Medium Priority
- [ ] Task C

## Low Priority
- [ ] Task D

## Completed
- [x] Task E (Completed: YYYY-MM-DD)
  - Resolution: [How it was addressed]
  - Session: [Link to session log]
```

### Session Log Structure
```markdown
# Session YYYY-MM-DD-HH-MM

## Objectives
- [What we aimed to accomplish]

## Accomplished
- [Completed tasks]
- [Code changes]
- [Documentation updates]

## Decisions
- [Key decisions]
- [Rationale]
- [Impact]

## Follow-up Tasks
- Added to BACKLOG.md:
  - [New tasks with priority]
  - [Context for each task]

## Notes
- [Additional context]
- [Important considerations]
```

## Session Workflow

### 1. Starting a Session

#### Required Checks
- [ ] Review BACKLOG.md for context and priorities
- [ ] Check current branch and repository state
- [ ] Verify environment and dependencies
- [ ] Review relevant documentation for task

#### AI Context Loading
The AI assistant will:
1. Review project documentation
2. Check existing codebase
3. Understand domain boundaries
4. Follow established patterns

### 2. During the Session

#### Documentation
- Create session file: `docs/sessions/YYYY-MM-DD-HH-MM.md`
- Document decisions and changes in real-time
- Update relevant documentation as needed

#### Code Changes
- Follow code reuse guidelines
- Maintain domain separation
- Update tests appropriately
- Document architectural decisions

#### Communication Guidelines
- Be specific about task requirements
- Provide clear success criteria
- Ask for clarification when needed
- Confirm understanding of complex tasks

### 3. Closing a Session

#### Required Actions
1. **Code Review**
   - Review all changes made
   - Ensure tests are updated
   - Check documentation updates
   - Verify style guidelines followed

2. **Documentation Update**
   - Update BACKLOG.md
   - Document any pending items
   - Note any discovered issues
   - Record architectural decisions

3. **Session Log**
   - Create detailed session summary
   - List all changes made
   - Document decisions
   - Note future considerations

## Session Directory Structure
```
docs/
└── sessions/
    ├── active/            # Current session notes
    │   └── YYYY-MM-DD.md
    └── archive/           # Past session summaries
        └── YYYY-MM/
            └── DD-HH-MM.md
```

## Related Documentation
- PROJECT_PLAN.md - Overall project structure
- MARIAN_DESIGN_AND_DECISIONS.md - Architectural decisions
- docs/development/guidelines.md - Development guidelines
