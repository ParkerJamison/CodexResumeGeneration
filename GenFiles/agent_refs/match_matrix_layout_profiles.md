# Match Matrix And Layout Profiles

Load this when generating `match_matrix.json` or choosing a resume layout
profile.

## Match Matrix

Write `GenFiles/tmp/<company_slug>/match_matrix.json` after `job_context.json`
and before `resume.xml` or `cover_letter.txt`. Use it as the planning source for
both artifacts; do not reselect projects from scratch after strong selections
are recorded.

Required top-level fields:

- `company`
- `role_title`
- `role_type`
- `location_or_remote`
- `layout_profile`
- `top_keywords`
- `top_requirements`
- `requirement_to_evidence`
- `selected_projects`
- `selected_employment`
- `selected_skills`
- `gaps`
- `gap_mitigation`
- `resume_strategy`
- `cover_letter_strategy`

Rules:

- Every evidence item must come from `GenFiles/cv.md` or `GenFiles/profile.yml`.
- If there is no strong evidence for a requirement, list it under `gaps`.
- `selected_projects` and `selected_employment` entries need `name`,
  `reason_selected`, and `priority`.

## Layout Profiles

- `focused_one_page`: default. Use for general, early-career, or narrow-fit
  roles. Target summary 2-3 lines, compact skills, 3 projects, 2 employment
  entries, compact education.
- `dense_one_page`: use when many experiences are relevant but one page is
  realistic, or the first render is underfilled. Target expanded skills, 3
  projects with 3-4 bullets, 2 employment entries, optional coursework/tools.
- `technical_extended`: use only when the role is highly aligned and forcing one
  page would remove strong technical evidence. Target 4 projects, 2-3 employment
  entries, expanded technical skills, and useful coursework; avoid sparse two
  page resumes.

All selected projects and employment entries still need at least three bullets.
