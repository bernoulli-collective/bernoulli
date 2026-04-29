import { opendir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const MARKDOWN_EXTENSION = ".md";

function stripBoldOutsideInlineCode(line) {
	let output = "";
	let index = 0;
	let inCode = false;

	while (index < line.length) {
		const char = line[index];

		if (char === "`") {
			let end = index + 1;
			while (end < line.length && line[end] === "`") end += 1;
			output += line.slice(index, end);
			index = end;
			inCode = !inCode;
			continue;
		}

		if (!inCode && line.startsWith("**", index)) {
			index += 2;
			continue;
		}

		if (!inCode && line.startsWith("__", index)) {
			index += 2;
			continue;
		}

		output += char;
		index += 1;
	}

	return output;
}

export function stripMarkdownBold(source) {
	const lines = source.split(/(\r?\n)/);
	let inFence = false;

	return lines
		.map((part) => {
			if (part === "\n" || part === "\r\n") return part;

			if (/^\s*(```|~~~)/.test(part)) {
				inFence = !inFence;
				return part;
			}

			if (inFence) return part;
			return stripBoldOutsideInlineCode(part);
		})
		.join("");
}

async function collectMarkdownFiles(directory) {
	const files = [];
	const entries = await opendir(directory);

	for await (const entry of entries) {
		const entryPath = path.join(directory, entry.name);

		if (entry.isDirectory()) {
			files.push(...(await collectMarkdownFiles(entryPath)));
			continue;
		}

		if (entry.isFile() && path.extname(entry.name) === MARKDOWN_EXTENSION) {
			files.push(entryPath);
		}
	}

	return files;
}

export async function stripOutputBold({ root = process.cwd() } = {}) {
	const outputDirectory = path.join(root, "outputs");
	const files = await collectMarkdownFiles(outputDirectory);
	let changed = 0;

	for (const file of files) {
		const source = await readFile(file, "utf8");
		const stripped = stripMarkdownBold(source);

		if (stripped !== source) {
			await writeFile(file, stripped);
			changed += 1;
		}
	}

	return { checked: files.length, changed };
}

const isCli = process.argv[1] === fileURLToPath(import.meta.url);

if (isCli) {
	const result = await stripOutputBold();
	console.log(`Stripped bold markers in ${result.changed} of ${result.checked} Markdown files under outputs/.`);
}
