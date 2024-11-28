import * as vscode from 'vscode';
import axios, { AxiosError } from 'axios';

/**
 * Extracts the error message from an AxiosError.
 * @param error - The AxiosError object.
 * @returns A string containing the error message.
 */
export function getErrorMessage(error: AxiosError): string {
    const responseData = error.response?.data;
    if (responseData && typeof responseData === 'object' && 'message' in responseData) {
        return (responseData as { message: string }).message;
    }
    return error.message || 'An error occurred.';
}

/**
 * Handles an unknown error, logging or showing the appropriate message.
 * @param error - The error to handle.
 */
export function handleAxiosError(error: unknown) {
    if (axios.isAxiosError(error)) {
        const message = getErrorMessage(error);
        console.error(`Axios Error: ${message}`);
        vscode.window.showErrorMessage(message);
    } else if (error instanceof Error) {
        console.error(`General Error: ${error.message}`);
        vscode.window.showErrorMessage(error.message);
    } else {
        console.error('An unknown error occurred.');
        vscode.window.showErrorMessage('An unknown error occurred.');
    }
}
