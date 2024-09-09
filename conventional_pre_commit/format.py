import re
import os
from typing import List, Optional

CONVENTIONAL_TYPES = ["feat", "fix"]
DEFAULT_TYPES = [
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
]
AUTOSQUASH_PREFIXES = [
    "amend",
    "fixup",
    "squash",
]


def r_types(types):
    """Join types with pipe "|" to form regex ORs."""
    return "|".join(types)


def _get_scope_pattern(scopes: Optional[List[str]] = None):
    scopes_str = r_types(scopes)
    escaped_delimiters = list(map(re.escape, [":", ",", "-", "/"]))  # type: ignore
    delimiters_pattern = r_types(escaped_delimiters)
    return rf"\(\s*(?:{scopes_str})(?:\s*(?:{delimiters_pattern})\s*(?:{scopes_str}))*\s*\)"


def r_scope(optional=True, scopes: Optional[List[str]] = None):
    """Regex str for an optional (scope)."""

    if scopes:
        scopes_pattern = _get_scope_pattern(scopes)
        return scopes_pattern

    if optional:
        return r"(\([\w \/:,-]+\))?"
    else:
        return r"(\([\w \/:,-]+\))"


def r_delim():
    """Regex str for optional breaking change indicator and colon delimiter."""
    return r"!?:"


def r_subject():
    """Regex str for subject line."""
    return r" .+$"


def r_body():
    """Regex str for the body"""
    return r"(?P<multi>\r?\n(?P<sep>^$\r?\n)?.+)?"


def r_autosquash_prefixes():
    """Regex str for autosquash prefixes."""
    return "|".join(AUTOSQUASH_PREFIXES)


def r_verbose_commit_ignored():
    """Regex str for the ignored part of verbose commit message templates"""
    return r"^# -{24} >8 -{24}\r?\n.*\Z"


def strip_verbose_commit_ignored(input):
    """Strip the ignored part of verbose commit message templates."""
    return re.sub(r_verbose_commit_ignored(), "", input, flags=re.DOTALL | re.MULTILINE)


def r_comment():
    """Regex str for comment"""
    return r"^#.*\r?\n?"


def strip_comments(input):
    return re.sub(r_comment(), "", input, flags=re.MULTILINE)


def conventional_types(types=[]):
    """Return a list of Conventional Commits types merged with the given types."""
    if set(types) & set(CONVENTIONAL_TYPES) == set():
        return CONVENTIONAL_TYPES + types
    return types


def get_git_directory():
    submodule_git_dir = os.path.join(os.getcwd(), '.git')

    if os.path.isfile(submodule_git_dir):
        with open(submodule_git_dir, 'r') as f:
            content = f.read().strip()
            if content.startswith('gitdir: '):
                git_dir = content.split('gitdir: ')[1]
                return os.path.abspath(git_dir)
    elif os.path.isdir(submodule_git_dir):
        return submodule_git_dir
    else:
        print("Não foi possível encontrar o diretório Git.")
        return None


def check_git_status(git_dir):
    if os.path.exists(os.path.join(git_dir, 'MERGE_HEAD')):
        print("Current stage: MERGE")
        return True
    elif os.path.exists(os.path.join(git_dir, 'CHERRY_PICK_HEAD')):
        return False
    elif os.path.exists(os.path.join(git_dir, 'REBASE_HEAD')):
        print("Current stage: REBASE")
        return False
    elif os.path.exists(os.path.join(git_dir, 'BISECT_LOG')):
        return False
    else:
        print("Current stage: COMMIT")
        return False


def get_current_branch(git_dir):
    """
    Obtém o nome da branch atual.
    """
    head_file = os.path.join(git_dir, 'HEAD')

    if os.path.exists(head_file):
        with open(head_file, 'r') as f:
            ref = f.read().strip()
            if ref.startswith('ref:'):
                # Extrair o nome da branch da referência
                return ref.split('refs/heads/')[-1]
            else:
                return "DETACHED HEAD"
    else:
        return "HEAD file not found"

def is_main_branch():
    git_directory = get_git_directory()
    current_branch = get_current_branch(git_directory)
    if current_branch == 'main':
        print(f"Current Branch: {current_branch}")
        return True

def is_merge_commit():
    git_directory = get_git_directory()

    if git_directory:
      return check_git_status(git_directory)

    return False

def is_conventional(input, types=DEFAULT_TYPES, optional_scope=True, scopes: Optional[List[str]] = None):
    """
    Returns True if input matches Conventional Commits formatting
    https://www.conventionalcommits.org

    Optionally provide a list of additional custom types.
    """
    input = strip_verbose_commit_ignored(input)
    input = strip_comments(input)
    types = conventional_types(types)
    pattern = f"^({r_types(types)}){r_scope(optional_scope, scopes=scopes)}{r_delim()}{r_subject()}{r_body()}"
    regex = re.compile(pattern, re.MULTILINE)

    result = regex.match(input)
    is_valid = bool(result)
    if is_valid and result.group("multi") and not result.group("sep"):
        is_valid = False

    return is_valid


def has_autosquash_prefix(input):
    """
    Returns True if input starts with one of the autosquash prefixes used in git.
    See the documentation, please https://git-scm.com/docs/git-rebase.

    It doesn't check whether the rest of the input matches Conventional Commits
    formatting.
    """
    pattern = f"^(({r_autosquash_prefixes()})! ).*$"
    regex = re.compile(pattern, re.DOTALL)

    return bool(regex.match(input))
