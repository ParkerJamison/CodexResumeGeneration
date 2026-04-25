# Resume and Cover Letter Agent Instructions

This repository generates tailored resume and cover letter PDFs from pasted job
descriptions using profile/CV sources, XML/TXT/JSON inputs, wrapper scripts,
validators, tracker updates, cleanup, and a manifest.

## Global Rules

- Source truth: `GenFiles/profile.yml` and `GenFiles/cv.md`.
- Do not fabricate experience, employers, credentials, dates, degrees, metrics,
  certifications, technologies, tools, or company claims.
- Prefer concrete source evidence over generic claims.
- Keep cover letters specific to the company and role.
- Preserve the candidate preferences defined in `GenFiles/profile.yml`, such as
  focus areas for AI/ML, automation, LLM applications, robotics, embedded
  systems, and developer tooling.
- Use wrapper scripts instead of direct Python unless inspecting/debugging.
- Validate outputs before reporting success; fix failures first.
- Keep progress updates concise and final reports compact.
- Path casing matters: use `GenFiles`, not `genFiles`.

## Skills

- Full package: `.agents/skills/generate-application-package/SKILL.md`
- Resume only: `.agents/skills/generate-resume-only/SKILL.md`
- Cover letter only: `.agents/skills/generate-cover-letter-only/SKILL.md`
- Validation/debugging: `.agents/skills/validate-application-package/SKILL.md`

Shared detailed rules live in `GenFiles/agent_refs/`; load only the referenced
file needed for the current skill step.

## Final Response

- `Created:` generated PDF path or paths
- `Tracker:` update status, when applicable
- `Cleanup:` temp input cleanup status, when applicable
- `Validation:` validators run and passed
- `Assumptions:` only material assumptions
