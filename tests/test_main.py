from src.main import run


def test_writes_report_file_for_vulnerable_code(tmp_path):
    target = tmp_path / "bad.py"
    target.write_text('password = "hunter2"\n')
    output = tmp_path / "report.md"
    code = run([str(target), "--output", str(output)], root=tmp_path)
    assert code == 0
    text = output.read_text(encoding="utf-8")
    assert "B105" in text
    assert str(tmp_path) not in text


def test_prints_report_without_output_option(tmp_path, capsys):
    target = tmp_path / "clean.py"
    target.write_text("x = 1\n")
    code = run([str(target)], root=tmp_path)
    assert code == 0
    assert "findings for clean.py: 0" in capsys.readouterr().out


def test_fails_for_file_outside_root(tmp_path, capsys):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("x = 1\n")
    code = run([str(outside)], root=root)
    out = capsys.readouterr().out
    assert code == 1
    assert "TargetOutsideRootError" in out
    assert str(tmp_path) not in out


def test_rejects_output_outside_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "a.py"
    target.write_text("x = 1\n")
    leak = tmp_path / "leak.md"
    code = run([str(target), "--output", str(leak)], root=root)
    assert code == 2
    assert not leak.exists()


def test_rejects_non_markdown_output(tmp_path):
    target = tmp_path / "a.py"
    target.write_text("x = 1\n")
    code = run([str(target), "--output", str(tmp_path / "report.txt")], root=tmp_path)
    assert code == 2