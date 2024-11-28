import axios, { AxiosInstance, AxiosError } from 'axios';
import * as vscode from 'vscode';

// Create an Axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000', // Replace with your backend URL
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

// Utility function to handle API errors
export function handleApiError(error: unknown): void {
    if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ message?: string }>;
        const errorMessage = axiosError.response?.data?.message || axiosError.message;
        vscode.window.showErrorMessage(`API Error: ${errorMessage}`);
    } else if (error instanceof Error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    } else {
        vscode.window.showErrorMessage('An unknown error occurred while communicating with the API.');
    }
}

// Utility function to send a prompt to the API
export async function sendPrompt(prompt: string): Promise<string> {
    try {
        const response = await apiClient.post<{ response: string }>('/submit', { prompt });
        return response.data.response;
    } catch (error) {
        handleApiError(error);
        throw error; // Rethrow the error for further handling if needed
    }
}

// Utility function to analyze multiple files or folder content
export async function analyzeFiles(files: { filePath: string; content: string }[]): Promise<void> {
    const analysisResults: { filePath: string; response: string }[] = [];
    for (const file of files) {
        try {
            const response = await apiClient.post<{ response: string }>('/submit', { prompt: file.content });
            analysisResults.push({ filePath: file.filePath, response: response.data.response });
        } catch (error) {
            handleApiError(error);
            vscode.window.showErrorMessage(`Error analyzing ${file.filePath}.`);
        }
    }

    // Display the analysis results collectively
    analysisResults.forEach(result => {
        vscode.window.showInformationMessage(`Analyzed ${result.filePath}: ${result.response}`);
    });
}

export default apiClient;
