---
name: sales-assessment-workflow
description: End-to-end workflow for arranging, scheduling, versioning, delivering, grading, recording, and repeating Slack-based sales assessments. Use when the user asks to create, run, check, or manage a sales exam or knowledge check; shuffle answer choices; schedule personal training-channel notifications; enforce thread submissions; calculate first-attempt KPI Training scores; issue results; or schedule retakes until 100%.
---

# Sales Assessment Workflow

Manage each assessment from advance notice through mastery. Treat Melbourne time, Slack thread placement, version-specific answer keys, and first-attempt KPI scoring as hard controls.

## Load supporting resources

- Read [references/slack-templates.md](references/slack-templates.md) before composing notices, reminders, exams, results, or retake messages.
- Read [references/record-schema.md](references/record-schema.md) before creating or updating assessment records.
- Use `scripts/shuffle_exam.py` when the source questions can be normalized to its JSON schema. Inspect its `--help` output before first use in a task.

## 1. Resolve the assessment scope

Confirm or discover:

- assessment name and source questions;
- original correct answers, selection rules, points, and total score;
- active candidates, locations, Slack user IDs, and personal training-channel IDs;
- Melbourne assessment date and time;
- each candidate's shift and next working day;
- where persistent assessment records should be stored.

Use the actual question count and point values. Never assume seven questions or one point per question.

Require the initial assessment to begin at least 30 minutes after the current Melbourne time. If the requested time is too soon, stop and ask for a later time.

## 2. Enforce the phone-call gate

Require a phone call before the initial Slack notice. Confirm that the salesperson was told:

- the Melbourne assessment time;
- the first-attempt KPI rule;
- the requirement to retake until 100%.

Do not claim to have made a call without a supported calling tool and explicit authorization. If no calling tool is available, ask the user to confirm that the call is complete, or record the unsuccessful call attempt if the user supplies that status.

Do not silently cancel or reschedule an assessment because a call was unanswered.

## 3. Send the advance Slack notice

Use the Slack workflow and re-resolve the destination before writing. Send a concise English notice to the candidate's personal training channel.

Require the notice to:

- begin with the real Slack user mention, not typed display-name text;
- state the date and Melbourne time;
- explain that the assessment helps the candidate fully understand company incentive policies so they do not miss any rewards or benefits they may be eligible to receive;
- include the exact first-attempt KPI and retake explanation from the template reference;
- require `Confirmed` in the notice thread.

Record the notice timestamp and permalink.

## 4. Schedule the confirmation check

Create a reliable follow-up for 30 minutes after the notice. Use the product's automation or monitoring mechanism; do not rely on conversational memory.

At the check:

- accept `Confirmed` only when it appears in the notice thread;
- record valid confirmation and stop the reminder path;
- if absent or posted elsewhere, send one reminder with a real Slack mention and direct the candidate to the original notice thread;
- record reminder and compliance status.

Do not treat a channel-level reply or another thread as valid confirmation.

## 5. Normalize and version the exam

Preserve:

- question wording and order;
- selection requirements;
- points and total score;
- substantive correct answers.

Shuffle only the answer-choice order. Recalculate answer letters from the new positions.

Create a traceable version for every distinct option order. A version may be assigned to one or more candidates only when the mapping is recorded explicitly. Create a new version for every retake.

Prefer `scripts/shuffle_exam.py` for deterministic generation. Verify the generated version against the source before scheduling it. Compare a retake with earlier attempts and regenerate if the option order is not materially different.

Persist:

- version ID;
- candidate and attempt number;
- complete shuffled questions;
- version-specific answer key;
- source-answer mapping;
- points and total score;
- scheduled time and channel.

Never expose answer keys in Slack.

## 6. Schedule the exam post

Schedule the version in the same personal training channel at the exact Melbourne time.

Require the exam post to:

- begin with the real Slack user mention;
- include all questions and selection instructions;
- require answers in the exam post's own thread;
- state that answers outside that thread will not be graded.

Before scheduling, verify candidate, channel, timestamp, version, question count, answer key, points, and absence of duplicate scheduled messages.

Create a follow-up monitor for the exam thread so a valid complete submission triggers grading without waiting for a new user instruction.

## 7. Validate the submission

Grade only a complete answer posted in the correct exam thread.

Reject as non-compliant:

- channel-level answers;
- answers in the advance-notice thread;
- answers in another message thread or channel;
- private-message submissions;
- incomplete answers;
- answers whose version cannot be resolved.

Notify the candidate of incorrect placement, record non-compliance, and require resubmission in the correct thread. Do not award a score for the misplaced answer.

## 8. Grade against the exact version

Before grading, resolve candidate, attempt number, exam message timestamp, version ID, version-specific key, question count, points, and submission compliance.

Apply these defaults unless the source assessment explicitly states otherwise:

- use source-defined points, or one point per question when no points are defined;
- award a single-select question only for the exact correct choice;
- award a multi-select question only for the exact correct set;
- award no partial credit for extra, missing, or incorrect selections.

Calculate percentage as:

`earned points / total possible points * 100`

Report attempt number, score, percentage, incorrect question numbers, candidate answers, correct version answers, concise targeted explanations, thread compliance, and retake requirement.

## 9. Record KPI correctly

For each assessment, freeze the first-attempt percentage as its KPI score. Never replace or modify it with a retake result.

Calculate the monthly KPI Training score from first-attempt percentages only:

`sum of each assessment's first-attempt percentage / number of assessments`

Do not use highest score, latest score, mastery score, retake average, or a mix of first attempts and retakes unless the user explicitly changes the policy.

## 10. Send results automatically

After a valid submission is graded, immediately send the English result message in the candidate's personal training channel.

- Use the real Slack mention.
- For 100%, state that all answers are correct and the assessment is complete.
- Below 100%, explain only incorrect questions, restate that the first attempt alone counts toward KPI, and give the next retake time.
- If thread placement was invalid, send the compliance message instead of a score.

Update the assessment record after sending.

## 11. Continue retakes until mastery

Stop only when the candidate reaches 100%.

When a valid attempt is below 100%:

1. determine one hour after grading/result time in Melbourne;
2. confirm that time falls within the candidate's shift;
3. if it does, schedule the retake then;
4. if the candidate has finished work or the time falls outside the shift, schedule the retake as the first task on the next working day;
5. if shift data is unavailable, obtain it rather than guessing;
6. send the retake notice and require `Confirmed` in its thread;
   - include the assessment-purpose statement from the retake template;
7. generate a new shuffled version and key;
8. schedule, monitor, grade, notify, and repeat until 100%.

Retakes demonstrate mastery only. Keep the first-attempt KPI score unchanged.

## 12. Maintain the audit trail

Use the record schema reference. Track every notice, confirmation, reminder, version, scheduled message, attempt, answer, score, explanation, compliance event, KPI value, retake, shift decision, and final mastery timestamp.

Use these statuses consistently:

- pending notice;
- phone notified;
- awaiting confirmation;
- confirmed;
- awaiting exam;
- awaiting submission;
- misplaced submission;
- awaiting grading;
- awaiting retake;
- retake in progress;
- deferred to next working day;
- mastered at 100%;
- absent.

## Final control checklist

Before completing any workflow step, confirm:

- Melbourne date and time are explicit;
- the initial exam has at least 30 minutes' lead time;
- phone status is recorded;
- Slack mention and channel are real and correct;
- confirmation and answer thread timestamps are known;
- option order and answer key match exactly;
- no duplicate scheduled message exists;
- the first-attempt KPI value is immutable;
- retakes continue until 100%;
- retakes do not fall outside the recorded shift.
