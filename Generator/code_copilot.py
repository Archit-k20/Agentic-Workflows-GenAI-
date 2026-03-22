import ast
import json
import os
import py_compile
import shutil
import subprocess
import tempfile

import streamlit as st
from openai import OpenAI


MODEL_NAME = "gpt-4o-mini"
LANGUAGE_CONFIG = {
    "python": {"extension": ".py", "command": None},
    "javascript": {"extension": ".js", "command": "node"},
    "java": {"extension": ".java", "command": "javac"},
    "c": {"extension": ".c", "command": "gcc"},
    "c++": {"extension": ".cpp", "command": "g++"},
}
SUPPORTED_LANGUAGES = list(LANGUAGE_CONFIG.keys())


def _strip_code_fences(value):
    cleaned = (value or "").strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _chat_text(client, system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return (response.choices[0].message.content or "").strip()


def generate_initial_code(prompt, language, client):
    return _strip_code_fences(
        _chat_text(
            client,
            (
                "You are a careful coding assistant. "
                "Return only the requested code with no prose. "
                "Produce clean, runnable code."
            ),
            f"Language: {language}\nTask:\n{prompt}",
        )
    )


def repair_code(prompt, language, code, verification, client):
    return _strip_code_fences(
        _chat_text(
            client,
            (
                "You fix code after verification failures. "
                "Return only corrected code with no prose. "
                "Preserve the user's intent and fix the reported issues."
            ),
            (
                f"Language: {language}\n"
                f"Original task:\n{prompt}\n\n"
                f"Current code:\n{code}\n\n"
                f"Verification report:\n{json.dumps(verification, indent=2)}"
            ),
        )
    )


def verify_python_code(code):
    verification = {
        "language": "python",
        "passed": False,
        "checks": [],
    }

    try:
        ast.parse(code)
        verification["checks"].append({"name": "ast_parse", "passed": True, "details": "AST parse passed."})
    except SyntaxError as exc:
        verification["checks"].append(
            {
                "name": "ast_parse",
                "passed": False,
                "details": f"SyntaxError at line {exc.lineno}: {exc.msg}",
            }
        )
        return verification

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            temp_path = tmp.name

        py_compile.compile(temp_path, doraise=True)
        verification["checks"].append({"name": "py_compile", "passed": True, "details": "Bytecode compilation passed."})
        verification["passed"] = True
    except py_compile.PyCompileError as exc:
        verification["checks"].append(
            {
                "name": "py_compile",
                "passed": False,
                "details": str(exc),
            }
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

    return verification


def verify_javascript_code(code):
    verification = {
        "language": "javascript",
        "passed": False,
        "checks": [],
    }
    node_path = shutil.which("node")
    if not node_path:
        verification["checks"].append(
            {
                "name": "node_check",
                "passed": False,
                "details": "Node.js is not installed locally, so JavaScript verification is unavailable on this machine.",
            }
        )
        return verification

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            temp_path = tmp.name

        result = subprocess.run(
            [node_path, "--check", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            verification["checks"].append({"name": "node_check", "passed": True, "details": "Node syntax check passed."})
            verification["passed"] = True
        else:
            verification["checks"].append(
                {
                    "name": "node_check",
                    "passed": False,
                    "details": (result.stderr or result.stdout or "JavaScript syntax check failed.").strip(),
                }
            )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

    return verification


def verify_java_code(code):
    verification = {
        "language": "java",
        "passed": False,
        "checks": [],
    }
    javac_path = shutil.which("javac")
    if not javac_path:
        verification["checks"].append(
            {
                "name": "javac_compile",
                "passed": False,
                "details": "JDK is not installed locally, so Java verification is unavailable on this machine.",
            }
        )
        return verification

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, "Main.java")
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(code)

        result = subprocess.run(
            [javac_path, temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            verification["checks"].append({"name": "javac_compile", "passed": True, "details": "Java compilation passed."})
            verification["passed"] = True
        else:
            verification["checks"].append(
                {
                    "name": "javac_compile",
                    "passed": False,
                    "details": (result.stderr or result.stdout or "Java compilation failed.").strip(),
                }
            )
    finally:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file_name in files:
                os.unlink(os.path.join(root, file_name))
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
        os.rmdir(temp_dir)

    return verification


def verify_c_family_code(code, language):
    compiler_name = "gcc" if language == "c" else "g++"
    verification = {
        "language": language,
        "passed": False,
        "checks": [],
    }
    compiler_path = shutil.which(compiler_name)
    if not compiler_path:
        verification["checks"].append(
            {
                "name": f"{compiler_name}_syntax",
                "passed": False,
                "details": f"{compiler_name} is not installed locally, so {language} verification is unavailable on this machine.",
            }
        )
        return verification

    suffix = ".c" if language == "c" else ".cpp"
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f"snippet{suffix}")
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(code)

        result = subprocess.run(
            [compiler_path, "-fsyntax-only", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            verification["checks"].append(
                {"name": f"{compiler_name}_syntax", "passed": True, "details": f"{language.upper()} syntax check passed."}
            )
            verification["passed"] = True
        else:
            verification["checks"].append(
                {
                    "name": f"{compiler_name}_syntax",
                    "passed": False,
                    "details": (result.stderr or result.stdout or f"{language.upper()} syntax check failed.").strip(),
                }
            )
    finally:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file_name in files:
                os.unlink(os.path.join(root, file_name))
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
        os.rmdir(temp_dir)

    return verification


def verify_code(code, language):
    if language == "python":
        return verify_python_code(code)
    if language == "javascript":
        return verify_javascript_code(code)
    if language == "java":
        return verify_java_code(code)
    if language in {"c", "c++"}:
        return verify_c_family_code(code, language)
    return {"language": language, "passed": False, "checks": [{"name": "language_support", "passed": False, "details": "Unsupported language."}]}


def run_code_copilot(prompt, api_key, language="python"):
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    client = OpenAI(api_key=api_key)
    initial_code = generate_initial_code(prompt, language, client)
    initial_verification = verify_code(initial_code, language)

    final_code = initial_code
    repair_attempted = False
    final_verification = initial_verification

    if not initial_verification["passed"]:
        repair_attempted = True
        repaired_code = repair_code(prompt, language, initial_code, initial_verification, client)
        repaired_verification = verify_code(repaired_code, language)
        final_code = repaired_code
        final_verification = repaired_verification

    return {
        "language": language,
        "initial_code": initial_code,
        "initial_verification": initial_verification,
        "repair_attempted": repair_attempted,
        "final_code": final_code,
        "final_verification": final_verification,
    }


def show_code_copilot(api_key=None):
    st.subheader("Code Copilot")
    st.caption("Prompt -> generate -> verify in temp sandbox -> repair once -> final code + report")

    if not api_key:
        st.error("OpenAI API key is required for Code Copilot.")
        return

    language = st.selectbox("Language", SUPPORTED_LANGUAGES, key="code_copilot_language")
    prompt = st.text_area(
        "Describe what the code should do",
        placeholder="Example: Write a Python function that reads a CSV file and returns the top 5 rows sorted by revenue descending.",
        height=140,
        key="code_copilot_prompt",
    )

    if "code_copilot_result" not in st.session_state:
        st.session_state.code_copilot_result = None

    if st.button("Run Code Copilot", type="primary"):
        if not prompt.strip():
            st.warning("Please describe the code task first.")
            return

        with st.spinner("Generating and verifying code..."):
            try:
                result = run_code_copilot(prompt.strip(), api_key, language)
            except Exception as exc:
                st.error(f"Code Copilot failed: {exc}")
                return
        st.session_state.code_copilot_result = result

    result = st.session_state.code_copilot_result
    if not result:
        return

    st.markdown("### Final Verification")
    st.write(f"Passed: {'Yes' if result['final_verification']['passed'] else 'No'}")
    st.json(result["final_verification"])

    unavailable_checks = [item for item in result["final_verification"]["checks"] if "unavailable" in item["details"].lower()]
    if unavailable_checks:
        st.info("Local verification for this language depends on compiler/runtime tools installed on this machine.")

    if result["repair_attempted"]:
        st.markdown("### Initial Verification")
        st.json(result["initial_verification"])

    st.markdown("### Final Code")
    st.code(result["final_code"], language=result["language"])
