# Cover Letter Rules

Load this when writing or revising tailored cover letter TXT.

- Write in the candidate's voice using evidence from `GenFiles/cv.md`.
- Address the company and role directly when known.
- Open with a specific reason the role fits the candidate's background.
- Highlight two or three supported proof points from the CV.
- Connect the candidate's experience to the company's stated needs.
- Stay concise, professional, and non-generic.
- Do not include unsupported praise or company claims.
- The TXT source must contain body paragraphs only.
- Do not include header/contact information, date, greeting/salutation, closing,
  signature, recipient metadata, or template-control text in the TXT source.
- The Python generator supplies the candidate header/contact line from
  `GenFiles/profile.yml`, the current date, `Dear Hiring Team,`, `Sincerely,`,
  and the candidate's signature.
- Metadata keys must never appear in the TXT source or rendered output:
  `company:`, `role:`, `location:`, `date:`, `salutation:`,
  `recipient_name:`, `recipient_title:`, `closing:`, `signature:`.
