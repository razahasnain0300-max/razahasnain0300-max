// Auto-refresh the public-project section of the GitHub profile README.
// Only public repository metadata is read. Never publish private repository details.
import fs from "node:fs";
const owner = "razahasnain0300-max";
const begin = "<!-- AUTO-PUBLIC-PROJECTS:START -->";
const end = "<!-- AUTO-PUBLIC-PROJECTS:END -->";
const token = process.env.GITHUB_TOKEN || "";
const headers = { Accept: "application/vnd.github+json", "User-Agent": "syeds-tech-profile-sync", ...(token ? { Authorization: `Bearer ${token}` } : {}) };
const repos = [];
for (let page = 1; page <= 10; page++) {
  const res = await fetch(`https://api.github.com/users/${owner}/repos?type=owner&sort=updated&per_page=100&page=${page}`, { headers });
  if (!res.ok) throw new Error(`GitHub API returned ${res.status}`);
  const batch = await res.json();
  repos.push(...batch);
  if (batch.length < 100) break;
}
const projects = repos.filter(r => !r.private && !r.fork && !r.archived && r.name !== owner);
const escape = v => String(v ?? "").replace(/[&<>\[\]|]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","[":"&#91;","]":"&#93;","|":"&#124;"}[ch]));
const labels = projects.map(r => ({
  name: escape(r.name), url: r.html_url, purpose: escape((r.description || "Project details are being prepared.").slice(0, 180)),
  tech: escape(r.language || "Multiple technologies"),
  updated: (r.pushed_at || r.updated_at || "").slice(0,10)
}));
const lines = [
  `**${labels.length} public project repositories** are currently discoverable. This list is automatically refreshed from GitHub repository metadata. Private project showcases above are curated separately and remain source-code protected.`,
  "",
  ...labels.flatMap((r,i) => [
    `**${String(i+1).padStart(2,"0")}. [${r.name}](${r.url})** — ${r.purpose}`,
    `<sub>Primary language: ${r.tech} · Last pushed: ${r.updated || "not available"}</sub>`,
    ""
  ]),
  ...(labels.length ? [] : ["No public project repositories are currently available.", ""]),
  "**Need a similar project?** [WhatsApp Pakistan](https://wa.me/923065967478) · [WhatsApp UAE](https://wa.me/971552615993) · [Email](https://mail.google.com/mail/?view=cm&fs=1&to=razahasnain0300@gmail.com)"
].join("\n");
const file = "README.md";
const readme = fs.readFileSync(file,"utf8");
const i = readme.indexOf(begin), j = readme.indexOf(end);
if (i < 0 || j < i) throw new Error("Missing auto-project section markers");
const next = readme.slice(0,i+begin.length)+"\n"+lines+"\n"+readme.slice(j);
if (next !== readme) fs.writeFileSync(file,next);
console.log(`Public project entries: ${labels.length}; README ${next === readme ? "unchanged" : "updated"}`);
