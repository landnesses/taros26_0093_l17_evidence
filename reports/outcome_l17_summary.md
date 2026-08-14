# Outcome-Annotated L17 Summary

- annotated tasks: 20
- success: 8
- fail: 10
- partial-score failures: 2

## Outcome Means

| outcome | tasks | mean best burst p99 | mean robust z | mean gripper events |
| --- | ---: | ---: | ---: | ---: |
| success | 8 | 5260.8 | 9.11 | 2.50 |
| partial | 2 | 6976.0 | 12.57 | 11.00 |
| fail | 10 | 5157.9 | 8.84 | 5.70 |

## Strongest L17 Bursts

| rank | task | outcome | chunk | p99 | robust z | events | prompt |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | FruitsMovingTask | fail | 39 | 7685.4 | 13.50 | 3 | Move an orange to the white bowl |
| 2 | BowlInBinTask | success | 7 | 7594.9 | 11.31 | 1 | put the bowl in the grey bin |
| 3 | PutTwoMugsOnShelfTask | partial | 49 | 7232.0 | 12.29 | 8 | Put two (2) mugs on the wire shelf |
| 4 | BananaInBowlTask | success | 31 | 6826.9 | 6.99 | 4 | Pick up the banana and place it in the bowl |
| 5 | NonHammerToolsInRightBinTask | fail | 58 | 6725.4 | 7.18 | 21 | Put the non-hammer tools in the right bin |
| 6 | HammersInLeftBinTask | partial | 145 | 6720.0 | 12.84 | 14 | Put the red hammer and black hammer in the left bin |
| 7 | BananasInCrateTask | success | 6 | 6565.4 | 6.37 | 2 | Put 2 bananas in the crate |
| 8 | FoodPackingByColorTask | fail | 120 | 6400.0 | 11.00 | 13 | Pack yellow objects in right container and blue object in the left container |
| 9 | WhiteMugsInBinTask | fail | 24 | 6144.0 | 10.54 | 4 | Clean up the white mugs |
| 10 | CannedFoodInBinTask | fail | 16 | 6122.9 | 15.56 | 6 | Put the canned food in the grey bin |
| 11 | CookingClearPlateTask | success | 22 | 5413.4 | 14.65 | 4 | Put the two measuring cups outside of the plate |
| 12 | YogurtInBowlTask | fail | 25 | 5056.0 | 4.77 | 2 | Put the small red yogurt in the red bowl |

## All Tasks

| task | outcome | chunks | events | best burst chunk | reason | p99 | robust z | prompt |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| BananaInBowlTask | success | 39 | 4 | 31 | gripper_window | 6826.9 | 6.99 | Pick up the banana and place it in the bowl |
| RubiksCubeTask | success | 10 | 1 | 7 | gripper_window | 4320.0 | 5.16 | Put the cube in the bowl |
| BowlInBinTask | success | 12 | 1 | 7 | gripper_window | 7594.9 | 11.31 | put the bowl in the grey bin |
| CannedFoodInBinTask | fail | 60 | 6 | 16 | gripper_window | 6122.9 | 15.56 | Put the canned food in the grey bin |
| FoodPacking1CansTask | fail | 60 | 1 | 5 | gripper_window | 2738.7 | 6.53 | Pack canned foods into the bin |
| YogurtInBowlTask | fail | 40 | 2 | 25 | l17_peak | 5056.0 | 4.77 | Put the small red yogurt in the red bowl |
| SauceBottlesCrateTask | fail | 40 | 5 | 31 | gripper_window | 4128.0 | 7.36 | Put the red bbq sauce bottle in the crate |
| FruitsMovingTask | fail | 60 | 3 | 39 | gripper_window | 7685.4 | 13.50 | Move an orange to the white bowl |
| BananasInCrateTask | success | 16 | 2 | 6 | gripper_window | 6565.4 | 6.37 | Put 2 bananas in the crate |
| FoodPackingByColorTask | fail | 120 | 13 | 120 | l17_peak | 6400.0 | 11.00 | Pack yellow objects in right container and blue object in the left container |
| FruitsOrangesOnPlateTask | success | 13 | 2 | 11 | gripper_window | 3696.0 | 12.23 | Put all the oranges on the plate |
| HammersInLeftBinTask | partial | 180 | 14 | 145 | l17_peak | 6720.0 | 12.84 | Put the red hammer and black hammer in the left bin |
| NonHammerToolsInRightBinTask | fail | 180 | 21 | 58 | gripper_window | 6725.4 | 7.18 | Put the non-hammer tools in the right bin |
| PutTwoMugsOnShelfTask | partial | 180 | 8 | 49 | gripper_window | 7232.0 | 12.29 | Put two (2) mugs on the wire shelf |
| CookingClearPlateTask | success | 74 | 4 | 22 | l17_peak | 5413.4 | 14.65 | Put the two measuring cups outside of the plate |
| WhiteMugsInBinTask | fail | 60 | 4 | 24 | gripper_window | 6144.0 | 10.54 | Clean up the white mugs |
| MarkerInMugTask | fail | 40 | 1 | 2 | l17_peak | 2496.0 | 4.36 | Put the whiteboard marker in the mug |
| SpoonInMugTask | fail | 60 | 1 | 14 | gripper_window | 4082.7 | 7.57 | Put the metal spoon that's in the wooden bowl in the mug |
| TakeMeasuringSpoonOutTask | success | 39 | 4 | 39 | gripper_window | 2768.0 | 6.40 | Take the white colored measuring spoon out of the red bowl and put it on the table. |
| StackYellowOnRedTask | success | 28 | 2 | 21 | gripper_window | 4901.4 | 9.80 | Stack the yellow block on the red block |

## Files

- `task_summary_with_outcomes.csv` joins prompt-level L17 metrics with the experiment summary you provided.
- Each `task_*` folder contains `l17_task_phase_overview.png`, chunk summaries, event CSVs, burst CSVs, and a short markdown report.
