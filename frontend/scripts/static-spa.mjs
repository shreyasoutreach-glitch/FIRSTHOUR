import fs from "node:fs";
import path from "node:path";

const root = path.resolve("dist");
const source = path.join(root, "index.html");
const routes = [
  "app",
  "app/incidents",
  "app/incidents/INC-001",
  "app/data-sources",
  "app/team",
  "demo/setup",
  "connect",
  "evidence",
  "reconstruction",
  "incident",
  "graph",
  "witness",
  "exposure",
  "recovery",
  "recovery/packet",
  "audit"
];

const html = fs.readFileSync(source, "utf8");
for (const route of routes) {
  const target = path.join(root, route, "index.html");
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, html);
}
