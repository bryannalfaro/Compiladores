import './App.css';
import Editor from '@monaco-editor/react';
function App() {
  return (

    <div className="App">
      <header className="App-header">
        <Editor
          height="90vh"
          defaultLanguage="javascript"
          theme='vs-dark'
        />
      </header>
    </div>
  );
}

export default App;
