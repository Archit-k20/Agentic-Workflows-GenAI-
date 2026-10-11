import type { Sample } from "../sample-state";
import { source } from "./source";
const sample = {
  input: {
    prompt:
      "Write a Python function that returns unique repair categories in their original order.",
    language: "python",
  },
  result: {
    tool: "code",
    language: "python",
    initial_code:
      "def unique_categories(categories):\n    return list(dict.fromkeys(categories))\n",
    final_code:
      "def unique_categories(categories):\n    return list(dict.fromkeys(categories))\n",
    repair_attempted: false,
    initial_verification: {
      language: "python",
      passed: true,
      checks: [
        {
          name: "ast_parse",
          passed: true,
          details: "Synthetic example of an AST parse result.",
        },
        {
          name: "py_compile",
          passed: true,
          details: "Synthetic example of a bytecode compilation result.",
        },
      ],
    },
    final_verification: {
      language: "python",
      passed: true,
      checks: [
        {
          name: "ast_parse",
          passed: true,
          details: "Synthetic example of an AST parse result.",
        },
        {
          name: "py_compile",
          passed: true,
          details: "Synthetic example of a bytecode compilation result.",
        },
      ],
    },
  },
} satisfies Sample;
export default sample;
