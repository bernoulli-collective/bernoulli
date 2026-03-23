import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

import { getDefaultSessionDir, getFeynmanConfigPath } from "./paths.js";

export type WebSearchProviderId = "auto" | "perplexity" | "gemini-api" | "gemini-browser";
export type PiWebSearchProvider = "auto" | "perplexity" | "gemini";

export type WebSearchConfig = Record<string, unknown> & {
	provider?: PiWebSearchProvider;
	perplexityApiKey?: string;
	geminiApiKey?: string;
	chromeProfile?: string;
	feynmanWebProvider?: WebSearchProviderId;
};

export type FeynmanConfig = {
	version: 1;
	sessionDir?: string;
	webSearch?: WebSearchConfig;
	preview?: {
		lastSetupAt?: string;
	};
};

export type WebSearchProviderDefinition = {
	id: WebSearchProviderId;
	label: string;
	description: string;
	runtimeProvider: PiWebSearchProvider;
	requiresApiKey: boolean;
};

export type WebSearchStatus = {
	selected: WebSearchProviderDefinition;
	configPath: string;
	perplexityConfigured: boolean;
	geminiApiConfigured: boolean;
	chromeProfile?: string;
	browserHint: string;
};

export const FEYNMAN_CONFIG_PATH = getFeynmanConfigPath();
export const LEGACY_WEB_SEARCH_CONFIG_PATH = resolve(process.env.HOME ?? "", ".pi", "web-search.json");
export const DEFAULT_WEB_SEARCH_PROVIDER: WebSearchProviderId = "gemini-browser";

export const WEB_SEARCH_PROVIDERS: ReadonlyArray<WebSearchProviderDefinition> = [
	{
		id: "auto",
		label: "Auto",
		description: "Prefer Perplexity when configured, otherwise fall back to Gemini.",
		runtimeProvider: "auto",
		requiresApiKey: false,
	},
	{
		id: "perplexity",
		label: "Perplexity API",
		description: "Use Perplexity Sonar directly for web answers and source lists.",
		runtimeProvider: "perplexity",
		requiresApiKey: true,
	},
	{
		id: "gemini-api",
		label: "Gemini API",
		description: "Use Gemini directly with an API key.",
		runtimeProvider: "gemini",
		requiresApiKey: true,
	},
	{
		id: "gemini-browser",
		label: "Gemini Browser",
		description: "Use your signed-in Chromium browser session through pi-web-access.",
		runtimeProvider: "gemini",
		requiresApiKey: false,
	},
] as const;

function readJsonFile<T>(path: string): T | undefined {
	if (!existsSync(path)) {
		return undefined;
	}

	try {
		return JSON.parse(readFileSync(path, "utf8")) as T;
	} catch {
		return undefined;
	}
}

function normalizeWebSearchConfig(value: unknown): WebSearchConfig | undefined {
	if (!value || typeof value !== "object") {
		return undefined;
	}

	return { ...(value as WebSearchConfig) };
}

function migrateLegacyWebSearchConfig(): WebSearchConfig | undefined {
	return normalizeWebSearchConfig(readJsonFile<WebSearchConfig>(LEGACY_WEB_SEARCH_CONFIG_PATH));
}

export function loadFeynmanConfig(configPath = FEYNMAN_CONFIG_PATH): FeynmanConfig {
	const config = readJsonFile<FeynmanConfig>(configPath);
	if (config && typeof config === "object") {
		return {
			version: 1,
			sessionDir: typeof config.sessionDir === "string" && config.sessionDir.trim() ? config.sessionDir : undefined,
			webSearch: normalizeWebSearchConfig(config.webSearch),
			preview: config.preview && typeof config.preview === "object" ? { ...config.preview } : undefined,
		};
	}

	const legacyWebSearch = migrateLegacyWebSearchConfig();
	return {
		version: 1,
		sessionDir: getDefaultSessionDir(),
		webSearch: legacyWebSearch,
	};
}

export function saveFeynmanConfig(config: FeynmanConfig, configPath = FEYNMAN_CONFIG_PATH): void {
	mkdirSync(dirname(configPath), { recursive: true });
	writeFileSync(
		configPath,
		JSON.stringify(
			{
				version: 1,
				...(config.sessionDir ? { sessionDir: config.sessionDir } : {}),
				...(config.webSearch ? { webSearch: config.webSearch } : {}),
				...(config.preview ? { preview: config.preview } : {}),
			},
			null,
			2,
		) + "\n",
		"utf8",
	);
}

export function getConfiguredSessionDir(config = loadFeynmanConfig()): string {
	return typeof config.sessionDir === "string" && config.sessionDir.trim()
		? config.sessionDir
		: getDefaultSessionDir();
}

export function loadWebSearchConfig(): WebSearchConfig {
	return loadFeynmanConfig().webSearch ?? {};
}

export function saveWebSearchConfig(config: WebSearchConfig): void {
	const current = loadFeynmanConfig();
	saveFeynmanConfig({
		...current,
		webSearch: config,
	});
}

export function getWebSearchProviderById(id: WebSearchProviderId): WebSearchProviderDefinition {
	return WEB_SEARCH_PROVIDERS.find((provider) => provider.id === id) ?? WEB_SEARCH_PROVIDERS[0];
}

export function hasPerplexityApiKey(config: WebSearchConfig = loadWebSearchConfig()): boolean {
	return typeof config.perplexityApiKey === "string" && config.perplexityApiKey.trim().length > 0;
}

export function hasGeminiApiKey(config: WebSearchConfig = loadWebSearchConfig()): boolean {
	return typeof config.geminiApiKey === "string" && config.geminiApiKey.trim().length > 0;
}

export function hasConfiguredWebProvider(config: WebSearchConfig = loadWebSearchConfig()): boolean {
	return hasPerplexityApiKey(config) || hasGeminiApiKey(config) || getConfiguredWebSearchProvider(config).id === DEFAULT_WEB_SEARCH_PROVIDER;
}

export function getConfiguredWebSearchProvider(
	config: WebSearchConfig = loadWebSearchConfig(),
): WebSearchProviderDefinition {
	const explicit = config.feynmanWebProvider;
	if (explicit === "auto" || explicit === "perplexity" || explicit === "gemini-api" || explicit === "gemini-browser") {
		return getWebSearchProviderById(explicit);
	}

	if (config.provider === "perplexity") {
		return getWebSearchProviderById("perplexity");
	}

	if (config.provider === "gemini") {
		return hasGeminiApiKey(config)
			? getWebSearchProviderById("gemini-api")
			: getWebSearchProviderById("gemini-browser");
	}

	return getWebSearchProviderById(DEFAULT_WEB_SEARCH_PROVIDER);
}

export function configureWebSearchProvider(
	current: WebSearchConfig,
	providerId: WebSearchProviderId,
	values: { apiKey?: string; chromeProfile?: string } = {},
): WebSearchConfig {
	const next: WebSearchConfig = { ...current };
	next.feynmanWebProvider = providerId;

	switch (providerId) {
		case "auto":
			next.provider = "auto";
			if (typeof values.chromeProfile === "string" && values.chromeProfile.trim()) {
				next.chromeProfile = values.chromeProfile.trim();
			}
			return next;
		case "perplexity":
			next.provider = "perplexity";
			if (typeof values.apiKey === "string" && values.apiKey.trim()) {
				next.perplexityApiKey = values.apiKey.trim();
			}
			if (typeof values.chromeProfile === "string" && values.chromeProfile.trim()) {
				next.chromeProfile = values.chromeProfile.trim();
			}
			return next;
		case "gemini-api":
			next.provider = "gemini";
			if (typeof values.apiKey === "string" && values.apiKey.trim()) {
				next.geminiApiKey = values.apiKey.trim();
			}
			if (typeof values.chromeProfile === "string" && values.chromeProfile.trim()) {
				next.chromeProfile = values.chromeProfile.trim();
			}
			return next;
		case "gemini-browser":
			next.provider = "gemini";
			delete next.geminiApiKey;
			if (typeof values.chromeProfile === "string") {
				const profile = values.chromeProfile.trim();
				if (profile) {
					next.chromeProfile = profile;
				} else {
					delete next.chromeProfile;
				}
			}
			return next;
	}
}

export function getWebSearchStatus(config: WebSearchConfig = loadWebSearchConfig()): WebSearchStatus {
	const selected = getConfiguredWebSearchProvider(config);
	return {
		selected,
		configPath: FEYNMAN_CONFIG_PATH,
		perplexityConfigured: hasPerplexityApiKey(config),
		geminiApiConfigured: hasGeminiApiKey(config),
		chromeProfile: typeof config.chromeProfile === "string" && config.chromeProfile.trim()
			? config.chromeProfile.trim()
			: undefined,
		browserHint: selected.id === "gemini-browser" ? "selected" : "fallback only",
	};
}

export function formatWebSearchDoctorLines(config: WebSearchConfig = loadWebSearchConfig()): string[] {
	const status = getWebSearchStatus(config);
	const configured = [];
	if (status.perplexityConfigured) configured.push("Perplexity API");
	if (status.geminiApiConfigured) configured.push("Gemini API");
	if (status.selected.id === "gemini-browser" || status.chromeProfile) configured.push("Gemini Browser");

	return [
		`web research provider: ${status.selected.label}`,
		`  runtime route: ${status.selected.runtimeProvider}`,
		`  configured credentials: ${configured.length > 0 ? configured.join(", ") : "none"}`,
		`  browser mode: ${status.browserHint}${status.chromeProfile ? ` (profile: ${status.chromeProfile})` : ""}`,
		`  config path: ${status.configPath}`,
	];
}
