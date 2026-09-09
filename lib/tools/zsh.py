# lib/tools/zsh.py
"""Zsh shell stack: zsh, modern CLI tools, plugins, ~/.zshrc (symlinked).

Ubuntu packages every one of these, so apt covers the whole list -- including
the two zsh plugins, which land in /usr/share instead of Homebrew's prefix
(.zshrc looks in both). Two of them install under a different command name
than the rest of the world uses, and get shimmed onto PATH: see lib/apt.py.

Making zsh the login shell has two paths on Linux. `chsh` is the real one,
but it writes /etc/passwd, so it cannot move an account that lives in a
directory service (Active Directory via centrifydc/sssd, LDAP). Those
accounts get a hand-off block appended to ~/.bashrc instead: see
_handoff_block.
"""
from __future__ import annotations

import os
import pwd
import shutil
from pathlib import Path

from lib import core
from lib.core import Link, Tool

# Debian renames these two binaries to dodge package-name collisions.
_RENAMED = (("bat", "batcat"), ("fd", "fdfind"))

_HANDOFF_BEGIN = "# >>> dotfiles: zsh hand-off >>>"
_HANDOFF_END = "# <<< dotfiles: zsh hand-off <<<"


def _bashrc() -> Path:
    return Path.home() / ".bashrc"


def _handoff_block(zsh_path: str) -> str:
    """The ~/.bashrc block that execs zsh, as a full text block.

    Interactive shells only, and never from inside zsh -- zsh does not read
    ~/.bashrc, so the exec cannot loop, but the guard also keeps `bash -c`
    and scp/rsync sessions on bash where they belong. If the exec fails the
    shell simply carries on as bash.
    """
    return (
        f"{_HANDOFF_BEGIN}\n"
        "# chsh cannot change the login shell of a directory-managed account\n"
        "# (the user is not in /etc/passwd), so bash hands off to zsh here.\n"
        "# Remove this block with: ./install.py uninstall zsh\n"
        "case $- in\n"
        "  *i*)\n"
        f"    if [ -z \"$ZSH_VERSION\" ] && [ -x {zsh_path} ]; then\n"
        f"      exec {zsh_path} -l\n"
        "    fi\n"
        "    ;;\n"
        "esac\n"
        f"{_HANDOFF_END}\n"
    )


def _strip_handoff(text: str) -> str:
    """Return `text` with any hand-off block (and its trailing blank line)
    removed. Unmarked text is returned unchanged."""
    if _HANDOFF_BEGIN not in text:
        return text
    out, skipping = [], False
    for line in text.splitlines(keepends=True):
        if line.startswith(_HANDOFF_BEGIN):
            skipping = True
            continue
        if skipping:
            skipping = not line.startswith(_HANDOFF_END)
            continue
        out.append(line)
    return "".join(out).rstrip("\n") + "\n" if out else ""


def install_handoff(zsh_path: str) -> None:
    """Append (or refresh) the zsh hand-off block in ~/.bashrc."""
    rc = _bashrc()
    old = rc.read_text() if rc.exists() else ""
    block = _handoff_block(zsh_path)
    if block in old:
        core.ok(f"~/.bashrc already hands off to {zsh_path}.")
        return
    body = _strip_handoff(old)
    if body and not body.endswith("\n"):
        body += "\n"
    rc.write_text(f"{body}\n{block}" if body else block)
    core.ok(f"~/.bashrc now execs {zsh_path} for interactive shells. "
            "Open a new terminal to pick it up.")


def remove_handoff() -> None:
    rc = _bashrc()
    if not rc.exists():
        return
    old = rc.read_text()
    new = _strip_handoff(old)
    if new != old:
        rc.write_text(new)
        core.ok("Removed the zsh hand-off block from ~/.bashrc.")


def login_shell() -> str:
    """This account's login shell, from the passwd database rather than
    $SHELL -- a directory-managed account is not in /etc/passwd, and $SHELL
    goes stale the moment chsh succeeds."""
    try:
        return pwd.getpwuid(os.getuid()).pw_shell
    except KeyError:
        return os.environ.get("SHELL", "")


def is_local_account() -> bool:
    """True when this user has a line in /etc/passwd, i.e. chsh can move
    them. False for AD/LDAP accounts served by centrifydc, sssd or winbind."""
    try:
        name = pwd.getpwuid(os.getuid()).pw_name
        lines = Path("/etc/passwd").read_text().splitlines()
    except (KeyError, OSError):
        return True  # Cannot tell -- let chsh speak for itself.
    return any(line.startswith(f"{name}:") for line in lines)


def _set_login_shell(zsh_path: str) -> None:
    if os.path.basename(login_shell()) == "zsh":
        core.ok("zsh is already the login shell.")
        remove_handoff()
        return

    if not is_local_account():
        core.info("Account is directory-managed (not in /etc/passwd), so "
                  "chsh cannot move it — using a ~/.bashrc hand-off instead.")
        install_handoff(zsh_path)
        return

    core.info("Setting zsh as login shell (chsh asks for your password)...")
    result = core.run(["chsh", "-s", zsh_path], check=False)
    if result.returncode == 0:
        core.ok(f"Login shell set to {zsh_path}. Takes effect on next login.")
        remove_handoff()
        return
    core.warn(f"chsh failed — falling back to a ~/.bashrc hand-off. To do it "
              f"properly instead: chsh -s {zsh_path}")
    install_handoff(zsh_path)


def _linux_post() -> None:
    """Linux only: PATH shims for Debian's renamed binaries, then make zsh
    the shell that interactive terminals actually land in."""
    if core.detect_os() != "linux":
        return
    from lib import apt

    for name, packaged in _RENAMED:
        apt.shim(name, packaged)
    apt.warn_if_local_bin_not_on_path()

    zsh_path = shutil.which("zsh")
    if zsh_path is None:
        core.warn("zsh not found after install — skipping login-shell change.")
        return
    _set_login_shell(zsh_path)


def _linux_uninstall() -> None:
    if core.detect_os() != "linux":
        return
    from lib import apt
    for name, _ in _RENAMED:
        apt.unshim(name)
    remove_handoff()


TOOL = Tool(
    name="zsh",
    doc="Zsh + CLI tools + plugins + .zshrc",
    platforms=frozenset({"macos", "linux"}),
    brew=("bat", "eza", "fzf", "zoxide", "ripgrep", "fd", "htop",
          "zsh-autosuggestions", "zsh-syntax-highlighting"),
    # zsh itself is in this list on Linux only: macOS already ships a modern
    # zsh as the default shell, while Ubuntu's default is bash.
    apt=("zsh", "bat", "eza", "fzf", "zoxide", "ripgrep", "fd-find", "htop",
         "zsh-autosuggestions", "zsh-syntax-highlighting"),
    links=(Link("zsh/.zshrc", "~/.zshrc"),),
    post_install=_linux_post,
    extra_uninstall=_linux_uninstall,
)
