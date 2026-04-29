import { FEYNMAN_ASCII_LOGO } from "../../logo.mjs";

export const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";

function rgb(red: number, green: number, blue: number): string {
	return `\x1b[38;2;${red};${green};${blue}m`;
}

// Match the outer CLI to a light-purple Bernoulli theme.
const INK = rgb(236, 227, 250);
const STONE = rgb(199, 182, 223);
export const ASH = rgb(180, 162, 207);
const DARK_ASH = rgb(128, 112, 156);
export const SAGE = rgb(209, 185, 242);
const TEAL = rgb(201, 168, 242);
const ROSE = rgb(233, 176, 232);

function paint(text: string, ...codes: string[]): string {
	return `${codes.join("")}${text}${RESET}`;
}

export function printInfo(text: string): void {
	console.log(paint(`  ${text}`, ASH));
}

export function printSuccess(text: string): void {
	console.log(paint(`✓ ${text}`, SAGE, BOLD));
}

export function printWarning(text: string): void {
	console.log(paint(`⚠ ${text}`, STONE, BOLD));
}

export function printError(text: string): void {
	console.log(paint(`✗ ${text}`, ROSE, BOLD));
}

export function printSection(title: string): void {
	console.log("");
	console.log(paint(`◆ ${title}`, TEAL, BOLD));
}

export function printAsciiHeader(subtitleLines: string[] = []): void {
	console.log("");
	for (const line of FEYNMAN_ASCII_LOGO) {
		console.log(paint(`  ${line}`, TEAL, BOLD));
	}
	for (const line of subtitleLines) {
		console.log(paint(`  ${line}`, ASH));
	}
	console.log("");
}

export function printPanel(title: string, subtitleLines: string[] = []): void {
	const inner = 53;
	const border = "─".repeat(inner + 2);
	const renderLine = (text: string, color: string, bold = false): string => {
		const content = text.length > inner ? `${text.slice(0, inner - 3)}...` : text;
		const codes = bold ? `${color}${BOLD}` : color;
		return `${DARK_ASH}${BOLD}│${RESET} ${codes}${content.padEnd(inner)}${RESET} ${DARK_ASH}${BOLD}│${RESET}`;
	};

	console.log("");
	console.log(paint(`┌${border}┐`, DARK_ASH, BOLD));
	console.log(renderLine(title, TEAL, true));
	if (subtitleLines.length > 0) {
		console.log(paint(`├${border}┤`, DARK_ASH, BOLD));
		for (const line of subtitleLines) {
			console.log(renderLine(line, INK));
		}
	}
	console.log(paint(`└${border}┘`, DARK_ASH, BOLD));
	console.log("");
}
