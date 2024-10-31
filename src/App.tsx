import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import square0 from "./assets/squares/square0.svg";
import square1 from "./assets/squares/square1.svg";
import square2 from "./assets/squares/square2.svg";
import square3 from "./assets/squares/square3.svg";
import square4 from "./assets/squares/square4.svg";
import square5 from "./assets/squares/square5.svg";
import square6 from "./assets/squares/square6.svg";
import square7 from "./assets/squares/square7.svg";
import square8 from "./assets/squares/square8.svg";
import squareflagged from "./assets/squares/squareflagged.svg";
import squarehidden from "./assets/squares/squarehidden.svg";

const squareSvgs = [
  square0,
  square1,
  square2,
  square3,
  square4,
  square5,
  square6,
  square7,
  square8,
];

import "./App.css";

function generateBoard() {
  const board = [];
  for (let i = 0; i < 9; i++) {
    const newRow = [];
    for (let j = 0; j < 9; j++) {
      newRow.push(Math.random() < 0.4 ? -1 : -2);
    }
    board.push(newRow);
  }
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const neighbors = [];
      if (i > 0) {
        if (j > 0) {
          neighbors.push(board[i - 1][j - 1]);
        }
        neighbors.push(board[i - 1][j]);
        if (j < 8) {
          neighbors.push(board[i - 1][j + 1]);
        }
      }
      if (j > 0) {
        neighbors.push(board[i][j - 1]);
      }
      if (j < 8) {
        neighbors.push(board[i][j + 1]);
      }
      if (i < 8) {
        if (j > 0) {
          neighbors.push(board[i + 1][j - 1]);
        }
        neighbors.push(board[i + 1][j]);
        if (j < 8) {
          neighbors.push(board[i + 1][j + 1]);
        }
      }
      if (board[i][j] == -1) {
        continue;
      }
      board[i][j] = neighbors.filter((n) => n == -1).length;
    }
  }
  return board;
}

function App() {
  const [board, setBoard] = useState(generateBoard());

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        {board.map((row, index) => {
          return (
            <div
              key={index}
              style={{
                display: "flex",
                flexDirection: "row",
                flexWrap: "nowrap",
              }}
            >
              {row.map((cell, index) => {
                return (
                  <img
                    src={cell >= 0 ? squareSvgs[cell] : squareflagged}
                    width={window.innerWidth / 2 / 10}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
