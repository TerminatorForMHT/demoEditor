require.config({ paths: { 'vs': './monaco-editor/vs' } });

require(['vs/editor/editor.main'], function () {
  const editor = monaco.editor.create(document.getElementById('editor-container'), {
    value: `# 初始化成功\n def demofunction():\n    print("Hello, World!")\n\n# 调用函数\nif __name__ == "__main__":\n    demofunction()`,
    language: 'python',
    theme: 'vs-light',
    font: 'MSYHack',
  });

  // 示例：监听内容变化
  editor.onDidChangeModelContent(() => {
    console.log('编辑器内容变更：', editor.getValue());
  });
});