import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const skillPath = path.resolve(
  __dirname,
  "..",
  "..",
  "..",
  "..",
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
