import {
	DEFAULT_WEB_SEARCH_PROVIDER,
	WEB_SEARCH_PROVIDERS,
	configureWebSearchProvider,
	getWebSearchStatus,
	loadFeynmanConfig,
	saveFeynmanConfig,
	type WebSearchProviderId,
} from "../config/feynman-config.js";
import { printInfo, printSuccess } from "../ui/terminal.js";

export function printSearchStatus(): void {
	const status = getWebSearchStatus(loadFeynmanConfig().webSearch ?? {});
	printInfo(`Provider: ${status.selected.label}`);
	printInfo(`Runtime route: ${status.selected.runtimeProvider}`);
	printInfo(`Perplexity API configured: ${status.perplexityConfigured ? "yes" : "no"}`);
	printInfo(`Gemini API configured: ${status.geminiApiConfigured ? "yes" : "no"}`);
	printInfo(`Browser mode: ${status.browserHint}${status.chromeProfile ? ` (${status.chromeProfile})` : ""}`);
}

export function printSearchProviders(): void {
	for (const provider of WEB_SEARCH_PROVIDERS) {
		const marker = provider.id === DEFAULT_WEB_SEARCH_PROVIDER ? " (default)" : "";
		printInfo(`${provider.id} — ${provider.label}${marker}: ${provider.description}`);
	}
}

export function setSearchProvider(providerId: string, value?: string): void {
	if (!WEB_SEARCH_PROVIDERS.some((provider) => provider.id === providerId)) {
		throw new Error(`Unknown search provider: ${providerId}`);
	}

	const config = loadFeynmanConfig();
	const nextWebSearch = configureWebSearchProvider(
		config.webSearch ?? {},
		providerId as WebSearchProviderId,
		providerId === "gemini-browser"
			? { chromeProfile: value }
			: providerId === "perplexity" || providerId === "gemini-api"
				? { apiKey: value }
				: {},
	);

	saveFeynmanConfig({
		...config,
		webSearch: nextWebSearch,
	});
	printSuccess(`Search provider set to ${providerId}`);
}
