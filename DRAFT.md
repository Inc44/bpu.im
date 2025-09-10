# Website Design Document

## Requirements

### Functional Requirements

- Display Markdown-formatted articles on mathematics (biography, cheatsheets, tests), computer science (AI, cybersecurity, cheatsheets, tests), languages (English, French, German, Russian, Ukrainian, Polish, Japanese, Chinese, Korean), physics, chemistry, and engineering.
- Render mathematical equations.
- Embed vector graphics.
- Execute code snippets with output display (Python, JavaScript, PHP, Lua, C, C++, C#, Java, Kotlin, Go, Rust, Zig).
- Include interactive quizzes and tests: multiple-choice, fill-in, code-based, with immediate feedback and scoring.
- User authentication for saving quiz progress and marking read articles; anonymous access for reading and basic interaction.
- Responsive design for desktop and mobile.
- Search functionality for articles.
- Admin interface for uploading/editing Markdown articles and quizzes.

### Non-Functional Requirements

- Aesthetic: Minimalistic layout with high contrast (black/white/gray/cyberpunk/colorful palettes), monochromatic scheme. Incorporate retro 8-bit pixel art elements (e.g., pixelated icons, borders, shadows). Use monospaced fonts (e.g., Google Fonts). Neo-brutalist structure: raw, blocky UI with optional rounded corners and shadows. Cyberpunk influences: glitch effects on hover, neon-like accents. USSR aesthetic: constructivist typography, bold sans-serif overlays, propaganda-poster simplicity.
- Performance: Page load under 2 seconds; code execution timeout at 4–6 seconds.
- Security: Sandbox code execution to prevent injection or resource abuse; validate quiz inputs.
- Scalability: Handle up to 100 concurrent users initially; modular for future expansion.
- Accessibility: High contrast ensures WCAG AA compliance; keyboard navigation for quizzes; image alt text.
- Development Simplicity: Easy modification; avoid complex build pipelines.

### User Stories

- As a reader, I view an article with rendered math and graphics.
- As a learner, I take a quiz embedded in an article and see results.
- As a learner, I run code from an article or my input and view output.
- As an author, I write articles in Markdown with quiz/code blocks.

### Tech Stack

Prioritize simplicity and ease of development: minimal code. Use the most popular languages, frameworks, and libraries with the biggest support. Use specialized tools instead of inventing our own. Avoid rare dependencies with little to no support.

### Backend (not yet decided)

- Framework: Django, Flask, Laravel
- Language:
- Database: MariaDB, MySQL, PostgreSQL, SQLite
- Markdown Processing:
- Code Execution:
- Other:

### Frontend (not yet decided)

- Framework: HTMX, Next, React, Solid, Svelte, Vanilla, Vue
- CSS: Bootstrap, Tailwind, Vanilla
- Fonts: Monospaced via Google Fonts
- Math Rendering: KaTeX, MathJax
- Graphics: Asymptote (interactive 3D graphs in HTML), Mermaid, TikZ, chemfig, pgfplots, tkz-tab
- Quizzes:
- Other:

### Deployment

- Domain: bpu.im, with several subdomains used for other projects.
- Proxy: Cloudflare
- Hosting: Netcup ARM64 6 vCore 8 GB RAM 256 GB NVMe Debian; may be migrated to x86_64 in the future.
- Server: Apache
- Compression: Precompressed and dynamic
- Version Control: Git
- IDE: VSCode

### Inspiration

- [Brilliant](https://brilliant.org)
- [Khan Academy](https://www.khanacademy.org)