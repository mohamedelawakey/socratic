# 🤝 Contributing to Socratic Debug

First off, thank you for considering contributing to **Socratic Debug** (`socratic`)! It's people like you who make open source such a powerful, fun, and educational community.

Please take a few minutes to read through these guidelines to ensure a smooth, transparent, and collaborative process for everyone.

---

## 📌 Ground Rules for Contributions

Before writing code or opening a Pull Request, please follow these guidelines based on the scope of your changes:

### 1. New Features, Architecture Refactors, or Large Changes
> **Rule:** If your idea introduces a new feature, changes core architecture, or modifies multiple files across the repository, **you MUST open a GitHub Discussion or Issue FIRST.**
- Give your Discussion a descriptive, clear title.
- Explain the motivation: What problem does this solve? Why is it needed?
- Outline your proposed technical approach.
- Wait for alignment and feedback from the maintainers before writing extensive code. This respects your time and ensures architectural harmony with the project's vision.

### 2. Bug Fixes & Minor Tweaks
> **Rule:** If you are fixing a verified bug, correcting a typo, or improving documentation/small components **that do not touch multiple files broadly**, you can jump straight to opening a **Pull Request (PR)**.
- Clearly describe the bug being fixed and steps to reproduce.
- Reference any existing issue if applicable (e.g., `Fixes #12`).

---

## 🚀 Step-by-Step Contribution Workflow

1. **Fork the Repository**
   Click the **Fork** button on GitHub to create your own copy of the repository.

2. **Clone & Set Up Locally**
   ```bash
   git clone https://github.com/<your-username>/socratic.git
   cd socratic
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"    # Or pip install -r requirements.txt
   ```

3. **Create a Feature Branch**
   Always create a new, descriptive branch off `main`:
   ```bash
   git checkout -b fix/extractor-frame-handling
   # or
   git checkout -b feat/support-custom-theme
   ```

4. **Make Your Changes**
   - Follow clean Python conventions (PEP 8).
   - Keep functions focused and well-documented.
   - Do not commit secrets, API keys, or personal `.socratic.yaml` configurations.

5. **Test Your Changes**
   Make sure existing functionality isn't broken:
   ```bash
   python3 -m unittest discover tests/
   # Or run target test scripts
   socratic run test/test_hook.py
   ```

6. **Commit & Push**
   Write clear, concise commit messages:
   ```bash
   git commit -m "fix(extractor): ensure accurate frame context line extraction"
   git push origin fix/extractor-frame-handling
   ```

7. **Open a Pull Request**
   - Head over to the upstream GitHub repository and open a Pull Request.
   - Fill out the PR template explaining what changes were made and why.
   - Wait for review: The maintainer will review your code, run automated CI checks, and either request minor adjustments or approve and merge it.

---

## 💡 Code Style & Standards

- **Python Version:** Supported on Python 3.10, 3.11, and 3.12.
- **Cross-Platform:** Code must run cleanly across Linux, macOS, and Windows.
- **Decoupling:** Keep core state logic in `src/` cleanly decoupled from UI implementations in `ui/`.

---

## 💬 Questions or Help?

If you ever get stuck or have questions, feel free to open a thread under **GitHub Discussions**. We are here to learn, build, and grow together!
