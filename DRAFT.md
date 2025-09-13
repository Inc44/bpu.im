# Website Design Document

## Requirements

### Functional Requirements

- Display Markdown-formatted articles on mathematics (biography, cheatsheets, tests), computer science (AI, cybersecurity, cheatsheets, tests), languages (English, French, German, Russian, Ukrainian, Polish, Japanese, Chinese, Korean), physics, chemistry, and engineering.
- Render mathematical equations using KaTeX or MathJax.
- Embed vector graphics using SVG/HTML from Asymptote and using SVG from Mermaid, TikZ, chemfig, pgfplots, or tkz-tab.
- Execute code snippets with output display for Python, JavaScript, PHP, Lua, C, C++, C#, Java, Kotlin, Go, Rust, and Zig.
- Include interactive quizzes and tests: multiple-choice, fill-in, code-based, with immediate feedback and scoring.
- User authentication for saving quiz progress and marking read articles; anonymous access for reading and basic interaction.
- Responsive design for desktop and mobile devices.
- Search functionality for articles by title, content, or tags.
- Admin interface for uploading and editing Markdown articles containing code blocks and quizzes; the admin is the only author.

### Non-Functional Requirements

- Aesthetic: Minimalistic layout with high contrast using black, white, gray, cyberpunk, or colorful palette themes in a monochromatic scheme. Incorporate retro 8-bit pixel art elements such as pixelated icons, borders, and shadows. Use monospaced fonts from Google Fonts. Apply neo-brutalist structure with raw, blocky UI elements, optional rounded corners, and shadows. Add cyberpunk influences like glitch effects on hover and neon-like accents. Integrate USSR aesthetic through constructivist typography, bold sans-serif overlays, and propaganda-poster simplicity.
- Performance: Page load time under 2 seconds; code execution timeout at 4–6 seconds.
- Security: Sandbox code execution to prevent injection or resource abuse; validate all quiz inputs and user data.
- Scalability: Handle up to 100 concurrent users initially; design modular components for future expansion.
- Accessibility: High contrast for WCAG AA compliance; keyboard navigation for quizzes; alt text for all images and graphics.
- Development Simplicity: Enable easy modifications; avoid complex build pipelines or rare dependencies.

### User Stories

- As a reader, I view an article with rendered math equations and embedded graphics.
- As a learner, I take a quiz embedded in an article and receive immediate feedback and scoring.
- As a learner, I run code snippets from an article or enter my own code and view the output.
- As an author, I write articles in Markdown format including quiz and code blocks.

## Tech Stack

Prioritize simplicity and ease of development with minimal code. Select popular languages, frameworks, and libraries with large community support. Use specialized tools for specific tasks instead of custom implementations. Avoid rare dependencies lacking support.

### Backend

- Framework: Flask.
- Language: Python.
- Database: SQLite.
- Markdown Processing: Python-Markdown (converts Markdown with special syntax for quizzes and code blocks to HTML without full article conversion where unnecessary).
- Code Execution: Judge0 API (self-hosted, supports most languages except Zig) or glot.io (self-hosted with all language support).
- Other: Flask-Login (session-based authentication); Flask-SQLAlchemy (database ORM); Werkzeug (security utilities).

### Frontend

- Framework: HTMX (partial page reload for dynamic updates without JavaScript frameworks).
- CSS: Tailwind.
- Fonts: Monospaced fonts loaded via Google Fonts.
- Math Rendering: KaTeX (fast, lightweight) as primary; MathJax as fallback for complex equations.
- Graphics (via LaTeX backend compilation): Asymptote (compiles to SVG/HTML for static/interactive graphs); Mermaid (charts and diagrams); TikZ (graphs and trees); chemfig, pgfplots, tkz-tab.
- Quizzes: Vanilla JavaScript with HTMX for submissions and feedback rendering.
- Other: Marked.js (client-side Markdown preview for admin editing), admin editing snippet completion.

### Deployment

- Domain: bpu.im, with several subdomains used for other projects.
- Proxy: Cloudflare (handles CDN, DDoS protection, CAPTCHA, compression).
- Hosting: Netcup ARM64 server (6 vCore, 8 GB RAM, 256 GB NVMe on Debian); prepare for potential x86_64 migration.
- Server: Apache (serves static assets and proxies to Flask).
- Compression: Precompress static files; enable dynamic Brotli/Zstd/Gzip/Deflate via Cloudflare.
- Version Control: Git.
- IDE: VSCode.

### Inspiration

- [Brilliant](https://brilliant.org)
- [GeeksforGeeks](https://www.geeksforgeeks.org)
- [Khan Academy](https://www.khanacademy.org)
- [Obsidian](https://obsidian.md)
- [Overleaf](https://www.overleaf.com)
- [W3Schools](https://www.w3schools.com)