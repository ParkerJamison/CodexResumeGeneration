# Codex Resume Generation

Codex Resume Generation is a repo-local Codex skill workspace. It is intended to be used from Codex CLI, not as a standalone resume builder.

The normal workflow is:

1. Start Codex from this repository root so Codex can discover `.agents/skills/`.
2. Invoke the `generate-application-package` skill.
3. Paste a job description.
4. Let Codex create the structured inputs and call the local rendering scripts.

Codex uses this repository's source files, wrapper scripts, validators, and templates to produce application-ready resume and cover-letter PDFs.

The repository is designed around one source-of-truth pattern:

- `GenFiles/profile.yml` contains candidate contact data, preferences, reusable positioning, and proof points.
- `GenFiles/cv.md` contains the candidate's source CV content.
- `examples/example_job_context.json`, `examples/example_match_matrix.json`, `examples/example_resume.xml`, and `examples/example_cover_letter.txt` show the expected input shapes.
- Wrapper scripts run the generators and validators behind the skill so local environment details stay consistent.

All checked-in candidate data is synthetic. Replace the placeholders in `GenFiles/profile.yml` and `GenFiles/cv.md` before generating real application materials.

## Codex Skill Setup

Run these commands from a terminal:

```bash
cd /path/to/CodexResumeGeneration
bin/setup_env.sh
codex
```

Then, inside Codex, invoke the skill:

```text
$generate-application-package
```

Paste the job description when Codex asks for the application target.

If the virtual environment needs to be rebuilt:

```bash
cd /path/to/CodexResumeGeneration
bin/setup_env.sh --recreate
codex
```

This repo is currently designed for repo-local skill discovery. Starting Codex from another directory may prevent Codex from finding `.agents/skills/` or may cause repo-relative paths such as `GenFiles/profile.yml`, `GenFiles/cv.md`, and `bin/run_application_package.sh` to resolve incorrectly.

## How It Works

The full workflow starts inside Codex with a pasted job description. The `generate-application-package` skill turns that job description into:

1. `job_context.json`: company, role, location, job summary, match notes, tracker status, assumptions, and output naming.
2. `match_matrix.json`: mapping from role requirements to supported source evidence, selected projects, selected employment, skills, gaps, and strategy.
3. `resume.xml`: tailored resume content selected from `GenFiles/profile.yml` and `GenFiles/cv.md`.
4. `cover_letter.txt`: body-only cover-letter paragraphs. The generator adds the header, date, salutation, closing, and signature from the profile/template.

Codex then calls `bin/run_application_package.sh` to render the resume and cover letter PDFs, update `data/Application Tracker.txt`, write a generation report, delete temporary XML/TXT inputs under `GenFiles/tmp/` by default, and write an application package manifest. That script does not decide what to write in the resume or cover letter; it expects Codex-created inputs.

## Local Environment

Use Python 3.10 or newer. On macOS, install the native libraries required by WeasyPrint before running PDF generation.

Create the project virtual environment:

```bash
bin/setup_env.sh
```

Rebuild it from scratch if needed:

```bash
bin/setup_env.sh --recreate
```

Dependencies are listed in `requirements.txt`.

## Usage Notes

Use this repository from Codex CLI. Invoke the application package skill and paste the job description:

```text
$generate-application-package
```

The shell commands below are implementation details used by the skill, plus debugging and validation helpers. They are not the intended user-facing workflow for generating real application materials without Codex because they require already-written structured inputs.

Render a complete application package manually for debugging after Codex, or a developer, has already written the required input files:

```bash
bin/run_application_package.sh GenFiles/tmp/example_robotics/job_context.json GenFiles/tmp/example_robotics/resume.xml GenFiles/tmp/example_robotics/cover_letter.txt
```

Generate only a resume PDF manually for debugging:

```bash
bin/run_resume.sh examples/example_resume.xml examples/output/output.pdf --html-output examples/output/output.html
```

Generate only a cover-letter PDF manually for debugging:

```bash
bin/run_cover_letter.sh examples/example_cover_letter.txt examples/output/output.pdf --html-output examples/output/output.html
```

Validate inputs and generated package manifests:

```bash
bin/validate_resume.sh examples/example_resume.xml
bin/validate_cover_letter.sh examples/example_cover_letter.txt
bin/validate_match_matrix.sh examples/example_match_matrix.json --resume-xml examples/example_resume.xml
bin/validate_application_package.sh GenFiles/tmp/<OutputBasename>/application_package_manifest.json
```

Run the smoke tests:

```bash
bin/smoke_test_application_package.sh
bin/smoke_test_resume.sh
bin/smoke_test_cover_letter.sh
bin/smoke_test_validators.sh
```

## General Generation Workflow

1. Customize `GenFiles/profile.yml` and `GenFiles/cv.md` with real candidate information.
2. Start Codex CLI in this repository and invoke the `generate-application-package` skill.
3. Paste the job description when Codex asks for the application target.
4. Codex creates a temporary folder under `GenFiles/tmp/<company_slug>/`.
5. Codex writes `job_context.json`, `match_matrix.json`, `resume.xml`, and `cover_letter.txt`.
6. Codex runs the validators before rendering PDFs.
7. Codex runs `bin/run_application_package.sh` to generate PDFs, update the tracker, write the manifest, and clean temporary inputs.
8. Codex runs `bin/validate_application_package.sh` against the generated manifest.
9. Review the generated PDFs before submitting an application.

## Repository Notes

- Use Codex and the included skills for real generation work. Use shell wrappers only for validation, debugging, or smoke tests.
- Keep `GenFiles/profile.yml` and `GenFiles/cv.md` as the source of truth.
- Do not include metadata, greetings, dates, closings, signatures, or contact information in cover-letter TXT inputs.
- Do not fabricate candidate experience. Only use evidence from the profile and CV files.
- Generated PDFs, temporary files, local virtual environments, caches, and personal historical application materials should be excluded from a public repository.
