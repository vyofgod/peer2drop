#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Python script path
const scriptPath = path.join(__dirname, '..', 'p2p_transfer.py');

// Check Python availability
function getPythonCommand() {
  const commands = ['python3', 'python'];
  
  for (const cmd of commands) {
    try {
      const result = require('child_process').spawnSync(cmd, ['--version'], { encoding: 'utf8' });
      if (result.status === 0) return cmd;
    } catch (e) {
      // Continue to next command
    }
  }
  
  console.error('\x1b[31mError: Python 3 is required but not found.\x1b[0m');
  console.error('Please install Python 3: https://www.python.org/downloads/');
  process.exit(1);
}

// Check and install dependencies
function checkDependencies(pythonCmd) {
  console.log('\x1b[36mChecking dependencies...\x1b[0m');
  
  const result = require('child_process').spawnSync(
    pythonCmd,
    ['-c', 'import cryptography, PyQt6, pyperclip'],
    { encoding: 'utf8' }
  );
  
  if (result.status !== 0) {
    console.log('\x1b[33mDependencies not found. Installing...\x1b[0m');
    console.log('\x1b[90mRunning: pip install -r requirements.txt\x1b[0m\n');
    
    const pipResult = require('child_process').spawnSync(
      pythonCmd,
      ['-m', 'pip', 'install', '-r', path.join(__dirname, '..', 'requirements.txt')],
      { stdio: 'inherit' }
    );
    
    if (pipResult.status !== 0) {
      console.error('\x1b[31mFailed to install dependencies.\x1b[0m');
      process.exit(1);
    }
    
    console.log('\x1b[32mDependencies installed successfully!\x1b[0m\n');
  }
}

// Main
const pythonCmd = getPythonCommand();
checkDependencies(pythonCmd);

console.log('\x1b[32mStarting Peer2Drop...\x1b[0m\n');

// Run Python app
const child = spawn(pythonCmd, [scriptPath], {
  stdio: 'inherit',
  cwd: path.join(__dirname, '..')
});

child.on('error', (err) => {
  console.error('\x1b[31mFailed to start Peer2Drop:\x1b[0m', err.message);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
