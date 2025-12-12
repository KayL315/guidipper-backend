import difflib
from typing import Optional, List

from unidiff import PatchSet


def generate_diff(original_text: str, modified_text: str) -> str:
    original_lines = original_text.splitlines(keepends=True)
    modified_lines = modified_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original_tour_plan.txt",
        tofile="modified_tour_plan.txt",
        lineterm="",
        n=3,
    )

    diff_text = "\n".join(diff)
    return diff_text


def _apply_single_file_patch(src_lines: List[str], diff_text: str) -> Optional[str]:
    """
    Apply a unified diff to a single text blob using unidiff for correctness.
    Returns the patched text or None if the patch cannot be applied.
    """
    try:
        patch = PatchSet(diff_text.splitlines(True))
    except Exception as exc:
        print("❌ Failed to parse diff:", exc)
        return None

    if not patch:
        print("⚠️ Empty patch; nothing to apply.")
        return "".join(src_lines)

    if len(patch) > 1:
        print("⚠️ Patch contains multiple files; only the first one will be applied.")

    file_patch = patch[0]
    lines = list(src_lines)
    new_lines: List[str] = []
    cursor = 0  # current index in original lines

    for hunk in file_patch:
        # Copy unchanged lines before this hunk
        target_start = hunk.source_start - 1  # convert to 0-based
        if target_start < cursor:
            print("❌ Overlapping or out-of-order hunk; aborting patch.")
            return None

        new_lines.extend(lines[cursor:target_start])
        cursor = target_start

        # Apply hunk
        for line in hunk:
            if line.is_context:
                if cursor >= len(lines) or lines[cursor].rstrip("\n") != line.value.rstrip("\n"):
                    print("❌ Context mismatch while applying patch; aborting.")
                    return None
                new_lines.append(lines[cursor])
                cursor += 1
            elif line.is_removed:
                if cursor >= len(lines) or lines[cursor].rstrip("\n") != line.value.rstrip("\n"):
                    print("❌ Removal mismatch while applying patch; aborting.")
                    return None
                cursor += 1  # skip the removed line
            elif line.is_added:
                # Added lines are inserted into the output
                new_lines.append(line.value if line.value.endswith("\n") else line.value + "\n")

    # Append remaining original lines after last hunk
    new_lines.extend(lines[cursor:])
    return "".join(new_lines)


def apply_diff(original_text: str, diff_text: str) -> Optional[str]:
    """
    Apply a unified diff to the original text.
    Returns patched text or None if the patch fails. Falls back to a lenient
    best-effort apply when strict parsing fails, to avoid hard failures from
    slightly malformed hunks.
    """
    try:
        strict_result = _apply_single_file_patch(original_text.splitlines(True), diff_text)
        if strict_result is not None:
            return strict_result

        # Fallback: lenient apply (ignores hunk headers and line counts).
        print("⚠️ Falling back to best-effort diff apply due to parse/match failure.")
        be_result = _apply_best_effort(original_text, diff_text)
        if be_result is not None:
            return be_result

        # Last resort: if diff only provides additions, treat the added lines as the new plan
        extracted = _extract_added_only(diff_text)
        if extracted is not None:
            print("⚠️ Using added-lines-only fallback (could not apply diff accurately).")
            return extracted
        return None
    except Exception as exc:
        print(f"❌ Error applying diff: {exc}")
        return None


def _apply_best_effort(original_text: str, diff_text: str) -> Optional[str]:
    """
    A permissive diff apply:
    - Ignores file headers/hunk headers.
    - Tries to track position using context lines.
    - Removes the first matching line at/after the cursor for '-' entries.
    - Inserts '+' entries at the current cursor to avoid dumping them at the end.
    This is to avoid hard failures on imperfect AI-generated diffs.
    """
    try:
        lines = original_text.splitlines(keepends=True)
        output = list(lines)
        cursor = 0  # current position in output we try to stay near
        changed = False

        for raw in diff_text.splitlines():
            if raw.startswith(("---", "+++", "@@")):
                continue
            if not raw:
                continue
            if raw[0] == "-":
                target = raw[1:]
                # find first line matching (ignore trailing newline)
                for idx in range(cursor, len(output)):
                    if output[idx].rstrip("\n") == target.rstrip("\n"):
                        output.pop(idx)
                        cursor = idx
                        changed = True
                        break
            elif raw[0] == "+":
                to_add = raw[1:]
                if not to_add.endswith("\n"):
                    to_add += "\n"
                output.insert(cursor, to_add)
                cursor += 1
                changed = True
            else:
                # context line: try to advance cursor to the next matching line
                for idx in range(cursor, len(output)):
                    if output[idx].rstrip("\n") == raw.rstrip("\n"):
                        cursor = idx + 1
                        break

        return "".join(output) if changed else None
    except Exception as exc:
        print(f"❌ Best-effort apply failed: {exc}")
        return None


def _extract_added_only(diff_text: str) -> Optional[str]:
    """
    If the diff is too malformed, but it contains added lines,
    fall back to using only the '+' lines (excluding file headers).
    """
    added = []
    for raw in diff_text.splitlines():
        if raw.startswith("+++"):
            continue
        if raw.startswith("+"):
            line = raw[1:]
            added.append(line if line.endswith("\n") else line + "\n")
    if added:
        return "".join(added)
    return None
