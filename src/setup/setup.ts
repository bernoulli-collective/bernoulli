import { isLoggedIn as isAlphaLoggedIn, login as loginAlpha } from "@companion-ai/alpha-hub/lib";

import {
	DEFAULT_WEB_SEARCH_PROVIDER,
	FEYNMAN_CONFIG_PATH,
	WEB_SEARCH_PROVIDERS,
	configureWebSearchProvider,
	getConfiguredWebSearchProvider,
	getWebSearchStatus,
	hasConfiguredWebProvider,
	loadFeynmanConfig,
	saveFeynmanConfig,
} from "../config/feynman-config.js";
import { getFeynmanHome } from "../config/paths.js";
import { normalizeFeynmanSettings } from "../pi/settings.js";
import type { ThinkingLevel } from "../pi/settings.js";
import { getCurrentModelSpec, runModelSetup } from "../model/commands.js";
import { buildModelStatusSnapshotFromRecords, getAvailableModelRecords, getSupportedModelRecords } from "../model/catalog.js";
import { promptChoice, promptText } from "./prompts.js";
import { setupPreviewDependencies } from "./preview.js";
import { runDoctor } from "./doctor.js";
import { printInfo, printPanel, printSection, printSuccess } from "../ui/terminal.js";

type SetupOptions = {
	section: string | undefined;
	settingsPath: string;
	bundledSettingsPath: string;
	authPath: string;
	workingDir: string;
	sessionDir: string;
	appRoot: string;
	defaultThinkingLevel?: ThinkingLevel;
};

async function setupWebProvider(): Promise<void> {
	const config = loadFeynmanConfig();
	const current = getConfiguredWebSearchProvider(config.webSearch ?? {});
	const preferredSelectionId = config.webSearch?.feynmanWebProvider ?? DEFAULT_WEB_SEARCH_PROVIDER;
	const choices = [
		...WEB_SEARCH_PROVIDERS.map((provider) => `${provider.label} — ${provider.description}`),
		"Skip",
	];
	const defaultIndex = WEB_SEARCH_PROVIDERS.findIndex((provider) => provider.id === preferredSelectionId);
	const selection = await promptChoice(
		"Choose a web search provider for Feynman:",
		choices,
		defaultIndex >= 0 ? defaultIndex : 0,
	);

	if (selection === WEB_SEARCH_PROVIDERS.length) {
		return;
	}

	const selected = WEB_SEARCH_PROVIDERS[selection] ?? WEB_SEARCH_PROVIDERS[0];
	let nextWebConfig = { ...(config.webSearch ?? {}) };

	if (selected.id === "perplexity") {
		const key = await promptText(
			"Perplexity API key",
			typeof nextWebConfig.perplexityApiKey === "string" ? nextWebConfig.perplexityApiKey : "",
		);
		nextWebConfig = configureWebSearchProvider(nextWebConfig, selected.id, { apiKey: key });
	} else if (selected.id === "gemini-api") {
		const key = await promptText(
			"Gemini API key",
			typeof nextWebConfig.geminiApiKey === "string" ? nextWebConfig.geminiApiKey : "",
		);
		nextWebConfig = configureWebSearchProvider(nextWebConfig, selected.id, { apiKey: key });
	} else if (selected.id === "gemini-browser") {
		const profile = await promptText(
			"Chrome profile (optional)",
			typeof nextWebConfig.chromeProfile === "string" ? nextWebConfig.chromeProfile : "",
		);
		nextWebConfig = configureWebSearchProvider(nextWebConfig, selected.id, { chromeProfile: profile });
	} else {
		nextWebConfig = configureWebSearchProvider(nextWebConfig, selected.id);
	}

	saveFeynmanConfig({
		...config,
		webSearch: nextWebConfig,
	});
	printSuccess(`Saved web search provider: ${selected.label}`);
	if (selected.id === "gemini-browser") {
		printInfo("Gemini Browser relies on a signed-in Chromium profile through pi-web-access.");
	}
}

function isPreviewConfigured() {
	return Boolean(loadFeynmanConfig().preview?.lastSetupAt);
}

function isInteractiveTerminal(): boolean {
	return Boolean(process.stdin.isTTY && process.stdout.isTTY);
}

function printNonInteractiveSetupGuidance(): void {
	printPanel("Feynman Setup", [
		"Non-interactive terminal detected.",
	]);
	printInfo("Use the explicit commands instead of the interactive setup wizard:");
	printInfo("  feynman status");
	printInfo("  feynman model providers");
	printInfo("  feynman model login <provider>");
	printInfo("  feynman model list");
	printInfo("  feynman model recommend");
	printInfo("  feynman model set <provider/model>");
	printInfo("  feynman search providers");
	printInfo("  feynman search set <provider> [value]");
	printInfo("  feynman alpha login");
	printInfo("  feynman doctor");
	printInfo("  feynman   # Pi's /login flow still works inside chat if you prefer it");
}

async function runPreviewSetup(): Promise<void> {
	const result = setupPreviewDependencies();
	printSuccess(result.message);
	saveFeynmanConfig({
		...loadFeynmanConfig(),
		preview: {
			lastSetupAt: new Date().toISOString(),
		},
	});
}

function printConfigurationLocation(appRoot: string): void {
	printSection("Configuration Location");
	printInfo(`Config file:  ${FEYNMAN_CONFIG_PATH}`);
	printInfo(`Data folder:  ${getFeynmanHome()}`);
	printInfo(`Install dir:  ${appRoot}`);
	printInfo("You can edit config.json directly or use `feynman config` commands.");
}

function printSetupSummary(settingsPath: string, authPath: string): void {
	const config = loadFeynmanConfig();
	const webStatus = getWebSearchStatus(config.webSearch ?? {});
	const modelStatus = buildModelStatusSnapshotFromRecords(
		getSupportedModelRecords(authPath),
		getAvailableModelRecords(authPath),
		getCurrentModelSpec(settingsPath),
	);
	printSection("Setup Summary");
	printInfo(`Model: ${getCurrentModelSpec(settingsPath) ?? "not set"}`);
	printInfo(`Model valid: ${modelStatus.currentValid ? "yes" : "no"}`);
	printInfo(`Recommended model: ${modelStatus.recommended ?? "not available"}`);
	printInfo(`alphaXiv: ${isAlphaLoggedIn() ? "configured" : "missing"}`);
	printInfo(`Web research: ${hasConfiguredWebProvider(config.webSearch ?? {}) ? webStatus.selected.label : "not configured"}`);
	printInfo(`Preview: ${isPreviewConfigured() ? "configured" : "not configured"}`);
	for (const line of modelStatus.guidance) {
		printInfo(line);
	}
}

async function runSetupSection(section: "model" | "alpha" | "web" | "preview", options: SetupOptions): Promise<void> {
	if (section === "model") {
		await runModelSetup(options.settingsPath, options.authPath);
		return;
	}

	if (section === "alpha") {
		if (!isAlphaLoggedIn()) {
			await loginAlpha();
			printSuccess("alphaXiv login complete");
		} else {
			printInfo("alphaXiv login already configured");
		}
		return;
	}

	if (section === "web") {
		await setupWebProvider();
		return;
	}

	if (section === "preview") {
		await runPreviewSetup();
		return;
	}
}

async function runFullSetup(options: SetupOptions): Promise<void> {
	printConfigurationLocation(options.appRoot);
	await runSetupSection("model", options);
	await runSetupSection("alpha", options);
	await runSetupSection("web", options);
	await runSetupSection("preview", options);
	normalizeFeynmanSettings(
		options.settingsPath,
		options.bundledSettingsPath,
		options.defaultThinkingLevel ?? "medium",
		options.authPath,
	);
	runDoctor({
		settingsPath: options.settingsPath,
		authPath: options.authPath,
		sessionDir: options.sessionDir,
		workingDir: options.workingDir,
		appRoot: options.appRoot,
	});
	printSetupSummary(options.settingsPath, options.authPath);
}

async function runQuickSetup(options: SetupOptions): Promise<void> {
	printSection("Quick Setup");
	let changed = false;
	const modelStatus = buildModelStatusSnapshotFromRecords(
		getSupportedModelRecords(options.authPath),
		getAvailableModelRecords(options.authPath),
		getCurrentModelSpec(options.settingsPath),
	);

	if (!modelStatus.current || !modelStatus.currentValid) {
		await runSetupSection("model", options);
		changed = true;
	}
	if (!isAlphaLoggedIn()) {
		await runSetupSection("alpha", options);
		changed = true;
	}
	if (!hasConfiguredWebProvider(loadFeynmanConfig().webSearch ?? {})) {
		await runSetupSection("web", options);
		changed = true;
	}
	if (!isPreviewConfigured()) {
		await runSetupSection("preview", options);
		changed = true;
	}

	if (!changed) {
		printSuccess("Everything already looks configured.");
		printInfo("Run `feynman setup` and choose Full Setup if you want to reconfigure everything.");
		return;
	}

	normalizeFeynmanSettings(
		options.settingsPath,
		options.bundledSettingsPath,
		options.defaultThinkingLevel ?? "medium",
		options.authPath,
	);
	printSetupSummary(options.settingsPath, options.authPath);
}

function hasExistingSetup(settingsPath: string, authPath: string): boolean {
	const config = loadFeynmanConfig();
	const modelStatus = buildModelStatusSnapshotFromRecords(
		getSupportedModelRecords(authPath),
		getAvailableModelRecords(authPath),
		getCurrentModelSpec(settingsPath),
	);
	return Boolean(
		modelStatus.current ||
		modelStatus.availableModels.length > 0 ||
		isAlphaLoggedIn() ||
		hasConfiguredWebProvider(config.webSearch ?? {}) ||
		config.preview?.lastSetupAt,
	);
}

async function runDefaultInteractiveSetup(options: SetupOptions): Promise<void> {
	const existing = hasExistingSetup(options.settingsPath, options.authPath);
	printPanel("Feynman Setup Wizard", [
		"Guided setup for the research-first Pi agent.",
		"Press Ctrl+C at any time to exit.",
	]);

	if (existing) {
		printSection("Full Setup");
		printInfo("Existing configuration detected. Rerunning the full guided setup.");
		printInfo("Use `feynman setup quick` if you only want to fill missing items.");
	} else {
		printInfo("We'll walk you through:");
		printInfo("  1. Model Selection");
		printInfo("  2. alphaXiv Login");
		printInfo("  3. Web Research Provider");
		printInfo("  4. Preview Dependencies");
	}
	printInfo("Press Enter to begin, or Ctrl+C to exit.");
	await promptText("Press Enter to start");
	await runFullSetup(options);
}

export async function runSetup(options: SetupOptions): Promise<void> {
	if (!isInteractiveTerminal()) {
		printNonInteractiveSetupGuidance();
		return;
	}

	if (!options.section) {
		await runDefaultInteractiveSetup(options);
		return;
	}

	if (options.section === "model") {
		await runSetupSection("model", options);
		return;
	}
	if (options.section === "alpha") {
		await runSetupSection("alpha", options);
		return;
	}
	if (options.section === "web") {
		await runSetupSection("web", options);
		return;
	}
	if (options.section === "preview") {
		await runSetupSection("preview", options);
		return;
	}
	if (options.section === "quick") {
		await runQuickSetup(options);
		return;
	}

	await runFullSetup(options);
}
