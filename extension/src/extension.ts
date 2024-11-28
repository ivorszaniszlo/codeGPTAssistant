import * as vscode from 'vscode';
import { getActiveFileContent, getFilesWithContent } from './utils/fileUtils';
import { sendPrompt, analyzeFiles } from './utils/apiUtils';
import { handleAxiosError } from './utils/errorUtils';

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeGPT Assistant extension is now active!');

    // Command: Ask CodeGPT a question
    let askGPTCommand = vscode.commands.registerCommand('codegpt-assistant.askGPT', async () => {
        try {
            const prompt = await vscode.window.showInputBox({
                prompt: "Ask CodeGPT a question or input code snippet",
            });

            if (!prompt) {
                vscode.window.showWarningMessage("No input provided!");
                return;
            }

            const response = await sendPrompt(prompt);
            vscode.window.showInformationMessage(`CodeGPT: ${response}`);
        } catch (error) {
            handleAxiosError(error);
        }
    });

    // Command: Analyze the active file
    let analyzeFileCommand = vscode.commands.registerCommand('codegpt-assistant.analyzeFile', async () => {
        const fileData = await getActiveFileContent();
        if (!fileData) { 
            return;
        }

        try {
            const response = await sendPrompt(fileData.content);
            vscode.window.showInformationMessage(`Analysis for ${fileData.filePath}: ${response}`);
        } catch (error) {
            handleAxiosError(error);
        }
    });

    // Command: Analyze selected text
    let analyzeSelectionCommand = vscode.commands.registerCommand('codegpt-assistant.analyzeSelection', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage("No active editor found!");
            return;
        }

        const selection = editor.document.getText(editor.selection);
        if (!selection) {
            vscode.window.showWarningMessage("No text selected!");
            return;
        }

        try {
            const response = await sendPrompt(selection);
            vscode.window.showInformationMessage(`CodeGPT Analysis of Selection: ${response}`);
        } catch (error) {
            handleAxiosError(error);
        }
    });

    context.subscriptions.push(askGPTCommand, analyzeFileCommand, analyzeSelectionCommand);
}

export function deactivate() {}
