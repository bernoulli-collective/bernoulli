---
name: applicant-encoder
description: Extract essential applicant data from resume, portfolio, and writing samples to populate the User model fields (pronouns, skill level, geolocation, roles, keywords, etc.). Outputs JSON for prototyping and direct DB insertion.
---

# Applicant Encoder

This skill processes applicant materials to extract structured data for the auto-apply workflow. It analyzes:
- Resume (PDF/text)
- Portfolio (PDF/website)
- Writing samples (links/files)
- Self-reported information

## Input

The skill expects a JSON file with basic applicant information (like `Yoyo.json`) containing:
- name
- email  
- pronouns
- geolocation
- skill_level
- resume_path
- portfolio_path
- public_links
- writing_samples
- private_writing_samples

## Processing Steps

1. **Resume Analysis**: Extract text from resume PDF, identify:
   - Technical keywords (programming languages, frameworks, tools)
   - Academic background (degrees, institutions)
   - Role indicators (titles, responsibilities)

2. **Portfolio Analysis**: Scan portfolio for:
   - Project descriptions and technologies used
   - Publications or research work
   - Code repositories links
   - Domain-specific keywords

3. **Writing Samples Review**: Analyze provided links for:
   - Technical depth indicators
   - Communication style assessment
   - Subject matter expertise

4. **Role Mapping**: Map extracted skills to role types:
   - AI and ML Engineering
   - Research Engineering  
   - Neuro Engineering
   - Software Engineering
   - Data Science

5. **Skill Level Assessment**: Determine appropriate level based on:
   - Educational background (e.g., undergraduate, graduate, PhD)
   - Years of experience indicators
   - Project complexity
   - Leadership indicators

## Output

Generates enhanced JSON with all User model fields populated, for example:

```json
{
  "id": 1,
  "name": "Ghosy Chan",
  "email": "ghosychan@gmail.com",
  "pronouns": "they/them",
  "geolocation": "Berkeley, CA",
  "skill_level": "internship",
  "roles": ["AI and ML Engineering", "Research Engineering", "Neuro Engineering"],
  "keywords": ["python", "pytorch", "tensorflow", "eeg", "bcI", "neural decoding", "machine learning", "data analysis", "signal processing"],
  "resume_text": "...extracted text...",
  "resume_path": "~/autoapply/data/Ghosy_Resume.pdf",
  "portfolio_url": "~/autoapply/data/Ghosy_Portfolio.pdf",
  "public_links": ["https://adiabatic.garden/", "https://github.com/exanova-y"],
  "writing_samples": [...],
  "private_writing_samples": []
}
```

## Usage

Run this skill when:
- Setting up a new applicant profile
- Updating existing applicant information
- Preparing for matching against job requirements

The output JSON can be:
1. Used directly for prototyping and testing
2. Inserted into the SQLite database via the setup workflow
3. Compared against job requirements for matching scores

## Integration

This skill feeds into:
- User profile completion in `/auto-apply setup`
- Keyword extraction for job matching
- Role-based filtering of opportunities
- Skill level appropriate application targeting
