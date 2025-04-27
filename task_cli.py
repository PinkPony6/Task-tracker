#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone


class ActionNotSupported(Exception):
    """Raised when the input value is not in ['add', 'update', 'delete']"""
    pass


class IdNotFound(Exception):
    """Raised when the task id does not exist"""
    pass


class AddCommandNotCorrect(Exception):
    """Raised when the `add` command is not complete"""
    pass


class UpdateCommandNotCorrect(Exception):
    """Raised when the `update` command is not complete"""
    pass


class StatusUnknown(Exception):
    """Raised when the `status` is unknown"""
    pass


def add_task(task_description):
    now_dt = datetime.now(timezone.utc)
    new_task = {
        'id': 0,
        'description': task_description,
        'status': 'todo',
        'createdAt': now_dt.isoformat(),
        'updatedAt': now_dt.isoformat()
    }
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

        tasks["count"] += 1
        new_task["id"] = tasks["count"]
        tasks["tasks"].append(new_task)

        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    except FileNotFoundError:
        with open("tasks.json", "w") as f:
            tasks = {"tasks": [], "count": 1}
            new_task["id"] = tasks["count"]
            tasks["tasks"].append(new_task)

            json.dump(tasks, f)


def update(task_id, task_description):
    now_dt = datetime.now(timezone.utc)
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

            id_exists = False
            for task in tasks["tasks"]:
                if task.get("id") == task_id:
                    id_exists = True
                    task["description"] = task_description
                    task["updatedAt"] = now_dt.isoformat()
            if not id_exists:
                raise IdNotFound

        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    except FileNotFoundError:
        print("File not found. To create file please add task first.")
    except IdNotFound:
        print("No such id. List tasks to see what's available.")


def list_tasks():
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)
            for task in tasks["tasks"]:
                print(task)

    except FileNotFoundError:
        print("File not found. To create file please add task first.")


def list_by_status(status):
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)
            tasks_to_list = []
            for task in tasks["tasks"]:
                if task["status"] == status:
                    tasks_to_list.append(task)
            if not tasks_to_list:
                print(f'No tasks with status "{status}".')
            else:
                for task in tasks_to_list:
                    print(task)

    except FileNotFoundError:
        print("File not found. To create file please add task first.")


def delete_task(task_id):
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

            id_exists = False
            for idx in range(len(tasks["tasks"])):
                if tasks["tasks"][idx]["id"] == task_id:
                    id_exists = True
                    del tasks["tasks"][idx]
                    if len(tasks["tasks"]) == 0:
                        tasks["count"] = 0
                    break
            if not id_exists:
                raise IdNotFound

        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    except FileNotFoundError:
        print("File not found. To create file please add task first.")
    except IdNotFound:
        print("No such id. List tasks to see what's available.")


def update_status(task_id, command):
    if command == "mark-in-progress":
        status = "in-progress"
    else:
        status = "done"

    now_dt = datetime.now(timezone.utc)
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

            id_exists = False
            for task in tasks["tasks"]:
                if task.get("id") == task_id:
                    id_exists = True
                    task["status"] = status
                    task["updatedAt"] = now_dt.isoformat()

            if not id_exists:
                raise IdNotFound

        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    except FileNotFoundError:
        print("File not found. To create file please add task first.")
    except IdNotFound:
        print("No such id. List tasks to see what's available.")


def print_help():
    help_text = """
    Usage: ./task_cli.py <command> [options]

    A simple task tracker CLI.

    Commands:
      add <description>           Add a new task. Requires a description.
      list [status]               List all pending tasks.
      update <id> <description>   Updates task description. Requires the task ID.
      delete <id>                 Delete task from the list. Requires the task ID.
      mark-in-progress <id>       Set task status to "in-progress".
      mark-done <id>              Set task status to "done".
      help                        Show this help message.

    Examples:
      ./task_cli.py add "Buy milk"
      ./task_cli.py list
      ./task_cli.py mark-done 1
      ./task_cli.py update 2 "Fix the dinner"
      ./task_cli.py help
    """
    print(help_text)


def main():
    try:
        command = sys.argv[1] if len(sys.argv) > 1 else None
        print(sys.argv)

        if command.lower() not in ['add', 'update', 'list', 'delete', 'mark-in-progress', 'mark-done', 'help']:
            raise ActionNotSupported

        if command.lower() == "add":
            if len(sys.argv) > 2:
                task_description = " ".join(sys.argv[2:])
                add_task(task_description)
            else:
                raise AddCommandNotCorrect
        elif command.lower() == "update":
            if len(sys.argv) >= 3:
                task_id = int(sys.argv[2])
                task_description = " ".join(sys.argv[3:])
                update(task_id, task_description)
            else:
                raise UpdateCommandNotCorrect
        elif command.lower() == "list":
            if len(sys.argv) == 3:
                status = sys.argv[2]
                if status not in ["todo", "in-progress", "done"]:
                    raise StatusUnknown
                list_by_status(status)
            elif len(sys.argv) == 2:
                list_tasks()
            else:
                raise ActionNotSupported
        elif command.lower() == "delete":
            task_id = int(sys.argv[2])
            delete_task(task_id)
        elif command.lower() in ["mark-in-progress", "mark-done"]:
            task_id = int(sys.argv[2])
            update_status(task_id, command)
        elif command.lower() == "help":
            print_help()

    except AddCommandNotCorrect:
        print("Error: Please provide a task description.")
    except UpdateCommandNotCorrect:
        print("Error: Please provide a task id or description.")
    except ActionNotSupported:
        print("Please choose the action.")
    except StatusUnknown:
        print('Choose status from: "todo", "in-progress", "done".')
    except Exception:
        print("Something went wrong. Please check your input.")


if __name__ == '__main__':
    main()
