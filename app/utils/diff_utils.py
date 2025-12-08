import difflib
from typing import Optional

def generate_diff(original_text: str, modified_text: str) -> str:
    original_lines = original_text.splitlines(keepends=True)
    modified_lines = modified_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile='original_tour_plan.txt',
        tofile='modified_tour_plan.txt',
        lineterm='',
        n=3
    )

    diff_text = '\n'.join(diff)
    return diff_text

def apply_diff(original_text: str, diff_text: str) -> Optional[str]:
    try:
        lines = original_text.splitlines(keepends=True)

        for line in diff_text.split('\n'):
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                continue
            elif line.startswith('-'):
                original_line = line[1:]
                if original_line in lines:
                    lines.remove(original_line)
            elif line.startswith('+'):
                new_line = line[1:]
                original_line_index = None

                next_original_line = None
                for i, l in enumerate(lines):
                    if i > 0:
                        next_original_line = lines[i - 1] if i > 0 else None

                for i, l in enumerate(lines):
                    if l.rstrip() == new_line.rstrip():
                        if i < len(lines) - 1:
                            original_line_index = i
                            break

                if original_line_index is not None:
                    lines.insert(original_line_index, new_line + '\n')
                else:
                    lines.append(new_line + '\n')

        return ''.join(lines)

    except Exception as e:
        print(f"❌ Error applying diff: {e}")
        return None
