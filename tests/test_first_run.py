import json
import os
import subprocess
import sys


def test_cli_initializer_creates_ready_project(tmp_path):
    answers = {
        "topic": "Mobilidade urbana", "course": "Engenharia", "institution": "IFC",
        "work_type": "monografia", "problem": "Ainda não definido",
        "objectives": "Ainda não definido", "method": "Ainda não definido",
    }
    answer_file = tmp_path / "answers.json"
    answer_file.write_text(json.dumps(answers, ensure_ascii=False), encoding="utf-8")
    destination = tmp_path / "meu-tcc"
    env = {**os.environ, "PYTHONPATH": str((__import__("pathlib").Path.cwd() / "src"))}
    result = subprocess.run([sys.executable, "-m", "tcc_kit.cli", "init", str(destination), "--answers-json", str(answer_file)],
                            capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    assert result.returncode == 0, result.stderr
    assert (destination / "tcc.toml").exists()
    assert (destination / "tcc.md").exists()
    assert (destination / "README.md").exists()
    assert (destination / "references.json").exists()
    assert (destination / "prompts" / "01-introducao.txt").exists()
