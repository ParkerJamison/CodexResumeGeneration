---
name: generate-cover-letter-only
description: "Generate only a tailored cover letter TXT and PDF for this repository from a job description, using source profile/CV data, the cover letter wrapper, and metadata leakage validation."
---

# Generate Cover Letter Only

Use this only for cover-letter-only requests.

Load only what is needed:

- Drafting content: `GenFiles/agent_refs/source_grounding.md`
- Cover letter format and leakage rules:
  `GenFiles/agent_refs/cover_letter_rules.md`
- Commands and validation: `GenFiles/agent_refs/cli_contracts.md`

## Workflow

1. Write tailored body-only TXT under
   `GenFiles/tmp/<company_slug>/cover_letter.txt`, using
   `examples/example_cover_letter.txt` as the format reference. Do not write
   metadata, greeting, date, closing, signature, or header/contact information.
2. Validate when available:

   ```bash
   bin/validate_cover_letter.sh GenFiles/tmp/<company_slug>/cover_letter.txt
   ```

3. Generate through the wrapper:

   ```bash
   bin/run_cover_letter.sh GenFiles/tmp/<company_slug>/cover_letter.txt output.pdf --html-output output.html
   ```

4. Validate rendered HTML when written:

   ```bash
   bin/validate_cover_letter.sh output.html
   ```

5. If validation or generation fails, fix the TXT and rerun before reporting.
