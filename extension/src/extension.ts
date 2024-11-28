import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeGPT Assistant extension is now active!');

    let disposable = vscode.commands.registerCommand('codegpt-assistant.askGPT', async () => {
        try {
            const prompt = await vscode.window.showInputBox({
                prompt: "Ask CodeGPT a question or input code snippet",
            });

            if (!prompt) {
                vscode.window.showWarningMessage("No input provided!");
                return;
            }

            const response = await axios.post('http://127.0.0.1:8000/submit', { prompt });

            vscode.window.showInformationMessage(`CodeGPT: ${response.data.response}`);
        } catch (error) {
        
            if (axios.isAxiosError(error)) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
            } else if (error instanceof Error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
            } else {
                vscode.window.showErrorMessage('An unknown error occurred.');
            }
        }
    });

    context.subscriptions.push(disposable);
}
export function deactivate() {}

