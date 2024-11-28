import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Get the content of the currently active file in VSCode.
 */
export async function getActiveFileContent(): Promise<{ filePath: string; content: string } | null> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage("No active file is currently open!");
        return null;
    }

    const filePath = editor.document.fileName;
    const content = editor.document.getText();
    return { filePath, content };
}

/**
 * Recursively collect all files within a folder.
 */
export async function getAllFilesInFolder(folderPath: string): Promise<string[]> {
    const files: string[] = [];

    async function collectFiles(dir: string) {
        const dirContents = await fs.promises.readdir(dir, { withFileTypes: true });
        for (const entry of dirContents) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                await collectFiles(fullPath);
            } else if (entry.isFile()) {
                files.push(fullPath);
            }
        }
    }

    await collectFiles(folderPath);
    return files;
}

/**
 * Read the content of a single file.
 */
export async function readFileContent(filePath: string): Promise<string> {
    try {
        const content = await fs.promises.readFile(filePath, 'utf-8');
        return content;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to read file: ${filePath}`);
        throw error;
    }
}

/**
 * Collect and read all files within a folder.
 */
export async function getFilesWithContent(folderPath: string): Promise<{ filePath: string; content: string }[]> {
    const filePaths = await getAllFilesInFolder(folderPath);
    const filesWithContent = [];

    for (const filePath of filePaths) {
        const content = await readFileContent(filePath);
        filesWithContent.push({ filePath, content });
    }

    return filesWithContent;
}
