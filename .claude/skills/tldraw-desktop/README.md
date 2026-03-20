# tldraw-desktop

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) for interacting with the [tldraw desktop](https://github.com/tldraw/tldraw-desktop) canvas via its local HTTP API.

## Prerequisites

- [tldraw desktop](https://github.com/tldraw/tldraw-desktop) installed and running — [Download latest release](https://github.com/tldraw/tldraw-desktop/releases/latest)
- The app exposes a local Canvas API on `http://localhost:7236`

## Install

```bash
npx skills add tmdgusya/tldraw-desktop-skill --yes --global
```

## What it does

This skill enables Claude Code to programmatically draw on tldraw canvases:

- **Create shapes** — rectangles, circles, diamonds, arrows, sticky notes, and more
- **Build diagrams** — flowcharts, wireframes, architecture diagrams
- **Layout shapes** — align, stack, distribute, place relative to other shapes
- **Take screenshots** — capture the canvas as JPEG for visual verification
- **Run advanced JS** — execute arbitrary code against the tldraw Editor SDK

## Usage

With tldraw desktop open and a document active, ask Claude Code:

- "Draw a flowchart for user authentication"
- "Create a wireframe for a login page"
- "Sketch an architecture diagram for a microservices system"
- "Draw an ERD for this database schema"

## License

MIT
