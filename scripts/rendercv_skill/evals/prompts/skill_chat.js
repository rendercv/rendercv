import fs from "fs";
import path from "path";

// The skill that `uv run scripts/rendercv_skill/generate.py <directory>` wrote:
const skillPath = path.join(
  process.env.RENDERCV_SKILL_DIRECTORY,
  "skills",
  "rendercv",
  "SKILL.md",
);
const skillContent = fs.readFileSync(skillPath, "utf-8");

export default function (context) {
  return [
    { role: "system", content: skillContent },
    { role: "user", content: context.vars.query },
  ];
}
