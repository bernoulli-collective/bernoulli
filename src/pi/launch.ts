import { spawn } from "node:child_process";
import { existsSync } from "node:fs";

import { buildPiArgs, buildPiEnv, type PiRuntimeOptions, resolvePiPaths } from "./runtime.js";

export async function launchPiChat(options: PiRuntimeOptions): Promise<void> {
	const { piCliPath, promisePolyfillPath } = resolvePiPaths(options.appRoot);
	if (!existsSync(piCliPath)) {
		throw new Error(`Pi CLI not found: ${piCliPath}`);
	}
	if (!existsSync(promisePolyfillPath)) {
		throw new Error(`Promise polyfill not found: ${promisePolyfillPath}`);
	}

	const child = spawn(process.execPath, ["--import", promisePolyfillPath, piCliPath, ...buildPiArgs(options)], {
		cwd: options.workingDir,
		stdio: "inherit",
		env: buildPiEnv(options),
	});

	await new Promise<void>((resolvePromise, reject) => {
		child.on("error", reject);
		child.on("exit", (code, signal) => {
			if (signal) {
				process.kill(process.pid, signal);
				return;
			}
			process.exitCode = code ?? 0;
			resolvePromise();
		});
	});
}
