import test from "node:test";
import assert from "node:assert/strict";

import { stripMarkdownBold } from "../scripts/strip-output-bold.mjs";

test("stripMarkdownBold removes bold markers from markdown prose", () => {
	const input = [
		"Plain **bold** text and __strong__ text.",
		"Keep `**inline code**` unchanged.",
		"```md",
		"Keep **fenced code** unchanged.",
		"```",
		"",
	].join("\n");

	assert.equal(
		stripMarkdownBold(input),
		[
			"Plain bold text and strong text.",
			"Keep `**inline code**` unchanged.",
			"```md",
			"Keep **fenced code** unchanged.",
			"```",
			"",
		].join("\n"),
	);
});
