# HAI

HAI helps you organize work with AI across projects and business activities.
It gives AI clear instructions for planning, carrying out tasks and checking
results, while keeping your work and decisions organized.

A **HAI role** defines a responsibility, such as business analysis or review.
A **skill** provides a reusable method, such as writing requirements. A **workflow**
sets the steps and handoffs between roles. Your **AI agent** carries out the work.

## What can it do?

- Help turn an idea into clear requirements and a plan.
- Support research, analysis, writing, software development and other tasks.
- Guide AI agents through repeatable steps and clearly defined roles.
- Keep requests, decisions and results so you can continue work later.

## What do you need?

- **An AI agent**, such as Codex, Claude Code or GitHub Copilot in agent mode.
  It must be able to read and update files in your project folder and run commands
  with your permission. You need access to the AI service used by your chosen
  tool; HAI does not provide the AI itself.
- **Python 3.11 or newer**, installed on your computer and accessible to your AI agent.
- **A project folder** where you want to use HAI.

You do not need Git to install HAI.
The core uses Python's standard library, so no extra Python packages are required.

## Install and start

1. Open the [latest HAI release](https://github.com/h111359/HAI/releases/latest).
2. Under **Assets**, download the HAI release ZIP.
3. Extract it and copy the complete `.hai` folder and `LICENSE` into your project
   folder. Make sure the hidden `.hai` folder is included.
4. Start your AI agent in your project folder and ask:

   > Set up HAI in this project by following `.hai/start.md`, then help me get started.

5. Describe what you want to do. You can also ask **"Help with HAI"**.

Roles, skills and workflows are optional and installed separately. For setup details and upgrades,
see [the installation guide](INSTALL.md).

HAI is available under the [MIT license](LICENSE).
