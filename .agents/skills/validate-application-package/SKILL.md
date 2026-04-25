---
name: validate-application-package
description: "Validate generated resume and cover letter application package artifacts in this repository, including manifest PDFs, tracker/cleanup status, cover letter metadata leakage, and resume bullet-count rules."
---

# Validate Application Package

Use this for validation, debugging, or audit requests.

Load only what is needed:

- Validation commands, tracker, cleanup, reporting:
  `GenFiles/agent_refs/cli_contracts.md`
- Match matrix and layout profile semantics:
  `GenFiles/agent_refs/match_matrix_layout_profiles.md`
- Resume validation semantics: `GenFiles/agent_refs/resume_rules.md`
- Cover letter leakage semantics: `GenFiles/agent_refs/cover_letter_rules.md`

Run existing validators first:

```bash
bin/validate_match_matrix.sh path/to/match_matrix.json --resume-xml path/to/resume.xml
bin/validate_resume.sh path/to/resume.xml
bin/validate_cover_letter.sh path/to/cover_letter.txt
bin/validate_cover_letter.sh path/to/rendered_cover_letter.html
bin/validate_application_package.sh path/to/application_package_manifest.json
```

If a validator fails, report the exact failure and what source artifact must be
fixed before the package can be considered complete.
