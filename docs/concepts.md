# Flagbase concepts
## Competition
A Competition is a single jeopardy-style CTF event. One instance of Flagbase
corresponds to one Competition.

## Challenge
A Challenge is a problem in a Competition. It either has a flag, or a grading
script. It has a fixed number of points.

## Team
A Team is a participant in a Competition. A Team can have multiple members, or
a single member. Flagbase does not keep track of team membership.

## ScoreAdjustment
Teams can score points in a Competition in two ways: they can either solve
Challenges, or have ScoreAdjustments set on them. ScoreAdjustments are
arbitrary point adjustments set by an AdminUser. They can be either positive or
negative.

## AdminUser
In the administrative interface, an AdminUser is an authorized user who can
perform certain maintenance actions on the Competition, Challenges, and Teams.
These actions can also be performed by the ctftool script, so an AdminUser can
also be considered someone with access to the database.
