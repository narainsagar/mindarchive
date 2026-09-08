mind-archive/
│
├── README.md
├── CLAUDE.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── apps/
│   ├── web/
│   └── api/
│
├── docs/
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── SECURITY.md
│   ├── ROADMAP.md
│   ├── BACKLOG.md
│   ├── DECISIONS.md
│   └── GITHUB_PAGES.md
│
├── prompts/
│   ├── AI-CODING.md
│   ├── CHATGPT.md
│   ├── CLAUDE.md
│   └── GEMINI.md
│
├── .claude/
│   ├── rules/
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   ├── security.md
│   │   ├── documentation.md
│   │   └── git.md
│   └── skills/
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
│
└── scripts/



💡 And I think we should exploit this for Mind Archive

Instead of putting one AI coding tool at the center of the project, our repository should remain completely agent-neutral.

We've already designed:

CLAUDE.md

but I recommend we expand that idea.

We should have:

Mind Archive
│
├── CLAUDE.md
├── AGENTS.md
├── GEMINI.md
├── QWEN.md
│
├── .claude/
│   └── rules/
│
├── .qwen/
│   └── ...
│
├── docs/
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── SECURITY.md
│   ├── ROADMAP.md
│   ├── BACKLOG.md
│   └── DECISIONS.md
│
└── prompts/
    └── AI-CODING.md

But the actual project knowledge should live primarily in docs/, not inside any particular AI's memory.

That means:

              Mind Archive Repository
                       │
                       ▼
                SOURCE OF TRUTH
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Claude Code     Qwen Code      OpenCode
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 SAME PROJECT