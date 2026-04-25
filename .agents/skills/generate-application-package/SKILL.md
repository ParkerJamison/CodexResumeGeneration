---
name: generate-application-package
description: "Generate a full tailored application package from a pasted job description: job_context.json, resume XML/PDF, cover letter TXT/PDF, tracker update, cleanup, manifest review, validation, and final artifact reporting for this repository."
---

# Generate Application Package

Use this for the full resume + cover letter workflow.

Load only what is needed:

- Drafting job/resume/letter content: `GenFiles/agent_refs/source_grounding.md`
- Creating match matrix and choosing layout profile:
  `GenFiles/agent_refs/match_matrix_layout_profiles.md`
- Writing resume XML: `GenFiles/agent_refs/resume_rules.md`
- Writing cover letter TXT: `GenFiles/agent_refs/cover_letter_rules.md`
- Running commands, validation, tracker, cleanup, reporting:
  `GenFiles/agent_refs/cli_contracts.md`

## Workflow

1. Create `GenFiles/tmp/<company_slug>/`.
2. Write `job_context.json`.
3. Write `match_matrix.json` and choose `layout_profile`.
4. Write `resume.xml` and body-only `cover_letter.txt` using the match matrix
   and layout profile. Do not put cover-letter metadata, greeting, date,
   closing, signature, or header/contact information in the TXT.
5. Preflight when validators exist:

   ```bash
   bin/validate_match_matrix.sh GenFiles/tmp/<company_slug>/match_matrix.json --resume-xml GenFiles/tmp/<company_slug>/resume.xml
   bin/validate_resume.sh GenFiles/tmp/<company_slug>/resume.xml
   bin/validate_cover_letter.sh GenFiles/tmp/<company_slug>/cover_letter.txt
   ```

6. Generate through the package wrapper:

   ```bash
   bin/run_application_package.sh GenFiles/tmp/<company_slug>/job_context.json GenFiles/tmp/<company_slug>/resume.xml GenFiles/tmp/<company_slug>/cover_letter.txt
   ```

7. Read the manifest from stdout or
   `GenFiles/tmp/<OutputBasename>/application_package_manifest.json`.
8. Run `bin/validate_application_package.sh <manifest>`.
9. If validation fails, fix XML/TXT/JSON and regenerate. Report success only
   after generation and validation pass.
