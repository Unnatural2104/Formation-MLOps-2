"""Architecture test: every to_csv call must explicitly set index=False."""

import ast
from pathlib import Path


def _iter_python_files(root_dir: Path) -> list[Path]:
    excluded_dirs = {"tests", "venv", ".venv", ".git", "__pycache__"}
    files: list[Path] = []

    for path in root_dir.rglob("*.py"):
        rel = path.relative_to(root_dir)
        if any(part in excluded_dirs for part in rel.parts):
            continue
        files.append(path)

    return sorted(files)


def _is_to_csv_call(node: ast.Call) -> bool:
    return isinstance(node.func, ast.Attribute) and node.func.attr == "to_csv"


def _has_index_false_keyword(node: ast.Call) -> bool:
    for keyword in node.keywords:
        if keyword.arg == "index" and isinstance(keyword.value, ast.Constant):
            return keyword.value.value is False
    return False


class _ToCsvIndexVisitor(ast.NodeVisitor):
    def __init__(self, root_dir: Path, file_path: Path) -> None:
        self._root_dir = root_dir
        self._file_path = file_path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        if _is_to_csv_call(node) and not _has_index_false_keyword(node):
            rel = self._file_path.relative_to(self._root_dir)
            self.violations.append(
                f"{rel}:{node.lineno}:{node.col_offset} -> to_csv(..., index=False) requis"
            )
        self.generic_visit(node)


def test_all_to_csv_calls_use_index_false() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    violations: list[str] = []

    for file_path in _iter_python_files(root_dir):
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        visitor = _ToCsvIndexVisitor(root_dir=root_dir, file_path=file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)

    assert not violations, "\n".join([
        "Appels to_csv sans index=False explicite:",
        *violations,
    ])
