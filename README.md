# Codex Resume Generation

Codex Resume Generation is a local workflow for creating tailored job application packages with Codex CLI.

You paste in a job description, and Codex uses your source profile and CV to generate:

- A tailored resume PDF
- A tailored cover letter PDF
- A job context file
- A match matrix showing why content was selected
- A generation report
- An application tracker update
- A package manifest for validation/debugging

This project is not meant to be a generic resume builder. It is designed around a source-of-truth workflow where Codex drafts the tailored content and the local scripts render, validate, and organize the final files.

## Why This Exists

Applying to jobs usually requires the same repeated work:

1. Read the job description.
2. Identify the most relevant projects and skills.
3. Rewrite the resume for that role.
4. Draft a cover letter.
5. Track the application.
6. Save the generated files somewhere consistent.

This repository automates that workflow while keeping the generated content grounded in your existing CV and profile data.

The goal is not to fabricate experience. The goal is to make it faster to turn real experience into focused, role-specific application materials.

## How It Works

The workflow has two main parts:

1. **Codex creates the structured application inputs**
   - `job_context.json`
   - `match_matrix.json`
   - `resume.xml`
   - `cover_letter.txt`

2. **The local Python scripts render and validate the package**
   - Resume PDF
   - Cover letter PDF
   - Tracker update
   - Manifest
   - Generation report

The Codex skills live in:

```text
.agents/skills/
```

The candidate source files live in:

```text
GenFiles/profile.yml
GenFiles/cv.md
```

The scripts use those files as the source of truth.

## Repository Structure

```text
.
├── .agents/skills/              # Codex CLI skills for package generation
├── GenFiles/
│   ├── profile.yml              # Candidate contact info, preferences, proof points
│   ├── cv.md                    # Source CV content
│   ├── agent_refs/              # Rules used by the Codex skills
│   └── tmp/                     # Temporary generated inputs
├── bin/                         # Shell wrappers for setup, generation, and validation
├── data/
│   └── Application Tracker.txt  # Application tracker
├── examples/                    # Example input files and sample outputs
├── scripts/                     # Validation scripts
├── src/                         # PDF generation and tracker update scripts
├── templates/                   # Resume and cover letter HTML templates
└── requirements.txt             # Python dependencies
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/CodexResumeGeneration.git
cd CodexResumeGeneration
```

### 2. Set up the Python environment

```bash
bin/setup_env.sh
```

If the environment needs to be rebuilt:

```bash
bin/setup_env.sh --recreate
```

### 3. Customize your source files

Edit these files before generating real application materials:

```text
GenFiles/profile.yml
GenFiles/cv.md
```

`profile.yml` should contain your contact information, target role preferences, reusable positioning, and proof points.

`cv.md` should contain your full source CV: education, work history, projects, skills, and any other experience Codex is allowed to use.

### 4. Start Codex from the repository root

```bash
codex
```

Codex should be started from the root of this repository so it can discover the local skills in `.agents/skills/`.

### 5. Run the application package skill

Inside Codex, invoke:

```text
$generate-application-package
```

Then paste the job description when Codex asks for it.

Codex will generate the structured inputs, run validation, call the rendering scripts, and report the generated output paths.

## Main Workflow

For most job applications, use:

```text
$generate-application-package
```

This creates the full package:

- Resume PDF
- Cover letter PDF
- Job context
- Match matrix
- Generation report
- Application tracker update
- Manifest

For resume-only generation, use:

```text
$generate-resume-only
```

For cover-letter-only generation, use:

```text
$generate-cover-letter-only
```

For validation/debugging, use:

```text
$validate-application-package
```

## Manual Commands

Most users should use the Codex skills instead of calling the scripts directly.

The manual commands below are mainly useful for debugging after the required XML, TXT, and JSON files already exist.

Generate a full application package:

```bash
bin/run_application_package.sh \
  GenFiles/tmp/example_job/job_context.json \
  GenFiles/tmp/example_job/resume.xml \
  GenFiles/tmp/example_job/cover_letter.txt
```

Generate only a resume PDF:

```bash
bin/run_resume.sh examples/example_resume.xml examples/output/output.pdf \
  --html-output examples/output/output.html
```

Generate only a cover letter PDF:

```bash
bin/run_cover_letter.sh examples/example_cover_letter.txt examples/output/example_cover_letter.pdf \
  --html-output examples/output/example_cover_letter.html
```

Run smoke tests:

```bash
bin/smoke_test_application_package.sh
bin/smoke_test_resume.sh
bin/smoke_test_cover_letter.sh
bin/smoke_test_validators.sh
```

## Output Files

Generated application packages are written to output locations controlled by the package generator.

A typical package includes:

```text
GenCoverLetters/<Company>-Resume.pdf
GenCoverLetters/<Company>-Cover-Letter.pdf
GenFiles/tmp/<Company>/application_package_manifest.json
GenFiles/tmp/<Company>/generation_report.md
```

The manifest is the best place to check the final paths, validation status, tracker status, cleanup status, and assumptions.

## Source-of-Truth Rules

The workflow is designed to avoid unsupported or fabricated resume content.

Codex should only use evidence from:

```text
GenFiles/profile.yml
GenFiles/cv.md
```

When tailoring a resume or cover letter, Codex should:

- Use concrete CV evidence before generic claims
- Preserve real dates, tools, employers, credentials, and project details
- Avoid inventing metrics, certifications, titles, or company claims
- Tailor the wording to the role without changing the underlying facts

## Cover Letter Format

Cover letter input files should contain body paragraphs only.

Do not include:

- Header/contact information
- Date
- Greeting
- Closing
- Signature
- Metadata such as `company:`, `role:`, or `location:`

The generator adds the header, current date, salutation, closing, and signature from `GenFiles/profile.yml`.

## Privacy and Git Hygiene

This repository is safe to publish only if it contains example data.

Before using it with real applications, make sure private files are not committed.

Recommended files/folders to keep out of public Git history:

```text
GenFiles/profile.yml
GenFiles/cv.md
GenFiles/tmp/
GenCoverLetters/
data/Application Tracker.txt
.runtime-cache/
.venv/
node_modules/
*.pdf
*.html
```

A safer pattern is to commit example files such as:

```text
GenFiles/profile.example.yml
GenFiles/cv.example.md
data/Application Tracker.example.txt
```

Then keep your real local files untracked.

## Recommended `.gitignore`

```gitignore
# Python
.venv/
__pycache__/
*.pyc

# Node/dependencies
node_modules/

# Runtime/cache files
.runtime-cache/
.cache/

# Generated application materials
GenFiles/tmp/
GenCoverLetters/
*.pdf
*.html

# Personal candidate data
GenFiles/profile.yml
GenFiles/cv.md
data/Application Tracker.txt

# Keep examples
!GenFiles/profile.example.yml
!GenFiles/cv.example.md
!data/Application Tracker.example.txt
!examples/**
```

## Requirements

Python 3.10 or newer is recommended.

Python dependencies are listed in:

```text
requirements.txt
```

On macOS, WeasyPrint may require native libraries. The wrapper scripts are designed to set the expected environment paths for local generation.

## Troubleshooting

### Codex cannot find the skill

Start Codex from the repository root:

```bash
cd /path/to/CodexResumeGeneration
codex
```

### The virtual environment is broken

Recreate it:

```bash
bin/setup_env.sh --recreate
```

### PDF generation fails on macOS

Use the wrapper scripts instead of calling Python directly. The wrappers set local paths needed by WeasyPrint and Fontconfig.

### Validation fails

Read the validator error first. The most common causes are:

- Resume XML does not match the expected structure
- Cover letter TXT includes metadata, a greeting, or a signature
- Match matrix references content not present in the resume
- Required resume sections have too few bullets

Fix the source XML/TXT/JSON and rerun validation before using the generated files.

## Current Status

This project is designed for local Codex CLI usage.

It is best suited for a personal job-application workflow where the user maintains one detailed source CV and asks Codex to produce tailored, evidence-grounded application materials for each role.
