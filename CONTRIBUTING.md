# Contributing

Thanks for your interest in contributing to the Claude Code Marketplace!

## How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-plugin`)
3. **Make** your changes
4. **Test** your plugin or agent locally
5. **Submit** a Pull Request

## Adding a New Plugin

1. Create a directory under `plugins/your-plugin-name/`
2. Add agents in `plugins/your-plugin-name/agents/`
3. Add commands in `plugins/your-plugin-name/commands/`
4. Add skills in `plugins/your-plugin-name/skills/` (optional)
5. Register your plugin in `.claude-plugin/marketplace.json`
6. Register agents and commands in `.claude-plugin/plugin.json`
7. Update the README with your plugin details

### Plugin Structure

```
plugins/your-plugin-name/
├── agents/
│   └── your-agent.md          # Agent definition with PROACTIVELY clause
├── commands/
│   └── your-command.md        # Slash command definition
└── skills/
    └── your-skill/
        └── SKILL.md           # Skill reference with pattern files
```

### Agent Guidelines

- Include a `PROACTIVELY` clause in the agent description for automatic delegation
- Define clear, non-overlapping responsibilities
- Specify the model (`opus` for complex tasks, `sonnet` for standard tasks)
- See [AGENT_PROMPT_GUIDE.md](./AGENT_PROMPT_GUIDE.md) for detailed guidance

### Skill Guidelines

- Use progressive disclosure: SKILL.md overview linking to detailed pattern files
- Include version-specific information and common gotchas
- Provide working code examples verified against current APIs

## Reporting Issues

- Use [GitHub Issues](https://github.com/skylence-be/claude-code-marketplace/issues) to report bugs or request features
- Include the plugin name and relevant context

## Code of Conduct

Please be respectful and constructive in all interactions. See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
