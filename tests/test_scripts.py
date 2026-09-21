import builtins
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-state.py"
SCANNER = ROOT / "scripts" / "scan-skills.py"
TEMPLATE = ROOT / "templates" / "project-status.md"


def load_scanner():
    spec = importlib.util.spec_from_file_location("scan_skills", SCANNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FrontmatterReader:
    def __init__(self):
        self.lines = iter([
            "name: example-skill\n",
            "description: >\n",
            "  Example description\n",
            "---\n",
        ])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def readline(self):
        return "---\n"

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.lines)
        except StopIteration as exc:
            raise AssertionError("parser read beyond frontmatter") from exc


class ScanSkillsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = pathlib.Path(temporary.name)
        self.root = self.directory / "explicit skills"
        self.root.mkdir()
        self.home = self.directory / "isolated home"
        self.home.mkdir()
        self.project = self.directory / "project"
        self.project.mkdir()
        # Never let scanner subprocesses read the developer's real home.
        self.environment = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                                CODEX_HOME="", PI_CODING_AGENT_DIR="")

    def write_skill(self, folder, name, description="", *, root=None,
                    filename="SKILL.md", extra=""):
        path = (self.root if root is None else root) / folder / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'---\nname: "{name}"\ndescription: "{description}"\n{extra}---\n',
            encoding="utf-8", newline="\n",
        )
        return str(path.resolve())

    def run_scanner(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCANNER), "--roots", str(self.root), *arguments],
            cwd=self.directory, env=self.environment,
            capture_output=True, check=False, timeout=30,
        )

    def scan(self, *arguments):
        process = self.run_scanner(*arguments)
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        self.assertEqual(process.stderr, b"")
        self.assertFalse(process.stdout.startswith(b"\xef\xbb\xbf"))
        payload = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(payload["candidates_returned"], len(payload["candidates"]))
        return payload

    def test_scoring_normalizes_terms_accumulates_and_filters(self):
        self.write_skill("exact", "Build", "BUILD and lint")
        self.write_skill("substring", "build-tools", "build helpers")
        self.write_skill("other-exact", "lint")
        self.write_skill("description", "docs", "build and lint")
        self.write_skill("unmatched", "unrelated", "nothing relevant")
        payload = self.scan("--query-terms", " BUILD ", "lint", "build", "  ")
        self.assertEqual(payload["query_terms"], ["build", "lint"])
        self.assertEqual(payload["unique_skills_scanned"], 5)
        self.assertEqual(
            [(item["name"], item["score"], item["matched_terms"])
             for item in payload["candidates"]],
            [("Build", 18, ["build", "lint"]), ("lint", 12, ["lint"]),
             ("build-tools", 11, ["build"]), ("docs", 6, ["build", "lint"])],
        )
        limited = self.scan("--query-terms", "build", "lint", "--max-results", "2")
        self.assertEqual(limited["unique_skills_scanned"], 5)
        self.assertEqual([item["name"] for item in limited["candidates"]], ["Build", "lint"])
        unmatched = self.scan("--query-terms", "not-present")
        self.assertEqual(unmatched["unique_skills_scanned"], 5)
        self.assertEqual(unmatched["candidates"], [])

    def test_no_terms_includes_all_and_ties_sort_case_insensitively(self):
        self.write_skill("first", "Zulu", "shared")
        self.write_skill("second", "alpha", "shared")
        self.write_skill("third", "Beta", "shared")
        for terms, score, matched in (([], 0, []), (["  "], 0, []),
                                      (["shared"], 3, ["shared"])):
            with self.subTest(terms=terms):
                payload = self.scan("--query-terms", *terms)
                self.assertEqual(
                    [(item["name"], item["score"], item["matched_terms"])
                     for item in payload["candidates"]],
                    [(name, score, matched) for name in ("alpha", "Beta", "Zulu")],
                )

    def test_name_dedupe_keeps_first_scanned_metadata_before_scoring(self):
        later_root = self.directory / "later"
        winner = self.write_skill("a-first", " Shared ", "first description",
                                  extra="disable-model-invocation: true\n")
        same_root = self.write_skill("z-second", "SHARED", "needle")
        later = self.write_skill("one", "shared", "needle", root=later_root)
        unique = self.write_skill("two", "Other", root=later_root)
        arguments = ("--roots", str(self.root), str(later_root))
        payload = self.scan(*arguments)
        self.assertEqual(payload["roots"], [str(self.root.resolve()),
                                           str(later_root.resolve())])
        self.assertEqual(payload["unique_skills_scanned"], 2)
        self.assertEqual([item["path"] for item in payload["candidates"]],
                         [unique, winner])
        self.assertEqual(payload["candidates"][1], {
            "name": "Shared", "description": "first description", "path": winner,
            "score": 0, "matched_terms": [], "disable_model_invocation": "true",
            "duplicate_paths": [same_root, later],
        })
        self.assertEqual(self.scan(*arguments, "--query-terms", "needle")["candidates"], [])
        reversed_roots = self.scan("--roots", str(later_root), str(self.root),
                                   "--query-terms", "needle")
        self.assertEqual(reversed_roots["candidates"][0]["path"], later)
        self.assertEqual(reversed_roots["candidates"][0]["score"], 3)
        self.assertEqual(reversed_roots["candidates"][0]["duplicate_paths"],
                         [winner, same_root])

    def test_explicit_roots_skip_missing_paths_and_do_not_discover_defaults(self):
        selected = self.write_skill("nested/deeper", "selected", filename="sKiLl.Md")
        self.write_skill("ignored", "default-only",
                         root=self.directory / ".agents" / "skills")
        self.write_skill("not-a-skill", "wrong-filename", filename="README.md")
        missing = self.directory / "missing"
        regular_file = self.directory / "file"
        regular_file.write_text("not a directory", encoding="utf-8")
        payload = self.scan("--roots", str(missing), str(regular_file), " ",
                            "explicit skills")
        self.assertEqual(payload["roots"], [str(self.root.resolve())])
        self.assertEqual(payload["unique_skills_scanned"], 1)
        self.assertEqual([item["path"] for item in payload["candidates"]], [selected])
        empty = self.scan("--roots", str(missing))
        self.assertEqual(empty["roots"], [])
        self.assertEqual(empty["unique_skills_scanned"], 0)
        self.assertEqual(empty["candidates"], [])

    def test_max_results_boundaries_and_default_truncate_after_sorting(self):
        # Reverse folder order ensures truncation cannot precede name sorting.
        for index in range(501):
            self.write_skill(f"{500 - index:03}", f"skill-{index:03}")
        for arguments, count in (([], 30), (["--max-results", "1"], 1),
                                 (["--max-results", "500"], 500)):
            with self.subTest(arguments=arguments):
                payload = self.scan(*arguments)
                self.assertEqual(payload["unique_skills_scanned"], 501)
                self.assertEqual(payload["candidates_returned"], count)
                self.assertEqual([item["name"] for item in payload["candidates"]],
                                 [f"skill-{index:03}" for index in range(count)])

    def test_invalid_max_results_is_an_argument_error_without_output(self):
        output = self.directory / "must-not-exist.json"
        for value in ("0", "-1", "501", "1.5", "invalid"):
            with self.subTest(value=value):
                process = self.run_scanner("--max-results", value,
                                           "--output-path", str(output))
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, b"")
                self.assertIn(b"--max-results", process.stderr)
                self.assertFalse(output.exists())

    def test_output_file_creates_parents_and_uses_utf8_lf_without_stdout(self):
        self.write_skill("unicode", "caf\u00e9", "\u4e2d\u6587 description")
        output = self.directory / "new" / "nested" / "scan.json"
        process = self.run_scanner("--output-path", str(output))
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        self.assertEqual(process.stdout, b"")
        self.assertEqual(process.stderr, b"")
        raw = output.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertIn("caf\u00e9".encode("utf-8"), raw)
        self.assertIn("\u4e2d\u6587".encode("utf-8"), raw)
        payload = json.loads(raw.decode("utf-8"))
        stdout_payload = self.scan()
        # Timestamp is generated per invocation; every other field must agree.
        self.assertIsInstance(payload.pop("generated_at"), str)
        stdout_payload.pop("generated_at")
        self.assertEqual(payload, stdout_payload)

    def test_real_frontmatter_boundaries_and_missing_names(self):
        contents = {
            "body-only": "---\ndescription: no name\n---\nname: body-only\n",
            "no-opening": "name: no-opening\n---\n",
            "blank-name": "---\nname: '   '\n---\n",
            "at-limit": "---\n" + "# padding\n" * 198 + "name: at-limit\n---\n",
            "past-limit": "---\n" + "# padding\n" * 199 + "name: past-limit\n---\n",
            "valid": "\ufeff---\nNAME: 'Valid'\nDESCRIPTION: >-\n"
                     "  first line\n  second line\n---\nname: body-override\n",
        }
        for folder, content in contents.items():
            path = self.root / folder / "SKILL.md"
            path.parent.mkdir()
            path.write_text(content, encoding="utf-8", newline="\n")
        payload = self.scan()
        self.assertEqual(payload["unique_skills_scanned"], 2)
        self.assertEqual([(item["name"], item["description"])
                          for item in payload["candidates"]],
                         [("at-limit", ""), ("Valid", "first line second line")])

    # Expectations are independent of the production profile constants.
    PROJECT_PATHS = (".opencode/skills", ".agents/skills", ".claude/skills",
                     ".cursor/skills", ".codex/skills", ".github/skills", ".pi/skills")
    USER_PATHS = (".config/opencode/skills", ".agents/skills", ".claude/skills",
                  ".cursor/skills", ".codex/skills", ".copilot/skills", ".pi/agent/skills")
    PLUGIN_PATHS = ("plugins/cache/openai-curated", "plugins/cache/openai-bundled",
                    "plugins/cache/openai-curated-remote")

    def make_discovery_tree(self):
        for base, paths in ((self.project, self.PROJECT_PATHS),
                            (self.home, self.USER_PATHS),
                            (self.home / ".codex", self.PLUGIN_PATHS)):
            for path in paths:
                (base / path).mkdir(parents=True, exist_ok=True)

    def discover(self, host="all", project_root=None, *, codex_home="", pi_home=""):
        scanner = load_scanner()
        start = self.project if project_root is None else project_root
        probe = subprocess.CompletedProcess([], 0, str(self.project) + "\n")
        with mock.patch.object(scanner.os.path, "expanduser", return_value=str(self.home)), \
                mock.patch.dict(os.environ, {"CODEX_HOME": codex_home,
                                             "PI_CODING_AGENT_DIR": pi_home}), \
                mock.patch.object(subprocess, "run", return_value=probe) as git:
            roots = scanner.default_roots(host, str(start))
        self.assertEqual(git.call_args.args[0], ["git", "rev-parse", "--show-toplevel"])
        self.assertEqual(git.call_args.kwargs["cwd"], str(start.resolve()))
        return roots

    def test_six_host_profiles_have_native_first_ordered_paths(self):
        self.make_discovery_tree()
        cases = {
            "codex": ((".agents/skills",), (".agents/skills", ".codex/skills",
                       *(".codex/" + path for path in self.PLUGIN_PATHS))),
            "opencode": ((".opencode/skills", ".agents/skills", ".claude/skills"),
                         (".config/opencode/skills", ".agents/skills", ".claude/skills")),
            "claude-code": ((".claude/skills",), (".claude/skills",)),
            "cursor": ((".cursor/skills", ".agents/skills", ".claude/skills", ".codex/skills"),
                       (".cursor/skills", ".agents/skills", ".claude/skills", ".codex/skills")),
            "copilot": ((".github/skills", ".claude/skills", ".agents/skills"),
                        (".copilot/skills", ".agents/skills")),
            "pi": ((".pi/skills", ".agents/skills"), (".pi/agent/skills", ".agents/skills")),
        }
        for host, (project_paths, user_paths) in cases.items():
            with self.subTest(host=host):
                expected = [str((self.project / path).resolve()) for path in project_paths]
                expected += [str((self.home / path).resolve()) for path in user_paths]
                self.assertEqual(self.discover(host), expected)

    def test_all_merges_profiles_in_stable_scope_order_without_duplicates(self):
        self.make_discovery_tree()
        child = self.project / "nested"
        child.mkdir()
        for path in self.PROJECT_PATHS:
            (child / path).mkdir(parents=True)
        expected = [str((base / path).resolve())
                    for base in (child, self.project) for path in self.PROJECT_PATHS
                    if path != ".pi/skills" or base == child]
        expected += [str((self.home / path).resolve()) for path in self.USER_PATHS]
        expected += [str((self.home / ".codex" / path).resolve()) for path in self.PLUGIN_PATHS]
        self.assertEqual(self.discover(project_root=child), expected)
        self.assertEqual(self.discover(project_root=child), expected)
        self.assertEqual(len(expected), len(set(expected)))

    def test_discovery_uses_project_start_not_cwd_and_stops_at_git_boundary(self):
        child = self.project / "nested" / "deep"
        child.mkdir(parents=True)
        for base in (child, child.parent, self.project, self.directory, self.root):
            (base / ".agents/skills").mkdir(parents=True)
        scanner = load_scanner()
        with mock.patch.object(scanner.os, "getcwd", return_value=str(self.root)):
            self.assertEqual(self.discover("codex", child), [
                str((base / ".agents/skills").resolve())
                for base in (child, child.parent, self.project)])

    def test_default_project_start_is_cwd(self):
        scanner = load_scanner()
        (self.project / ".pi/skills").mkdir(parents=True)
        probe = subprocess.CompletedProcess([], 0, str(self.project))
        with mock.patch.object(scanner.os, "getcwd", return_value=str(self.project)), \
                mock.patch.object(scanner.os.path, "expanduser", return_value=str(self.home)), \
                mock.patch.dict(os.environ, {"PI_CODING_AGENT_DIR": ""}), \
                mock.patch.object(subprocess, "run", return_value=probe) as git:
            roots = scanner.default_roots("pi")
        self.assertEqual(roots, [str((self.project / ".pi/skills").resolve())])
        self.assertEqual(git.call_args.kwargs["cwd"], str(self.project.resolve()))

    def test_no_git_failed_probe_and_timeout_walk_to_filesystem_root(self):
        scanner = load_scanner()
        wanted = [self.project / ".agents/skills", self.directory / ".agents/skills"]
        for path in wanted:
            path.mkdir(parents=True)
        allowed = {os.path.normcase(str(path.resolve())) for path in wanted}
        allowed.add(os.path.normcase(str(self.project.resolve())))
        fs_root_candidate = str(pathlib.Path(self.project.anchor) / ".agents/skills")
        for outcome in (FileNotFoundError("git"), subprocess.TimeoutExpired("git", 10),
                        subprocess.CompletedProcess([], 128, ""),
                        subprocess.CompletedProcess([], 0, "")):
            with self.subTest(outcome=outcome), \
                    mock.patch.object(scanner.os.path, "expanduser", return_value=str(self.home)), \
                    mock.patch.dict(os.environ, {"PI_CODING_AGENT_DIR": ""}), \
                    mock.patch.object(scanner.os.path, "isdir",
                                      side_effect=lambda p: os.path.normcase(str(p)) in allowed) as isdir, \
                    mock.patch.object(subprocess, "run") as git:
                if isinstance(outcome, Exception):
                    git.side_effect = outcome
                else:
                    git.return_value = outcome
                self.assertEqual(scanner.default_roots("pi", str(self.project)),
                                 [str(path.resolve()) for path in wanted])
                self.assertIn(os.path.normcase(fs_root_candidate),
                              [os.path.normcase(call.args[0]) for call in isdir.call_args_list])

    def test_codex_home_override_keeps_agents_and_replaces_legacy_base(self):
        self.make_discovery_tree()
        custom = self.directory / "custom codex"
        for path in ("skills", *self.PLUGIN_PATHS):
            (custom / path).mkdir(parents=True)
        expected = [str((base / ".agents/skills").resolve())
                    for base in (self.project, self.home)]
        expected += [str((custom / path).resolve()) for path in ("skills", *self.PLUGIN_PATHS)]
        self.assertEqual(self.discover("codex", codex_home=str(custom)), expected)
        all_roots = self.discover(codex_home=str(custom))
        self.assertEqual(all_roots[-4:], expected[-4:])
        # Cursor's ~/.codex/skills compatibility path is independent of CODEX_HOME.
        self.assertIn(str((self.home / ".codex/skills").resolve()), all_roots)
        self.assertFalse(any(str(custom) in path for path in
                             self.discover("opencode", codex_home=str(custom))))

    def test_pi_config_override_and_local_project_boundary(self):
        self.make_discovery_tree()
        custom = self.directory / "custom pi"
        (custom / "skills").mkdir(parents=True)
        child = self.project / "nested"
        (child / ".pi/skills").mkdir(parents=True)
        expected = [str((child / ".pi/skills").resolve()),
                    str((self.project / ".agents/skills").resolve()),
                    str((custom / "skills").resolve()),
                    str((self.home / ".agents/skills").resolve())]
        self.assertEqual(self.discover("pi", child, pi_home=str(custom)), expected)
        all_roots = self.discover(project_root=child, pi_home=str(custom))
        self.assertIn(str((custom / "skills").resolve()), all_roots)
        self.assertNotIn(str((self.project / ".pi/skills").resolve()), all_roots)
        self.assertNotIn(str((self.home / ".pi/agent/skills").resolve()), all_roots)
        self.assertFalse(any(str(custom) in path for path in
                             self.discover("opencode", pi_home=str(custom))))

    def test_missing_profile_paths_do_not_trigger_other_host_fallbacks(self):
        self.make_discovery_tree()
        (self.project / ".pi/skills").rmdir()
        (self.home / ".pi/agent/skills").rmdir()
        (self.project / ".agents/skills").rmdir()
        (self.home / ".agents/skills").rmdir()
        self.assertEqual(self.discover("pi"), [])

    def test_explicit_roots_override_host_home_and_project_and_dedupe(self):
        selected = self.write_skill("chosen", "chosen")
        self.write_skill("home-only", "home-only", root=self.home / ".agents/skills")
        self.write_skill("project-only", "project-only", root=self.project / ".agents/skills")
        for host in ("all", "codex", "opencode", "claude-code", "cursor", "copilot", "pi"):
            with self.subTest(host=host):
                payload = self.scan("--host", host, "--project-root", str(self.project),
                                    "--roots", str(self.root), str(self.root / "."),
                                    str(self.root / "chosen"))
                self.assertEqual(payload["roots"], [str(self.root.resolve()),
                                                   str((self.root / "chosen").resolve())])
                self.assertEqual([entry["path"] for entry in payload["candidates"]], [selected])
                self.assertEqual(payload["candidates"][0]["duplicate_paths"], [])
        # Explicit roots must never even run the Git/home discovery code.
        scanner = load_scanner()
        with mock.patch.object(sys, "argv", [str(SCANNER), "--roots", str(self.root)]), \
                mock.patch.object(sys, "stdout") as stdout, \
                mock.patch.object(sys, "stderr"), \
                mock.patch.object(scanner, "default_roots", side_effect=AssertionError("discovery")):
            scanner.main()
        self.assertEqual(json.loads(stdout.write.call_args.args[0])["roots"],
                         [str(self.root.resolve())])

    def test_empty_roots_preserves_automatic_discovery(self):
        scanner = load_scanner()
        for arguments in ([], ["--roots"]):
            with self.subTest(arguments=arguments), \
                    mock.patch.object(sys, "argv", [str(SCANNER), *arguments]), \
                    mock.patch.object(sys, "stdout"), mock.patch.object(sys, "stderr"), \
                    mock.patch.object(scanner, "default_roots", return_value=[]) as discover:
                scanner.main()
            discover.assert_called_once()

    def test_invalid_host_and_project_paths_are_argument_errors(self):
        regular_file = self.directory / "not-a-directory"
        regular_file.write_text("file", encoding="utf-8")
        for flag, value in (("--host", "unknown"), ("--project-root", str(regular_file)),
                            ("--project-root", str(self.directory / "missing")),
                            ("--project-root", ""), ("--project-root", " ")):
            with self.subTest(flag=flag, value=value):
                process = self.run_scanner(flag, value)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, b"")
                self.assertIn(flag.encode(), process.stderr)

    def test_auto_cli_host_project_root_and_real_git_boundary(self):
        try:
            git = subprocess.run(["git", "init", str(self.project)], env=self.environment,
                                 capture_output=True, check=False, timeout=30)
        except FileNotFoundError:
            self.skipTest("git is unavailable; mocked boundary tests still run")
        if git.returncode:
            self.skipTest("git init is unavailable")
        self.write_skill("outside", "outside", root=self.directory / ".agents/skills")
        self.write_skill("project", "project", root=self.project / ".agents/skills")
        self.write_skill("home", "home", root=self.home / ".pi/agent/skills")
        self.write_skill("other", "other", root=self.project / ".cursor/skills")
        child = self.project / "nested"
        child.mkdir()
        process = subprocess.run(
            [sys.executable, str(SCANNER), "--host", "pi", "--project-root", str(child)],
            cwd=self.root, env=self.environment, capture_output=True, check=False, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        payload = json.loads(process.stdout)
        self.assertEqual(payload["roots"], [str((self.project / ".agents/skills").resolve()),
                                           str((self.home / ".pi/agent/skills").resolve())])
        self.assertEqual([entry["name"] for entry in payload["candidates"]], ["home", "project"])

    def symlink_or_skip(self, link, target, *, directory=True):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")

    def test_symlink_skills_cycles_root_aliases_and_overlaps_are_scanned_once(self):
        external = self.directory / "external"
        skill = self.write_skill("skill", "linked", root=external)
        self.symlink_or_skip(self.root / "a-linked", external)
        self.symlink_or_skip(self.root / "b-linked", external)
        self.symlink_or_skip(external / "cycle", self.root)
        alias = self.directory / "root-alias"
        self.symlink_or_skip(alias, self.root)
        self.symlink_or_skip(self.root / "broken", self.directory / "absent")
        payload = self.scan("--roots", str(self.root), str(alias), str(external))
        self.assertEqual(payload["roots"], [str(self.root.resolve()), str(external.resolve())])
        self.assertEqual(payload["unique_skills_scanned"], 1)
        self.assertEqual(payload["candidates"][0]["path"], skill)
        self.assertEqual(payload["candidates"][0]["duplicate_paths"], [])
        scanner = load_scanner()
        self.assertEqual(scanner.find_skill_files(str(self.root)), [skill])

    def test_auto_discovery_dedupes_symlink_roots_across_scopes(self):
        target = self.project / ".agents/skills"
        target.mkdir(parents=True)
        (self.project / ".claude").mkdir()
        (self.home / ".agents").mkdir()
        self.symlink_or_skip(self.project / ".claude/skills", target)
        self.symlink_or_skip(self.home / ".agents/skills", target)
        self.assertEqual(self.discover(), [str(target.resolve())])

    def test_path_identity_uses_normcase_as_well_as_realpath(self):
        scanner = load_scanner()
        upper = str(self.directory / "Alias")
        lower = str(self.directory / "alias")
        with mock.patch.object(scanner.os.path, "isdir", return_value=True), \
                mock.patch.object(scanner.os.path, "realpath", side_effect=lambda p: p), \
                mock.patch.object(scanner.os.path, "normcase", side_effect=lambda p: p.lower()):
            self.assertEqual(scanner.existing_unique_roots([upper, lower]), [upper])

    def test_parser_stops_at_frontmatter_boundary(self):
        scanner = load_scanner()
        with mock.patch.object(builtins, "open", return_value=FrontmatterReader()):
            parsed = scanner.parse_frontmatter("ignored")
        self.assertEqual(parsed, ("example-skill", "Example description", ""))


class ProjectStateValidationTests(unittest.TestCase):
    def run_validator(self, content, *extra_args):
        with tempfile.TemporaryDirectory() as directory:
            state_path = pathlib.Path(directory) / "project-status.md"
            state_path.write_text(content, encoding="utf-8", newline="\n")
            process = subprocess.run(
                [sys.executable, str(VALIDATOR), "--path", str(state_path), *extra_args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                cwd=directory,
                timeout=30,
            )
            self.assertEqual(process.stderr, "")
            payload = json.loads(process.stdout)
            self.assertEqual(payload["path"], str(state_path.resolve()))
            return process, payload

    def test_valid_template_passes(self):
        process, payload = self.run_validator(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(process.returncode, 0)
        self.assertTrue(payload["valid"])

    def test_malformed_task_row_fails(self):
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "|---|---|---|---|---|---|---|---|---|---|---|\n| 01 | Broken | TODO |",
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("Malformed task table row" in error for error in payload["errors"]))

    def test_malformed_blocked_row_fails(self):
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "\n|---|---|---|---|---|---|\n",
            "\n|---|---|---|---|---|---|\n| 01 |\n",
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("Malformed blocked table row" in error for error in payload["errors"]))

    def test_duplicate_task_id_fails(self):
        row = "| 01 | Example | TODO | P1 | Executor | None | No | No | No | task-output/01/ | now |"
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "|---|---|---|---|---|---|---|---|---|---|---|\n" + row + "\n" + row,
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertTrue(any("Duplicate task id" in error for error in payload["errors"]))

    # Explicit expectations, not loaded from the spec: an accidental change to
    # an edge in the production transition table must fail this regression test.
    STATES = ("TODO", "In Progress", "In Review", "Needs Revision", "QA Pending",
              "Awaiting Acceptance", "Completed", "Blocked", "Cancelled")
    ALLOWED = {
        "TODO": {"In Progress", "Blocked", "Cancelled"},
        "In Progress": {"In Review", "QA Pending", "Awaiting Acceptance",
                        "Needs Revision", "Blocked", "Cancelled"},
        "In Review": {"Needs Revision", "QA Pending", "Awaiting Acceptance",
                      "Blocked", "Cancelled"},
        "Needs Revision": {"In Progress", "Blocked", "Cancelled"},
        "QA Pending": {"Needs Revision", "Awaiting Acceptance", "Blocked", "Cancelled"},
        "Awaiting Acceptance": {"Completed", "Needs Revision", "Blocked", "Cancelled"},
        "Completed": set(),
        "Cancelled": set(),
    }

    def state_content(self, state="TODO", *, reviewer="No", qa="No", blocked=(),
                      other_tasks=()):
        content = TEMPLATE.read_text(encoding="utf-8")
        task_row = "\n".join(
            f"| {task_id} | Example | {current} | P1 | Executor | None | No | "
            f"{reviewer} | {qa} | task-output/01/ | now |"
            for task_id, current in [("TC-01", state), *other_tasks])
        task_separator = "|---|---|---|---|---|---|---|---|---|---|---|"
        blocked_separator = "|---|---|---|---|---|---|"
        content = content.replace(task_separator, task_separator + "\n" + task_row)
        rows = [f"| {task_id} | {before} | Dependency | Commander | Resolved | now |"
                for task_id, before in blocked]
        return content.replace("\n" + blocked_separator + "\n",
                               "\n" + blocked_separator + "\n" + "\n".join(rows) + "\n")

    def assert_transition(self, content, source, target, *, valid=True,
                          error=None, task_id="TC-01", task_count=1):
        arguments = ["--from-state", source, "--to-state", target]
        if task_id is not None:
            arguments.extend(["--task-id", task_id])
        process, payload = self.run_validator(content, *arguments)
        self.assertEqual(process.returncode, 0 if valid else 1, payload)
        self.assertEqual(payload["valid"], valid, payload)
        self.assertEqual(payload["task_count"], task_count)
        if valid:
            self.assertEqual(payload["errors"], [])
        else:
            self.assertTrue(any((error or
                                 f"Invalid state transition: {source} -> {target}") in message
                                for message in payload["errors"]), payload)

    def test_transition_matrix_including_terminal_states_and_self_transitions(self):
        for source, targets in self.ALLOWED.items():
            for target in self.STATES:
                with self.subTest(source=source, target=target):
                    self.assert_transition(self.state_content(source), source, target,
                                           valid=target in targets)

    def test_optional_reviewer_and_qa_paths_still_require_acceptance(self):
        # These are supported routes, not enforcement of the Reviewer/QA cells:
        # the current validator checks edges, not per-task gate configuration.
        for reviewer, qa, middle in (
            ("Yes", "Yes", ["In Review", "QA Pending"]),
            ("Yes", "No", ["In Review"]),
            ("No", "Yes", ["QA Pending"]),
            ("No", "No", []),
        ):
            path = ["In Progress", *middle, "Awaiting Acceptance", "Completed"]
            for source, target in zip(path, path[1:]):
                with self.subTest(reviewer=reviewer, qa=qa, source=source, target=target):
                    self.assert_transition(
                        self.state_content(source, reviewer=reviewer, qa=qa), source, target)
            with self.subTest(reviewer=reviewer, qa=qa, direct_completion=True):
                self.assert_transition(
                    self.state_content("In Progress", reviewer=reviewer, qa=qa),
                    "In Progress", "Completed", valid=False)

    def test_transition_lookup_ignores_case_and_surrounding_whitespace(self):
        self.assert_transition(self.state_content("in progress"),
                               "  IN PROGRESS ", " awaiting ACCEPTANCE  ")

    def test_transition_arguments_must_be_paired_and_states_known(self):
        for arguments, error in (
            (["--from-state", "TODO"], "FromState and ToState must be provided together"),
            (["--to-state", "In Progress"], "FromState and ToState must be provided together"),
            (["--from-state", "Unknown", "--to-state", "TODO"], "Invalid source state: Unknown"),
            (["--from-state", "TODO", "--to-state", "Unknown"], "Invalid target state: Unknown"),
        ):
            with self.subTest(arguments=arguments):
                process, payload = self.run_validator(
                    self.state_content(), *arguments, "--task-id", "TC-01")
                self.assertEqual(process.returncode, 1)
                self.assertFalse(payload["valid"])
                self.assertTrue(any(error in message for message in payload["errors"]), payload)

    def test_blocked_restores_each_nonterminal_previous_state_by_task_id(self):
        for previous in self.ALLOWED:
            if previous in ("Completed", "Cancelled"):
                continue
            with self.subTest(previous=previous):
                content = self.state_content(" bLoCkEd ", blocked=[("tC-01", previous.swapcase())])
                self.assert_transition(content, " blocked ", previous.upper(),
                                       task_id=" tc-01 ")

    def test_blocked_recovery_requires_task_id_and_matching_record(self):
        content = self.state_content("Blocked", blocked=[("TC-01", "In Review")])
        cases = (
            (None, "In Review", "nonblank --task-id"),
            ("missing", "In Review", "Unknown task id"),
            ("TC-01", "QA Pending", "pre-block state of task TC-01 is In Review"),
            ("TC-01", "Completed", "pre-block state of task TC-01 is In Review"),
        )
        for task_id, target, error in cases:
            with self.subTest(task_id=task_id, target=target):
                self.assert_transition(content, "Blocked", target, valid=False,
                                       task_id=task_id, error=error)
        self.assert_transition(content, "Blocked", "In Review")
        self.assert_transition(self.state_content("Blocked"), "Blocked", "In Review",
                               valid=False, error="Missing blocked record")

    def test_blocked_cancellation_requires_id_and_consistent_metadata_not_restore(self):
        content = self.state_content(" bLoCkEd ", blocked=[(" tc-01 ", " in REVIEW ")])
        self.assert_transition(content, " BLOCKED ", " cancelled ", task_id=" tC-01 ")
        self.assert_transition(content, "Blocked", "Cancelled", task_id=None,
                               valid=False, error="nonblank --task-id")
        self.assert_transition(self.state_content("Blocked"), "Blocked", "Cancelled",
                               valid=False, error="Missing blocked record")

    def test_transition_source_must_match_selected_task_current_state(self):
        for current, source, target in (
            ("TODO", "Awaiting Acceptance", "Completed"),
            ("In Review", "TODO", "In Progress"),
        ):
            with self.subTest(current=current, source=source):
                self.assert_transition(self.state_content(current), source, target,
                                       valid=False, error="Source state mismatch")

    def test_every_transition_requires_known_nonblank_task_id(self):
        for task_id in (None, "", " \t ", "TC-UNKNOWN"):
            with self.subTest(task_id=task_id):
                self.assert_transition(
                    self.state_content(), "TODO", "In Progress", task_id=task_id,
                    valid=False, error="Unknown task id" if task_id == "TC-UNKNOWN"
                    else "nonblank --task-id")

    def test_task_id_alone_is_never_silently_ignored(self):
        for task_id in ("TC-01", "unknown", "", " \t "):
            with self.subTest(task_id=task_id):
                process, payload = self.run_validator(self.state_content(), "--task-id", task_id)
                self.assertEqual(process.returncode, 1)
                self.assertFalse(payload["valid"])
                self.assertTrue(any("--task-id requires" in error for error in payload["errors"]))

    def test_empty_transition_flags_never_degrade_to_structural_only(self):
        for blank in ("", " \t "):
            cases = (
                (["--from-state", blank], "provided together"),
                (["--to-state", blank], "provided together"),
                (["--from-state", blank, "--to-state", blank], "nonblank"),
                (["--from-state", blank, "--to-state", "In Progress"], "nonblank"),
                (["--from-state", "TODO", "--to-state", blank], "nonblank"),
            )
            for arguments, error in cases:
                for id_args in ([], ["--task-id", "TC-01"]):
                    with self.subTest(arguments=arguments, id_args=id_args):
                        process, payload = self.run_validator(
                            self.state_content(), *arguments, *id_args)
                        self.assertEqual(process.returncode, 1)
                        self.assertFalse(payload["valid"])
                        self.assertTrue(any(error in message for message in payload["errors"]),
                                        payload)

    def test_inconsistent_blocked_metadata_fails_structural_and_cancellation_calls(self):
        cases = [
            (self.state_content("Blocked", blocked=[("TC-01", "In Progress"),
                                                    (" tc-01 ", "QA Pending")]),
             "Duplicate blocked record"),
            (self.state_content("Blocked", blocked=[("TC-01", "In Progress"),
                                                    ("TC-UNKNOWN", "QA Pending")]),
             "Orphan blocked record"),
            (self.state_content("Blocked", other_tasks=[("TC-02", "TODO")],
                                blocked=[("TC-01", "In Progress"), ("TC-02", "TODO")]),
             "Blocked record for non-Blocked task"),
            (self.state_content("Blocked"), "Missing blocked record"),
            (self.state_content("Blocked", other_tasks=[("TC-02", "Blocked")],
                                blocked=[("TC-01", "In Progress")]),
             "Missing blocked record"),
            (self.state_content("Blocked", blocked=[("", "TODO")]),
             "task id must be nonblank"),
        ]
        for previous in ("Completed", "Cancelled", "Blocked", "Unknown", "", " \t "):
            cases.append((self.state_content("Blocked", blocked=[("TC-01", previous)]),
                          "Invalid pre-block state"))
        for content, error in cases:
            for arguments in ([], ["--from-state", "Blocked", "--to-state", "Cancelled",
                                   "--task-id", "TC-01"]):
                with self.subTest(content=content, arguments=arguments):
                    process, payload = self.run_validator(content, *arguments)
                    self.assertEqual(process.returncode, 1, payload)
                    self.assertFalse(payload["valid"])
                    self.assertTrue(any(error in message for message in payload["errors"]), payload)

    def test_pre_block_legality_uses_loaded_spec(self):
        spec = (ROOT / "templates" / "task-state-spec.txt").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            spec_path = pathlib.Path(directory) / "custom-spec.txt"
            # A declared state is insufficient: its loaded edge to Blocked matters.
            spec_path.write_text(spec.replace("transition.TODO=In Progress|Blocked|Cancelled",
                                              "transition.TODO=In Progress|Cancelled"),
                                 encoding="utf-8")
            process, payload = self.run_validator(
                self.state_content("Blocked", blocked=[("TC-01", "TODO")]),
                "--spec-path", str(spec_path))
            self.assertEqual(process.returncode, 1)
            self.assertTrue(any("Invalid pre-block state" in error for error in payload["errors"]))
            # Do not hard-code default terminal states as forbidden predecessors.
            spec_path.write_text(spec.replace("transition.Completed=", "transition.Completed=Blocked"),
                                 encoding="utf-8")
            process, payload = self.run_validator(
                self.state_content("Blocked", blocked=[("TC-01", "Completed")]),
                "--spec-path", str(spec_path), "--from-state", "Blocked",
                "--to-state", "Completed", "--task-id", "TC-01")
            self.assertEqual(process.returncode, 0, payload)
            self.assertTrue(payload["valid"])

    def test_multiple_tasks_bind_source_and_recovery_to_selected_id(self):
        content = self.state_content("TODO", other_tasks=[
            ("TC-02", "Awaiting Acceptance"), ("TC-03", "Blocked"), ("TC-04", "Blocked"),
        ], blocked=[("tc-04", " QA PENDING "), ("tc-03", " in REVIEW ")])
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["task_count"], 4)
        for task_id, source, target, valid, error in (
            ("TC-01", "TODO", "In Progress", True, None),
            (" tc-02 ", " awaiting ACCEPTANCE ", "Completed", True, None),
            ("TC-01", "Awaiting Acceptance", "Completed", False, "Source state mismatch"),
            ("TC-03", "Blocked", "In Review", True, None),
            ("TC-04", "Blocked", "QA Pending", True, None),
            ("TC-03", "Blocked", "QA Pending", False, "pre-block state"),
            ("TC-04", "Blocked", "In Review", False, "pre-block state"),
            ("TC-04", "Blocked", "Cancelled", True, None),
        ):
            with self.subTest(task_id=task_id, source=source, target=target):
                self.assert_transition(content, source, target, task_id=task_id,
                                       task_count=4, valid=valid, error=error)


if __name__ == "__main__":
    unittest.main()