# Перебираем все назначения: у каждой задачи один исполнитель a_i.
# h_i — часы задачи, p_ij — предпочтение участника j к задаче i.
# Загрузка L_j = COMMON_HOURS + сумма h_i для задач, где a_i = j.
# Отбрасываем назначения с L_j > LIMIT.
# Из оставшихся выбираем максимум F = сумма h_i * p_i,a_i.

import csv
from itertools import product
from pathlib import Path

LIMIT = 15
COMMON_HOURS = 3
ROOT = Path(__file__).resolve().parent

with (ROOT / "tasks.csv").open(encoding="utf-8", newline="") as file:
    tasks: list[dict[str, str]] = list(csv.DictReader(file))

with (ROOT / "preferences.csv").open(encoding="utf-8", newline="") as file:
    rows: list[dict[str, str]] = list(csv.DictReader(file))

people = [name for name in rows[0] if name != "task_id"]
hours = [int(task["hours"]) for task in tasks]
preferences = {row["task_id"]: [int(row[person]) for person in people] for row in rows}
scores = [preferences[task["id"]] for task in tasks]


def workloads(assignment: tuple[int, ...]) -> list[int]:
    loads = [COMMON_HOURS] * len(people)
    for duration, person in zip(hours, assignment):
        loads[person] += duration
    return loads


def task_score(duration: int, preference: int) -> int:
    return duration * preference


best_score = -1
best_assignment: tuple[int, ...] | None = None
feasible_count = 0

for assignment in product(range(len(people)), repeat=len(tasks)):
    if max(workloads(assignment)) > LIMIT:
        continue

    feasible_count += 1
    score = sum(
        task_score(duration, preference[person])
        for duration, preference, person in zip(hours, scores, assignment)
    )

    if score > best_score:
        best_score = score
        best_assignment = assignment

if best_assignment is None:
    raise SystemExit("Нет распределения, удовлетворяющего ограничениям")

result = ROOT / "result.csv"

with result.open("w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["task_id", "title", "hours", "assignee", "preference", "score"])

    for task, duration, preference, person in zip(
        tasks, hours, scores, best_assignment
    ):
        writer.writerow(
            [
                task["id"],
                task["title"],
                duration,
                people[person],
                preference[person],
                task_score(duration, preference[person]),
            ]
        )
        print(f"{task['id']}  {people[person]:12}  {duration} ч  {task['title']}")

print(f"\nЦелевая функция: {best_score}")
print(f"Допустимых распределений: {feasible_count}")

for name, load in zip(people, workloads(best_assignment)):
    print(f"{name}: {load - COMMON_HOURS} + {COMMON_HOURS} = {load} ч")

print(f"\nРезультат: {result.relative_to(ROOT)}")
