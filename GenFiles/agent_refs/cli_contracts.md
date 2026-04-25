# CLI Contracts

Load this when running generation, validation, tracker, cleanup, or reporting.

## Commands

Use wrappers instead of direct Python unless debugging a script:

```bash
bin/run_application_package.sh GenFiles/tmp/<company_slug>/job_context.json GenFiles/tmp/<company_slug>/resume.xml GenFiles/tmp/<company_slug>/cover_letter.txt
bin/run_resume.sh input.xml output.pdf --html-output output.html
bin/run_cover_letter.sh input.txt output.pdf --html-output output.html
```

Default package PDFs are written to `GenCoverLetters/<OutputBasename>-Resume.pdf`
and `GenCoverLetters/<OutputBasename>-Cover-Letter.pdf`.

Use validators when present:

```bash
bin/validate_resume.sh path/to/resume.xml
bin/validate_match_matrix.sh path/to/match_matrix.json --resume-xml path/to/resume.xml
bin/validate_cover_letter.sh path/to/cover_letter.txt
bin/validate_cover_letter.sh path/to/rendered_cover_letter.html
bin/validate_application_package.sh path/to/application_package_manifest.json
```

## Tracker And Cleanup

- Update `data/Application Tracker.txt` only through the package workflow or
  tracker script.
- Use the manifest as the source of truth for final artifact paths, tracker
  status, cleanup status, validation status, and assumptions.
- After successful generation, delete only temporary XML/TXT inputs under
  `GenFiles/tmp/`; do not delete generated PDFs or source files.
- If generation or validation fails, keep temporary inputs for diagnosis.
