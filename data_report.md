# Redrob Dataset EDA Report

Generated from the local Redrob challenge bundle. This is data analysis only; no model training or ranking model construction is included.

## Dataset Inventory

- Candidate records: 100,000
- Main data file: `[PUB] India_runs_data_and_ai_challenge/.../candidates.jsonl`
- Schema file: `candidate_schema.json`
- Job context: `job_description.docx`, Senior AI Engineer, Redrob AI founding team
- Submission format reference: `sample_submission.csv`

## Target Columns

The candidate dataset itself does not contain supervised ground-truth target labels. The challenge output target is a ranked list for the job description. The sample submission defines these output columns:

| Column | Role | Notes |
|---|---|---|
| `candidate_id` | identifier/key | Candidate to rank. Present in input and output. |
| `rank` | target output | Integer rank order in final submission. Not present as a training label. |
| `score` | target output | Ranking confidence/relevance score. Not present as a training label. |
| `reasoning` | target output | Human-readable justification for the rank. Not present as a training label. |

Implication: this is primarily an unsupervised/rules/evaluation-driven candidate ranking problem unless external labels are added later.

## Column Groups

### Text Features

- `profile.headline`, `profile.summary`
- `profile.location`, `profile.country`, `profile.current_title`, `profile.current_company`, `profile.current_industry`
- `career_history[].company`, `career_history[].title`, `career_history[].industry`, `career_history[].description`
- `education[].institution`, `education[].degree`, `education[].field_of_study`, `education[].grade`, `education[].tier`
- `skills[].name`, `skills[].proficiency`
- `certifications[].name`, `certifications[].issuer`
- `languages[].language`, `languages[].proficiency`

### Numerical Features

- `profile.years_of_experience`
- `career_history[].duration_months`
- `education[].start_year`, `education[].end_year`
- `skills[].endorsements`, `skills[].duration_months`
- `certifications[].year`
- `redrob_signals.profile_completeness_score`
- `redrob_signals.profile_views_received_30d`
- `redrob_signals.applications_submitted_30d`
- `redrob_signals.recruiter_response_rate`
- `redrob_signals.avg_response_time_hours`
- `redrob_signals.skill_assessment_scores.<dynamic_key>`
- `redrob_signals.connection_count`
- `redrob_signals.endorsements_received`
- `redrob_signals.notice_period_days`
- `redrob_signals.expected_salary_range_inr_lpa.min`
- `redrob_signals.expected_salary_range_inr_lpa.max`
- `redrob_signals.github_activity_score`
- `redrob_signals.search_appearance_30d`
- `redrob_signals.saved_by_recruiters_30d`
- `redrob_signals.interview_completion_rate`
- `redrob_signals.offer_acceptance_rate`
- Derived counts: number of jobs, education entries, skills, certifications, languages, completed assessments
- Derived aggregates: total skill endorsements, max/mean skill duration, career tenure summaries, salary midpoint/spread

### Behavioral Signals

All behavioral signals live under `redrob_signals`:
- `redrob_signals.profile_completeness_score` (number)
- `redrob_signals.signup_date` (string)
- `redrob_signals.last_active_date` (string)
- `redrob_signals.open_to_work_flag` (boolean)
- `redrob_signals.profile_views_received_30d` (integer)
- `redrob_signals.applications_submitted_30d` (integer)
- `redrob_signals.recruiter_response_rate` (number)
- `redrob_signals.avg_response_time_hours` (number)
- `redrob_signals.skill_assessment_scores.<dynamic_key>` (number)
- `redrob_signals.connection_count` (integer)
- `redrob_signals.endorsements_received` (integer)
- `redrob_signals.notice_period_days` (integer)
- `redrob_signals.expected_salary_range_inr_lpa` (object)
- `redrob_signals.expected_salary_range_inr_lpa.min` (number)
- `redrob_signals.expected_salary_range_inr_lpa.max` (number)
- `redrob_signals.preferred_work_mode` (string)
- `redrob_signals.willing_to_relocate` (boolean)
- `redrob_signals.github_activity_score` (number)
- `redrob_signals.search_appearance_30d` (integer)
- `redrob_signals.saved_by_recruiters_30d` (integer)
- `redrob_signals.interview_completion_rate` (number)
- `redrob_signals.offer_acceptance_rate` (number)
- `redrob_signals.verified_email` (boolean)
- `redrob_signals.verified_phone` (boolean)
- `redrob_signals.linkedin_connected` (boolean)

### Career Features

- Profile/current role: title, company, company size, industry, location, country, years of experience
- Career history: company, title, dates, duration, current flag, industry, company size, role description
- Education: institution, degree, field, years, grade, institution tier
- Skills: skill name, proficiency, endorsements, duration
- Certifications and languages

## All Schema Columns

| Path | Type | Feature Group | Description / Values |
|---|---:|---|---|
| `candidate_id` | `string` | categorical | Unique identifier for the candidate. Format: CAND_XXXXXXX (7 digits). |
| `profile` | `object` | career/profile feature, nested structure |  |
| `profile.anonymized_name` | `string` | career/profile feature, text/categorical | Anonymized full name. |
| `profile.headline` | `string` | career/profile feature, text/categorical | One-line professional headline. |
| `profile.summary` | `string` | career/profile feature, text/categorical | Multi-sentence professional summary. |
| `profile.location` | `string` | career/profile feature, text/categorical | City, region/state. |
| `profile.country` | `string` | career/profile feature, text/categorical |  |
| `profile.years_of_experience` | `number` | career/profile feature, numerical |  |
| `profile.current_title` | `string` | career/profile feature, text/categorical |  |
| `profile.current_company` | `string` | career/profile feature, text/categorical |  |
| `profile.current_company_size` | `string` | career/profile feature, text/categorical | values: `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+` |
| `profile.current_industry` | `string` | career/profile feature, text/categorical |  |
| `career_history` | `array` | career/profile feature, nested structure |  |
| `career_history[]` | `object` | career/profile feature, nested structure |  |
| `career_history[].company` | `string` | career/profile feature, text/categorical |  |
| `career_history[].title` | `string` | career/profile feature, text/categorical |  |
| `career_history[].start_date` | `string` | career/profile feature, categorical |  |
| `career_history[].end_date` | `string|null` | career/profile feature, categorical |  |
| `career_history[].duration_months` | `integer` | career/profile feature, numerical |  |
| `career_history[].is_current` | `boolean` | career/profile feature, boolean/categorical |  |
| `career_history[].industry` | `string` | career/profile feature, text/categorical |  |
| `career_history[].company_size` | `string` | career/profile feature, text/categorical | values: `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+` |
| `career_history[].description` | `string` | career/profile feature, text/categorical | Role responsibilities and achievements. |
| `education` | `array` | career/profile feature, nested structure |  |
| `education[]` | `object` | career/profile feature, nested structure |  |
| `education[].institution` | `string` | career/profile feature, text/categorical |  |
| `education[].degree` | `string` | career/profile feature, text/categorical |  |
| `education[].field_of_study` | `string` | career/profile feature, text/categorical |  |
| `education[].start_year` | `integer` | career/profile feature, numerical |  |
| `education[].end_year` | `integer` | career/profile feature, numerical |  |
| `education[].grade` | `string|null` | career/profile feature, text/categorical | GPA / percentage / class. |
| `education[].tier` | `string` | career/profile feature, categorical | values: `tier_1`, `tier_2`, `tier_3`, `tier_4`, `unknown`; Internal tiering for institution prestige. |
| `skills` | `array` | career/profile feature, nested structure |  |
| `skills[]` | `object` | career/profile feature, nested structure |  |
| `skills[].name` | `string` | career/profile feature, text/categorical |  |
| `skills[].proficiency` | `string` | career/profile feature, categorical | values: `beginner`, `intermediate`, `advanced`, `expert` |
| `skills[].endorsements` | `integer` | career/profile feature, numerical |  |
| `skills[].duration_months` | `integer` | career/profile feature, numerical | Months the candidate has used this skill |
| `certifications` | `array` | career/profile feature, nested structure |  |
| `certifications[]` | `object` | career/profile feature, nested structure |  |
| `certifications[].name` | `string` | career/profile feature, text/categorical |  |
| `certifications[].issuer` | `string` | career/profile feature, text/categorical |  |
| `certifications[].year` | `integer` | career/profile feature, numerical |  |
| `languages` | `array` | career/profile feature, nested structure |  |
| `languages[]` | `object` | career/profile feature, nested structure |  |
| `languages[].language` | `string` | career/profile feature, text/categorical |  |
| `languages[].proficiency` | `string` | career/profile feature, categorical | values: `basic`, `conversational`, `professional`, `native` |
| `redrob_signals` | `object` | behavioral signal, nested structure | Simulated platform activity and engagement signals from the Redrob ecosystem. |
| `redrob_signals.profile_completeness_score` | `number` | behavioral signal, numerical | Percentage of profile completeness. |
| `redrob_signals.signup_date` | `string` | behavioral signal, categorical |  |
| `redrob_signals.last_active_date` | `string` | behavioral signal, categorical |  |
| `redrob_signals.open_to_work_flag` | `boolean` | behavioral signal, boolean/categorical |  |
| `redrob_signals.profile_views_received_30d` | `integer` | behavioral signal, numerical |  |
| `redrob_signals.applications_submitted_30d` | `integer` | behavioral signal, numerical |  |
| `redrob_signals.recruiter_response_rate` | `number` | behavioral signal, numerical | Fraction of recruiter messages the candidate has responded to. |
| `redrob_signals.avg_response_time_hours` | `number` | behavioral signal, numerical |  |
| `redrob_signals.skill_assessment_scores` | `object` | behavioral signal, nested structure | Dict of skill_name -> score 0-100. Assessments completed on Redrob platform. |
| `redrob_signals.skill_assessment_scores.<dynamic_key>` | `number` | behavioral signal, numerical |  |
| `redrob_signals.connection_count` | `integer` | behavioral signal, numerical |  |
| `redrob_signals.endorsements_received` | `integer` | behavioral signal, numerical |  |
| `redrob_signals.notice_period_days` | `integer` | behavioral signal, numerical |  |
| `redrob_signals.expected_salary_range_inr_lpa` | `object` | behavioral signal, nested structure | Expected salary in INR Lakhs Per Annum. |
| `redrob_signals.expected_salary_range_inr_lpa.min` | `number` | behavioral signal, numerical |  |
| `redrob_signals.expected_salary_range_inr_lpa.max` | `number` | behavioral signal, numerical |  |
| `redrob_signals.preferred_work_mode` | `string` | behavioral signal, categorical | values: `remote`, `hybrid`, `onsite`, `flexible` |
| `redrob_signals.willing_to_relocate` | `boolean` | behavioral signal, boolean/categorical |  |
| `redrob_signals.github_activity_score` | `number` | behavioral signal, numerical | 0-100 score based on commits, PRs, stars in last 12 months. -1 if no GitHub linked. |
| `redrob_signals.search_appearance_30d` | `integer` | behavioral signal, numerical | Number of times profile appeared in recruiter searches in last 30 days. |
| `redrob_signals.saved_by_recruiters_30d` | `integer` | behavioral signal, numerical | Number of recruiters who saved this profile in last 30 days. |
| `redrob_signals.interview_completion_rate` | `number` | behavioral signal, numerical | Fraction of scheduled interviews actually attended. |
| `redrob_signals.offer_acceptance_rate` | `number` | behavioral signal, numerical | Historical offer acceptance rate. -1 if no offer history. |
| `redrob_signals.verified_email` | `boolean` | behavioral signal, boolean/categorical |  |
| `redrob_signals.verified_phone` | `boolean` | behavioral signal, boolean/categorical |  |
| `redrob_signals.linkedin_connected` | `boolean` | behavioral signal, boolean/categorical |  |

## High-Level Distributions

| Collection | Min | Mean | Median | Max | Empty Count | Most Common Lengths |
|---|---:|---:|---:|---:|---:|---|
| `career_history` | 1 | 3.00 | 3.0 | 9 | 0 | 2: 24,186, 3: 22,126, 1: 18,508, 4: 17,131, 5: 11,469 |
| `education` | 1 | 1.40 | 1.0 | 2 | 0 | 1: 60,222, 2: 39,778 |
| `skills` | 5 | 9.60 | 9.0 | 23 | 0 | 10: 14,107, 9: 13,512, 8: 12,961, 7: 12,369, 6: 11,279 |
| `certifications` | 0 | 0.37 | 0.0 | 3 | 75,019 | 0: 75,019, 2: 12,495, 1: 12,482, 3: 4 |
| `languages` | 2 | 2.00 | 2.0 | 2 | 0 | 2: 100,000 |

## Selected Scalar Summaries

| Column | Non-null | Missing | Summary |
|---|---:|---:|---|
| `profile.years_of_experience` | 100,000 | 0 | min 1.00, median 6.80, mean 7.17, max 16.90 |
| `profile.country` | 100,000 | 0 | India: 75,113, USA: 9,978, Australia: 2,579, Canada: 2,506, UK: 2,472, Germany: 2,469 |
| `profile.current_title` | 100,000 | 0 | Business Analyst: 5,833, HR Manager: 5,830, Mechanical Engineer: 5,791, Accountant: 5,764, Project Manager: 5,754, Customer Support: 5,750 |
| `profile.current_industry` | 100,000 | 0 | IT Services: 29,881, Software: 22,417, Manufacturing: 22,305, Conglomerate: 7,571, Paper Products: 7,467, Fintech: 2,808 |
| `redrob_signals.profile_completeness_score` | 100,000 | 0 | min 25.00, median 56.80, mean 56.76, max 99.90 |
| `redrob_signals.open_to_work_flag` | 100,000 | 0 | False: 64,661, True: 35,339 |
| `redrob_signals.profile_views_received_30d` | 100,000 | 0 | min 0.00, median 45.00, mean 47.99, max 374.00 |
| `redrob_signals.applications_submitted_30d` | 100,000 | 0 | min 0.00, median 5.00, mean 5.39, max 24.00 |
| `redrob_signals.recruiter_response_rate` | 100,000 | 0 | min 0.02, median 0.44, mean 0.44, max 0.95 |
| `redrob_signals.avg_response_time_hours` | 100,000 | 0 | min 2.10, median 129.90, mean 132.70, max 280.00 |
| `redrob_signals.connection_count` | 100,000 | 0 | min 10.00, median 335.00, mean 345.66, max 1898.00 |
| `redrob_signals.endorsements_received` | 100,000 | 0 | min 0.00, median 28.00, mean 30.07, max 242.00 |
| `redrob_signals.notice_period_days` | 100,000 | 0 | min 0.00, median 90.00, mean 87.39, max 150.00 |
| `redrob_signals.expected_salary_range_inr_lpa.min` | 100,000 | 0 | min 3.00, median 11.90, mean 12.17, max 49.70 |
| `redrob_signals.expected_salary_range_inr_lpa.max` | 100,000 | 0 | min 6.00, median 19.40, mean 19.84, max 74.50 |
| `redrob_signals.preferred_work_mode` | 100,000 | 0 | hybrid: 25,076, onsite: 25,000, flexible: 25,000, remote: 24,924 |
| `redrob_signals.willing_to_relocate` | 100,000 | 0 | False: 71,196, True: 28,804 |
| `redrob_signals.github_activity_score` | 100,000 | 0 | min -1.00, median -1.00, mean 9.62, max 96.90 |
| `redrob_signals.search_appearance_30d` | 100,000 | 0 | min 0.00, median 105.00, mean 117.54, max 1490.00 |
| `redrob_signals.saved_by_recruiters_30d` | 100,000 | 0 | min 0.00, median 7.00, mean 7.66, max 80.00 |
| `redrob_signals.interview_completion_rate` | 100,000 | 0 | min 0.30, median 0.62, mean 0.62, max 1.00 |
| `redrob_signals.offer_acceptance_rate` | 100,000 | 0 | min -1.00, median -1.00, mean -0.40, max 0.93 |
| `redrob_signals.verified_email` | 100,000 | 0 | True: 72,003, False: 27,997 |
| `redrob_signals.verified_phone` | 100,000 | 0 | True: 61,789, False: 38,211 |
| `redrob_signals.linkedin_connected` | 100,000 | 0 | False: 64,001, True: 35,999 |

## Top Nested Values

- Career titles: Business Analyst: 19,042, Graphic Designer: 19,018, Project Manager: 19,016, Mechanical Engineer: 18,992, Accountant: 18,955, Civil Engineer: 18,882, HR Manager: 18,875, Customer Support: 18,842, Operations Manager: 18,799, Marketing Manager: 18,793
- Career industries: IT Services: 88,077, Software: 70,746, Manufacturing: 70,541, Conglomerate: 23,556, Paper Products: 23,416, Fintech: 6,513, Food Delivery: 5,902, E-commerce: 3,644, Consulting: 2,871, EdTech: 1,384
- Education degrees: M.E.: 17,650, M.S.: 17,604, M.Sc: 17,562, M.Tech: 17,535, Ph.D: 17,526, B.Tech: 17,465, B.E.: 17,259, B.Sc: 17,177
- Education fields: Information Technology: 12,328, Data Science: 12,222, Machine Learning: 12,216, Computer Engineering: 12,114, Artificial Intelligence: 12,009, Computer Science: 11,868, Statistics: 6,762, Chemical Engineering: 6,740, Electronics: 6,726, Physics: 6,726
- Education tiers: tier_3: 53,220, tier_4: 51,885, tier_2: 27,821, tier_1: 6,852
- Skill names: HTML: 12,246, Databricks: 12,244, Redux: 12,222, Terraform: 12,187, Angular: 12,173, Figma: 12,157, Salesforce CRM: 12,157, Vue.js: 12,142, Sales: 12,138, Accounting: 12,136
- Skill proficiencies: intermediate: 470,309, beginner: 379,097, advanced: 109,585, expert: 1,311
- Assessment skill names: YOLO: 1,195, Feature Engineering: 1,174, CNN: 1,174, Weights & Biases: 1,173, Forecasting: 1,167, Speech Recognition: 1,159, MLOps: 1,159, BentoML: 1,157, OpenCV: 1,155, Data Science: 1,147
- Languages: English: 100,000, Hindi: 100,000
- Certification names: AWS Certified Cloud Practitioner: 12,499, Six Sigma Green Belt: 12,280, Scrum Master Certified: 12,147, AWS Certified Machine Learning Specialty: 131, Deep Learning Specialization: 111, Google Cloud Professional ML Engineer: 111, NLP Specialization: 105, LangChain for LLM Application Development: 100

## Data Quality Notes

- Duplicate `candidate_id` values: 0
- Records without a current career item: 0
- Salary ranges with min greater than max: 18,865
- Records where `last_active_date` is before `signup_date`: 7,496
- `github_activity_score = -1` sentinel/no GitHub linked: 64,637
- `offer_acceptance_rate = -1` sentinel/no offer history: 59,554

## EDA Recommendations Before Modeling

- Treat nested arrays as first-class sources: aggregate skills, career history, education, certifications, languages, and assessment dictionaries into interpretable features.
- Preserve text fields for later semantic matching against the Senior AI Engineer job description.
- Keep behavioral signals separate from profile fit signals at first so availability/engagement does not overwhelm skill relevance.
- Handle sentinel values explicitly: `github_activity_score = -1` and `offer_acceptance_rate = -1` mean missing/no history, not low performance.
- Audit generated-data inconsistencies before feature engineering, especially salary min/max inversions and active-date anomalies.
- Do not treat sample submission ranks/scores as labels; they are format examples only.
