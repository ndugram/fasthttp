import subprocess
import sys
import time
from pathlib import Path


def get_example_files() -> list[Path]:
    examples_dir = Path(__file__).parent
    example_files = []

    for py_file in examples_dir.rglob("*.py"):
        if py_file.name == "run_all.py":
            continue

        if py_file.parent.name == "__pycache__":
            continue

        example_files.append(py_file)

    return sorted(example_files)


def run_example(example_file: Path) -> bool:
    print(f"\n{'='*80}")
    print(f"🚀 Running: {example_file.relative_to(Path(__file__).parent)}")
    print(f"{'='*80}\n")

    try:
        result = subprocess.run(
            [sys.executable, str(example_file)],
            cwd=example_file.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(result.stdout)

        if result.stderr:
            print(f"⚠️  stderr: {result.stderr}")

        if result.returncode == 0:
            print(f"✅ Success: {example_file.name}")
            return True
        print(f"❌ Failed: {example_file.name} (exit code: {result.returncode})")
        return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout: {example_file.name}")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {example_file.name} - {e}")
        return False


def run_all_examples(*, sequential: bool = True) -> None:
    example_files = get_example_files()

    if not example_files:
        print("No example files found!")
        return

    print(f"\n📋 Found {len(example_files)} example files\n")

    if sequential:
        print("Running examples sequentially...\n")

        successes = 0
        failures = 0

        for i, example_file in enumerate(example_files, 1):
            print(f"\n[{i}/{len(example_files)}] ", end="")

            if run_example(example_file):
                successes += 1
            else:
                failures += 1

            time.sleep(1)

        print(f"\n\n{'='*80}")
        print(f"📊 Summary: {successes} ✅ | {failures} ❌ | Total: {len(example_files)}")
        print(f"{'='*80}\n")

    else:
        print("Running examples in parallel...\n")
        print("Note: Output may be mixed when running in parallel.\n")

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {
                executor.submit(run_example, example_file): example_file
                for example_file in example_files
            }

            successes = 0
            failures = 0

            for future in concurrent.futures.as_completed(future_to_file):
                example_file = future_to_file[future]
                try:
                    if future.result():
                        successes += 1
                    else:
                        failures += 1
                except Exception as e:  # noqa: BLE001
                    print(f"❌ Error running {example_file}: {e}")
                    failures += 1

        print(f"\n\n{'='*80}")
        print(f"📊 Summary: {successes} ✅ | {failures} ❌ | Total: {len(example_files)}")
        print(f"{'='*80}\n")


def list_examples() -> None:
    example_files = get_example_files()

    if not example_files:
        print("No example files found!")
        return

    print(f"\n📋 Available examples ({len(example_files)}):\n")

    by_category = {}

    for example_file in example_files:
        category = example_file.parent.name
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(example_file.name)

    for category, files in sorted(by_category.items()):
        print(f"📁 {category}/")
        for file_name in sorted(files):
            print(f"   • {file_name}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "list":
            list_examples()
        elif command == "parallel":
            run_all_examples(sequential=False)
        elif command == "sequential":
            run_all_examples(sequential=True)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python run_all.py [list|sequential|parallel]")
            sys.exit(1)
    else:
        run_all_examples(sequential=True)
