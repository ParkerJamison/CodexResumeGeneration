# Source Grounding

Load this when drafting resume, cover letter, or job context content.

- Use `GenFiles/profile.yml` and `GenFiles/cv.md` as the source of truth.
- Use concrete CV evidence before generic claims.
- Do not fabricate experience, employers, credentials, dates, degrees, tools,
  technologies, metrics, certifications, or company claims.
- Preserve the candidate preferences defined in `GenFiles/profile.yml`, such as
  focus areas for AI/ML, automation, LLM applications, robotics, embedded
  systems, and developer tooling.
- Extract from the job description when present: company, role, location/remote
  status, responsibilities, required/preferred skills, ATS keywords,
  constraints, compensation, job URL, and job ID.
- Ask for the company name only if missing. Proceed without inventing other
  missing details.
- Use `examples/example_job_context.json`, `examples/example_match_matrix.json`,
  `examples/example_resume.xml`, and `examples/example_cover_letter.txt` as
  shape references.
- `examples/example_cover_letter.txt` is body-only; the generator supplies
  header, date, salutation, closing, and signature.
