import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

import { FEYNMAN_CONFIG_PATH, loadFeynmanConfig, saveFeynmanConfig } from "./feynman-config.js";

function coerceConfigValue(raw: string): unknown {
	const trimmed = raw.trim();
	if (trimmed === "true") return true;
	if (trimmed === "false") return false;
	if (trimmed === "null") return null;
	if (trimmed === "") return "";
	if (/^-?\d+(\.\d+)?$/.test(trimmed)) return Number(trimmed);

	try {
		return JSON.parse(trimmed);
	} catch {
		return raw;
	}
}

function getNestedValue(record: Record<string, unknown>, path: string): unknown {
	return path.split(".").reduce<unknown>((current, segment) => {
		if (!current || typeof current !== "object") {
			return undefined;
		}
		return (current as Record<string, unknown>)[segment];
	}, record);
}

function setNestedValue(record: Record<string, unknown>, path: string, value: unknown): void {
	const segments = path.split(".");
	let current: Record<string, unknown> = record;

	for (const segment of segments.slice(0, -1)) {
		const existing = current[segment];
		if (!existing || typeof existing !== "object" || Array.isArray(existing)) {
			current[segment] = {};
		}
		current = current[segment] as Record<string, unknown>;
	}

	current[segments[segments.length - 1]!] = value;
}

export function printConfig(): void {
	console.log(JSON.stringify(loadFeynmanConfig(), null, 2));
}

export function printConfigPath(): void {
	console.log(FEYNMAN_CONFIG_PATH);
}

export function editConfig(): void {
	if (!existsSync(FEYNMAN_CONFIG_PATH)) {
		saveFeynmanConfig(loadFeynmanConfig());
	}

	const editor = process.env.VISUAL || process.env.EDITOR || "vi";
	const result = spawnSync(editor, [FEYNMAN_CONFIG_PATH], {
		stdio: "inherit",
	});
	if (result.status !== 0) {
		throw new Error(`Failed to open editor: ${editor}`);
	}
}

export function printConfigValue(key: string): void {
	const config = loadFeynmanConfig() as Record<string, unknown>;
	const value = getNestedValue(config, key);
	console.log(typeof value === "string" ? value : JSON.stringify(value, null, 2));
}

export function setConfigValue(key: string, rawValue: string): void {
	const config = loadFeynmanConfig() as Record<string, unknown>;
	setNestedValue(config, key, coerceConfigValue(rawValue));
	saveFeynmanConfig(config as ReturnType<typeof loadFeynmanConfig>);
	console.log(`Updated ${key}`);
}
