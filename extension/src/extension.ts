// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
	// 注册webview提供者
	const provider = new MyWebviewViewProvider(context);
	context.subscriptions.push(
	  vscode.window.registerWebviewViewProvider(
		'iotpilot',
		provider
	  )
	);

	// 监听编辑器选择变化事件，发送选中内容到webview
	context.subscriptions.push(
		vscode.window.onDidChangeTextEditorSelection(event => {
			if (provider.webviewView) {
				provider.sendEditorSelectionToWebview();
			}
		})
	);

	// 监听活动编辑器变化事件，发送当前文件内容到webview
	context.subscriptions.push(
		vscode.window.onDidChangeActiveTextEditor(editor => {
			if (provider.webviewView && editor) {
				provider.sendEditorSelectionToWebview();
			}
		})
	);
  }


class MyWebviewViewProvider implements vscode.WebviewViewProvider {
	public webviewView: vscode.WebviewView | undefined;

	constructor(private readonly context: vscode.ExtensionContext){}

	resolveWebviewView(webviewView: vscode.WebviewView, context: vscode.WebviewViewResolveContext, token: vscode.CancellationToken){
		this.webviewView = webviewView;
		
		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [this.context.extensionUri]
		};
		webviewView.webview.html = this.getWebviewContent(webviewView.webview);

		// 处理来自webview的消息
		webviewView.webview.onDidReceiveMessage(
			message => {
				console.log("Extension received message:", message);
				switch (message.command) {
					case 'acceptCode':
						// 应用代码到当前编辑器
						console.log("Accepting code to editor, length:", message.code?.length || 0);
						this.applyCodeToCurrentEditor(message.code);
						break;
					case 'getSelectedCode':
						// 响应webview的代码选择请求
						this.sendEditorSelectionToWebview();
						break;
					default:
						console.log("Unknown command received:", message.command);
				}
			},
			undefined,
			this.context.subscriptions
		);

		// 初始发送当前编辑器选中内容
		this.sendEditorSelectionToWebview();
	}

	// 获取并发送当前编辑器选中的代码和文件内容到webview
	public sendEditorSelectionToWebview() {
		if (!this.webviewView) {
			return;
		}
		
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			// 没有活动编辑器
			this.webviewView.webview.postMessage({
				command: 'updateEditorContext',
				selectedCode: '',
				fileContent: '',
				fileName: '',
				fileType: '',
				hasSelection: false,
				startLine: 0,
				endLine: 0
			});
			return;
		}

		const document = editor.document;
		const selection = editor.selection;
		const selectedText = document.getText(selection);
		const hasSelection = !selection.isEmpty;
		const fileContent = document.getText();
		const fileName = document.fileName.split(/[\\/]/).pop() || '';
		const fileType = document.languageId;
		const startLine = selection.start.line + 1; // 1-indexed line number
		const endLine = selection.end.line + 1; // 1-indexed line number

		// 发送数据到webview
		this.webviewView.webview.postMessage({
			command: 'updateEditorContext',
			selectedCode: selectedText,
			fileContent: fileContent,
			fileName: fileName,
			fileType: fileType,
			hasSelection: hasSelection,
			startLine: startLine,
			endLine: endLine
		});
	}

	private applyCodeToCurrentEditor(code: string) {
		console.log("Attempting to apply code to editor");
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			console.log("Active editor found:", editor.document.fileName);
			const document = editor.document;
			const fullRange = new vscode.Range(
				document.positionAt(0),
				document.positionAt(document.getText().length)
			);

			editor.edit(editBuilder => {
				console.log("Replacing editor content");
				editBuilder.replace(fullRange, code);
			}).then(success => {
				if (success) {
					console.log("Code successfully applied");
					vscode.window.showInformationMessage('Code successfully applied to current file!');
				} else {
					console.error("Failed to apply code");
					vscode.window.showErrorMessage('Failed to apply code to current file.');
				}
			}, error => {
				console.error("Error applying code:", error);
				vscode.window.showErrorMessage(`Error applying code: ${error}`);
			});
		} else {
			console.warn("No active text editor found");
			vscode.window.showErrorMessage('No active text editor found. Please open a file first.');
		}
	}

	private getWebviewContent(webview: vscode.Webview): string {
		const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'style.css'));
		const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'main.js'));
		const iconUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'icon'));
		const HtmlPath = path.join(this.context.extensionUri.fsPath,'media','index.html');
		let html = fs.readFileSync(HtmlPath, 'utf8');
		html = html.replace('placeholder_style.css', styleUri.toString());
		html = html.replace('placeholder_main.js', scriptUri.toString());
		html = html.replace(/placeholder_icon/g, iconUri.toString());
		return html;
	}
}
// This method is called when your extension is deactivated
export function deactivate() {}
