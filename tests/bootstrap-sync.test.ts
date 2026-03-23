import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { syncBundledAssets } from "../src/bootstrap/sync.js";

function createAppRoot(): string {
	const appRoot = mkdtempSync(join(tmpdir(), "feynman-app-"));
	mkdirSync(join(appRoot, ".pi", "themes"), { recursive: true });
	mkdirSync(join(appRoot, ".pi", "agents"), { recursive: true });
	writeFileSync(join(appRoot, ".pi", "themes", "feynman.json"), '{"theme":"v1"}\n', "utf8");
	writeFileSync(join(appRoot, ".pi", "agents", "researcher.md"), "# v1\n", "utf8");
	return appRoot;
}

test("syncBundledAssets copies missing bundled files", () => {
	const appRoot = createAppRoot();
	const home = mkdtempSync(join(tmpdir(), "feynman-home-"));
	process.env.FEYNMAN_HOME = home;
	const agentDir = join(home, "agent");
	mkdirSync(agentDir, { recursive: true });

	const result = syncBundledAssets(appRoot, agentDir);

	assert.deepEqual(result.copied.sort(), ["feynman.json", "researcher.md"]);
	assert.equal(readFileSync(join(agentDir, "themes", "feynman.json"), "utf8"), '{"theme":"v1"}\n');
	assert.equal(readFileSync(join(agentDir, "agents", "researcher.md"), "utf8"), "# v1\n");
});

test("syncBundledAssets preserves user-modified files and updates managed files", () => {
	const appRoot = createAppRoot();
	const home = mkdtempSync(join(tmpdir(), "feynman-home-"));
	process.env.FEYNMAN_HOME = home;
	const agentDir = join(home, "agent");
	mkdirSync(agentDir, { recursive: true });

	syncBundledAssets(appRoot, agentDir);

	writeFileSync(join(appRoot, ".pi", "themes", "feynman.json"), '{"theme":"v2"}\n', "utf8");
	writeFileSync(join(appRoot, ".pi", "agents", "researcher.md"), "# v2\n", "utf8");
	writeFileSync(join(agentDir, "agents", "researcher.md"), "# user-custom\n", "utf8");

	const result = syncBundledAssets(appRoot, agentDir);

	assert.deepEqual(result.updated, ["feynman.json"]);
	assert.deepEqual(result.skipped, ["researcher.md"]);
	assert.equal(readFileSync(join(agentDir, "themes", "feynman.json"), "utf8"), '{"theme":"v2"}\n');
	assert.equal(readFileSync(join(agentDir, "agents", "researcher.md"), "utf8"), "# user-custom\n");
});
