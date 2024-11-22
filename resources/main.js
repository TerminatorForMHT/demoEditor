require.config({ paths: { 'vs': './monaco-editor/vs' } });

let editor;

require(['vs/editor/editor.main'], function () {
  editor = monaco.editor.create(document.getElementById('editor-container'), {
    value: "# Welcome to Monaco Editor\nprint('Hello, Python!')",
    language: 'python', // 默认语言
    theme: 'vs',   // 默认深色主题
    fontSize: 14,       // 默认字体大小
    fontFamily: 'Consolas'
  });
});