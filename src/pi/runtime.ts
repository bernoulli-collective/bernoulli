import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";

import {
	BROWSER_FALLBACK_PATHS,
	MERMAID_FALLBACK_PATHS,
	PANDOC_FALLBACK_PATHS,
	resolveExecutable,
} from "../system/executables.js";

export type PiRuntimeOptions = {
	appRoot: string;
	workingDir: string;
	sessionDir: string;
	feynmanAgentDir: string;
	feynmanVersion?: string;
	thinkingLevel?: string;
	explicitModelSpec?: string;
	oneShotPrompt?: string;
	initialPrompt?: string;
	systemPrompt: string;
};

export function resolvePiPaths(appRoot: string) {
	return {
		piPackageRoot: resolve(appRoot, "node_modules", "@mariozechner", "pi-coding-agent"),
		piCliPath: resolve(appRoot, "node_modules", "@mariozechner", "pi-coding-agent", "dist", "cli.js"),
		promisePolyfillPath: resolve(appRoot, "dist", "system", "promise-polyfill.js"),
		researchToolsPath: resolve(appRoot, "extensions", "research-tools.ts"),
		skillsPath: resolve(appRoot, "skills"),
		promptTemplatePath: resolve(appRoot, "prompts"),
		piWorkspaceNodeModulesPath: resolve(appRoot, ".pi", "npm", "node_modules"),
	};
}

export function validatePiInstallation(appRoot: string): string[] {
	const paths = resolvePiPaths(appRoot);
	const missing: string[] = [];

	if (!existsSync(paths.piCliPath)) missing.push(paths.piCliPath);
	if (!existsSync(paths.promisePolyfillPath)) missing.push(paths.promisePolyfillPath);
	if (!existsSync(paths.researchToolsPath)) missing.push(paths.researchToolsPath);
	if (!existsSync(paths.skillsPath)) missing.push(paths.skillsPath);
	if (!existsSync(paths.promptTemplatePath)) missing.push(paths.promptTemplatePath);

	return missing;
}

export function buildPiArgs(options: PiRuntimeOptions): string[] {
	const paths = resolvePiPaths(options.appRoot);
	const args = [
		"--session-dir",
		options.sessionDir,
		"--extension",
		paths.researchToolsPath,
		"--skill",
		paths.skillsPath,
		"--prompt-template",
		paths.promptTemplatePath,
		"--system-prompt",
		options.systemPrompt,
	];

	if (options.explicitModelSpec) {
		args.push("--model", options.explicitModelSpec);
	}
	if (options.thinkingLevel) {
		args.push("--thinking", options.thinkingLevel);
	}
	if (options.oneShotPrompt) {
		args.push("-p", options.oneShotPrompt);
	} else if (options.initialPrompt) {
		args.push(options.initialPrompt);
	}

	return args;
}

export function buildPiEnv(options: PiRuntimeOptions): NodeJS.ProcessEnv {
	const paths = resolvePiPaths(options.appRoot);

	return {
		...process.env,
		PI_CODING_AGENT_DIR: options.feynmanAgentDir,
		FEYNMAN_CODING_AGENT_DIR: options.feynmanAgentDir,
		FEYNMAN_VERSION: options.feynmanVersion,
		FEYNMAN_PI_NPM_ROOT: paths.piWorkspaceNodeModulesPath,
		FEYNMAN_SESSION_DIR: options.sessionDir,
		PI_SESSION_DIR: options.sessionDir,
		FEYNMAN_MEMORY_DIR: resolve(dirname(options.feynmanAgentDir), "memory"),
		FEYNMAN_NODE_EXECUTABLE: process.execPath,
		FEYNMAN_BIN_PATH: resolve(options.appRoot, "bin", "feynman.js"),
		PANDOC_PATH: process.env.PANDOC_PATH ?? resolveExecutable("pandoc", PANDOC_FALLBACK_PATHS),
		PI_SKIP_VERSION_CHECK: process.env.PI_SKIP_VERSION_CHECK ?? "1",
		MERMAID_CLI_PATH: process.env.MERMAID_CLI_PATH ?? resolveExecutable("mmdc", MERMAID_FALLBACK_PATHS),
		PUPPETEER_EXECUTABLE_PATH:
			process.env.PUPPETEER_EXECUTABLE_PATH ?? resolveExecutable("google-chrome", BROWSER_FALLBACK_PATHS),
	};
}
