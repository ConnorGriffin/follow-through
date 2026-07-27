# Draft launch post

## Title

Follow Through: personal AI memory that reviews what happened after the plan

## Draft

AI memory and the decision journal have mostly developed as separate ideas.
Memory systems try to help an assistant recall the facts around your life.
Decision journals preserve what you believed before an outcome makes the past
look obvious.

I wanted both.

I use AI for personal decisions and planning, but remembering context is not
enough. A useful assistant should be able to record why I chose something,
capture what I expect a plan to accomplish, return when evidence exists, and
compare the result with the prediction. It should not quietly turn one
experience into a permanent belief about me.

Follow Through is the open-source version of that workflow. It is an Agent Skill
for Claude Code and Codex backed by a private Markdown and Git repository. It
stores approved personal context, ADR-style decisions, plans, and append-only
outcomes. A validator checks schemas, links, the index, and legal status changes
through Git history.

The public example is deliberately synthetic. Its fictional user predicts that
a four-day-workweek trial will increase deep-work output by 25 percent. It
doesn't. The outcome records the miss, identifies plausible causes, ends the
trial, and declines to generalize from one event.

That failed prediction is the product. A memory system that only accumulates
facts can make an assistant more informed. Closing the loop can make its advice
more honest.

Repository: https://github.com/ConnorGriffin/follow-through
