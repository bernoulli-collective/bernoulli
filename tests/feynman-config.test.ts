import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import {
	configureWebSearchProvider,
	getConfiguredWebSearchProvider,
	loadFeynmanConfig,
	saveFeynmanConfig,
} from "../src/config/feynman-config.js";

test("loadFeynmanConfig falls back to legacy web-search config", () => {
	const root = mkdtempSync(join(tmpdir(), "feynman-config-"));
	const configPath = join(root, "config.json");
	const legacyDir = join(process.env.HOME ?? root, ".pi");
	const legacyPath = join(legacyDir, "web-search.json");
	mkdirSync(legacyDir, { recursive: true });
	writeFileSync(
		legacyPath,
		JSON.stringify({
			feynmanWebProvider: "perplexity",
			perplexityApiKey: "legacy-key",
		}),
		"utf8",
	);

	const config = loadFeynmanConfig(configPath);
	assert.equal(config.version, 1);
	assert.equal(config.webSearch?.feynmanWebProvider, "perplexity");
	assert.equal(config.webSearch?.perplexityApiKey, "legacy-key");
});

test("saveFeynmanConfig persists sessionDir and webSearch", () => {
	const root = mkdtempSync(join(tmpdir(), "feynman-config-"));
	const configPath = join(root, "config.json");
	const webSearch = configureWebSearchProvider({}, "gemini-browser", { chromeProfile: "Profile 2" });

	saveFeynmanConfig(
		{
			version: 1,
			sessionDir: "/tmp/feynman-sessions",
			webSearch,
		},
		configPath,
	);

	const config = loadFeynmanConfig(configPath);
	assert.equal(config.sessionDir, "/tmp/feynman-sessions");
	assert.equal(config.webSearch?.feynmanWebProvider, "gemini-browser");
	assert.equal(config.webSearch?.chromeProfile, "Profile 2");
});

test("default web provider falls back to Pi web via gemini-browser", () => {
	const provider = getConfiguredWebSearchProvider({});

	assert.equal(provider.id, "gemini-browser");
	assert.equal(provider.runtimeProvider, "gemini");
});
