---
name: generate-resume-only
description: "Generate only a tailored resume XML and PDF for this repository from a job description, using GenFiles/profile.yml and GenFiles/cv.md, the resume wrapper, and resume validation."
---

# Generate Resume Only

Use this only for resume-only requests.

Load only what is needed:

- Drafting content: `GenFiles/agent_refs/source_grounding.md`
- Choosing a layout profile: `GenFiles/agent_refs/match_matrix_layout_profiles.md`
- Resume structure and tailoring: `GenFiles/agent_refs/resume_rules.md`
- Commands and validation: `GenFiles/agent_refs/cli_contracts.md`

## Workflow

1. Choose a layout profile before drafting.
2. Write tailored XML under `GenFiles/tmp/<company_slug>/resume.xml`, using
   `examples/example_resume.xml` as the shape reference.
3. Validate when available:

   ```bash
   bin/validate_resume.sh GenFiles/tmp/<company_slug>/resume.xml
   ```

4. Generate through the wrapper:

   ```bash
   bin/run_resume.sh GenFiles/tmp/<company_slug>/resume.xml output.pdf --html-output output.html
   ```

5. If validation or generation fails, fix the XML and rerun before reporting.
