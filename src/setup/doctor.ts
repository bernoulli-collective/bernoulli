import { AuthStorage, ModelRegistry } from "@mariozechner/pi-coding-agent";
import { getUserName as getAlphaUserName, isLoggedIn as isAlphaLoggedIn } from "@companion-ai/alpha-hub/lib";

import {
	FEYNMAN_CONFIG_PATH,
	formatWebSearchDoctorLines,
	getWebSearchStatus,
	loadFeynmanConfig,
} from "../config/feynman-config.js";
import { BROWSER_FALLBACK_PATHS, PANDOC_FALLBACK_PATHS, resolveExecutable } from "../system/executables.js";
import { readJson } from "../pi/settings.js";
import { validatePiInstallation } from "../pi/runtime.js";
import { printInfo, printPanel, printSection } from "../ui/terminal.js";
import { getCurrentModelSpec } from "../model/commands.js";
import { buildModelStatusSnapshotFromRecords, getAvailableModelRecords, getSupportedModelRecords } from "../model/catalog.js";

export type DoctorOptions = {
	settingsPath: string;
	authPath: string;
	sessionDir: string;
	workingDir: string;
	appRoot: string;
};

export type FeynmanStatusSnapshot = {
	model?: string;
	modelValid: boolean;
	recommendedModel?: string;
	recommendedModelReason?: string;
	authenticatedModelCount: number;
	authenticatedProviderCount: number;
	modelGuidance: string[];
	alphaLoggedIn: boolean;
	alphaUser?: string;
	webProviderLabel: string;
	webConfigured: boolean;
	previewConfigured: boolean;
	sessionDir: string;
	configPath: string;
	pandocReady: boolean;
	browserReady: boolean;
	piReady: boolean;
	missingPiBits: string[];
};

export function collectStatusSnapshot(options: DoctorOptions): FeynmanStatusSnapshot {
	const config = loadFeynmanConfig();
	const pandocPath = resolveExecutable("pandoc", PANDOC_FALLBACK_PATHS);
	const browserPath = process.env.PUPPETEER_EXECUTABLE_PATH ?? resolveExecutable("google-chrome", BROWSER_FALLBACK_PATHS);
	const missingPiBits = validatePiInstallation(options.appRoot);
	const webStatus = getWebSearchStatus(config.webSearch ?? {});
	const modelStatus = buildModelStatusSnapshotFromRecords(
		getSupportedModelRecords(options.authPath),
		getAvailableModelRecords(options.authPath),
		getCurrentModelSpec(options.settingsPath),
	);

	return {
		model: modelStatus.current,
		modelValid: modelStatus.currentValid,
		recommendedModel: modelStatus.recommended,
		recommendedModelReason: modelStatus.recommendationReason,
		authenticatedModelCount: modelStatus.availableModels.length,
		authenticatedProviderCount: modelStatus.providers.filter((provider) => provider.configured).length,
		modelGuidance: modelStatus.guidance,
		alphaLoggedIn: isAlphaLoggedIn(),
		alphaUser: isAlphaLoggedIn() ? getAlphaUserName() ?? undefined : undefined,
		webProviderLabel: webStatus.selected.label,
		webConfigured: webStatus.perplexityConfigured || webStatus.geminiApiConfigured || webStatus.selected.id === "gemini-browser",
		previewConfigured: Boolean(config.preview?.lastSetupAt),
		sessionDir: options.sessionDir,
		configPath: FEYNMAN_CONFIG_PATH,
		pandocReady: Boolean(pandocPath),
		browserReady: Boolean(browserPath),
		piReady: missingPiBits.length === 0,
		missingPiBits,
	};
}

export function runStatus(options: DoctorOptions): void {
	const snapshot = collectStatusSnapshot(options);
	printPanel("Feynman Status", [
		"Current setup summary for the research shell.",
	]);
	printSection("Core");
	printInfo(`Model: ${snapshot.model ?? "not configured"}`);
	printInfo(`Model valid: ${snapshot.modelValid ? "yes" : "no"}`);
	printInfo(`Authenticated models: ${snapshot.authenticatedModelCount}`);
	printInfo(`Authenticated providers: ${snapshot.authenticatedProviderCount}`);
	printInfo(`Recommended model: ${snapshot.recommendedModel ?? "not available"}`);
	printInfo(`alphaXiv: ${snapshot.alphaLoggedIn ? snapshot.alphaUser ?? "configured" : "not configured"}`);
	printInfo(`Web research: ${snapshot.webConfigured ? snapshot.webProviderLabel : "not configured"}`);
	printInfo(`Preview: ${snapshot.previewConfigured ? "configured" : "not configured"}`);

	printSection("Paths");
	printInfo(`Config: ${snapshot.configPath}`);
	printInfo(`Sessions: ${snapshot.sessionDir}`);

	printSection("Runtime");
	printInfo(`Pi runtime: ${snapshot.piReady ? "ready" : "missing files"}`);
	printInfo(`Pandoc: ${snapshot.pandocReady ? "ready" : "missing"}`);
	printInfo(`Browser preview: ${snapshot.browserReady ? "ready" : "missing"}`);
	if (snapshot.missingPiBits.length > 0) {
		for (const entry of snapshot.missingPiBits) {
			printInfo(`  missing: ${entry}`);
		}
	}
	if (snapshot.modelGuidance.length > 0) {
		printSection("Next Steps");
		for (const line of snapshot.modelGuidance) {
			printInfo(line);
		}
	}
}

export function runDoctor(options: DoctorOptions): void {
	const settings = readJson(options.settingsPath);
	const config = loadFeynmanConfig();
	const modelRegistry = new ModelRegistry(AuthStorage.create(options.authPath));
	const availableModels = modelRegistry.getAvailable();
	const pandocPath = resolveExecutable("pandoc", PANDOC_FALLBACK_PATHS);
	const browserPath = process.env.PUPPETEER_EXECUTABLE_PATH ?? resolveExecutable("google-chrome", BROWSER_FALLBACK_PATHS);
	const missingPiBits = validatePiInstallation(options.appRoot);

	printPanel("Feynman Doctor", [
		"Checks config, auth, runtime wiring, and preview dependencies.",
	]);
	console.log(`working dir: ${options.workingDir}`);
	console.log(`session dir: ${options.sessionDir}`);
	console.log(`config path: ${FEYNMAN_CONFIG_PATH}`);
	console.log("");
	console.log(`alphaXiv auth: ${isAlphaLoggedIn() ? "ok" : "missing"}`);
	if (isAlphaLoggedIn()) {
		const name = getAlphaUserName();
		if (name) {
			console.log(`  user: ${name}`);
		}
	}
	console.log(`models available: ${availableModels.length}`);
	if (availableModels.length > 0) {
		const sample = availableModels
			.slice(0, 6)
			.map((model) => `${model.provider}/${model.id}`)
			.join(", ");
		console.log(`  sample: ${sample}`);
	}
	console.log(
		`default model: ${typeof settings.defaultProvider === "string" && typeof settings.defaultModel === "string"
			? `${settings.defaultProvider}/${settings.defaultModel}`
			: "not set"}`,
	);
	const modelStatus = collectStatusSnapshot(options);
	console.log(`default model valid: ${modelStatus.modelValid ? "yes" : "no"}`);
	console.log(`authenticated providers: ${modelStatus.authenticatedProviderCount}`);
	console.log(`authenticated models: ${modelStatus.authenticatedModelCount}`);
	console.log(`recommended model: ${modelStatus.recommendedModel ?? "not available"}`);
	if (modelStatus.recommendedModelReason) {
		console.log(`  why: ${modelStatus.recommendedModelReason}`);
	}
	console.log(`pandoc: ${pandocPath ?? "missing"}`);
	console.log(`browser preview runtime: ${browserPath ?? "missing"}`);
	console.log(`configured session dir: ${config.sessionDir ?? "not set"}`);
	for (const line of formatWebSearchDoctorLines(config.webSearch ?? {})) {
		console.log(line);
	}
	console.log(`quiet startup: ${settings.quietStartup === true ? "enabled" : "disabled"}`);
	console.log(`theme: ${typeof settings.theme === "string" ? settings.theme : "not set"}`);
	if (missingPiBits.length > 0) {
		console.log("pi runtime: missing files");
		for (const entry of missingPiBits) {
			console.log(`  ${entry}`);
		}
	} else {
		console.log("pi runtime: ok");
	}
	for (const line of modelStatus.modelGuidance) {
		console.log(`next step: ${line}`);
	}
	console.log("setup hint: feynman setup");
}
