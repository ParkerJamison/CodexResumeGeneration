## Environment bootstrap

Create or rebuild the project virtual environment with a non-Conda Python 3.10+
interpreter:

```bash
bin/setup_env.sh
bin/setup_env.sh --recreate
```

## Resume generation

Preferred one-command workflow:

```bash
bin/run_application_package.sh job_context.json resume.xml cover_letter.txt
```

Reference input file:

- `examples/example_job_context.json` for the shared job context JSON
- `examples/example_match_matrix.json` for the pre-generation match matrix JSON

What `run_application_package.sh` does:

- uses `.venv/bin/python` explicitly
- refuses to run if the `.venv` is based on Anaconda
- sets `DYLD_FALLBACK_LIBRARY_PATH` for Homebrew macOS libraries
- sets Fontconfig paths and a writable cache directory
- runs `src/generateApplicationPackage.py`
- validates `match_matrix.json` next to `job_context.json`
- generates both PDFs
- updates `data/Application Tracker.txt`
- deletes temp XML/TXT inputs under `GenFiles/tmp/` unless `--keep-inputs` is set
- writes a manifest JSON file

Output path conventions:

- temp inputs: `GenFiles/tmp/<CompanySlug>/`
- final artifact paths are recorded in the generated manifest
- default PDFs: `GenCoverLetters/<CompanySlug>-Resume.pdf` and
  `GenCoverLetters/<CompanySlug>-Cover-Letter.pdf`
- use `--resume-output` and `--cover-letter-output` only when a different output
  path is required

Validate a generated package manifest:

```bash
bin/validate_application_package.sh GenFiles/tmp/<OutputBasename>/application_package_manifest.json
```

Preferred command:

```bash
bin/run_resume.sh input.xml output.pdf --html-output output.html
```

Example:

```bash
bin/run_resume.sh examples/example_resume.xml examples/output/output.pdf --html-output examples/output/output.html
```

Validate tailored resume XML before generation:

```bash
bin/validate_resume.sh examples/example_resume.xml
bin/validate_match_matrix.sh examples/example_match_matrix.json --resume-xml examples/example_resume.xml
```

What `run_resume.sh` does:

- uses `.venv/bin/python` explicitly
- refuses to run if the `.venv` is based on Anaconda
- sets `DYLD_FALLBACK_LIBRARY_PATH` for Homebrew macOS libraries
- sets Fontconfig paths and a writable cache directory
- runs `src/generateResume.py`

## Cover letter generation

Preferred command:

```bash
bin/run_cover_letter.sh input.txt output.pdf --html-output output.html
```

Example:

```bash
bin/run_cover_letter.sh examples/example_cover_letter.txt examples/output/output.pdf --html-output examples/output/output.html
```

Validate cover letter source text or rendered HTML:

```bash
bin/validate_cover_letter.sh examples/example_cover_letter.txt
bin/validate_cover_letter.sh examples/output/output.html
```

What `run_cover_letter.sh` does:

- uses `.venv/bin/python` explicitly
- refuses to run if the `.venv` is based on Anaconda
- sets `DYLD_FALLBACK_LIBRARY_PATH` for Homebrew macOS libraries
- sets Fontconfig paths and a writable cache directory
- runs `src/generateCoverLetter.py`

## Smoke test

Use these to verify the checked-in samples:

```bash
bin/smoke_test_application_package.sh
bin/smoke_test_resume.sh
bin/smoke_test_cover_letter.sh
bin/smoke_test_validators.sh
```

Reference input files:

- `examples/example_resume.xml` for resume XML generation
- `examples/example_cover_letter.txt` for body-only cover letter TXT generation

## Dependencies

Project Python dependencies are recorded in:

```bash
requirements.txt
```

Install them into the project `.venv` with:

```bash
bin/setup_env.sh
```
