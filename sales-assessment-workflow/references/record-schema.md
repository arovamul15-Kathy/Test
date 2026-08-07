# Assessment record schema

Maintain one assessment record per candidate and link every attempt to a version.

## Candidate assessment record

```yaml
assessment_id: string
assessment_name: string
candidate:
  name: string
  slack_user_id: string
  training_channel_id: string
  location: string
timezone: Australia/Melbourne
shift:
  assessment_day_start: datetime|null
  assessment_day_end: datetime|null
  next_working_day_start: datetime|null
phone:
  attempted_at: datetime|null
  connected: boolean|null
  verbally_confirmed: boolean|null
notice:
  message_ts: string|null
  permalink: string|null
  sent_at: datetime|null
  confirmed_in_thread: boolean
  confirmed_at: datetime|null
  reminder_sent_at: datetime|null
first_attempt_kpi_percentage: number|null
mastered: boolean
mastered_at: datetime|null
status: string
attempts: []
```

## Attempt record

```yaml
attempt_number: integer
attempt_type: first_attempt|retake
version_id: string
scheduled_at: datetime
exam_message_ts: string|null
exam_permalink: string|null
submission_message_ts: string|null
submitted_in_correct_thread: boolean
submitted_answers: object|null
earned_points: number|null
total_points: number
percentage: number|null
incorrect_questions: []
result_message_ts: string|null
result_sent_at: datetime|null
retake_scheduled_at: datetime|null
retake_deferred_reason: string|null
```

## Version record

```yaml
version_id: string
assessment_id: string
candidate_name: string
attempt_number: integer
source_question_count: integer
total_points: number
questions:
  - number: integer
    prompt: string
    points: number
    shuffled_options: []
    correct_letters: []
    source_index_order: []
created_at: datetime
```

Freeze `first_attempt_kpi_percentage` after attempt 1. Never update it from a retake.
